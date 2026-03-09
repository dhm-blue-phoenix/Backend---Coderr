# CODERR API Backend

Welcome to the backend of the CODERR platform! This Django-based API provides the server logic for a freelance marketplace application. It allows managing users, business profiles, service offers, orders, and reviews through RESTful endpoints.

## Requirements

**Python:** 3.10+ (the project requires Python 3.10 or higher for local development).

Check your Python version:

```bash
python --version
```

## Quick Start

1. Clone the repository and navigate to the folder:

   ```bash
   git clone https://github.com/dhm-blue-phoenix/Backend---Coderr.git
   cd Backend---Coderr
   ```

## Manual Setup

2. Create and activate a virtual environment:

   ```bash
   python -m venv .venv
   ```

   ### On Windows

   ```bash
   .venv\Scripts\activate
   ```

   ### On macOS and Linux

   ```bash
   source .venv/bin/activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the root directory of the project:

   ```
   SECRET_KEY=your-secret-key-here
   DEBUG=True
   ```

   > **Note:** Never commit your `.env` file to version control. It is listed in `.gitignore` by default.

5. Apply migrations and create the database (SQLite is used for local development):

   ```bash
   cd backend
   python manage.py migrate
   ```

6. Create a superuser for admin access (optional):

   This allows you to access the Django admin interface at `/admin/`.

   ```bash
   python manage.py createsuperuser
   ```

7. Run the development server:

   ```bash
   python manage.py runserver
   ```

   The API will be available at `http://127.0.0.1:8000/`.

## API Endpoints

### Authentication

- `POST /api/registration/` - Register a new user (customer or business)
- `POST /api/login/` - Authenticate and receive a token

### Profiles

- `GET /api/profile/{id}/` - Get a user's profile details
- `PATCH /api/profile/{id}/` - Update own profile
- `GET /api/profiles/business/` - List all business users
- `GET /api/profiles/customer/` - List all customer users

### Offers

- `GET /api/offers/` - List all available offers (with filters, search, and pagination)
- `POST /api/offers/` - Create a new offer (business users only)
- `GET /api/offers/{id}/` - Get offer details
- `PATCH /api/offers/{id}/` - Update an offer (owner only)
- `DELETE /api/offers/{id}/` - Delete an offer (owner only)
- `GET /api/offerdetails/{id}/` - Get specific offer detail tier

### Orders

- `GET /api/orders/` - List orders (for customer or business)
- `POST /api/orders/` - Create a new order (customer only)
- `PATCH /api/orders/{id}/` - Update order status (business only)
- `DELETE /api/orders/{id}/` - Delete an order (admin only)
- `GET /api/order-count/{business_user_id}/` - Get count of in-progress orders
- `GET /api/completed-order-count/{business_user_id}/` - Get count of completed orders

### Reviews

- `GET /api/reviews/` - List reviews with filtering and ordering
- `POST /api/reviews/` - Create a review (customer only, one per business user)
- `PATCH /api/reviews/{id}/` - Update your review
- `DELETE /api/reviews/{id}/` - Delete your review

### Platform Info

- `GET /api/base-info/` - Get platform statistics (review count, average rating, business count, offer count)

## Running Tests

To run the automated test suite, execute the following command:

```bash
python manage.py test
```

This will run all tests across the project and display a coverage report (95%+ coverage).

## Project Structure

```
backend/
├── core/                 # Main Django project configuration
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── views.py
├── authentication/       # User registration and login
│   ├── models.py
│   ├── api/
│   │   ├── views.py
│   │   ├── serializers.py
│   │   ├── urls.py
│   │   └── permissions.py
├── profiles/             # User profiles
│   ├── models.py
│   ├── api/
│   │   ├── views.py
│   │   ├── serializers.py
│   │   ├── urls.py
│   │   └── permissions.py
├── offers/               # Service offers
│   ├── models.py
│   ├── api/
│   │   ├── views.py
│   │   ├── serializers.py
│   │   ├── urls.py
│   │   ├── permissions.py
│   │   └── filters.py
├── orders/               # Order management
│   ├── models.py
│   ├── api/
│   │   ├── views.py
│   │   ├── serializers.py
│   │   ├── urls.py
│   │   └── permissions.py
├── reviews/              # Review system
│   ├── models.py
│   ├── api/
│   │   ├── views.py
│   │   ├── serializers.py
│   │   ├── urls.py
│   │   └── permissions.py
├── db.sqlite3            # Local SQLite database
├── manage.py
└── requirements.txt
```

## Authentication

The API uses token-based authentication. After registering or logging in, you receive a token that must be included in all subsequent requests:

## Technologies Used

- **Django 5.2.12** - Web framework
- **Django REST Framework** - REST API framework
- **Django Filter** - Filtering for querysets
- **python-dotenv** - Environment variable management
- **SQLite** - Database (local development)