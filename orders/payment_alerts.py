"""
Payment Alerting System
========================
Sends alerts for:
1. Amount tampering detected on a callback
2. Replay attack attempts
3. Suspicious callback patterns (high volume from one IP)
4. Reconciliation anomalies (payments stuck in Processing too long)

Delivery channels:
- Always: Django logger (ERROR / CRITICAL level)
- If configured: Email to PAYMENT_ALERT_EMAILS in settings
- If configured: SMS to PAYMENT_ALERT_PHONE in settings (via TextPie)
"""

import logging
from datetime import timedelta

from django.conf import settings
from django.core.cache import cache
from django.core.mail import send_mail
from django.utils import timezone

logger = logging.getLogger(__name__)

# ── Settings helpers ─────────────────────────────────────────────────────────

def _alert_emails() -> list[str]:
    """Return list of admin emails to alert. From PAYMENT_ALERT_EMAILS setting."""
    raw = getattr(settings, "PAYMENT_ALERT_EMAILS", "")
    if not raw:
        return []
    if isinstance(raw, (list, tuple)):
        return list(raw)
    return [e.strip() for e in raw.split(",") if e.strip()]


def _alert_phone() -> str:
    """Return admin phone number for SMS alerts. From PAYMENT_ALERT_PHONE setting."""
    return getattr(settings, "PAYMENT_ALERT_PHONE", "")


def _send_email_alert(subject: str, body: str):
    """Send email alert to all configured admin emails."""
    emails = _alert_emails()
    if not emails:
        return
    from_email = getattr(settings, "DEFAULT_FROM_EMAIL", "no-reply@fagierrands.com")
    try:
        send_mail(
            subject=f"[FagiErrands Payment Alert] {subject}",
            message=body,
            from_email=from_email,
            recipient_list=emails,
            fail_silently=True,
        )
        logger.info("Payment alert email sent to %s: %s", emails, subject)
    except Exception as exc:
        logger.error("Failed to send payment alert email: %s", exc)


def _send_sms_alert(message: str):
    """Send SMS alert to configured admin phone."""
    phone = _alert_phone()
    if not phone:
        return
    try:
        from core.sms_service import send_sms
        send_sms(phone, f"[FagiErrands Alert] {message}")
        logger.info("Payment alert SMS sent to %s", phone)
    except Exception as exc:
        logger.error("Failed to send payment alert SMS: %s", exc)


# ── Alert functions ───────────────────────────────────────────────────────────

def alert_amount_tampering(transaction_id: str, initiated_amount: float, callback_amount: float, ip: str = "unknown"):
    """
    Fire when callback amount doesn't match the initiated payment amount.
    This is the most critical alert — someone is trying to cheat the system.
    """
    subject = f"AMOUNT TAMPERING DETECTED — TX {transaction_id}"
    body = (
        f"CRITICAL: Payment amount tampering detected.\n\n"
        f"Transaction ID : {transaction_id}\n"
        f"Initiated amount: KES {initiated_amount:.2f}\n"
        f"Callback amount : KES {callback_amount:.2f}\n"
        f"Difference      : KES {abs(callback_amount - initiated_amount):.2f}\n"
        f"Source IP       : {ip}\n"
        f"Time            : {timezone.now().isoformat()}\n\n"
        f"The callback was REJECTED. Investigate this IP immediately."
    )

    logger.critical(
        "PAYMENT ALERT — Amount tampering: TX=%s initiated=%.2f callback=%.2f IP=%s",
        transaction_id, initiated_amount, callback_amount, ip,
    )
    _send_email_alert(subject, body)
    _send_sms_alert(f"Amount tampering TX {transaction_id}: KES {initiated_amount:.2f} vs {callback_amount:.2f} from {ip}")


def alert_replay_attack(transaction_id: str, ip: str = "unknown"):
    """
    Fire when the same TransactionID is submitted more than once.
    Could be an attacker replaying a captured callback.
    """
    # Rate-limit this alert — don't spam for the same TX
    cache_key = f"alert_replay_sent_{transaction_id}"
    if cache.get(cache_key):
        return  # Already alerted for this TX
    cache.set(cache_key, 1, 3600)  # Only alert once per hour per TX

    subject = f"REPLAY ATTACK — TX {transaction_id}"
    body = (
        f"WARNING: Duplicate payment callback received.\n\n"
        f"Transaction ID : {transaction_id}\n"
        f"Source IP       : {ip}\n"
        f"Time            : {timezone.now().isoformat()}\n\n"
        f"The duplicate was REJECTED. This may be a replay attack."
    )

    logger.warning(
        "PAYMENT ALERT — Replay attack: TX=%s IP=%s", transaction_id, ip,
    )
    _send_email_alert(subject, body)


def alert_suspicious_callback_volume(ip: str, count: int, window_minutes: int = 10):
    """
    Fire when too many callbacks arrive from the same IP in a short window.
    Threshold: PAYMENT_ALERT_CALLBACK_VOLUME_THRESHOLD (default 20 per 10 min).
    """
    threshold = getattr(settings, "PAYMENT_ALERT_CALLBACK_VOLUME_THRESHOLD", 20)
    if count < threshold:
        return

    # Rate-limit: alert once per IP per hour
    cache_key = f"alert_volume_sent_{ip}"
    if cache.get(cache_key):
        return
    cache.set(cache_key, 1, 3600)

    subject = f"SUSPICIOUS CALLBACK VOLUME from {ip}"
    body = (
        f"WARNING: High callback volume from single IP.\n\n"
        f"Source IP      : {ip}\n"
        f"Count          : {count} callbacks in {window_minutes} minutes\n"
        f"Threshold      : {threshold}\n"
        f"Time           : {timezone.now().isoformat()}\n\n"
        f"Consider blocking this IP via NCBA_ALLOWED_IPS whitelist."
    )

    logger.warning(
        "PAYMENT ALERT — Suspicious volume: IP=%s count=%d in %dmin",
        ip, count, window_minutes,
    )
    _send_email_alert(subject, body)


def alert_reconciliation_anomaly(payment_id: int, order_id: int, transaction_id: str, stuck_minutes: int):
    """
    Fire when a payment has been stuck in 'Processing' longer than the threshold.
    Called by the reconcile_payments management command.
    """
    subject = f"STUCK PAYMENT — Payment #{payment_id} Order #{order_id}"
    body = (
        f"Payment has been stuck in 'Processing' status.\n\n"
        f"Payment ID     : {payment_id}\n"
        f"Order ID       : {order_id}\n"
        f"Transaction ID : {transaction_id or 'N/A'}\n"
        f"Stuck for      : {stuck_minutes} minutes\n"
        f"Time           : {timezone.now().isoformat()}\n\n"
        f"The reconciliation job has queried NCBA for the current status.\n"
        f"Check the server logs for the resolution result."
    )

    logger.warning(
        "PAYMENT ALERT — Stuck payment: payment_id=%d order_id=%d tx=%s stuck=%dmin",
        payment_id, order_id, transaction_id or "N/A", stuck_minutes,
    )
    _send_email_alert(subject, body)


def track_callback_volume(ip: str):
    """
    Track callback count per IP in a 10-minute window.
    Call on every incoming callback (before or after validation).
    Automatically fires alert_suspicious_callback_volume if threshold exceeded.
    """
    cache_key = f"callback_volume_{ip}"
    count = cache.get(cache_key, 0) + 1
    cache.set(cache_key, count, 600)  # 10-minute rolling window

    if count >= getattr(settings, "PAYMENT_ALERT_CALLBACK_VOLUME_THRESHOLD", 20):
        alert_suspicious_callback_volume(ip, count, window_minutes=10)

    return count
