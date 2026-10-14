import os
from datetime import datetime
from flask import Flask, render_template, session
from config import config_by_name
from extensions import db, login_manager, csrf
from models import RestaurantSetting, MenuItem


def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get("FLASK_ENV", "development")

    app = Flask(__name__)
    app.config.from_object(config_by_name.get(config_name, config_by_name["default"]))

    # Ensure instance folder exists
    os.makedirs(app.instance_path, exist_ok=True)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    # Register blueprints
    from routes.main import main_bp
    from routes.auth import auth_bp
    from routes.menu import menu_bp
    from routes.cart import cart_bp
    from routes.orders import orders_bp
    from routes.reservations import reservations_bp
    from routes.admin import admin_bp
    from routes.api import api_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(menu_bp, url_prefix="/menu")
    app.register_blueprint(cart_bp, url_prefix="/cart")
    app.register_blueprint(orders_bp, url_prefix="/orders")
    app.register_blueprint(reservations_bp, url_prefix="/reservations")
    app.register_blueprint(admin_bp)
    app.register_blueprint(api_bp)

    # Context processors to inject global data into templates
    @app.context_processor
    def inject_global_data():
        # Cart item count
        cart = session.get("cart", {})
        cart_count = sum(int(qty) for qty in cart.values() if isinstance(qty, (int, str)) and str(qty).isdigit())

        # Safe defaults if db tables are not initialized yet
        try:
            settings_dict = RestaurantSetting.get_all_as_dict()
        except Exception:
            settings_dict = {}

        defaults = {
            "restaurant_name": "FORKS & KNIFE",
            "tagline": "A Symphony of Global Flavors",
            "phone": "+91 98971 23456",
            "email": "forks.knife.dining@gmail.com",
            "address": "42 Gourmet Avenue, Connaught Place, New Delhi - 110001",
            "weekday_hours": "Monday - Friday: 11:00 AM - 11:00 PM",
            "weekend_hours": "Saturday - Sunday: 10:00 AM - 12:00 AM",
            "currency_symbol": "₹",
        }
        for k, v in defaults.items():
            if k not in settings_dict or not settings_dict[k]:
                settings_dict[k] = v

        return {
            "cart_count": cart_count,
            "settings": settings_dict,
            "current_year": datetime.now().year,
        }

    # Error Handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template("errors/500.html"), 500

    @app.errorhandler(403)
    def forbidden(e):
        return render_template("errors/403.html"), 403

    # Custom CLI Commands
    @app.cli.command("init-db")
    def init_db():
        """Initialize SQLite database tables."""
        with app.app_context():
            db.create_all()
            print("Database initialized successfully.")

    @app.cli.command("seed-data")
    def seed_data():
        """Seed sample restaurant data."""
        from seed import seed_database
        with app.app_context():
            seed_database()
            print("Database seeded with sample data successfully.")

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
