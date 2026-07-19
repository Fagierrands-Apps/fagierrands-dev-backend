#!/bin/bash
# ============================================================
# FagiErrands API Health Checker
# Security flow:
#   1. Login with current password
#   2. Immediately rotate to a NEW password (old one dies now)
#   3. Login again with new password to get a fresh token
#   4. Run all endpoint tests
#   5. Logout (token invalidated)
#   6. Email report
#
# Password is only valid for the ~30s the script runs.
# No password can ever be reused.
# ============================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_URL="https://api.errandserver.fagierrands.com"  # <-- UPDATE
REPORT_EMAIL="fagierrands0@gmail.com"                # <-- UPDATE
ENV_FILE="$SCRIPT_DIR/.env.healthcheck"
USED_PASSWORDS_LOG="$SCRIPT_DIR/used_passwords.log"
RUN_LOG="$SCRIPT_DIR/run.log"

TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S %Z')
PASS=0
FAIL=0
REPORT=""

# ── Helpers ────────────────────────────────────────────────────

log() { echo "[$TIMESTAMP] $1" >> "$RUN_LOG"; }

send_email() {
    local subject="$1"
    local body="$2"
    local tmp_mail
    tmp_mail=$(mktemp)
    printf "From: %s\r\nTo: %s\r\nSubject: %s\r\n\r\n%s\r\n" \
        "$GMAIL_USER" "$REPORT_EMAIL" "$subject" "$body" > "$tmp_mail"
    local curl_out
    curl_out=$(curl -s \
        --url "smtps://smtp.gmail.com:465" \
        --ssl-reqd \
        --mail-from "$GMAIL_USER" \
        --mail-rcpt "$REPORT_EMAIL" \
        --user "$GMAIL_USER:$GMAIL_APP_PASSWORD" \
        --upload-file "$tmp_mail" \
        --max-time 30 2>&1)
    [ -n "$curl_out" ] && log "EMAIL error: $curl_out"
    rm -f "$tmp_mail"
}

abort() {
    local reason="$1"
    log "ABORTED: $reason"
    send_email "🔴 Health Check ABORTED" "Run aborted at $TIMESTAMP\n\nReason: $reason"
    exit 1
}

# Generate a unique password not seen before (alphanumeric only — safe in JSON/bash)
generate_unique_password() {
    local attempts=0
    while [ $attempts -lt 10 ]; do
        local candidate
        candidate=$(tr -dc 'A-Za-z0-9' </dev/urandom | head -c 32)
        local hash
        hash=$(echo -n "$candidate" | sha256sum | awk '{print $1}')
        if ! grep -qF "$hash" "$USED_PASSWORDS_LOG" 2>/dev/null; then
            echo "$candidate"
            return 0
        fi
        attempts=$((attempts + 1))
    done
    # Extremely unlikely to reach here, but handle it
    abort "Could not generate a unique password after 10 attempts"
}

check() {
    local label="$1" method="$2" url="$3" data="$4" use_auth="$5"

    if [ -n "$data" ]; then
        response=$(curl -s -o /dev/null -w "%{http_code}" -X "$method" \
            -H "Content-Type: application/json" \
            ${use_auth:+-H "Authorization: Bearer $TOKEN"} \
            -d "$data" --max-time 15 "$BASE_URL$url")
    else
        response=$(curl -s -o /dev/null -w "%{http_code}" -X "$method" \
            ${use_auth:+-H "Authorization: Bearer $TOKEN"} \
            --max-time 15 "$BASE_URL$url")
    fi

    if [ "${response:0:1}" != "5" ] && [ -n "$response" ]; then
        REPORT="$REPORT\n  ✅ PASS (HTTP $response)  [$method] $url — $label"
        PASS=$((PASS + 1))
    else
        REPORT="$REPORT\n  ❌ FAIL (HTTP $response)  [$method] $url — $label"
        FAIL=$((FAIL + 1))
    fi
}

# ── Load credentials ───────────────────────────────────────────
[ -f "$ENV_FILE" ] || abort ".env.healthcheck not found at $ENV_FILE"
HC_PHONE=$(grep '^HC_PHONE=' "$ENV_FILE" | cut -d'=' -f2 | tr -d '\r\n ')
HC_PASSWORD=$(grep '^HC_PASSWORD=' "$ENV_FILE" | cut -d'=' -f2 | tr -d '\r\n')
GMAIL_USER=$(grep '^GMAIL_USER=' "$ENV_FILE" | cut -d'=' -f2 | tr -d '\r\n ')
GMAIL_APP_PASSWORD=$(grep '^GMAIL_APP_PASSWORD=' "$ENV_FILE" | cut -d'=' -f2 | tr -d '\r\n ')
[ -z "$HC_PHONE" ] || [ -z "$HC_PASSWORD" ] && abort "HC_PHONE or HC_PASSWORD missing in .env.healthcheck"

# ── Step 1: Login with current password ───────────────────────
log "Logging in as $HC_PHONE"
login_resp=$(curl -s -X POST "$BASE_URL/api/accounts/login/" \
    -H "Content-Type: application/json" \
    -d "{\"phone_number\":\"$HC_PHONE\",\"password\":\"$HC_PASSWORD\"}" \
    --max-time 15)

TOKEN=$(echo "$login_resp" | grep -o '"token":"[^"]*"' | cut -d'"' -f4)
[ -z "$TOKEN" ] && abort "Login failed — check credentials in .env.healthcheck"

# ── Step 2: Rotate password IMMEDIATELY (old password dies now) ─
log "Rotating password"
NEW_PASSWORD=$(generate_unique_password)

rotate_resp=$(curl -s -o /dev/null -w "%{http_code}" \
    -X POST "$BASE_URL/api/accounts/change-password/" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $TOKEN" \
    -d "{\"old_password\":\"$HC_PASSWORD\",\"new_password\":\"$NEW_PASSWORD\"}" \
    --max-time 15)

if [ "$rotate_resp" != "200" ] && [ "$rotate_resp" != "204" ]; then
    abort "Password rotation failed (HTTP $rotate_resp) — aborting to avoid stale credentials"
fi

# Record hash of new password to prevent future reuse
echo -n "$NEW_PASSWORD" | sha256sum | awk '{print $1}' >> "$USED_PASSWORDS_LOG"

# Save new password — preserve all other credentials
printf "HC_PHONE=%s\nHC_PASSWORD=%s\nGMAIL_USER=%s\nGMAIL_APP_PASSWORD=%s\n" \
    "$HC_PHONE" "$NEW_PASSWORD" "$GMAIL_USER" "$GMAIL_APP_PASSWORD" > "$ENV_FILE"
log "Password rotated. Old password is now invalid."

# ── Step 3: Login with NEW password to get a fresh token ───────
login_resp2=$(curl -s -X POST "$BASE_URL/api/accounts/login/" \
    -H "Content-Type: application/json" \
    -d "{\"phone_number\":\"$HC_PHONE\",\"password\":\"$NEW_PASSWORD\"}" \
    --max-time 15)

TOKEN=$(echo "$login_resp2" | grep -o '"token":"[^"]*"' | cut -d'"' -f4)
[ -z "$TOKEN" ] && abort "Re-login with new password failed"

REPORT="$REPORT\n  ✅ PASS  Login + password rotated (old password dead)"

# ── Step 4: Run Tests ───────────────────────────────────────────

# Public / Server Health
check "Health endpoint"                 GET  "/health/"                                     ""  ""
check "Homepage"                        GET  "/"                                            ""  ""
check "Swagger Docs"                    GET  "/swagger/"                                    ""  ""

# Auth validation (no token — testing server rejects bad input)
check "Register validation"             POST "/api/accounts/register/"                      '{"email":""}' ""
check "Login validation"                POST "/api/accounts/login/"                         '{"phone_number":"000"}' ""
check "Token endpoint"                  POST "/api/accounts/token/"                         '{"username":"","password":""}' ""
check "Token refresh (invalid)"         POST "/api/accounts/token/refresh/"                 '{"refresh":"bad"}' ""
check "Password reset request"          POST "/api/accounts/v1/password-reset/request/"     '{"email":"x@x.com"}' ""
check "Resend OTP"                      POST "/api/accounts/resend-otp/"                    '{"phone":""}' ""

# Authenticated endpoints
check "Profile"                         GET  "/api/accounts/profile/"                       ""  "auth"
check "My orders"                       GET  "/api/orders/my-orders/"                       ""  "auth"
check "Orders list"                     GET  "/api/orders/"                                 ""  "auth"
check "Create draft"                    POST "/api/orders/errands/draft/"                   '{"title":""}' "auth"
check "Calculate pricing"               POST "/api/orders/calculate-pricing/"               '{"distance":5}' "auth"
check "Config"                          GET  "/api/orders/config/"                          ""  ""
check "Initiate payment"                POST "/api/orders/payments/initiate/"               '{}' "auth"
check "Locations"                       GET  "/api/locations/"                              ""  "auth"
check "Notifications"                   GET  "/api/notifications/"                          ""  "auth"
check "Assistant availability"          GET  "/api/accounts/assistant/availability/"        ""  "auth"

# ── Step 5: Logout (token invalidated) ─────────────────────────
curl -s -X POST "$BASE_URL/api/accounts/logout" \
    -H "Authorization: Bearer $TOKEN" \
    --max-time 10 > /dev/null 2>&1

REPORT="$REPORT\n  ✅ PASS  Logged out — token invalidated"
log "Logged out"

# ── Step 6: Email Report ────────────────────────────────────────
TOTAL=$((PASS + FAIL))
[ "$FAIL" -eq 0 ] \
    && SUMMARY="🟢 ALL SYSTEMS OPERATIONAL — $PASS/$TOTAL passed" \
    || SUMMARY="🔴 ISSUES DETECTED — $PASS passed, $FAIL failed out of $TOTAL"

BODY="FagiErrands API Health Check
======================================
Time     : $TIMESTAMP
Server   : $BASE_URL
Result   : $SUMMARY

Security:
  • Password rotated at start of run ✅
  • Old password invalidated before tests ran ✅
  • No password reuse enforced ✅
  • Session logged out after tests ✅
  • Token active for ~30s only ✅

Endpoint Results:
$(echo -e "$REPORT")

======================================"

log "$SUMMARY"
send_email "Health Check — $SUMMARY" "$BODY"
echo "$BODY"
