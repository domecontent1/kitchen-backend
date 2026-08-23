
# Kitchen App

## Purpose
Homemade food ordering app for wife's kitchen.

## Current business model
- One kitchen
- Admin = owner
- Delivery = owner
- Small town
- Maximum delivery radius = 10 km
- Fixed menu
- Same-day ordering
- Advance ordering up to 7 days
- Customer selects delivery slot

## Intentionally excluded
- Payment gateway
- Delivery tracking
- Delivery fee
- Platform fee
- Inventory/stock management
- Customer limits
- Marketplace
- Multiple kitchens in V1

## Technology
Backend:
- Python
- FastAPI
- MongoDB
- Redis
- Celery

Frontend:
- Ionic
- Angular
- TypeScript

Tools:
- Backend → PyCharm
- Frontend → WebStorm
- Docker

## Current development step
Step 6 — FastAPI + MongoDB connection


Kitchen App — Development Progress

## Current Step

Step 6 — FastAPI + MongoDB connection

## Completed

- [x] Project root created
- [x] Backend created
- [x] Frontend directory created
- [x] Python virtual environment created
- [x] FastAPI installed
- [x] Uvicorn installed
- [x] FastAPI application running
- [x] Swagger documentation working
- [x] Backend folder structure created
- [x] MongoDB domain designed
- [x] MongoDB approach selected
- [x] PyMongo installed

## Current Task

Connect FastAPI to local MongoDB.

## Next

Create the first MongoDB document for the Dish entity.



# Kitchen App — Project Context

## 1. Project Purpose

A simple, clean homemade-food ordering app for the user's wife's kitchen.

The goal is NOT to build a Zomato/Swiggy-style platform.

The application should make it very easy for customers to:

* View the fixed homemade-food menu
* Select a delivery date
* Select dishes and quantities
* Select a delivery slot
* Select/save their address
* Place an order
* View their orders

The admin/operator is the user, who will prepare and personally deliver the food.

---

## 2. Current Business Model

### Kitchen

* One kitchen initially
* The user's wife's kitchen
* User is the only admin
* User personally handles delivery
* Future possibility: approximately 4–5 additional kitchens/cooks
* Multiple kitchens are NOT part of V1

### Location

* Small town
* Maximum delivery radius: 10 km
* Backend should validate the customer's delivery location against the kitchen location

### Food

* Fixed menu
* Same menu is available every day
* Food preparation starts after customer orders
* No inventory management
* No stock tracking
* No minimum quantity
* No maximum quantity
* No "available quantity" concept
* Customer quantity is not restricted by the application

### Ordering

* Same-day orders are allowed
* Customers can schedule orders up to 7 days in advance
* Customer selects the delivery date
* Customer selects a delivery slot

### Delivery

* User personally delivers the food
* Maximum delivery radius: 10 km
* No delivery-person system
* No live delivery tracking
* No map tracking
* No Zomato/Swiggy-style delivery status
* No delivery fee

### Pricing

Only the dish price is charged.

There are currently:

* No delivery fee
* No platform fee
* No service fee
* No additional fee

Order total is:

`sum(quantity × dish price)`

### Payment

* No payment gateway in V1
* No complex payment system currently
* No wallet model currently
* Payment architecture can be added later if required

### Customer limits

* No application-level customer limit
* No artificial order/customer capacity restrictions

---

# 3. Technology Stack

## Backend

* Python
* FastAPI
* PyMongo
* MongoDB
* Redis
* Celery

## Frontend

* Ionic
* Angular
* TypeScript

## Infrastructure

* Docker
* Docker Compose eventually

## Development Tools

* Backend: PyCharm
* Frontend: WebStorm

## Project Root

`D:\Github\kitchen`

Structure:

```text
D:\Github\kitchen
│
├── backend
└── frontend
```

---

# 4. Backend Structure

Current structure:

```text
backend
│
├── app
│   ├── __init__.py
│   ├── main.py
│   │
│   ├── routes
│   │   ├── __init__.py
│   │   ├── test.py
│   │   └── dishes.py
│   │
│   ├── models
│   │   └── __init__.py
│   │
│   ├── schemas
│   │   ├── __init__.py
│   │   └── dish.py
│   │
│   ├── services
│   │   └── __init__.py
│   │
│   └── core
│       ├── __init__.py
│       └── database.py
│
└── .venv
```

---

# 5. Architecture Direction

Current architecture:

```text
Ionic Angular
      │
      │ HTTP/REST
      ▼
   FastAPI
      │
      ▼
   PyMongo
      │
      ▼
   MongoDB
```

Redis and Celery will be introduced where they provide a real purpose, rather than adding unnecessary complexity.

Eventually:

```text
FastAPI
   │
   ├── MongoDB
   │
   └── Redis
          │
          ▼
       Celery
```

Docker will be introduced later after the application is understood and working locally.

---

# 6. Domain Design

Current core entities:

```text
User
Address
Dish
Order
Delivery Slot
```

Order contains:

```text
Customer
Order Items
Delivery Date
Delivery Slot
Delivery Address Snapshot
Total Amount
Status
```

Current order statuses:

```text
PLACED
CONFIRMED
COMPLETED
CANCELLED
```

No complex delivery-status lifecycle is required.

---

# 7. MongoDB Design

Initial database:

`kitchen_db`

Initial collections:

```text
users
dishes
addresses
orders
delivery_slots
```

Intentionally excluded for V1:

```text
inventory
payments
wallets
delivery_persons
sellers
kitchens
commissions
coupons
```

### Important MongoDB design decisions

Order items will be embedded inside an order.

Example:

```text
Order
└── items[]
    ├── dish_id
    ├── dish_name
    ├── quantity
    ├── unit_price
    └── total
```

The order will also contain a snapshot of the delivery address.

Reason:

Orders are historical records and should not change when a customer's saved address or a dish's current price/name changes.

---

# 8. Completed Development Steps

## Step 1 — Initial Project Setup

Completed:

* Created project root
* Created `backend`
* Created `frontend`
* Created Python virtual environment
* Installed FastAPI
* Installed Uvicorn
* Created initial FastAPI application
* Verified FastAPI server
* Verified Swagger documentation

---

## Step 2 — FastAPI Backend Structure

Completed:

* Created `app`
* Moved `main.py` into `app`
* Created Python package files
* Created:

  * `routes`
  * `models`
  * `schemas`
  * `services`
  * `core`
* Verified application still runs with:

```text
uvicorn app.main:app --reload
```

---

## Step 3 — Domain Design

Completed:

* Defined User
* Defined Dish
* Defined Address
* Defined Order
* Defined Order Items
* Defined Delivery Slot
* Defined order lifecycle
* Defined 10 km delivery rule
* Defined 7-day advance ordering
* Defined fixed menu
* Removed unnecessary inventory/capacity concepts

---

## Step 4 — MongoDB Design

Completed:

* Designed `kitchen_db`
* Designed initial collections
* Decided to embed order items
* Decided to snapshot dish information inside orders
* Decided to snapshot delivery address inside orders
* Identified future indexing requirements
* Decided not to prematurely create marketplace/payment/inventory collections

---

## Step 5 — MongoDB Driver

Completed:

* Selected PyMongo
* Selected the modern async PyMongo API
* Decided not to use MongoEngine
* Decided not to use Beanie initially
* Decided not to use Motor for this new project

Installed:

```text
pymongo
```

---

## Step 6 — MongoDB Connection

Completed:

* MongoDB is installed locally
* MongoDB Compass is installed
* Created `app/core/database.py`
* Created MongoDB client using `AsyncMongoClient`
* Connected application to:

```text
mongodb://localhost:27017
```

* Selected database:

```text
kitchen_db
```

* Created temporary `/db-test` route
* Verified FastAPI can communicate with MongoDB

---

## Step 7 — First Dish

Completed:

* Created `schemas/dish.py`
* Created `DishCreate` Pydantic schema
* Created `routes/dishes.py`
* Created `POST /dishes/`
* Inserted first Dish into MongoDB
* Verified Dish in MongoDB Compass
* Created `GET /dishes/`
* Successfully retrieved dishes through FastAPI

Current example dish:

```text
Poha
Price: ₹50
```

---

# 9. Current API Endpoints

## Test

```text
GET /
GET /db-test
```

## Dishes

```text
POST /dishes/
GET /dishes/
```

These are currently basic implementations and will be improved/refactored later.

---

# 10. Current Development Position

### Completed

```text
Step 1 ✓ Project setup
Step 2 ✓ FastAPI structure
Step 3 ✓ Domain design
Step 4 ✓ MongoDB design
Step 5 ✓ MongoDB driver
Step 6 ✓ MongoDB connection
Step 7 ✓ First Dish
```

### Current next step

**Step 8 — Pydantic validation and response schemas**

We need to improve the Dish API before adding more functionality.

Topics:

* Proper validation
* Positive price validation
* Required/non-empty fields
* Response schemas
* MongoDB `_id` handling
* Difference between create schema and response schema

---

# 11. Development Method

The project is being built deliberately step-by-step for learning.

Rules:

1. Do not provide the entire application at once.
2. Introduce one concept at a time.
3. Explain why the architecture is being chosen.
4. Implement a small feature.
5. Test it.
6. Understand it.
7. Update this `PROJECT_CONTEXT.md`.
8. Move to the next step.

The user wants to understand the application rather than copy a complete codebase.

---

# 12. Important Future Direction

The architecture should remain clean enough that approximately 4–5 additional kitchens/cooks can be introduced in the future.

However, marketplace functionality should NOT be implemented now.

Future expansion may introduce:

```text
Kitchen
kitchen_id
Cook
seller-related functionality
```

Only when the real business requires it.

---

# 13. Current Rule

Keep the application:

**Simple + Clean + Practical + Learnable**

Do not add features merely because large food-delivery platforms have them.



Do these in order:

Update schemas/dish.py
Add DishResponse
Update routes/dishes.py
Delete the old Poha document from Compass
Create Poha again
Test valid data
Test invalid price
Test missing fields
Test GET /dishes/

Expected valid response:

{
    "id": "...",
    "name": "Poha",
    "description": "Fresh homemade poha",
    "price": 50,
    "active": true
}


## Step 9 — Service Layer and Dish CRUD

Completed:

- Introduced `DishService`
- Moved MongoDB operations out of the route
- Route now handles HTTP/API concerns
- Service handles dish database operations
- Added dish creation service
- Added get-all-dishes service
- Added get-single-dish service
- Added deactivate-dish service

Current dish endpoints:

POST   /dishes/
GET    /dishes/
GET    /dishes/{dish_id}
DELETE /dishes/{dish_id}

Important business decision:

DELETE does not physically remove a dish.

It sets:

active = false

Reason:

Historical orders may reference dishes that are no longer on the active menu.

Architecture:

Route
  ↓
Service
  ↓
MongoDB

Next step:

Step 10 — Dish update + proper error handling.

Topics:
- DishUpdate schema
- PUT vs PATCH
- Invalid ObjectId handling
- 404 Dish Not Found
- Cleaner API error responses


## Step 11 — Dish Module Refactoring

Completed:

- Added `dish_to_response()` helper
- Removed repeated MongoDB-to-API response conversion code
- Kept HTTP/API responsibilities in the route
- Kept database operations in `DishService`
- Decided NOT to introduce a repository layer yet
- Current architecture remains:

Route
  ↓
Service
  ↓
PyMongo
  ↓
MongoDB

Dish module structure:

schemas/dish.py
    ↓
routes/dishes.py
    ↓
services/dish_service.py
    ↓
core/database.py
    ↓
MongoDB

Important business rule:

Inactive dishes should eventually be hidden from customer-facing menus.

Admin should still be able to see inactive dishes.

We will handle this properly after authentication/authorization is implemented.

Current Dish endpoints:

POST   /dishes/
GET    /dishes/
GET    /dishes/{dish_id}
PUT    /dishes/{dish_id}
DELETE /dishes/{dish_id}

DELETE means deactivate:

active = false

No physical deletion is performed.

Next major step:

Step 12 — User and Authentication Design.

Before coding authentication, decide:

- Customer registration
- Admin account
- Login method
- Password handling
- JWT access token
- Refresh token requirements
- User roles
- Authorization rules



## Step 13 — User Database and Schema Design

Authentication design locked:

- Roles: CUSTOMER and ADMIN
- Registration: phone + password
- Login: phone + password
- Authentication: JWT Bearer token
- Access token: yes
- Refresh token: no for V1
- OTP: no for V1
- Email authentication: no
- Google/social login: no
- Public admin registration: no
- Guest orders: no

User MongoDB document:

- _id
- name
- phone
- password_hash
- role
- active
- created_at
- updated_at

User rules:

- Public registration always creates CUSTOMER
- ADMIN cannot be selected through public registration
- User accounts are deactivated rather than physically deleted
- Phone number must be unique
- Password is never stored directly
- Password will be hashed using Argon2
- JWT will identify the authenticated user
- JWT should contain minimal claims

Created schema:

app/schemas/user.py

Schemas:

- UserRole
- UserRegister
- UserLogin
- UserResponse
- TokenResponse

Next:

Step 14 — Password hashing and security foundation.


## Step 14 — Password Security Foundation

Completed:

- Installed `pwdlib[argon2]`
- Added `app/core/security.py`
- Added `hash_password()`
- Added `verify_password()`
- Passwords will be stored only as Argon2 hashes
- Plaintext passwords will never be stored
- Password test confirmed:
  - Correct password → True
  - Wrong password → False

Security direction:

password
  ↓
Argon2
  ↓
password_hash
  ↓
MongoDB

Authentication implementation order:

Step 14 → Password hashing
Step 15 → User service + registration
Step 16 → JWT + login
Step 17 → Current user + protected routes

JWT secret will be stored through environment configuration rather than hardcoded in Python.

Temporary `/password-test` endpoint should be removed after verification.

Next:

Step 15 — User service + customer registration.



## Step 15 — User Service and Registration

Completed:

- Created `app/services/user_service.py`
- Created `app/routes/auth.py`
- Added `POST /auth/register`
- Added customer creation flow
- Password is hashed using Argon2 before storage
- Public registration always creates CUSTOMER
- Added `active` field
- Added `created_at`
- Added `updated_at`
- Added phone-number lookup
- Added duplicate-phone validation
- Added `app/core/indexes.py`
- Added unique MongoDB index on `users.phone`
- Added FastAPI lifespan initialization
- Application creates required user indexes during startup

Registration flow:

POST /auth/register
    ↓
UserRegister validation
    ↓
Check phone
    ↓
Hash password
    ↓
role = CUSTOMER
    ↓
active = true
    ↓
MongoDB
    ↓
UserResponse

Current user collections:

users

Current user fields:

_id
name
phone
password_hash
role
active
created_at
updated_at

Next:

Step 16 — Login and JWT authentication.
## Step 16 — JWT Login

Completed:

- Created `.env`
- Created `.gitignore`
- Created `backend/requirements.txt`
- Added `PyJWT`
- Added `python-dotenv`
- Added JWT configuration
- Added JWT secret through environment variables
- Added `create_access_token()`
- Added `decode_access_token()`
- Added `POST /auth/login`
- Added password verification during login
- Added inactive-account check
- Added JWT access token generation
- JWT contains:
  - sub = user ID
  - role = user role
  - exp = expiration time

Authentication behavior:

Wrong phone/password:
401 Unauthorized

Inactive account:
403 Forbidden

Successful login:
JWT access token returned

JWT is not stored in MongoDB.

Current authentication flow:

Register
  ↓
Hash password
  ↓
MongoDB

Login
  ↓
Find user
  ↓
Verify password
  ↓
Create JWT
  ↓
Return access token

Environment/configuration:

.env
  ↓
JWT_SECRET_KEY
JWT_ALGORITHM
JWT_ACCESS_TOKEN_EXPIRE_MINUTES

.gitignore prevents .env from being committed.

Next:

## Step 17 — Current User and Protected Routes

Completed:

- Created `app/core/auth.py`
- Added `OAuth2PasswordBearer`
- Added `get_current_user()`
- JWT is decoded for protected requests
- User ID is extracted from JWT `sub`
- User is loaded from MongoDB
- Inactive users are rejected
- Created `app/routes/users.py`
- Added `GET /users/me`
- Protected `/users/me` using FastAPI `Depends()`
- Verified unauthenticated requests receive 401
- Verified authenticated requests return current user information

Authentication flow:

Authorization header
    ↓
Bearer JWT
    ↓
decode JWT
    ↓
extract user ID
    ↓
MongoDB users lookup
    ↓
check active
    ↓
current_user
    ↓
protected endpoint

Authentication:
Who are you?
    ↓
JWT

Authorization:
What are you allowed to do?
    ↓
Role

Current roles:

CUSTOMER
ADMIN

Next:

Step 18 — Role-based authorization.

Goals:

- Create `require_admin()`
- Protect admin-only dish operations
- Allow customers to access customer functionality
- Keep public/customer/admin responsibilities clear


## Step 19 — Admin Account

Completed:

- Created controlled admin creation script
- Admin is NOT created through public registration
- Admin role is assigned only through controlled setup
- Admin password is stored as Argon2 hash
- Admin account contains:
  - name
  - phone
  - password_hash
  - role
  - active
  - created_at
  - updated_at
- Successfully logged in as ADMIN
- ADMIN can manage dishes
- CUSTOMER cannot manage dishes
- Role-based authorization is working

Admin creation:

Terminal
  ↓
scripts/create_admin.py
  ↓
ADMIN user
  ↓
MongoDB

Current roles:

CUSTOMER
ADMIN

Next:

Step 20 — Authentication/authorization cleanup and user-service refactoring.
## Step 20 — Authentication Cleanup

Completed:

- Moved user lookup by ID into `UserService`
- `get_current_user()` no longer accesses MongoDB directly
- Authentication dependency now uses `UserService`
- `security.py` handles password hashing and JWT operations
- `auth.py` handles authentication dependencies and authorization checks
- `UserService` handles user database operations
- `require_admin()` provides ADMIN authorization
- Customer authentication tested
- Admin authentication tested
- Customer access to admin dish operations rejected
- Admin access to dish management confirmed

Current authentication architecture:

Route
  ↓
Authentication dependency
  ↓
UserService
  ↓
MongoDB

Security responsibilities:

security.py
- hash_password()
- verify_password()
- create_access_token()
- decode_access_token()

auth.py
- get_current_user()
- require_admin()

user_service.py
- get_user_by_phone()
- get_user_by_id()
- create_customer()

Next:

Step 21 — Application domain design before building Addresses and Orders.
## Step 21 — Application Domain Design

V1 application remains intentionally simple.

Core entities:

- User
- Dish
- Address
- Order

Relationships:

User
  ├── many Addresses
  └── many Orders

Order
  └── embedded Order Items
          └── references Dish

Order contains a historical snapshot of:

- Dish name
- Dish price
- Quantity
- Subtotal
- Delivery address

Reason for snapshots:

Historical orders must not change when a dish price or customer address changes later.

Address V1 fields:

- id
- user_id
- label
- address_line
- landmark
- town
- pincode
- active
- created_at
- updated_at

No GPS/latitude/longitude for V1.

No Google Maps integration for V1.

Delivery:

- Maximum delivery radius: 10 km
- Same-day delivery supported
- Customers can book up to 7 days ahead
- Customer selects delivery date
- Customer selects delivery slot
- No delivery fee
- No platform fee
- No payment gateway in V1
- No delivery tracking/GPS
- Admin personally handles delivery

Inventory:

- No inventory tracking
- No stock quantity system
- No minimum/maximum dish quantity rules
- Food preparation starts after customer order

Order status:

- PLACED
- PREPARING
- OUT_FOR_DELIVERY
- DELIVERED
- CANCELLED

Order does not initially contain payment gateway information.

Order total is calculated by backend from dish prices and quantities.

Delivery slots:

- Keep V1 simple
- No separate delivery_slots collection yet unless later requirements justify it
- Selected slot will be stored with the order

Next:

Step 22 — Address schema and AddressService.

## Step 23 — Address API

Completed:

- Created `app/routes/addresses.py`
- Added customer-protected address endpoints
- Added POST /addresses/
- Added GET /addresses/
- Added GET /addresses/{address_id}
- Added PUT /addresses/{address_id}
- Added DELETE /addresses/{address_id}
- DELETE deactivates address rather than physically deleting it
- Address ownership is determined from authenticated user
- Customers cannot access another customer's address
- Address list only returns active addresses

Address flow:

JWT
  ↓
get_current_user()
  ↓
current user ID
  ↓
AddressService
  ↓
MongoDB

Address ownership rule:

Every address query includes the authenticated user's ID.

Address data:

- user_id
- label
- address_line
- landmark
- town
- pincode
- active
- created_at
- updated_at

Next:

Step 24 — Order schema and order-item design.
## Step 25 — Order Creation

Completed:

- Created `app/services/order_service.py`
- Created `app/routes/orders.py`
- Added `POST /orders/`
- Order creation requires authenticated customer
- Customer ID comes from JWT/current user
- Address ownership is validated
- Only active customer addresses can be used
- Delivery date cannot be in the past
- Delivery date can be booked up to 7 days ahead
- Order requires at least one item
- Quantity must be greater than zero
- No inventory/stock limits implemented
- Dish must exist and be active
- Dish price is read from MongoDB
- Backend calculates item subtotal
- Backend calculates order total
- Customer cannot submit the final price
- Dish name and price are snapshotted into order items
- Delivery address is snapshotted into the order
- Initial order status is `PLACED`
- No payment gateway logic
- No delivery fee
- No platform fee
- No delivery tracking

Order creation flow:

JWT
  ↓
Current customer
  ↓
Address ownership validation
  ↓
Delivery date validation
  ↓
Dish validation
  ↓
Price calculation
  ↓
Dish snapshots
  ↓
Address snapshot
  ↓
Total calculation
  ↓
MongoDB order

Next:

Step 26 — Customer order retrieval + admin order retrieval.
## Step 26 — Order Retrieval

Completed:

- Customer can retrieve their own orders
- Customer can retrieve an individual own order
- Orders are sorted newest first
- Customer ownership is enforced using customer_id
- Customer cannot retrieve another customer's order
- Added ADMIN order retrieval endpoint
- ADMIN can retrieve all orders
- CUSTOMER receives 403 for admin order retrieval

Customer endpoints:

GET /orders/
GET /orders/{order_id}

Admin endpoint:

GET /orders/admin/all

Next:

Step 27 — Order status management.
## Step 27 — Order Status Management

Completed:

- Added OrderStatusUpdate schema
- Added ADMIN-only order status endpoint
- Added order status transition validation
- Initial order status is PLACED
- Allowed transitions:

PLACED
  -> PREPARING
  -> OUT_FOR_DELIVERY
  -> DELIVERED

Cancellation:

PLACED -> CANCELLED
PREPARING -> CANCELLED

Terminal states:

DELIVERED
CANCELLED

- CUSTOMER cannot change order status
- ADMIN controls order status
- Invalid status transitions are rejected
- No delivery tracking system
- No GPS tracking
- No separate status collection

Next:

Step 28 — Delivery date and delivery-slot rules.
## Step 28 — Delivery Date and Slot Rules

Completed:

- Created `app/services/delivery_service.py`
- Moved delivery-date validation out of OrderService
- Same-day delivery is supported
- Delivery can be booked up to 7 days ahead
- Past delivery dates are rejected
- Delivery slot start time must be before end time
- Created delivery configuration structure
- No delivery-slot database collection
- No slot capacity system
- No inventory limits
- No delivery tracking
- No GPS tracking

Current delivery rules:

Maximum booking window:
Today → Today + 7 days

Delivery radius:
Maximum 10 km

Current V1 approach:

Delivery date:
Validated by DeliveryService

Delivery slot:
Validated by DeliveryService

Slot availability/capacity:
Not implemented yet

GPS/distance:
Not implemented yet

Next:

Step 29 — Dish/menu API cleanup and customer menu behavior.
## Step 29 — Dish/Menu Refinement

Completed:

- Customer menu now returns active dishes only
- Added `get_active_dishes()` to DishService
- Added `get_all_dishes()` to DishService
- Added ADMIN-only `GET /dishes/admin/all`
- Customer/public menu remains accessible without authentication
- Admin can see both active and inactive dishes
- Admin remains the only role allowed to create/update/deactivate dishes
- Removed/avoided stray dish database logic from route layer
- Dish menu does not use inventory quantities
- No minimum/maximum dish quantity rules
- No daily menu collection
- No menu scheduling system

Customer menu:

GET /dishes/
    ↓
active dishes only

Admin menu:

GET /dishes/admin/all
    ↓
all dishes

Next:

Step 30 — Order validation and business-rule cleanup.
## Step 30 — Order Validation and Business Rules

Completed:

- Duplicate dishes are rejected within a single order
- Delivery slots are validated against configured available slots
- Arbitrary delivery time ranges are rejected
- Delivery slots remain configuration-based
- No delivery slot capacity system
- No inventory system
- Same configured slots can apply across multiple delivery dates
- Backend remains responsible for business-rule validation

Current order validation:

Customer identity:
JWT/current user

Address:
Must belong to customer
Must be active

Dish:
Must exist
Must be active

Quantity:
Must be greater than zero

Duplicate dishes:
Not allowed

Delivery date:
Today through today + 7 days

Delivery slot:
Must match configured available slot

Price:
Calculated from current active dish price

Total:
Calculated by backend

Historical snapshot:
Dish name + price + quantity + subtotal
Delivery address

Next:

Step 31 — Backend project configuration cleanup
## Step 31 — Backend Configuration Files

Created backend configuration files:

D:\Github\kitchen\backend\.env
D:\Github\kitchen\backend\.gitignore
D:\Github\kitchen\backend\requirements.txt

`.env` contains private configuration and must not be committed.

Current environment variables:

- MONGODB_URL
- DATABASE_NAME
- JWT_SECRET_KEY
- JWT_ALGORITHM
- ACCESS_TOKEN_EXPIRE_MINUTES

`.gitignore` protects:

- .env
- virtual environments
- Python cache
- IDE files
- logs
- test/coverage files

`requirements.txt` initially generated from the working virtual environment.

Configuration has not yet been wired into the application code.

Next:

Step 32 — Wire environment configuration into database and security settings.
## Step 32 — Environment Configuration Integration

Completed:

- MongoDB configuration moved to `.env`
- `MONGODB_URL` loaded from environment
- `DATABASE_NAME` loaded from environment
- JWT secret loaded from environment
- JWT algorithm loaded from environment
- JWT expiration loaded from environment
- Added `python-dotenv`
- MongoDB connection tested successfully
- Customer login tested after configuration change
- Admin login tested after configuration change
- Protected endpoint tested after configuration change
- No secrets are hard-coded in source code

Backend private configuration:

.env

Required variables:

- MONGODB_URL
- DATABASE_NAME
- JWT_SECRET_KEY
- JWT_ALGORITHM
- ACCESS_TOKEN_EXPIRE_MINUTES

Next:

Step 33 — Final backend dependency/configuration cleanup.
## Step 33 — Backend Configuration Cleanup

Completed:

- Created `app/core/settings.py`
- Centralized environment configuration
- MongoDB configuration now uses `settings`
- JWT configuration now uses `settings`
- `.env` remains private
- `.env.example` created as configuration template
- `.env` remains ignored by Git
- `requirements.txt` regenerated after dependency installation
- Added/confirmed required dependencies including Motor and python-dotenv
- Database connection tested
- Authentication tested after configuration refactor
- Protected endpoint tested after configuration refactor

Configuration architecture:

.env
  ↓
app/core/settings.py
  ↓
database.py
security.py

Private configuration:

.env

Public configuration template:

.env.example

Next:

Step 34 — Backend API consistency and error-handling cleanup.
