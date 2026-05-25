# 📋 FagiErrands API Flow - Quick Reference

## All Errand Types Complete Flow

---

## 🔐 ONBOARDING (Same for All)

### Client Onboarding
1. Client registration - `POST /api/accounts/register/`
2. Phone verification - `POST /api/accounts/verify-phone/`

### Rider Onboarding
3. Rider registration with documents - `POST /api/accounts/rider/register/`
4. Rider phone verification - `POST /api/accounts/verify-phone/`
5. Handler login - `POST /api/accounts/login/`
6. Handler reviews pending riders - `GET /api/accounts/pending-verifications/`
7. Handler approves rider - `PATCH /api/accounts/assistant-verification/{id}/approve/`

---

## 🛒 TYPE 1: SHOPPING ERRAND

### Order Creation & Assignment
8. Client places shopping order - `POST /api/orders/shopping/`
9. Handler reviews pending orders - `GET /api/orders/handler/orders/?status=pending`
10. Handler checks available riders - `GET /api/accounts/available-assistants/`
11. Handler assigns rider - `PATCH /api/orders/{id}/assign/`

### Order Execution
12. Rider views order details - `GET /api/orders/{id}/`
13. Rider starts order - `PATCH /api/orders/{id}/update-status/` (status: in_progress)
    - System generates release code & sends to client
14. Rider uploads receipt - `POST /api/orders/{id}/images/`
15. Rider updates final price - `PATCH /api/orders/{id}/finalize-price/`
16. Client tracks rider location - `GET /api/orders/{id}/rider-location/`
17. Rider completes order with release code - `PATCH /api/orders/{id}/update-status/` (status: completed, release_code)

### Post-Order
18. Client rates service - `POST /api/orders/{id}/review/`
19. Client initiates payment - `POST /api/orders/{id}/initiate-payment/`
20. M-Pesa callback - `POST /api/payments/mpesa-callback/`

---

## 📦 TYPE 2: PICKUP & DELIVERY

### Order Creation & Assignment
8. Client places pickup/delivery order - `POST /api/orders/pickup-delivery/`
   - Required: pickup_address, delivery_address, recipient_name, contact_number
9. Handler reviews pending orders - `GET /api/orders/handler/orders/?status=pending`
10. Handler checks available riders - `GET /api/accounts/available-assistants/`
11. Handler assigns rider - `PATCH /api/orders/{id}/assign/`

### Order Execution
12. Rider views order details - `GET /api/orders/{id}/`
13. Rider starts order - `PATCH /api/orders/{id}/update-status/` (status: in_progress)
    - System generates release code & sends to client
14. Rider uploads pickup proof - `POST /api/orders/{id}/images/` (stage: pickup)
15. Client tracks rider location - `GET /api/orders/{id}/rider-location/`
16. Rider uploads delivery proof - `POST /api/orders/{id}/images/` (stage: delivery)
17. Rider completes order with release code - `PATCH /api/orders/{id}/update-status/` (status: completed, release_code)

### Post-Order
18. Client rates service - `POST /api/orders/{id}/review/`
19. Client initiates payment - `POST /api/orders/{id}/initiate-payment/`
20. M-Pesa callback - `POST /api/payments/mpesa-callback/`

---

## 🚚 TYPE 3: CARGO DELIVERY

### Order Creation & Assignment
8. Client places cargo delivery order - `POST /api/orders/cargo-delivery/`
   - Required: pickup_address, delivery_address, cargo_type, cargo_weight, cargo_dimensions
   - Optional: cargo_value, special_instructions
9. Handler reviews pending orders - `GET /api/orders/handler/orders/?status=pending`
10. Handler checks available riders - `GET /api/accounts/available-assistants/`
11. Handler assigns rider - `PATCH /api/orders/{id}/assign/`

### Order Execution
12. Rider views order details - `GET /api/orders/{id}/`
13. Rider starts order - `PATCH /api/orders/{id}/update-status/` (status: in_progress)
    - System generates release code & sends to client
14. Rider uploads cargo photos at pickup - `POST /api/orders/{id}/images/` (stage: pickup)
15. Rider sets cargo value (if applicable) - `POST /api/orders/cargo-value/`
16. Client tracks rider location - `GET /api/orders/{id}/rider-location/`
17. Rider uploads cargo photos at delivery - `POST /api/orders/{id}/images/` (stage: delivery)
18. Rider completes order with release code - `PATCH /api/orders/{id}/update-status/` (status: completed, release_code)

### Post-Order
19. Client rates service - `POST /api/orders/{id}/review/`
20. Client initiates payment - `POST /api/orders/{id}/initiate-payment/`
21. M-Pesa callback - `POST /api/payments/mpesa-callback/`

---

## 🔑 KEY DIFFERENCES BY TYPE

### Shopping Errand
- **Unique**: Shopping items list, receipt upload, price finalization
- **Payment**: Delivery fee + items total
- **Images**: Receipt required

### Pickup & Delivery
- **Unique**: Recipient details, pickup/delivery proof
- **Payment**: Based on distance only
- **Images**: Pickup proof + delivery proof

### Cargo Delivery
- **Unique**: Cargo details (type, weight, dimensions), cargo value, multiple photos
- **Payment**: Based on distance + cargo weight/size
- **Images**: Multiple cargo photos at pickup & delivery

---

## 📱 SMS NOTIFICATIONS (All Types)

1. Client registration verification
2. Rider registration verification
3. Rider approval notification
4. Order confirmation (client)
5. Rider assigned (client)
6. Order started + release code (client)
7. Order completed (client)
8. Payment confirmation (client)

---

## 🔐 SECURITY FEATURES (All Types)

- Phone verification required
- Document verification for riders
- Handler approval required
- **Release code verification** (6 digits)
- JWT authentication
- Image proof required

---

## 💰 PRICING BY TYPE

### Shopping
```
Base: KSh 200 (up to 7km)
Extra: KSh 20/km (beyond 7km)
Items: Actual shopping total
Total: Delivery fee + Items total
```

### Pickup & Delivery
```
Base: KSh 200 (up to 7km)
Extra: KSh 20/km (beyond 7km)
Total: Delivery fee only
```

### Cargo Delivery
```
Base: KSh 200 (up to 7km)
Extra: KSh 20/km (beyond 7km)
Weight surcharge: Variable
Total: Delivery fee + weight surcharge
```

---

## 📊 ORDER STATUS FLOW (All Types)

```
pending → assigned → in_progress → completed
                  ↓
              cancelled (optional)
```

---

**Created**: 2026-05-25  
**Source**: Actual system endpoints from codebase
