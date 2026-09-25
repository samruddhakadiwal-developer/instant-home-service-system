# Home Service Application

A complete backend application for managing home services like grooming, mopping, cleaning, plumbing, and electrician services.

## Features

### Core Services
- **Grooming** - Personal grooming services
- **Mopping** - Floor cleaning/mopping
- **Cleaning Utensils** - Kitchen and household utensils cleaning
- **Plumbing** - Plumbing repair and maintenance
- **Electrician** - Electrical repair and installation

### Application Features
- User authentication and authorization (Customer, Owner, Gig Worker, Admin roles)
- Email OTP login and registration support
- Service catalog with pricing and availability
- Service provider management and ratings
- Service request system with detailed requirements and address fields
- Booking system with status tracking (Pending, Confirmed, Completed, Cancelled)
- **Payment Processing** with Stripe card payments plus UPI, Cash, and Netbanking options
- Real-time service availability
- Dashboard with statistics
- RESTful API with comprehensive endpoints

## Project Structure

```
home_service_app/
├── main.py           # FastAPI application with all routes
├── database.py       # SQLAlchemy database configuration
├── models.py         # Database models (Service, Customer, Booking, Provider)
├── schemas.py        # Pydantic schemas for request/response validation
├── requirements.txt  # Python dependencies
└── README.md         # This file
```

## Installation

1. Navigate to the project directory:
```bash
cd home_service_app
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Stripe Payment Setup

1. Create a Stripe account at [stripe.com](https://stripe.com)

2. Get your API keys from the Stripe Dashboard:
   - Test Publishable Key (starts with `pk_test_`)
   - Test Secret Key (starts with `sk_test_`)

3. Set environment variables:
```bash
# Windows
set STRIPE_SECRET_KEY=sk_test_your_secret_key_here
set STRIPE_PUBLISHABLE_KEY=pk_test_your_publishable_key_here

# Linux/Mac
export STRIPE_SECRET_KEY=sk_test_your_secret_key_here
export STRIPE_PUBLISHABLE_KEY=pk_test_your_publishable_key_here
```

4. Update the publishable key in `payment.html`:
```javascript
const stripe = Stripe('pk_test_your_publishable_key_here');
```

## Running the Application

1. Start the FastAPI server:
```bash
python main.py
```

Or using uvicorn directly:
```bash
uvicorn main:app --reload
```

2. The API will be available at `http://localhost:8000`

3. Interactive API documentation:
   - Swagger UI: `http://localhost:8000/docs`
   - ReDoc: `http://localhost:8000/redoc`

## API Endpoints

### Services
- `POST /services/` - Create a new service
- `GET /services/` - Get all services
- `GET /services/{service_id}` - Get service by ID
- `GET /services/type/{service_type}` - Get services by type
- `PUT /services/{service_id}` - Update service
- `DELETE /services/{service_id}` - Delete service

### Customers
- `POST /customers/` - Register new customer
- `GET /customers/` - Get all customers
- `GET /customers/{customer_id}` - Get customer by ID
- `PUT /customers/{customer_id}` - Update customer info

### Bookings
- `POST /bookings/` - Create new booking
- `GET /bookings/` - Get all bookings
- `GET /bookings/{booking_id}` - Get booking by ID
- `GET /customers/{customer_id}/bookings` - Get customer's bookings
- `PUT /bookings/{booking_id}` - Update booking status
- `DELETE /bookings/{booking_id}` - Cancel booking

### Service Providers
- `POST /providers/` - Register new service provider
- `GET /providers/` - Get all providers
- `GET /providers/{provider_id}` - Get provider by ID
- `GET /providers/specialization/{specialization}` - Get providers by specialization
- `PUT /providers/{provider_id}` - Update provider info

### Dashboard
- `GET /dashboard/stats` - Get application statistics

### Payments
- `POST /payments/create-intent` - Create payment record for booking (supports card, UPI, cash, netbanking)
- `POST /payments/webhook` - Handle Stripe webhooks
- `GET /payments/{payment_id}` - Get payment details
- `GET /bookings/{booking_id}/payment` - Get payment for booking
- `GET /payment` - Payment page (HTML interface)

### Authentication
- `POST /auth/request-otp` - Request a mobile OTP for login or registration (SMS delivery via Twilio if configured)
- `POST /auth/verify-otp` - Verify mobile OTP (returns user_exists flag)
- `POST /auth/complete-registration` - Complete registration for new users after OTP verification
- `GET /auth/me` - Get current user info

### SMS Configuration
To enable SMS delivery for OTP, configure Twilio in your `.env` file:
```
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_FROM_NUMBER=+1234567890
```

If Twilio is not configured, OTP codes will be returned in the API response for development.
- `GET /dashboard` - User dashboard (HTML interface)
- `GET /dashboard/user` - Customer portal page
- `GET /dashboard/owner` - Owner portal page
- `GET /dashboard/gig-worker` - Gig worker portal page

### Service Requests
- `POST /service-requests/` - Create service request (authenticated users)
- `GET /service-requests/` - Get user's service requests
- `GET /service-requests/{request_id}` - Get service request by ID
- `PUT /service-requests/{request_id}` - Update service request
- `DELETE /service-requests/{request_id}` - Delete service request
- `GET /dashboard` - User dashboard (HTML interface)

### Admin (Admin only)
- `GET /admin/dashboard` - Admin dashboard statistics
- `GET /admin/users` - Get all users

## User Roles & Authentication

The application supports three user roles:

- **Customer** - Can register, login, submit service requests, and track their requests
- **Admin** - Full access to all features, can manage users and service requests
- **Provider** - Service providers (future enhancement)

### Authentication Flow:
1. User registers with email, username, and password
2. User logs in to receive JWT access token
3. Token is used for all authenticated API calls
4. Token expires after 30 minutes

### Service Request Process:
1. User logs in to dashboard (`/dashboard`)
2. Fills detailed service request form with:
   - Service type (plumbing, electrician, etc.)
   - Title and detailed description
   - Preferred date/time
   - Urgency level
   - Location and contact information
   - Additional notes
3. Admin reviews and assigns requests to providers
4. Status updates: Pending → Assigned → In Progress → Completed

## Example Usage

### 1. Create a Service
```bash
curl -X POST "http://localhost:8000/services/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Professional Plumbing",
    "type": "plumbing",
    "description": "Expert plumbing repair and installation",
    "price": 75.00,
    "duration_hours": 2.0,
    "is_available": true
  }'
```

### 2. Register a Customer
```bash
curl -X POST "http://localhost:8000/customers/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "555-1234",
    "address": "123 Main St"
  }'
```

### 3. Create a Booking
```bash
curl -X POST "http://localhost:8000/bookings/" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": 1,
    "service_id": 1,
    "booking_date": "2024-05-15T10:00:00",
    "notes": "Fix kitchen sink leak"
  }'
```

### 4. Update Booking Status
```bash
curl -X PUT "http://localhost:8000/bookings/1" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "completed",
    "notes": "Successfully fixed the leak"
  }'
```

### 5. Create Payment Intent
```bash
curl -X POST "http://localhost:8000/payments/create-intent" \
  -H "Content-Type: application/json" \
  -d '{
    "booking_id": 1,
    "payment_method": "card"
  }'
```

### 6. Check Payment Status
```bash
curl -X GET "http://localhost:8000/bookings/1/payment"
```

### 7. Register New User
```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "testuser",
    "password": "password123",
    "full_name": "Test User",
    "phone": "555-1234",
    "address": "123 Test St"
  }'
```

### 8. Login User
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -d "username=testuser&password=password123"
```

### 9. Create Service Request (with JWT token)
```bash
curl -X POST "http://localhost:8000/service-requests/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "service_type": "plumbing",
    "title": "Fix leaking faucet",
    "description": "Kitchen faucet is leaking continuously",
    "preferred_date": "2026-05-01T10:00:00",
    "preferred_time": "morning",
    "urgency": "normal",
    "location": "123 Main St, Kitchen",
    "contact_phone": "555-1234",
    "additional_notes": "Faucet under sink"
  }'
```

## Database

The application uses SQLite by default. The database file (`home_service.db`) is created automatically in the application directory.

### Models
- **User** - User accounts with roles (customer, admin, provider)
- **Service** - Service offerings with pricing and availability
- **Customer** - Customer information and contacts
- **ServiceRequest** - Detailed service requests from users
- **Booking** - Service bookings with status tracking
- **ServiceProvider** - Service providers with specialization and ratings
- **Payment** - Payment records with Stripe integration

## Future Enhancements

- SMS/Email notifications
- Service provider ratings and reviews
- Advanced booking calendar
- Real-time availability tracking
- Admin dashboard
- User authentication and authorization
- Multi-language support

## Dependencies

- **FastAPI** - Web framework
- **SQLAlchemy** - ORM and database toolkit
- **Pydantic** - Data validation
- **Uvicorn** - ASGI server
- **Stripe** - Payment processing
- **Python-JOSE** - JWT token handling
- **PassLib** - Password hashing

## License

This project is open source and available for use and modification.
