"""
FagiErrands Security Test — Steps 1 to 4
Tests every fix made during the security assessment.
Run: python security_test.py
"""

import requests
import time
import sys

BASE = "https://fagierrands-dev-backend.onrender.com"

PASS = "\033[92m✅ PASS\033[0m"
FAIL = "\033[91m❌ FAIL\033[0m"
WARN = "\033[93m⚠️  WARN\033[0m"
INFO = "\033[94mℹ️  INFO\033[0m"

results = {"pass": 0, "fail": 0, "warn": 0}


def check(label, condition, expected_info="", warn_only=False):
    if condition:
        print(f"  {PASS}  {label}")
        results["pass"] += 1
    elif warn_only:
        print(f"  {WARN}  {label}  {expected_info}")
        results["warn"] += 1
    else:
        print(f"  {FAIL}  {label}  {expected_info}")
        results["fail"] += 1


def section(title):
    print(f"\n{'='*65}")
    print(f"  {title}")
    print(f"{'='*65}")


def get(path, token=None, **kwargs):
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    return requests.get(f"{BASE}{path}", headers=headers, timeout=15, **kwargs)


def post(path, data=None, token=None, headers_extra=None, **kwargs):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    if headers_extra:
        headers.update(headers_extra)
    return requests.post(f"{BASE}{path}", json=data, headers=headers, timeout=15, **kwargs)


# ─────────────────────────────────────────────────────────────────────────────
section("STEP 1A — Rate Limiting: /api/accounts/register/")
# ─────────────────────────────────────────────────────────────────────────────
# RegisterThrottle scope = 'register' → 10/day per IP.
# Send 12 attempts with same payload — all hit same IP+scope bucket.
print("  Sending 12 rapid registration attempts (limit: 10/hour per IP)...")
codes = []
for i in range(12):
    r = post("/api/accounts/register/", {"phone_number": "+254711111111", "password": "Test1234!", "user_type": "client"})
    codes.append(r.status_code)

got_throttled = any(c == 429 for c in codes)
check("register/ throttles after 10 attempts (HTTP 429 seen)", got_throttled,
      f"got codes: {codes}")

# ─────────────────────────────────────────────────────────────────────────────
section("STEP 1B — Rate Limiting: /api/accounts/verify-phone/")
# ─────────────────────────────────────────────────────────────────────────────
print("  Sending 12 OTP attempts for same phone (limit: 10/hour)...")
codes = []
for i in range(12):
    r = post("/api/accounts/verify-phone/", {"phone_number": "+254700000099", "otp": f"{i:06d}"})
    codes.append(r.status_code)

got_throttled = any(c == 429 for c in codes)
lockout_fired = any(c == 429 for c in codes[4:])  # lockout kicks in at 5 failures
check("verify-phone/ throttles / lockout fires (HTTP 429 seen)", got_throttled,
      f"got codes: {codes[-4:]}")
check("Lockout fires within first 12 attempts", lockout_fired,
      f"429 not seen in attempts 5-12: {codes[4:]}")

# ─────────────────────────────────────────────────────────────────────────────
section("STEP 1C — Rate Limiting: /api/accounts/resend-otp/")
# ─────────────────────────────────────────────────────────────────────────────
# ResendOTPThrottle scope = 'resend_otp' → 6/hour per IP.
print("  Sending 8 resend-otp attempts (limit: 6/hour per IP)...")
codes = []
for i in range(8):
    r = post("/api/accounts/resend-otp/", {"phone_number": "+254711111111"})
    codes.append(r.status_code)

got_throttled = any(c == 429 for c in codes)
check("resend-otp/ throttles after 6 attempts (HTTP 429 seen)", got_throttled,
      f"got codes: {codes}")

# ─────────────────────────────────────────────────────────────────────────────
section("STEP 2A — Payment Callback: No signature (should 403)")
# ─────────────────────────────────────────────────────────────────────────────
r = post("/api/orders/payments/ncba/callback/", {"OrderID": 1, "TransactionStatus": "SUCCESS", "Amount": 99999})
check("Callback with no signature → 403", r.status_code == 403,
      f"got {r.status_code}")

# ─────────────────────────────────────────────────────────────────────────────
section("STEP 2B — Payment Callback: Wrong signature (should 403)")
# ─────────────────────────────────────────────────────────────────────────────
r = post(
    "/api/orders/payments/ncba/callback/",
    {"OrderID": 1, "TransactionStatus": "SUCCESS", "Amount": 99999},
    headers_extra={"X-Signature": "totallyfakesignature", "X-Timestamp": "9999999999"}
)
check("Callback with wrong signature → 403", r.status_code == 403,
      f"got {r.status_code}")

# ─────────────────────────────────────────────────────────────────────────────
section("STEP 2C — Payment Callback: Old endpoint gone (should 404)")
# ─────────────────────────────────────────────────────────────────────────────
r = post("/api/orders/ncba-callback/", {"test": "data"})
check("Old /ncba-callback/ endpoint → 404", r.status_code == 404,
      f"got {r.status_code}")

# ─────────────────────────────────────────────────────────────────────────────
section("STEP 3A — Secrets: .env files not served")
# ─────────────────────────────────────────────────────────────────────────────
for env_file in [".env", ".env.dev", ".env.cpanel"]:
    r = get(f"/{env_file}")
    check(f"{env_file} not publicly served → 404", r.status_code == 404,
          f"got {r.status_code} — FILE MAY BE EXPOSED")

# ─────────────────────────────────────────────────────────────────────────────
section("STEP 3B — Debug mode off (no stack traces)")
# ─────────────────────────────────────────────────────────────────────────────
r = get("/api/this-endpoint-does-not-exist-at-all/")
has_traceback = "traceback" in r.text.lower() or "exception" in r.text.lower()
check("No Django debug stack trace on 404", not has_traceback,
      f"DEBUG may be True — stack trace found in response")
check("Non-existent endpoint returns 404", r.status_code == 404,
      f"got {r.status_code}")

# ─────────────────────────────────────────────────────────────────────────────
section("STEP 4A — Swagger restricted (should 401/403 without auth)")
# ─────────────────────────────────────────────────────────────────────────────
r = get("/swagger/")
check("Swagger UI requires auth → not 200 publicly", r.status_code != 200,
      f"got {r.status_code} — Swagger is PUBLIC, full API schema exposed")
r = get("/redoc/")
check("ReDoc requires auth → not 200 publicly", r.status_code != 200,
      f"got {r.status_code} — ReDoc is PUBLIC")

# ─────────────────────────────────────────────────────────────────────────────
section("STEP 4B — Unauthenticated access to protected endpoints (all → 401)")
# ─────────────────────────────────────────────────────────────────────────────
protected = [
    ("GET",  "/dashboard/stats/",                    "dashboard stats"),
    ("GET",  "/dashboard/orders/",                   "dashboard all orders"),
    ("GET",  "/dashboard/overview/",                 "dashboard overview"),
    ("POST", "/dashboard/verifications/1/approve/",  "approve rider (admin-only)"),
    ("POST", "/dashboard/verifications/1/reject/",   "reject rider (admin-only)"),
    ("POST", "/dashboard/users/1/suspend/",          "suspend user (admin-only)"),
    ("POST", "/dashboard/users/1/activate/",         "activate user (admin-only)"),
    ("GET",  "/dashboard/export/",                   "export data (admin-only)"),
    ("GET",  "/api/orders/",                         "list orders (handler)"),
    ("GET",  "/api/orders/stats/",                   "order stats (handler)"),
    ("GET",  "/api/orders/handler/all/",             "handler all orders"),
    ("GET",  "/api/orders/handler/pending/",         "handler pending orders"),
    ("GET",  "/api/orders/sos-alerts/",              "SOS alerts (handler)"),
    ("GET",  "/api/accounts/handlers/",              "list handlers"),
    ("GET",  "/api/accounts/user/list/",             "user list (admin/handler)"),
    ("GET",  "/api/locations/saved/",                "saved locations"),
    ("GET",  "/api/locations/rider/1/",              "rider location"),
    ("GET",  "/api/locations/update-current/",       "update current location"),
    ("GET",  "/api/orders/my-orders/",               "my orders"),
    ("GET",  "/api/orders/1/",                       "order detail"),
]

for method, path, label in protected:
    if method == "GET":
        r = get(path)
    else:
        r = post(path)
    check(f"{label} → 401 unauthenticated", r.status_code == 401,
          f"got {r.status_code} at {path}")

# ─────────────────────────────────────────────────────────────────────────────
section("STEP 4C — is_admin() split: handler cannot reach admin-only endpoints")
# ─────────────────────────────────────────────────────────────────────────────
print(f"  {INFO}  These require a live handler token to test fully.")
print(f"        Verifying endpoints exist and reject unauthenticated (401)...")

admin_only = [
    ("/dashboard/verifications/1/approve/", "approve rider"),
    ("/dashboard/verifications/1/reject/",  "reject rider"),
    ("/dashboard/users/1/suspend/",         "suspend user"),
    ("/dashboard/export/",                  "export data"),
]
for path, label in admin_only:
    r = post(path) if "approve" in path or "reject" in path or "suspend" in path else get(path)
    check(f"{label} endpoint exists and gated → 401", r.status_code == 401,
          f"got {r.status_code}")

# ─────────────────────────────────────────────────────────────────────────────
section("STEP 4D — Location privacy: rider location locked down")
# ─────────────────────────────────────────────────────────────────────────────
r = get("/api/locations/rider/1/")
check("Rider location requires auth → 401", r.status_code == 401,
      f"got {r.status_code}")

r = get("/api/locations/rider/999/")
check("Rider location for non-existent ID requires auth → 401", r.status_code == 401,
      f"got {r.status_code}")

# ─────────────────────────────────────────────────────────────────────────────
section("STEP 4E — Order IDOR: order detail requires auth")
# ─────────────────────────────────────────────────────────────────────────────
for oid in [1, 2, 100]:
    r = get(f"/api/orders/{oid}/")
    check(f"Order {oid} detail unauthenticated → 401", r.status_code == 401,
          f"got {r.status_code}")

# ─────────────────────────────────────────────────────────────────────────────
section("SUMMARY")
# ─────────────────────────────────────────────────────────────────────────────
total = results["pass"] + results["fail"] + results["warn"]
print(f"\n  Total checks : {total}")
print(f"  {PASS} Passed  : {results['pass']}")
print(f"  {WARN} Warnings: {results['warn']}")
print(f"  {FAIL} Failed  : {results['fail']}")

if results["fail"] == 0:
    print(f"\n  \033[92m🎉 All checks passed!\033[0m")
else:
    print(f"\n  \033[91m⚠️  {results['fail']} check(s) failed — review output above.\033[0m")
    sys.exit(1)
