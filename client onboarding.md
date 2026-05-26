client onboarding

1. registration  - client registers as new user
POST /api/accounts/register/

2. accounts verification - client verifies there phone number
POST /api/accounts/verify-phone/

rider onboarding

3.rider registers as new rider to the system
POST /api/accounts/rider/register/

4. rider phone verification
POST /api/accounts/verify-phone/

riderwaits for verification from fagi errands

5. john logs into handler dashboard
POST /api/accounts/login/

6. john reviews pending rider verifications
GET /api/accounts/rider/pending-verifications/

7. john approves or rejects rider verification
POST /api/accounts/rider/verify/ (with rider ID and approval status)

rider get notification ans sms and email for approval

the order journey

8. client places an order
POST /api/orders/shopping/

9. john reviews pending orders
GET /api/orders/handler/orders/?status=pending

10. john check available riders
GET /api/accounts/available-assistants/

11. rider asighnment 
PATCH /api/orders/1001/assign/
rider id is also atached to the asignmet for the purpose to send rider info to the client

12. rider get notification of newly asigned order and views the order
GET /api/orders/1001/

13. rider starts the order
PATCH /api/orders/1001/update-status/


14. client tracks riders real location
GET /api/orders/1001/rider-location/

15. rider completes the order
PATCH /api/orders/1001/update-status/ (with status set to completed)

16. client receives notification of order completion and can rate the service
POST /api/orders/1001/review/

17. Part 3: Payment Flow
POST /api/orders/1001/initiate-payment/

18. client completes payment and mpesa creats call back to fagi errands 
POST /api/payments/mpesa-callback/

payment complete