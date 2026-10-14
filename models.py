from datetime import datetime, date, time, timezone
import secrets
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db, login_manager


def utc_now():
    return datetime.now(timezone.utc)


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(20), nullable=True)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=utc_now, nullable=False)

    orders = db.relationship("Order", backref="user", lazy=True, order_by="desc(Order.created_at)")
    reservations = db.relationship("Reservation", backref="user", lazy=True, order_by="desc(Reservation.reservation_date)")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.email} (Admin: {self.is_admin})>"


class MenuCategory(db.Model):
    __tablename__ = "menu_categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False, unique=True)
    slug = db.Column(db.String(80), nullable=False, unique=True, index=True)
    description = db.Column(db.String(255), nullable=True)
    image_url = db.Column(db.String(255), nullable=True)
    display_order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=utc_now)

    items = db.relationship(
        "MenuItem", backref="category", lazy=True, cascade="all, delete-orphan", order_by="MenuItem.display_order"
    )

    def __repr__(self):
        return f"<MenuCategory {self.name}>"


class MenuItem(db.Model):
    __tablename__ = "menu_items"

    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey("menu_categories.id"), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    slug = db.Column(db.String(120), nullable=True)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=False)
    is_veg = db.Column(db.Boolean, default=True, nullable=False)
    is_available = db.Column(db.Boolean, default=True, nullable=False)
    is_special = db.Column(db.Boolean, default=False, nullable=False)
    image_url = db.Column(db.String(255), nullable=True)
    prep_time_minutes = db.Column(db.Integer, default=20)
    display_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=utc_now)

    def to_dict(self):
        return {
            "id": self.id,
            "category_id": self.category_id,
            "category_name": self.category.name if self.category else "",
            "name": self.name,
            "description": self.description or "",
            "price": self.price,
            "is_veg": self.is_veg,
            "is_available": self.is_available,
            "is_special": self.is_special,
            "image_url": self.image_url or "/static/images/other/Menu-card.png",
            "prep_time_minutes": self.prep_time_minutes,
        }

    def __repr__(self):
        return f"<MenuItem {self.name} - ₹{self.price}>"


class Order(db.Model):
    __tablename__ = "orders"

    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(32), unique=True, nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)

    customer_name = db.Column(db.String(100), nullable=False)
    customer_email = db.Column(db.String(120), nullable=False)
    customer_phone = db.Column(db.String(20), nullable=False)
    delivery_address = db.Column(db.Text, nullable=False)
    order_notes = db.Column(db.Text, nullable=True)

    subtotal = db.Column(db.Float, nullable=False, default=0.0)
    delivery_fee = db.Column(db.Float, nullable=False, default=0.0)
    tax_amount = db.Column(db.Float, nullable=False, default=0.0)
    total_amount = db.Column(db.Float, nullable=False, default=0.0)

    payment_method = db.Column(db.String(40), default="Cash on Delivery")
    status = db.Column(db.String(30), default="Pending")  # Pending, Confirmed, Preparing, Out for Delivery, Delivered, Cancelled
    created_at = db.Column(db.DateTime, default=utc_now, index=True)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now)

    items = db.relationship("OrderItem", backref="order", lazy=True, cascade="all, delete-orphan")

    @staticmethod
    def generate_order_number():
        today_str = utc_now().strftime("%Y%m%d")
        rand_hex = secrets.token_hex(3).upper()
        return f"ORD-{today_str}-{rand_hex}"

    def __repr__(self):
        return f"<Order {self.order_number} - ₹{self.total_amount}>"


class OrderItem(db.Model):
    __tablename__ = "order_items"

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"), nullable=False)
    menu_item_id = db.Column(db.Integer, db.ForeignKey("menu_items.id"), nullable=True)

    item_name = db.Column(db.String(120), nullable=False)
    item_price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    subtotal = db.Column(db.Float, nullable=False)

    menu_item = db.relationship("MenuItem", lazy=True)

    def __repr__(self):
        return f"<OrderItem {self.item_name} x {self.quantity}>"


class Reservation(db.Model):
    __tablename__ = "reservations"

    id = db.Column(db.Integer, primary_key=True)
    reference_number = db.Column(db.String(32), unique=True, nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)

    customer_name = db.Column(db.String(100), nullable=False)
    customer_email = db.Column(db.String(120), nullable=False)
    customer_phone = db.Column(db.String(20), nullable=False)

    reservation_date = db.Column(db.Date, nullable=False, index=True)
    reservation_time = db.Column(db.String(10), nullable=False)  # e.g., "19:00"
    num_guests = db.Column(db.Integer, nullable=False, default=2)
    special_requests = db.Column(db.Text, nullable=True)

    status = db.Column(db.String(30), default="Confirmed")  # Pending, Confirmed, Cancelled, Completed
    created_at = db.Column(db.DateTime, default=utc_now)

    @staticmethod
    def generate_reference_number():
        rand_str = secrets.token_hex(4).upper()
        return f"RES-{rand_str}"

    def __repr__(self):
        return f"<Reservation {self.reference_number} - {self.customer_name} ({self.num_guests} guests)>"


class ContactMessage(db.Model):
    __tablename__ = "contact_messages"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    subject = db.Column(db.String(150), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=utc_now)

    def __repr__(self):
        return f"<ContactMessage from {self.name} - {self.subject}>"


class CarouselSlide(db.Model):
    __tablename__ = "carousel_slides"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    subtitle = db.Column(db.String(200), nullable=False)
    image_url = db.Column(db.String(255), nullable=False)
    button_text = db.Column(db.String(50), nullable=True, default="View Menu")
    button_url = db.Column(db.String(255), nullable=True, default="/menu")
    display_order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<CarouselSlide {self.title}>"


class RestaurantSetting(db.Model):
    __tablename__ = "restaurant_settings"

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(60), unique=True, nullable=False, index=True)
    value = db.Column(db.Text, nullable=True)
    description = db.Column(db.String(255), nullable=True)

    @classmethod
    def get_value(cls, key, default=None):
        setting = cls.query.filter_by(key=key).first()
        return setting.value if setting and setting.value is not None else default

    @classmethod
    def set_value(cls, key, value, description=None):
        setting = cls.query.filter_by(key=key).first()
        if not setting:
            setting = cls(key=key, value=value, description=description)
            db.session.add(setting)
        else:
            setting.value = value
            if description:
                setting.description = description
        db.session.commit()
        return setting

    @classmethod
    def get_all_as_dict(cls):
        settings = cls.query.all()
        return {s.key: s.value for s in settings}

    def __repr__(self):
        return f"<Setting {self.key}={self.value}>"
