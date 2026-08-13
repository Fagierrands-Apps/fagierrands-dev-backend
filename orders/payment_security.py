"""
NCBA Payment Security Utilities
================================
Handles all security checks for incoming NCBA payment callbacks:

1. HMAC-SHA256 signature validation
2. IP whitelist enforcement
3. Replay attack prevention (idempotency key tracking via cache)
4. Amount verification (callback amount vs. initiated amount)

Usage in NCBACallbackView:
    from .payment_security import PaymentSecurityValidator

    validator = PaymentSecurityValidator(request)
    ok, error_response = validator.validate_all(payload)
    if not ok:
        return error_response
"""

import hashlib
import hmac
import logging
import time

from django.conf import settings
from django.core.cache import cache
from rest_framework import status
from rest_framework.response import Response

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
REPLAY_CACHE_PREFIX = "ncba_callback_idempotency_"
REPLAY_CACHE_TTL = 60 * 60 * 24  # 24 hours — reject duplicate transaction IDs within this window
AMOUNT_TOLERANCE = 1  # KES — allow 1 shilling rounding difference
DEFAULT_ALLOWED_IPS: list[str] = []  # Populated from settings below


def _get_allowed_ips() -> list[str]:
    """Return the list of allowed NCBA callback source IPs from settings."""
    allowed = getattr(settings, "NCBA_ALLOWED_IPS", "")
    if not allowed:
        return []
    if isinstance(allowed, (list, tuple)):
        return [ip.strip() for ip in allowed if ip.strip()]
    # Support comma-separated string from .env
    return [ip.strip() for ip in allowed.split(",") if ip.strip()]


# ---------------------------------------------------------------------------
# Individual validation functions
# ---------------------------------------------------------------------------

def validate_hmac_signature(request, payload: dict) -> tuple[bool, str | None]:
    """
    Validate the HMAC-SHA256 signature on the callback request.

    NCBA (or your proxy) must send the signature in the header:
        X-NCBA-Signature: sha256=<hex_digest>

    The signature is computed as:
        HMAC-SHA256(secret=NCBA_CALLBACK_SECRET, message=raw_request_body)

    Returns (True, None) if valid, (False, reason) if invalid.
    """
    secret = getattr(settings, "NCBA_CALLBACK_SECRET", "")
    if not secret:
        # Secret not configured — hard fail. Never allow unauthenticated callbacks.
        logger.critical(
            "NCBA_CALLBACK_SECRET is not configured. "
            "Rejecting all callbacks until secret is set."
        )
        return False, "Payment callback security not configured. Contact admin."

    provided_sig = (
        request.headers.get("X-NCBA-Signature")
        or request.headers.get("X-Callback-Signature")
        or request.headers.get("X-Signature")
    )

    if not provided_sig:
        logger.warning(
            "NCBA callback rejected: missing signature header from %s",
            _get_client_ip(request),
        )
        return False, "Missing signature header."

    # Strip optional 'sha256=' prefix
    if provided_sig.startswith("sha256="):
        provided_sig = provided_sig[7:]

    # Compute expected signature from raw body
    try:
        raw_body: bytes = request.body
    except Exception:
        raw_body = b""

    expected_sig = hmac.new(
        secret.encode("utf-8"),
        raw_body,
        hashlib.sha256,
    ).hexdigest()

    if not hmac.compare_digest(expected_sig, provided_sig.lower()):
        logger.warning(
            "NCBA callback rejected: invalid HMAC signature from %s",
            _get_client_ip(request),
        )
        return False, "Invalid signature."

    return True, None


def validate_ip_whitelist(request) -> tuple[bool, str | None]:
    """
    Verify the request comes from a known NCBA IP address.

    Configure allowed IPs via the NCBA_ALLOWED_IPS setting:
        NCBA_ALLOWED_IPS = "196.201.214.200,196.201.214.206"  # comma-separated

    If NCBA_ALLOWED_IPS is empty/not set, the check is SKIPPED (with a warning).
    Set it as soon as you know NCBA's outbound IP range.
    """
    allowed_ips = _get_allowed_ips()

    if not allowed_ips:
        logger.warning(
            "NCBA_ALLOWED_IPS is not configured. IP whitelist check skipped. "
            "Set NCBA_ALLOWED_IPS in .env to enable this protection."
        )
        return True, None  # Skip — don't block, but warn loudly

    client_ip = _get_client_ip(request)

    if client_ip not in allowed_ips:
        logger.warning(
            "NCBA callback rejected: IP %s is not in whitelist %s",
            client_ip,
            allowed_ips,
        )
        return False, f"Request from unauthorized IP: {client_ip}"

    logger.debug("NCBA callback IP %s is whitelisted.", client_ip)
    return True, None


def validate_replay_attack(payload: dict) -> tuple[bool, str | None]:
    """
    Prevent replay attacks by tracking processed transaction IDs.

    Uses Django cache to remember seen TransactionIDs for REPLAY_CACHE_TTL seconds.
    If the same TransactionID arrives again within that window, it is rejected.
    """
    transaction_id = payload.get("TransactionID") or payload.get("transaction_id")

    if not transaction_id:
        # No transaction ID means we can't check — let the handler deal with it
        return True, None

    cache_key = f"{REPLAY_CACHE_PREFIX}{transaction_id}"

    if cache.get(cache_key):
        logger.warning(
            "NCBA callback replay attack detected: TransactionID '%s' already processed.",
            transaction_id,
        )
        return False, f"Duplicate callback: TransactionID '{transaction_id}' already processed."

    # Mark as processed. Use add() so we don't overwrite a value set by a concurrent request.
    # add() is atomic and only sets if the key doesn't already exist.
    stored = cache.add(cache_key, int(time.time()), REPLAY_CACHE_TTL)
    if not stored:
        # Another request beat us to it (race condition) — reject as duplicate
        logger.warning(
            "NCBA callback replay (race): TransactionID '%s' set concurrently.",
            transaction_id,
        )
        return False, f"Duplicate callback: TransactionID '{transaction_id}' already processed."

    return True, None


def validate_amount(payload: dict) -> tuple[bool, str | None]:
    """
    Verify the amount in the callback matches what was initiated.

    Looks up the Payment record by TransactionID and compares:
        callback_amount  vs  payment.final_amount (or payment.amount)

    A tolerance of AMOUNT_TOLERANCE KES is allowed for rounding.

    Returns (True, None) if amounts match, (False, reason) if tampered.
    """
    # Import here to avoid circular imports
    from .models import Payment, OrderPrepayment  # noqa: PLC0415

    transaction_id = payload.get("TransactionID") or payload.get("transaction_id")
    callback_amount_raw = payload.get("Amount") or payload.get("amount")

    if not transaction_id or callback_amount_raw is None:
        # Can't verify without both fields — let the handler decide
        return True, None

    try:
        callback_amount = float(callback_amount_raw)
    except (TypeError, ValueError):
        logger.warning(
            "NCBA callback: cannot parse callback amount '%s' for TX %s",
            callback_amount_raw,
            transaction_id,
        )
        return False, "Invalid amount format in callback."

    # Look up the initiated payment
    payment = None
    try:
        payment = Payment.objects.get(mpesa_checkout_request_id=transaction_id)
    except Payment.DoesNotExist:
        pass

    if payment is None:
        try:
            prepayment = OrderPrepayment.objects.get(mpesa_checkout_request_id=transaction_id)
            initiated_amount = float(prepayment.deposit_amount)
        except OrderPrepayment.DoesNotExist:
            # Payment not found — the handler will return an error; skip amount check
            return True, None
    else:
        # Use final_amount if set and positive, else fall back to amount
        if payment.final_amount and float(payment.final_amount) > 0:
            initiated_amount = float(payment.final_amount)
        else:
            initiated_amount = float(payment.amount)

    if abs(callback_amount - initiated_amount) > AMOUNT_TOLERANCE:
        logger.critical(
            "NCBA AMOUNT TAMPERING DETECTED: TX %s — initiated=%.2f, callback=%.2f",
            transaction_id,
            initiated_amount,
            callback_amount,
        )
        return False, (
            f"Amount mismatch: expected KES {initiated_amount:.2f}, "
            f"got KES {callback_amount:.2f}."
        )

    logger.info(
        "NCBA amount verified for TX %s: KES %.2f matches initiated amount.",
        transaction_id,
        callback_amount,
    )
    return True, None


# ---------------------------------------------------------------------------
# Composite validator
# ---------------------------------------------------------------------------

class PaymentSecurityValidator:
    """
    Run all security checks for an incoming NCBA callback.

    Usage:
        validator = PaymentSecurityValidator(request)
        ok, error_response = validator.validate_all(payload)
        if not ok:
            return error_response
        # proceed with processing...
    """

    def __init__(self, request):
        self.request = request

    def validate_all(self, payload: dict) -> tuple[bool, Response | None]:
        """
        Run all checks in order. Returns (True, None) on success, or
        (False, Response) with the appropriate HTTP error on failure.
        """
        checks = [
            ("hmac_signature", lambda: validate_hmac_signature(self.request, payload)),
            ("ip_whitelist", lambda: validate_ip_whitelist(self.request)),
            ("replay_attack", lambda: validate_replay_attack(payload)),
            ("amount_verification", lambda: validate_amount(payload)),
        ]

        for check_name, check_fn in checks:
            try:
                valid, reason = check_fn()
            except Exception as exc:
                logger.exception("Unexpected error in payment security check '%s': %s", check_name, exc)
                return False, Response(
                    {"status": "error", "message": "Internal security check failed."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            if not valid:
                logger.warning(
                    "NCBA callback BLOCKED by '%s' check: %s | IP: %s",
                    check_name,
                    reason,
                    _get_client_ip(self.request),
                )
                return False, Response(
                    {"status": "error", "message": "Callback validation failed."},
                    status=status.HTTP_403_FORBIDDEN,
                )

        return True, None


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_client_ip(request) -> str:
    """Extract the real client IP, respecting X-Forwarded-For behind a proxy."""
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        # Take the first (leftmost) address — that's the originating client
        return x_forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "unknown")
