"""
Management Command: reconcile_payments
=======================================
Finds payments stuck in 'Processing' status and queries NCBA
to get their real status, then updates DB accordingly.

Usage:
    python manage.py reconcile_payments
    python manage.py reconcile_payments --minutes 60       # stuck > 60 min (default: 30)
    python manage.py reconcile_payments --dry-run          # show what would be fixed, don't write
    python manage.py reconcile_payments --limit 50         # max payments to process

Schedule: Run via cron every 15 minutes in production.
    */15 * * * * /path/to/venv/bin/python manage.py reconcile_payments >> /logs/reconcile.log 2>&1
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Reconcile stuck Processing payments by querying NCBA for their real status."

    def add_arguments(self, parser):
        parser.add_argument(
            "--minutes",
            type=int,
            default=30,
            help="Consider payments stuck if in Processing for more than N minutes (default: 30)",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            default=False,
            help="Print what would be changed without writing to DB",
        )
        parser.add_argument(
            "--limit",
            type=int,
            default=100,
            help="Maximum number of payments to process per run (default: 100)",
        )

    def handle(self, *args, **options):
        minutes = options["minutes"]
        dry_run = options["dry_run"]
        limit = options["limit"]

        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN — no changes will be written."))

        cutoff = timezone.now() - timedelta(minutes=minutes)

        from orders.models import Payment, Order
        from orders.ncba_service import NCBAService
        from orders.payment_alerts import alert_reconciliation_anomaly

        stuck_payments = Payment.objects.filter(
            status="Processing",
            updated_at__lt=cutoff,
            mpesa_checkout_request_id__isnull=False,
        ).exclude(
            mpesa_checkout_request_id=""
        ).select_related("order")[:limit]

        total = stuck_payments.count()
        self.stdout.write(f"Found {total} stuck payment(s) older than {minutes} minutes.")

        if total == 0:
            self.stdout.write(self.style.SUCCESS("Nothing to reconcile."))
            return

        ncba = NCBAService()
        resolved_completed = 0
        resolved_failed = 0
        still_processing = 0
        errors = 0

        for payment in stuck_payments:
            tx_id = payment.mpesa_checkout_request_id
            stuck_minutes = int((timezone.now() - payment.updated_at).total_seconds() / 60)

            self.stdout.write(
                f"  Payment #{payment.id} | Order #{payment.order_id} | "
                f"TX: {tx_id} | Stuck: {stuck_minutes}min"
            )

            # Fire reconciliation alert for admin awareness
            try:
                alert_reconciliation_anomaly(
                    payment_id=payment.id,
                    order_id=payment.order_id,
                    transaction_id=tx_id,
                    stuck_minutes=stuck_minutes,
                )
            except Exception as e:
                logger.warning("Failed to send reconciliation alert: %s", e)

            # Query NCBA for real status
            try:
                query_result = ncba.stk_query(tx_id)
                ncba_status = query_result.get("status") or query_result.get("Status", "")
                ncba_status = str(ncba_status).upper()

                self.stdout.write(f"    NCBA status: {ncba_status}")

                if ncba_status == "SUCCESS":
                    if not dry_run:
                        from django.db import transaction as db_transaction
                        with db_transaction.atomic():
                            payment.status = "Completed"
                            payment.transaction_id = (
                                query_result.get("MpesaReceiptNumber")
                                or query_result.get("TransactionID")
                                or tx_id
                            )
                            payment.save(update_fields=["status", "transaction_id", "updated_at"])

                            # Update order if still in a payable state
                            order = payment.order
                            if order.status in ["Pending", "PaymentPending"]:
                                order.status = "Completed"
                                order.completed_at = timezone.now()
                                order.save(update_fields=["status", "completed_at"])
                                self.stdout.write(
                                    self.style.SUCCESS(
                                        f"    ✅ Payment #{payment.id} → Completed | Order #{order.id} → Completed"
                                    )
                                )
                            else:
                                self.stdout.write(
                                    self.style.SUCCESS(
                                        f"    ✅ Payment #{payment.id} → Completed (order already {order.status})"
                                    )
                                )
                    else:
                        self.stdout.write(self.style.SUCCESS(f"    [DRY RUN] Would mark Payment #{payment.id} Completed"))
                    resolved_completed += 1

                elif ncba_status in ("FAILED", "CANCELLED", "EXPIRED"):
                    if not dry_run:
                        payment.status = "Failed"
                        payment.save(update_fields=["status", "updated_at"])
                        self.stdout.write(
                            self.style.WARNING(f"    ⚠️  Payment #{payment.id} → Failed ({ncba_status})")
                        )
                    else:
                        self.stdout.write(
                            self.style.WARNING(f"    [DRY RUN] Would mark Payment #{payment.id} Failed")
                        )
                    resolved_failed += 1

                else:
                    # Still processing at NCBA side — leave it, check again next run
                    self.stdout.write(f"    ⏳ Still pending at NCBA ({ncba_status})")
                    still_processing += 1

            except Exception as exc:
                logger.error(
                    "reconcile_payments: error querying NCBA for payment %d TX %s: %s",
                    payment.id, tx_id, exc,
                )
                self.stdout.write(self.style.ERROR(f"    ❌ NCBA query failed: {exc}"))
                errors += 1

        # Summary
        self.stdout.write("")
        self.stdout.write("=" * 50)
        self.stdout.write(f"Reconciliation complete {'(DRY RUN) ' if dry_run else ''}:")
        self.stdout.write(self.style.SUCCESS(f"  Resolved → Completed : {resolved_completed}"))
        self.stdout.write(self.style.WARNING(f"  Resolved → Failed    : {resolved_failed}"))
        self.stdout.write(f"  Still processing     : {still_processing}")
        if errors:
            self.stdout.write(self.style.ERROR(f"  Errors               : {errors}"))
        self.stdout.write("=" * 50)

        logger.info(
            "reconcile_payments: total=%d completed=%d failed=%d pending=%d errors=%d dry_run=%s",
            total, resolved_completed, resolved_failed, still_processing, errors, dry_run,
        )
