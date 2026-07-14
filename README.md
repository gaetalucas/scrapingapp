# Pulso — Price Intelligence Platform

Multi-tenant SaaS for MAP (Minimum Advertised Price) compliance monitoring in Argentina/LatAm.

## Stack

- **Backend:** Django 4.2 + Django REST Framework
- **Frontend:** HTMX + Tailwind CSS (Django templates)
- **Database:** SQLite (dev) / PostgreSQL (production)
- **Auth:** Custom JWT (PyJWT)
- **Deploy:** Railway + gunicorn

## Quick Start

```bash
# Clone and setup
git clone <repo-url> && cd pulso
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Environment
cp .env.example .env
# Edit .env with your values

# Database
python manage.py migrate

# Create admin user
python manage.py createsuperuser

# Run dev server
python manage.py runserver
```

## Running Tests

```bash
# All tests
pytest

# With coverage
pytest --cov=apps --cov-report=html

# Specific test file
pytest tests/test_products_api.py -v
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/login/` | Login (email + password) |
| POST | `/api/v1/auth/refresh/` | Refresh access token |
| POST | `/api/v1/auth/logout/` | Logout |
| GET/POST | `/api/v1/products/` | List/Create products |
| GET/PUT/DELETE | `/api/v1/products/{id}/` | Product detail |
| POST | `/api/v1/products/{id}/archive/` | Archive product |
| POST | `/api/v1/products/{id}/unarchive/` | Unarchive product |
| GET | `/api/v1/products/export/` | Export products (Excel) |
| GET/POST | `/api/v1/sellers/` | List/Create sellers |
| GET/POST | `/api/v1/brands/` | List/Create brands |
| GET/POST | `/api/v1/categories/` | List/Create categories |
| GET/POST | `/api/v1/channels/` | List/Create channels |

## Deployment (Railway)

1. Connect GitHub repo to Railway
2. Set environment variables (see `.env.example`)
3. Railway auto-deploys on push to `main`

The `Procfile` handles migrations automatically on each deploy.

## Project Structure

```
pulso/
├── apps/
│   ├── auth_custom/    # JWT authentication
│   ├── brands/         # Brand management
│   ├── categories/     # Category management
│   ├── channels/       # Sales channels
│   ├── core/           # Shared permissions, pagination
│   ├── frontend/       # HTMX templates
│   ├── products/       # Product CRUD + pricing
│   ├── sellers/        # Seller/retailer management
│   └── tenants/        # Multi-tenant (Tenant + User)
├── tests/              # pytest test suite
├── templates/          # Django templates
├── static/             # Static assets
├── pulso_config/       # Django settings
└── manage.py
```
