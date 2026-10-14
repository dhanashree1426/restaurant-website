# 🍴 FORKS & KNIFE — Dynamic Full-Stack Restaurant Web Application

A complete, production-ready, dynamic full-stack restaurant website transformed from the static HTML5/CSS3/Bootstrap 5 frontend into an interactive database-driven application powered by **Python Flask**, **SQLAlchemy ORM**, **SQLite**, and **Flask-Login**.

---

## 🌟 Highlights & Preserved Design
- **Original Brand Identity Preserved:**
  - Primary Maroon (`#6B0F1A`) & Accent Orange (`#ff9041`).
  - Warm, luxury restaurant typography using *Playfair Display* and *Inter*.
  - Clean white & subtle gray backgrounds with high-resolution food imagery.
- **Fixed HTML & CSS Bugs:**
  - Resolved stray unclosed tags, malformed `<p>` tags, and misaligned responsive headings.
  - Upgraded carousel with automatic rotation, indicators, and dynamic database loading.
  - Converted static specials into dynamic database-driven cuisine cards with rupee (`₹`) pricing and direct category filtering.
- **Full-Stack Dynamic Architecture:**
  - **Dynamic Food Menu** with live category filtering, search, veg/non-veg toggle, and sorting.
  - **Interactive Shopping Cart** with real-time AJAX additions, quantity adjustment, and server-side price validation.
  - **Online Order Checkout** with unique order number generation (`ORD-YYYYMMDD-XXXX`), address collection, and Cash on Delivery / Pay at Restaurant support.
  - **Table Reservations** with live slot capacity checks, past-date rejection, and unique booking reference generation (`RES-XXXXXX`).
  - **Secure User Authentication** (Registration, Login, Profile with Order & Reservation History).
  - **Executive Admin Dashboard** for managing menu items, categories, customer orders, table reservations, carousel slides, contact inquiries, and operational restaurant settings.
  - **Documented REST API** (`/api/menu`, `/api/categories`, `/api/reservations`, `/api/contact`, `/api/cart`).
  - **Automated Pytest Suite** verifying all core workflows.

---

## 📂 Project Directory Structure

```text
restaurant_website/
│
├── app.py                      # Application factory (create_app), context processors, CLI commands
├── config.py                   # App configuration (Development, Testing, Production)
├── extensions.py               # Flask extensions (SQLAlchemy, LoginManager, CSRFProtect)
├── models.py                   # Database models (User, MenuCategory, MenuItem, Order, Reservation, etc.)
├── forms.py                    # WTForms classes with server-side validation & CSRF
├── seed.py                     # Database initialization and sample data seeder
├── requirements.txt            # Python dependencies
├── .env.example                # Example environment configuration
├── .env                        # Local development environment configuration
├── README.md                   # Complete documentation
│
├── routes/                     # Modular route blueprints
│   ├── __init__.py
│   ├── main.py                 # Homepage, about, and contact routes
│   ├── auth.py                 # Registration, login, logout, and profile
│   ├── menu.py                 # Menu display, cuisine filter, search, and sort
│   ├── cart.py                 # Shopping cart (session-backed, server-side price checks)
│   ├── orders.py               # Checkout, order confirmation, and live order tracking
│   ├── reservations.py         # Table reservation booking & capacity validation
│   ├── admin.py                # Protected admin dashboard & management actions
│   └── api.py                  # Public and internal REST API endpoints
│
├── templates/                  # Jinja2 HTML templates
│   ├── base.html               # Shared layout, navbar with cart badge, footer
│   ├── index.html              # Dynamic homepage (carousel, specials, contact)
│   ├── menu.html               # Full menu with filters, search, and add-to-cart
│   ├── cart.html               # Shopping cart review & quantities
│   ├── checkout.html           # Customer delivery address & order placement
│   ├── order_confirmation.html # Order receipt & tracking
│   ├── order_track.html        # Order status tracking by order number
│   ├── reservations.html       # Table booking form
│   ├── reservation_confirmation.html # Booking receipt
│   ├── contact.html            # Contact inquiry form & restaurant info
│   ├── about.html              # Restaurant philosophy & culinary story
│   ├── login.html              # User login
│   ├── register.html           # User registration
│   ├── profile.html            # User profile, past orders, and reservations
│   ├── errors/                 # 404, 500, 403 error templates
│   └── admin/                  # Protected administrative templates
│       ├── layout.html         # Admin sidebar & topbar layout
│       ├── dashboard.html      # Overview metric cards & recent activity
│       ├── menu_items.html     # Dish inventory list, stock toggle, actions
│       ├── menu_form.html      # Add & edit dish form
│       ├── categories.html     # Cuisines management
│       ├── category_edit.html  # Edit cuisine category
│       ├── orders.html         # Orders list with status filter
│       ├── order_detail.html   # Order details & status updater
│       ├── reservations.html   # Table reservations management
│       ├── slides.html         # Homepage carousel slides manager
│       ├── messages.html       # Contact message inquiries
│       └── settings.html       # Restaurant operational settings & opening hours
│
├── static/                     # Static assets
│   ├── css/
│   │   └── style.css           # Preserved & enhanced restaurant styling
│   ├── js/
│   │   └── main.js             # Client-side AJAX cart & interactive toast notifications
│   └── images/
│       ├── slider/             # High-resolution hero slides (slider-1 to slider-4)
│       ├── dishes/             # Dish photography for Italian, Mexican, Chinese, Japanese
│       └── other/
│           └── Menu-card.png   # International cuisine spread graphic
│
├── instance/
│   └── restaurant.db           # SQLite database
│
└── tests/
    └── test_app.py             # Pytest automated test suite (9 test suites)
```

---

## 🛠️ Technology Stack
- **Frontend:** HTML5, CSS3, JavaScript (Vanilla ES6+ for AJAX cart), Bootstrap 5.3.8, Bootstrap Icons 1.13.1, Google Fonts (*Playfair Display* & *Inter*).
- **Backend:** Python 3.10+ / 3.14, Flask 3.1.
- **Database:** SQLite with SQLAlchemy ORM (SQLAlchemy 2.x).
- **Authentication:** Flask-Login with secure PBKDF2/SHA-256 password hashing and role-based access control (`is_admin`).
- **Validation & Forms:** Flask-WTF with CSRF protection and WTForms.
- **Testing:** Pytest.

---

## 🚀 Quickstart Guide (PowerShell on Windows)

Follow these exact steps in your VS Code terminal:

### 1. Open Workspace Directory
```powershell
cd "D:\My projects\restaurant webiste"
```

### 2. Create and Activate Virtual Environment
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```
*(If PowerShell displays an execution policy restriction, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` first).*

### 3. Install Required Dependencies
```powershell
pip install -r requirements.txt
```

### 4. Initialize Database & Seed Sample Data
```powershell
python seed.py
```
This initializes `instance/restaurant.db` with:
- 6 Cuisine Categories (Italian, Mexican, Chinese, Japanese, Beverages, Desserts).
- 16 Sample Gourmet Dishes with Indian Rupee (`₹`) pricing and Veg/Non-Veg indicators.
- 4 Homepage Hero Carousel Slides.
- Restaurant opening hours, contact details, and delivery fee settings.
- Default Administrator and Customer test accounts.

### 5. Run the Application Server
```powershell
python app.py
```

### 6. Open in Browser
Open your browser and navigate to:
```text
http://127.0.0.1:5000/
```

---

## 🔑 Default Credentials

| Role | Email | Password | Access |
| :--- | :--- | :--- | :--- |
| **Administrator** | `admin@forksandknife.com` | `AdminPassword123!` | Full Admin Dashboard (`/admin/`), Menu editing, Order status updates, Table reservation management, Settings |
| **Customer** | `customer@example.com` | `Customer123!` | Ordering, Cart, Table reservations, Order history, User profile (`/auth/profile`) |

> You can also register any new customer account through the **Sign Up** button on the website.

---

## 🧪 Running Automated Tests

Run the full pytest suite to verify all workflows:

```powershell
.\venv\Scripts\python.exe -m pytest -v tests/test_app.py
```

All 9 test suites verify:
1. `test_homepage_loads` — Verifies HTTP 200, brand title, carousel slides.
2. `test_menu_page_and_filtering` — Tests category filter, search, and pure-vegetarian toggle.
3. `test_api_endpoints` — Tests `/api/categories` and `/api/menu` JSON responses.
4. `test_cart_workflow` — Tests adding dishes, updating quantities, and subtotal calculation.
5. `test_order_creation_and_confirmation` — Verifies server-side price validation, checkout submission, unique order ID generation, and database persistence.
6. `test_reservation_validation_and_past_date_rejection` — Verifies rejection of past dates and confirmation of future bookings.
7. `test_authentication_workflow` — Tests customer registration, login, profile view, and logout.
8. `test_admin_route_protection` — Tests that anonymous and customer users cannot access `/admin`, while administrators can.
9. `test_contact_form` — Tests contact message persistence to SQLite.

---

## 📡 REST API Documentation

| Method | Endpoint | Description | Sample Response / Body |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/menu` | List available dishes (supports `?category=slug&search=text&is_veg=true`) | `{"status": "success", "count": 16, "data": [...]}` |
| `GET` | `/api/categories` | List active cuisine categories | `{"status": "success", "count": 6, "data": [...]}` |
| `GET` | `/api/menu/<id>` | Details of a single dish | `{"status": "success", "data": {...}}` |
| `GET` | `/api/cart` | Current shopping cart items & subtotal | `{"status": "success", "items": [...], "grand_total": 560.0}` |
| `POST` | `/api/reservations` | Create a table reservation (JSON) | Body: `{"customer_name": "...", "customer_email": "...", "customer_phone": "...", "reservation_date": "2026-10-20", "reservation_time": "19:30", "num_guests": 4}` |
| `POST` | `/api/contact` | Submit an inquiry message (JSON) | Body: `{"name": "...", "email": "...", "subject": "...", "message": "..."}` |

---

## 💡 Troubleshooting Common Windows Issues

1. **PowerShell Script Execution Policy Error:**
   - *Error:* `File ... Activate.ps1 cannot be loaded because running scripts is disabled on this system.`
   - *Fix:* Run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` in PowerShell, then re-run `.\venv\Scripts\Activate.ps1`.

2. **SQLite Database Path on Windows:**
   - On Windows, SQLite URLs with relative paths can conflict with drive letters. The `config.py` in this project automatically resolves `instance/restaurant.db` using `Path.resolve().as_posix()` into an absolute URI (`sqlite:///D:/...`) to avoid this.

3. **Port 5000 Already in Use:**
   - If port 5000 is occupied by another process, run `python app.py` on another port:
     ```python
     app.run(debug=True, port=5001)
     ```
     and open `http://127.0.0.1:5001/`.

4. **Resetting Database to Fresh State:**
   - Delete `instance/restaurant.db` and run `python seed.py` to re-seed fresh sample data.
