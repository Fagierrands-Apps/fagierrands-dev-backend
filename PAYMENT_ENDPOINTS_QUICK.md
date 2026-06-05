# NCBA Payment Endpoints - Quick Reference

## 🎯 Payment Flow (3 Steps)

### 1. Initiate Payment (Triggers STK Push)
```
POST /api/orders/payments/initiate/
```
**Body:**
```json
{
  "order": 1,
  "amount": 100,
  "payment_method": "ncba",
  "phone_number": "0712345678"
}
```
**Response:** Payment ID + STK pushed to phone

---

### 2. Check Payment Status (Poll this)
```
GET /api/orders/payments/{payment_id}/
```
**Response:**
```json
{
  "id": 123,
  "status": "completed",
  "amount": "100.00"
}
```

---

### 3. Check Order Payment Status (Alternative)
```
GET /api/orders/{order_id}/payment-status/
```
**Response:**
```json
{
  "order_id": 1,
  "has_payment": true,
  "payment": {
    "status": "completed"
  }
}
```

---

## 🔄 Optional Endpoints

### Retry STK Push (if failed)
```
POST /api/orders/payments/{payment_id}/process/
```

### Cancel Payment
```
POST /api/orders/payments/{payment_id}/cancel/
```

### Generate QR Code
```
POST /api/orders/payments/ncba/qr-generate/
```
**Body:**
```json
{
  "amount": 100,
  "order_id": 1
}
```

---

## ⚡ Typical Flow

1. **POST** `/payments/initiate/` → Get payment_id, STK sent
2. **Poll** `/payments/{payment_id}/` every 3 seconds
3. **Status** changes from `pending` → `processing` → `completed`
4. Done!
