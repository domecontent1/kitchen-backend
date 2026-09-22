# Kitchen App — Project Context

## 1. Project Purpose

Pallavi's Kitchen is a simple homemade-food ordering application for the user's wife's kitchen.

The application is intentionally **not** designed to become a Zomato/Swiggy-style marketplace.

The primary customer flow is:

1. View the available homemade-food menu.
2. Select dishes and quantities.
3. Select a delivery date.
4. Select an available delivery slot.
5. Select or save a delivery address.
6. Place an order.
7. View previously placed orders.
8. Receive order-status notifications.

The admin/operator is the kitchen owner and personally handles food preparation and delivery.

---

# 2. Current Business Model

## Kitchen

* One kitchen.
* The user's wife's kitchen.
* One ADMIN user/operator.
* Admin personally handles delivery.
* Multiple kitchens are not part of V1.

## Location

* Small-town operation.
* Maximum intended delivery radius: 10 km.
* No GPS/map tracking in V1.
* No delivery-person system.

### Important implementation status

The 10 km delivery-radius rule is a business requirement but is **not currently implemented in the backend**.

The current backend has no latitude/longitude fields and no distance-calculation system.

This should be implemented only when location data is intentionally introduced.

## Food

* Fixed menu.
* Same menu can be available every day.
* Food preparation starts after an order is placed.
* No inventory management.
* No stock tracking.
* No minimum quantity.
* No maximum quantity.
* No application-level customer capacity limits.

## Ordering

* Same-day orders are allowed.
* Orders can be scheduled up to 7 days ahead.
* Customer selects delivery date.
* Customer selects a configured delivery slot.

## Delivery

* Admin personally delivers the food.
* No delivery fee.
* No live delivery tracking.
* No GPS tracking.
* No delivery-person system.

## Pricing

Only dish prices are charged.

Order total:

`sum(quantity × current dish price)`

There is currently:

* No delivery fee.
* No platform fee.
* No service fee.
* No additional fee.

The backend calculates the final total from the current dish prices stored in MongoDB.

The customer does not submit the final price.

## Payment

No payment gateway is implemented in V1.

There is currently:

* No payment gateway.
* No wallet.
* No online payment processing.
* No payment collection inside the order API.

Payment architecture can be introduced later if required.

---

# 3. Technology Stack

## Backend

* Python
* FastAPI
* PyMongo
* MongoDB
* Redis — planned, not currently used
* Celery — planned, not currently used

## Frontend

* Ionic
* Angular
* TypeScript

## Infrastructure

* Docker
* Docker Compose

Dockerization is a future infrastructure step and should not be introduced merely to add complexity.

## Development Tools

* Backend: PyCharm
* Frontend: WebStorm

## Project Root

`D:\Github\kitchen`

```text
D:\Github\kitchen
├── backend
└── frontend
```

---

# 4. Backend Architecture

Current architecture:

```text
Ionic Angular
      │
      │ HTTP/REST
      ▼
   FastAPI
      │
      ▼
   Services
      │
      ▼
   PyMongo Async
      │
      ▼
   MongoDB
```

Authentication architecture:

```text
HTTP Authorization Header
        │
        ▼
Bearer JWT
        │
        ▼
decode_access_token()
        │
        ▼
get_current_user()
        │
        ▼
UserService
        │
        ▼
MongoDB
```

Authorization:

```text
get_current_user()
        │
        ▼
require_admin()
        │
        ▼
ADMIN-only endpoint
```

Current application layering:

```text
Route
  ↓
Service
  ↓
PyMongo Async
  ↓
MongoDB
```

A repository layer has intentionally not been introduced.

Redis and Celery should only be added when a real asynchronous/background-processing requirement exists.

---

# 5. Backend Project Structure

Current application structure:

```text
backend
├── app
│   ├── __init__.py
│   ├── main.py
│   │
│   ├── core
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── database.py
│   │   ├── delivery_config.py
│   │   ├── enums.py
│   │   ├── indexes.py
│   │   ├── security.py
│   │   └── settings.py
│   │
│   ├── models
│   │   └── __init__.py
│   │
│   ├── routes
│   │   ├── __init__.py
│   │   ├── addresses.py
│   │   ├── auth.py
│   │   ├── dashboard.py
│   │   ├── dishes.py
│   │   ├── notifications.py
│   │   ├── orders.py
│   │   └── users.py
│   │
│   ├── schemas
│   │   ├── __init__.py
│   │   ├── address.py
│   │   ├── common.py
│   │   ├── dashboard.py
│   │   ├── dish.py
│   │   ├── notification.py
│   │   ├── order.py
│   │   └── user.py
│   │
│   └── services
│       ├── __init__.py
│       ├── address_service.py
│       ├── dashboard_service.py
│       ├── delivery_service.py
│       ├── dish_service.py
│       ├── notification_service.py
│       ├── order_service.py
│       └── user_service.py
│
├── scripts
│   └── create_admin.py
│
├── tests
│   ├── conftest.py
│   └── test_auth.py
│
├── uploads
│   └── dishes
│
├── .env
├── .env.example
├── .env.test
├── .gitignore
└── requirements.txt
```

All application package `__init__.py` files are intentionally blank.

---

# 6. MongoDB

## Database

Current database:

`kitchen_db`

## Driver

The application uses the modern asynchronous PyMongo API:

```text
pymongo.AsyncMongoClient
```

Motor is not used by the application.

## Connection

Configured through environment variables:

```text
MONGODB_URL
DATABASE_NAME
```

Current local MongoDB URL:

```text
mongodb://localhost:27017
```

---

# 7. MongoDB Collections

Current collections:

```text
users
addresses
dishes
orders
notifications
```

There is intentionally no separate delivery-slots collection.

Delivery slots are configuration-based.

## Intentionally excluded

The following collections are not required for V1:

```text
inventory
payments
wallets
delivery_persons
sellers
kitchens
commissions
coupons
delivery_slots
```

A future business requirement can justify adding additional collections.

---

# 8. MongoDB Indexes

Application startup creates the required indexes.

## Users

Unique phone-number index:

```text
users.phone
```

This prevents duplicate customer phone numbers.

## Addresses

Compound index:

```text
user_id
active
created_at
```

## Orders

Unique idempotency index:

```text
customer_id
idempotency_key
```

The idempotency index uses a partial filter so orders without an idempotency key are not affected.

Additional order indexes:

```text
customer_id + created_at
created_at
```

## Dishes

Compound index:

```text
active
created_at
```

## Notifications

Indexes:

```text
user_id + created_at
user_id + read
```

---

# 9. Domain Entities

Current core entities:

```text
User
Address
Dish
Order
Notification
Delivery Slot configuration
```

## User

User roles:

```text
CUSTOMER
ADMIN
```

User document contains:

```text
_id
name
phone
password_hash
role
active
created_at
updated_at
```

Rules:

* Public registration always creates CUSTOMER.
* ADMIN cannot be selected through public registration.
* Phone number is unique.
* Password is never stored directly.
* Password is hashed with Argon2.
* Accounts can be deactivated.
* JWT identifies the authenticated user.
* JWT contains minimal required claims.

---

# 10. Authentication

Authentication uses:

```text
Phone + Password
```

No OTP is implemented.

No email authentication is implemented.

No social login is implemented.

No refresh token is implemented in V1.

No guest ordering is allowed.

## Registration

Endpoint:

```text
POST /auth/register
```

Flow:

```text
UserRegister validation
        ↓
Phone lookup
        ↓
Duplicate check
        ↓
Argon2 password hash
        ↓
role = CUSTOMER
        ↓
MongoDB
        ↓
UserResponse
```

## Login

Endpoint:

```text
POST /auth/login
```

Flow:

```text
Phone lookup
        ↓
Active-account check
        ↓
Password verification
        ↓
JWT creation
        ↓
TokenResponse
```

Successful login returns:

```text
access_token
token_type
role
```

JWT contains:

```text
sub = user ID
role = user role
exp = expiration time
```

JWT is not stored in MongoDB.

## Swagger authentication

A hidden OAuth2-compatible endpoint exists:

```text
POST /auth/token
```

This allows Swagger's authorization mechanism to authenticate using the same phone/password credentials.

---

# 11. Password Security

Password hashing uses Argon2 through `pwdlib`.

Security responsibilities:

```text
app/core/security.py
```

Functions:

```text
hash_password()
verify_password()
create_access_token()
decode_access_token()
```

Plaintext passwords are never stored in MongoDB.

JWT configuration is loaded from environment variables.

---

# 12. Authorization

Authentication answers:

```text
Who are you?
```

JWT identifies the user.

Authorization answers:

```text
What are you allowed to do?
```

Role determines access.

## Customer

Customers can:

* View active dishes.
* Register.
* Login.
* View/update their profile.
* Create addresses.
* View their addresses.
* Update their addresses.
* Deactivate their addresses.
* Create orders.
* View their own orders.
* View an individual own order.
* Cancel an eligible own order.
* View notifications.
* Mark notifications as read.

## Admin

Admin can additionally:

* View all dishes.
* Create dishes.
* Update dishes.
* Deactivate dishes.
* Reactivate dishes.
* Upload dish images.
* View all orders.
* View individual orders.
* Filter/search orders.
* View order status counts.
* Update order statuses.
* View customer list.
* Search/filter customers.
* View customer details.
* View dashboard statistics.

Customers cannot access ADMIN-only endpoints.

---

# 13. Admin Account

ADMIN is not created through public registration.

Admin creation is controlled through:

```text
scripts/create_admin.py
```

The admin account uses the same secure password hashing system.

Admin document contains:

```text
name
phone
password_hash
role = ADMIN
active
created_at
updated_at
```

The admin account has been designed separately from public customer registration.

---

# 14. Dish Domain

Dish fields:

```text
_id
name
description
price
category
active
image_url
created_at
updated_at
```

## Validation

Dish creation/update validates:

* Name is required.
* Name length is restricted.
* Description is required.
* Description length is restricted.
* Category is required.
* Category length is restricted.
* Price must be greater than zero.

## Dish lifecycle

A dish is not physically deleted.

Deactivation sets:

```text
active = false
```

Reason:

Historical orders must continue to retain their historical dish information.

## Customer menu

Endpoint:

```text
GET /dishes/
```

Returns active dishes only.

## Admin menu

Endpoint:

```text
GET /dishes/admin/all
```

Returns active and inactive dishes.

## Dish management

```text
POST   /dishes/
GET    /dishes/
GET    /dishes/{dish_id}
PUT    /dishes/{dish_id}
DELETE /dishes/{dish_id}
PATCH  /dishes/{dish_id}/reactivate
```

Admin-only operations are protected with `require_admin()`.

---

# 15. Dish Images

Admin can upload an image for a dish.

Endpoint:

```text
PUT /dishes/{dish_id}/image
```

Allowed formats:

```text
JPEG
PNG
WebP
```

Maximum size:

```text
5 MB
```

The backend validates:

* MIME type.
* File is not empty.
* File size.
* File signature.
* WebP file signature.

Images are stored under:

```text
uploads/dishes/
```

The dish stores the resulting image URL.

When a dish image is replaced, the previous image file is removed when possible.

---

# 16. Address Domain

Customer addresses contain:

```text
_id
user_id
label
address_line
landmark
town
pincode
active
created_at
updated_at
```

No latitude/longitude fields currently exist.

No Google Maps integration exists.

## Address ownership

Every address query is restricted using the authenticated user's ID.

Customers cannot access another customer's addresses.

## Address lifecycle

Addresses are deactivated rather than physically deleted.

```text
active = false
```

Customer address endpoints:

```text
POST   /addresses/
GET    /addresses/
GET    /addresses/{address_id}
PUT    /addresses/{address_id}
DELETE /addresses/{address_id}
```

---

# 17. Order Domain

An order contains:

```text
_id
customer_id
customer
items
delivery_date
delivery_slot
delivery_address
total_amount
status
notes
idempotency_key
created_at
updated_at
```

## Order items

Order items are embedded inside the order.

Each item contains:

```text
dish_id
name
price
quantity
subtotal
```

The dish name and price are snapshots.

Reason:

Historical orders must not change when the current dish name or price changes.

## Delivery address snapshot

The order also stores a copy of the selected delivery address.

This means later changes to the customer's saved address do not modify an existing order.

---

# 18. Order Creation

Endpoint:

```text
POST /orders/
```

The endpoint requires authentication.

The customer ID comes from the authenticated JWT user.

The customer cannot submit a customer ID for another user.

## Validation flow

```text
JWT/current user
        ↓
Address ownership validation
        ↓
Address active check
        ↓
Delivery date validation
        ↓
Delivery slot validation
        ↓
Dish validation
        ↓
Active dish check
        ↓
Duplicate dish validation
        ↓
Quantity validation
        ↓
Read current dish price
        ↓
Calculate subtotal
        ↓
Create dish snapshots
        ↓
Create address snapshot
        ↓
Calculate total
        ↓
Insert order
```

## Business rules

* At least one item is required.
* Quantity must be greater than zero.
* Duplicate dishes in one order are rejected.
* Dish must exist.
* Dish must be active.
* Address must belong to the customer.
* Address must be active.
* Delivery date cannot be in the past.
* Delivery date cannot be more than 7 days ahead.
* Delivery slot must match a configured slot.
* Backend calculates the price.
* Backend calculates the total.
* Customer cannot submit the final total.
* Initial order status is `PLACED`.
* No inventory limit exists.
* No minimum/maximum order quantity exists.
* No delivery fee exists.
* No platform fee exists.
* No payment gateway is involved.

---

# 19. Order Idempotency

Order creation supports:

```text
X-Idempotency-Key
```

The key is required by the order creation endpoint.

The database uses a unique compound index involving:

```text
customer_id
idempotency_key
```

This protects against accidental duplicate order creation caused by repeated requests.

---

# 20. Delivery Date Rules

Delivery validation is handled by:

```text
app/services/delivery_service.py
```

Business timezone:

```text
Asia/Kolkata
```

Allowed delivery date range:

```text
Today
through
Today + 7 days
```

Past dates are rejected.

Same-day delivery is supported.

---

# 21. Delivery Slots

Delivery slots are currently configuration-based.

Configuration:

```text
app/core/delivery_config.py
```

Current configured slots:

```text
10:00 - 11:00
11:00 - 12:00
12:00 - 13:00
13:00 - 14:00
17:00 - 18:00
18:00 - 19:00
19:00 - 20:00
```

The backend validates that the requested slot exactly matches a configured slot.

For same-day orders, a slot that has already started is rejected.

There is currently:

* No slot database collection.
* No slot capacity system.
* No maximum orders per slot.
* No slot inventory.
* No dynamic slot management.

---

# 22. Order Status

Current order statuses are centralized in:

```text
app/core/enums.py
```

```text
PLACED
PREPARING
OUT_FOR_DELIVERY
DELIVERED
CANCELLED
```

## Allowed ADMIN transitions

```text
PLACED
  ├── PREPARING
  └── CANCELLED

PREPARING
  ├── OUT_FOR_DELIVERY
  └── CANCELLED

OUT_FOR_DELIVERY
  └── DELIVERED
```

Terminal states:

```text
DELIVERED
CANCELLED
```

A terminal order cannot be moved to another status.

CUSTOMER cannot directly change order status.

ADMIN controls operational order status.

## Customer cancellation

A customer can cancel only an eligible order while it is still:

```text
PLACED
```

After the order progresses, customer cancellation is rejected.

---

# 23. Order Retrieval

## Customer

```text
GET /orders/
GET /orders/{order_id}
```

Customers receive only their own orders.

Orders are sorted newest first.

Ownership is enforced using:

```text
customer_id
```

## Admin

```text
GET /orders/admin
GET /orders/admin/{order_id}
```

Admin can retrieve all orders.

Admin order listing supports:

* Pagination.
* Status filtering.
* Search.

Admin order status counts are available through:

```text
GET /orders/admin/status-counts
```

---

# 24. Notifications

Notifications are stored in MongoDB.

Notification fields:

```text
_id
user_id
order_id
title
message
type
read
created_at
```

Customer notification endpoints:

```text
GET   /notifications/
GET   /notifications/unread-count
PATCH /notifications/{notification_id}/read
PATCH /notifications/read-all
```

Notifications are generated for relevant order-status changes.

Unread notification count is available separately.

---

# 25. Dashboard

Admin dashboard statistics are available through:

```text
GET /dashboard/
```

Dashboard currently provides:

```text
total_orders
placed_orders
preparing_orders
out_for_delivery_orders
delivered_orders
cancelled_orders
active_orders
pending_orders
total_revenue
today_orders
today_revenue
```

Revenue excludes cancelled orders.

Dashboard access is ADMIN-only.

---

# 26. Customer Administration

ADMIN can view customer information.

Customer list endpoint:

```text
GET /users/customers
```

Supports:

* Pagination.
* Search.
* Active/inactive filtering.

Customer details endpoint:

```text
GET /users/customers/{customer_id}
```

Customer details include:

```text
name
phone
active
order_count
total_spent
orders
```

Customer order statistics are calculated from MongoDB order data.

---

# 27. User Profile

Authenticated users can retrieve their own profile:

```text
GET /users/me
```

They can update their name:

```text
PUT /users/me
```

Phone number is not currently changed through the profile endpoint.

---

# 28. API Summary

## Authentication

```text
POST /auth/register
POST /auth/login
POST /auth/token
```

## Users

```text
GET /users/me
PUT /users/me
GET /users/customers
GET /users/customers/{customer_id}
```

## Dishes

```text
POST   /dishes/
GET    /dishes/
GET    /dishes/{dish_id}
PUT    /dishes/{dish_id}
DELETE /dishes/{dish_id}
PATCH  /dishes/{dish_id}/reactivate
PUT    /dishes/{dish_id}/image
GET    /dishes/admin/all
```

## Addresses

```text
POST   /addresses/
GET    /addresses/
GET    /addresses/{address_id}
PUT    /addresses/{address_id}
DELETE /addresses/{address_id}
```

## Orders

```text
POST  /orders/
GET   /orders/
GET   /orders/{order_id}
PATCH /orders/{order_id}/cancel

GET   /orders/admin
GET   /orders/admin/{order_id}
GET   /orders/admin/status-counts
PATCH /orders/admin/{order_id}/status
```

## Notifications

```text
GET   /notifications/
GET   /notifications/unread-count
PATCH /notifications/{notification_id}/read
PATCH /notifications/read-all
```

## Dashboard

```text
GET /dashboard/
```

## Root

```text
GET /
```

---

# 29. Current Configuration

Environment configuration is centralized in:

```text
app/core/settings.py
```

Current variables:

```text
MONGODB_URL
DATABASE_NAME
JWT_SECRET_KEY
JWT_ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES
```

`.env` contains private local configuration.

`.env.example` provides the configuration template.

`.env.test` is used for test configuration.

`.gitignore` prevents environment files and other local/generated files from being committed.

---

# 30. Dependencies

The backend currently uses:

```text
FastAPI
Uvicorn
PyMongo
Pydantic
python-dotenv
python-jose
PyJWT
pwdlib
argon2-cffi
python-multipart
```

Testing dependencies include:

```text
pytest
pytest-asyncio
httpx
```

The application uses:

```text
pymongo.AsyncMongoClient
```

Motor is intentionally not used.

---

# 31. Testing

Current test structure:

```text
backend/tests/
├── conftest.py
└── test_auth.py
```

The test client uses:

```text
httpx.AsyncClient
ASGITransport
```

Tests use a separate MongoDB database:

```text
pallavis_kitchen_test
```

The test setup uses the asynchronous PyMongo client.

`test_auth.py` currently contains no tests and should be expanded as backend functionality becomes stabilized.

Future testing should cover:

* Registration.
* Duplicate registration.
* Login.
* Wrong password.
* Inactive user.
* JWT authentication.
* ADMIN authorization.
* Customer authorization.
* Dish validation.
* Address ownership.
* Order creation.
* Order price calculation.
* Delivery date validation.
* Delivery slot validation.
* Order status transitions.
* Customer cancellation.
* Idempotency.
* Notifications.
* Dashboard calculations.

---

# 32. Current Backend Development Status

The backend has progressed significantly beyond the original MongoDB/Dish prototype.

Completed areas:

```text
✓ FastAPI application
✓ MongoDB connection
✓ PyMongo Async migration
✓ Environment configuration
✓ Security configuration
✓ Password hashing
✓ JWT authentication
✓ Customer registration
✓ Customer login
✓ Admin account
✓ Role-based authorization
✓ User profile
✓ Dish CRUD
✓ Dish activation/deactivation
✓ Dish reactivation
✓ Dish categories
✓ Dish image upload
✓ Address CRUD
✓ Address ownership validation
✓ Order creation
✓ Order price calculation
✓ Order snapshots
✓ Order idempotency
✓ Customer order retrieval
✓ Admin order retrieval
✓ Order search/filter/pagination
✓ Order status transitions
✓ Customer order cancellation
✓ Delivery date validation
✓ Delivery slot validation
✓ Notifications
✓ Unread notification count
✓ Admin dashboard
✓ Admin customer listing
✓ Admin customer details
✓ MongoDB indexes
✓ Configuration cleanup
```

---

# 33. Current Backend Architecture

The current backend follows:

```text
FastAPI Route
      ↓
Authentication / Authorization
      ↓
Service Layer
      ↓
PyMongo Async
      ↓
MongoDB
```

Examples:

```text
routes/dishes.py
      ↓
services/dish_service.py
      ↓
MongoDB
```

```text
routes/orders.py
      ↓
services/order_service.py
      ↓
services/delivery_service.py
      ↓
MongoDB
```

```text
routes/users.py
      ↓
services/user_service.py
      ↓
MongoDB
```

This keeps HTTP concerns separate from business/database operations.

---

# 34. Important Design Decisions

## No repository layer

A repository abstraction has not been introduced because the current application is still small.

If database access becomes sufficiently complex, a repository layer can be introduced later.

## No Beanie

Beanie is not being used.

## No Motor

Motor is not being used.

The project uses modern asynchronous PyMongo.

## No inventory

The application intentionally does not track:

* Stock.
* Available quantity.
* Ingredient inventory.
* Daily dish capacity.

## No payment system

Payment is intentionally excluded from V1.

## No marketplace

There is one kitchen.

No seller marketplace functionality exists.

## No delivery tracking

The admin personally delivers orders.

No GPS tracking or live map tracking exists.

## Historical snapshots

Orders snapshot dish and address information so historical orders remain stable.

---

# 35. Features Not Yet Implemented

The following are known future items rather than completed backend functionality:

```text
- 10 km GPS-based delivery-radius validation
- Latitude/longitude storage
- Google Maps integration
- Dynamic delivery-slot management
- Delivery-slot capacity
- Payment gateway
- Online payment status
- Delivery tracking
- Redis
- Celery
- Background jobs
- Push notifications
- Advanced notification delivery
- Automated order reminders
- Production deployment
- Docker/Compose production setup
- Expanded automated test suite
```

These should only be implemented when there is a real requirement.

---

# 36. Recommended Next Backend Work

The core backend domain is now substantially implemented.

Before adding new business features, the next phase should focus on **backend quality and verification**.

Recommended order:

```text
1. Run the complete backend test suite.
2. Fix any test/configuration issues.
3. Add authentication tests.
4. Add dish validation tests.
5. Add address ownership tests.
6. Add order creation tests.
7. Add order status-transition tests.
8. Add idempotency tests.
9. Add notification tests.
10. Add dashboard tests.
11. Review API response/error consistency.
12. Review MongoDB indexes against actual queries.
13. Review production security configuration.
14. Then continue with frontend integration.
```

The backend should not be considered feature-complete until the important business rules are covered by automated tests.

---

# 37. Development Philosophy

The application should remain:

**Simple + Clean + Practical + Learnable**

Do not add functionality merely because large food-delivery platforms have it.

Every new feature should answer a real business requirement.

The preferred development process is:

```text
Understand
   ↓
Design
   ↓
Implement
   ↓
Test
   ↓
Verify
   ↓
Document
   ↓
Move forward
```

Changes should be incremental.

Existing working functionality should not be unnecessarily redesigned.

---

# 38. Current Position

The original project context described the project as being around the initial MongoDB/Dish development stages.

That is now obsolete.

The actual backend has progressed through:

```text
Project setup
      ↓
FastAPI structure
      ↓
MongoDB integration
      ↓
Dish domain
      ↓
Validation
      ↓
Service architecture
      ↓
Authentication
      ↓
Authorization
      ↓
Admin account
      ↓
Addresses
      ↓
Orders
      ↓
Delivery rules
      ↓
Order lifecycle
      ↓
Notifications
      ↓
Dashboard
      ↓
Customer administration
      ↓
Image uploads
      ↓
Idempotency
      ↓
Configuration cleanup
```

The backend is now at the **testing, verification, consistency, and hardening phase** rather than the initial MongoDB/Dish phase.

---

# 39. Source of Truth

This document describes the **actual implemented backend**, not the original planned implementation.

When this document conflicts with old development notes, the current source code is the source of truth.

The project should continue to update this document whenever a meaningful backend architectural or business-rule change is completed.
