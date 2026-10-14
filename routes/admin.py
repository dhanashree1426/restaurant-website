from functools import wraps
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort, jsonify
from flask_login import login_required, current_user
from extensions import db
from models import (
    User,
    MenuCategory,
    MenuItem,
    Order,
    OrderItem,
    Reservation,
    ContactMessage,
    CarouselSlide,
    RestaurantSetting,
)
from forms import (
    MenuItemForm,
    CategoryForm,
    SlideForm,
    RestaurantSettingsForm,
)

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


def admin_required(f):
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            flash("Administrator access required.", "danger")
            return redirect(url_for("main.index"))
        return f(*args, **kwargs)

    return decorated_function


@admin_bp.route("/")
@admin_required
def dashboard():
    total_menu_items = MenuItem.query.count()
    total_customers = User.query.filter_by(is_admin=False).count()
    total_orders = Order.query.count()
    pending_orders = Order.query.filter_by(status="Pending").count()
    total_reservations = Reservation.query.count()
    pending_reservations = Reservation.query.filter_by(status="Pending").count()
    unread_messages = ContactMessage.query.filter_by(is_read=False).count()

    total_revenue = db.session.query(db.func.sum(Order.total_amount)).filter(Order.status != "Cancelled").scalar() or 0.0

    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(6).all()
    recent_reservations = Reservation.query.order_by(Reservation.created_at.desc()).limit(6).all()

    return render_template(
        "admin/dashboard.html",
        total_menu_items=total_menu_items,
        total_customers=total_customers,
        total_orders=total_orders,
        pending_orders=pending_orders,
        total_revenue=total_revenue,
        total_reservations=total_reservations,
        pending_reservations=pending_reservations,
        unread_messages=unread_messages,
        recent_orders=recent_orders,
        recent_reservations=recent_reservations,
    )


# ---------------- MENU ITEMS MANAGEMENT ----------------
@admin_bp.route("/menu")
@admin_required
def menu_items():
    category_id = request.args.get("category_id", type=int)
    search = request.args.get("q", "").strip()

    query = MenuItem.query
    if category_id:
        query = query.filter_by(category_id=category_id)
    if search:
        query = query.filter(MenuItem.name.ilike(f"%{search}%"))

    items = query.order_by(MenuItem.display_order.asc(), MenuItem.name.asc()).all()
    categories = MenuCategory.query.order_by(MenuCategory.display_order).all()

    return render_template("admin/menu_items.html", items=items, categories=categories, selected_category=category_id, search=search)


@admin_bp.route("/menu/add", methods=["GET", "POST"])
@admin_required
def add_menu_item():
    form = MenuItemForm()
    form.category_id.choices = [(c.id, c.name) for c in MenuCategory.query.order_by(MenuCategory.name).all()]

    if form.validate_on_submit():
        item = MenuItem(
            name=form.name.data.strip(),
            category_id=form.category_id.data,
            description=form.description.data.strip() if form.description.data else None,
            price=form.price.data,
            is_veg=form.is_veg.data,
            is_available=form.is_available.data,
            is_special=form.is_special.data,
            image_url=form.image_url.data.strip() if form.image_url.data else None,
            prep_time_minutes=form.prep_time_minutes.data,
            display_order=form.display_order.data,
        )
        db.session.add(item)
        db.session.commit()
        flash(f"Dish '{item.name}' added successfully!", "success")
        return redirect(url_for("admin.menu_items"))

    return render_template("admin/menu_form.html", form=form, title="Add New Menu Item")


@admin_bp.route("/menu/edit/<int:item_id>", methods=["GET", "POST"])
@admin_required
def edit_menu_item(item_id):
    item = MenuItem.query.get_or_404(item_id)
    form = MenuItemForm(obj=item)
    form.category_id.choices = [(c.id, c.name) for c in MenuCategory.query.order_by(MenuCategory.name).all()]

    if form.validate_on_submit():
        item.name = form.name.data.strip()
        item.category_id = form.category_id.data
        item.description = form.description.data.strip() if form.description.data else None
        item.price = form.price.data
        item.is_veg = form.is_veg.data
        item.is_available = form.is_available.data
        item.is_special = form.is_special.data
        item.image_url = form.image_url.data.strip() if form.image_url.data else None
        item.prep_time_minutes = form.prep_time_minutes.data
        item.display_order = form.display_order.data

        db.session.commit()
        flash(f"Dish '{item.name}' updated successfully!", "success")
        return redirect(url_for("admin.menu_items"))

    return render_template("admin/menu_form.html", form=form, title=f"Edit: {item.name}", item=item)


@admin_bp.route("/menu/toggle-stock/<int:item_id>", methods=["POST"])
@admin_required
def toggle_item_stock(item_id):
    item = MenuItem.query.get_or_404(item_id)
    item.is_available = not item.is_available
    db.session.commit()
    flash(f"Updated status for '{item.name}' to {'Available' if item.is_available else 'Out of Stock'}.", "info")
    return redirect(request.referrer or url_for("admin.menu_items"))


@admin_bp.route("/menu/delete/<int:item_id>", methods=["POST"])
@admin_required
def delete_menu_item(item_id):
    item = MenuItem.query.get_or_404(item_id)
    name = item.name
    db.session.delete(item)
    db.session.commit()
    flash(f"Dish '{name}' deleted.", "warning")
    return redirect(url_for("admin.menu_items"))


# ---------------- CATEGORIES MANAGEMENT ----------------
@admin_bp.route("/categories", methods=["GET", "POST"])
@admin_required
def categories():
    form = CategoryForm()
    if form.validate_on_submit():
        cat = MenuCategory(
            name=form.name.data.strip(),
            slug=form.slug.data.strip().lower(),
            description=form.description.data.strip() if form.description.data else None,
            image_url=form.image_url.data.strip() if form.image_url.data else None,
            display_order=form.display_order.data,
        )
        db.session.add(cat)
        db.session.commit()
        flash(f"Category '{cat.name}' created successfully!", "success")
        return redirect(url_for("admin.categories"))

    all_categories = MenuCategory.query.order_by(MenuCategory.display_order).all()
    return render_template("admin/categories.html", categories=all_categories, form=form)


@admin_bp.route("/categories/edit/<int:category_id>", methods=["GET", "POST"])
@admin_required
def edit_category(category_id):
    cat = MenuCategory.query.get_or_404(category_id)
    form = CategoryForm(obj=cat)

    if form.validate_on_submit():
        cat.name = form.name.data.strip()
        cat.slug = form.slug.data.strip().lower()
        cat.description = form.description.data.strip() if form.description.data else None
        cat.image_url = form.image_url.data.strip() if form.image_url.data else None
        cat.display_order = form.display_order.data

        db.session.commit()
        flash(f"Category '{cat.name}' updated successfully!", "success")
        return redirect(url_for("admin.categories"))

    return render_template("admin/category_edit.html", form=form, category=cat)


@admin_bp.route("/categories/delete/<int:category_id>", methods=["POST"])
@admin_required
def delete_category(category_id):
    cat = MenuCategory.query.get_or_404(category_id)
    name = cat.name
    db.session.delete(cat)
    db.session.commit()
    flash(f"Category '{name}' deleted.", "warning")
    return redirect(url_for("admin.categories"))


# ---------------- ORDERS MANAGEMENT ----------------
@admin_bp.route("/orders")
@admin_required
def orders():
    status = request.args.get("status")
    query = Order.query
    if status and status != "All":
        query = query.filter_by(status=status)

    orders_list = query.order_by(Order.created_at.desc()).all()
    return render_template("admin/orders.html", orders=orders_list, current_status=status or "All")


@admin_bp.route("/orders/<int:order_id>")
@admin_required
def order_detail(order_id):
    order = Order.query.get_or_404(order_id)
    return render_template("admin/order_detail.html", order=order)


@admin_bp.route("/orders/<int:order_id>/status", methods=["POST"])
@admin_required
def update_order_status(order_id):
    order = Order.query.get_or_404(order_id)
    new_status = request.form.get("status")
    valid_statuses = ["Pending", "Confirmed", "Preparing", "Out for Delivery", "Delivered", "Cancelled"]
    if new_status in valid_statuses:
        order.status = new_status
        db.session.commit()
        flash(f"Order #{order.order_number} status updated to '{new_status}'.", "success")
    return redirect(request.referrer or url_for("admin.order_detail", order_id=order.id))


# ---------------- RESERVATIONS MANAGEMENT ----------------
@admin_bp.route("/reservations")
@admin_required
def reservations():
    status = request.args.get("status")
    query = Reservation.query
    if status and status != "All":
        query = query.filter_by(status=status)

    res_list = query.order_by(Reservation.reservation_date.desc(), Reservation.reservation_time.asc()).all()
    return render_template("admin/reservations.html", reservations=res_list, current_status=status or "All")


@admin_bp.route("/reservations/<int:res_id>/status", methods=["POST"])
@admin_required
def update_reservation_status(res_id):
    res = Reservation.query.get_or_404(res_id)
    new_status = request.form.get("status")
    valid_statuses = ["Pending", "Confirmed", "Completed", "Cancelled"]
    if new_status in valid_statuses:
        res.status = new_status
        db.session.commit()
        flash(f"Reservation {res.reference_number} marked as '{new_status}'.", "success")
    return redirect(request.referrer or url_for("admin.reservations"))


# ---------------- SLIDES MANAGEMENT ----------------
@admin_bp.route("/slides", methods=["GET", "POST"])
@admin_required
def slides():
    form = SlideForm()
    if form.validate_on_submit():
        slide = CarouselSlide(
            title=form.title.data.strip(),
            subtitle=form.subtitle.data.strip(),
            image_url=form.image_url.data.strip(),
            button_text=form.button_text.data.strip() if form.button_text.data else None,
            button_url=form.button_url.data.strip() if form.button_url.data else None,
            display_order=form.display_order.data,
            is_active=form.is_active.data,
        )
        db.session.add(slide)
        db.session.commit()
        flash(f"Slide '{slide.title}' added successfully!", "success")
        return redirect(url_for("admin.slides"))

    all_slides = CarouselSlide.query.order_by(CarouselSlide.display_order).all()
    return render_template("admin/slides.html", slides=all_slides, form=form)


@admin_bp.route("/slides/toggle/<int:slide_id>", methods=["POST"])
@admin_required
def toggle_slide(slide_id):
    slide = CarouselSlide.query.get_or_404(slide_id)
    slide.is_active = not slide.is_active
    db.session.commit()
    flash(f"Slide '{slide.title}' {'activated' if slide.is_active else 'deactivated'}.", "info")
    return redirect(url_for("admin.slides"))


@admin_bp.route("/slides/delete/<int:slide_id>", methods=["POST"])
@admin_required
def delete_slide(slide_id):
    slide = CarouselSlide.query.get_or_404(slide_id)
    db.session.delete(slide)
    db.session.commit()
    flash("Slide removed.", "warning")
    return redirect(url_for("admin.slides"))


# ---------------- RESTAURANT SETTINGS ----------------
@admin_bp.route("/settings", methods=["GET", "POST"])
@admin_required
def settings():
    form = RestaurantSettingsForm()

    if request.method == "GET":
        form.restaurant_name.data = RestaurantSetting.get_value("restaurant_name", "FORKS & KNIFE")
        form.tagline.data = RestaurantSetting.get_value("tagline", "A Symphony of Global Flavors")
        form.phone.data = RestaurantSetting.get_value("phone", "+91 98971 23456")
        form.email.data = RestaurantSetting.get_value("email", "forks.knife.dining@gmail.com")
        form.address.data = RestaurantSetting.get_value("address", "42 Gourmet Avenue, Connaught Place, New Delhi - 110001")
        form.weekday_hours.data = RestaurantSetting.get_value("weekday_hours", "Monday - Friday: 11:00 AM - 11:00 PM")
        form.weekend_hours.data = RestaurantSetting.get_value("weekend_hours", "Saturday - Sunday: 10:00 AM - 12:00 AM")
        form.delivery_fee.data = float(RestaurantSetting.get_value("delivery_fee", 40.0))
        form.free_delivery_threshold.data = float(RestaurantSetting.get_value("free_delivery_threshold", 500.0))
        form.max_guests_per_slot.data = int(RestaurantSetting.get_value("max_guests_per_slot", 30))

    if form.validate_on_submit():
        RestaurantSetting.set_value("restaurant_name", form.restaurant_name.data.strip())
        RestaurantSetting.set_value("tagline", form.tagline.data.strip())
        RestaurantSetting.set_value("phone", form.phone.data.strip())
        RestaurantSetting.set_value("email", form.email.data.strip())
        RestaurantSetting.set_value("address", form.address.data.strip())
        RestaurantSetting.set_value("weekday_hours", form.weekday_hours.data.strip())
        RestaurantSetting.set_value("weekend_hours", form.weekend_hours.data.strip())
        RestaurantSetting.set_value("delivery_fee", str(form.delivery_fee.data))
        RestaurantSetting.set_value("free_delivery_threshold", str(form.free_delivery_threshold.data))
        RestaurantSetting.set_value("max_guests_per_slot", str(form.max_guests_per_slot.data))

        flash("Restaurant settings and opening hours updated successfully!", "success")
        return redirect(url_for("admin.settings"))

    return render_template("admin/settings.html", form=form)


# ---------------- CONTACT MESSAGES ----------------
@admin_bp.route("/messages")
@admin_required
def messages():
    all_msgs = ContactMessage.query.order_by(ContactMessage.created_at.desc()).all()
    return render_template("admin/messages.html", messages=all_msgs)


@admin_bp.route("/messages/toggle-read/<int:msg_id>", methods=["POST"])
@admin_required
def toggle_message_read(msg_id):
    msg = ContactMessage.query.get_or_404(msg_id)
    msg.is_read = not msg.is_read
    db.session.commit()
    return redirect(url_for("admin.messages"))


@admin_bp.route("/messages/delete/<int:msg_id>", methods=["POST"])
@admin_required
def delete_message(msg_id):
    msg = ContactMessage.query.get_or_404(msg_id)
    db.session.delete(msg)
    db.session.commit()
    flash("Message deleted.", "info")
    return redirect(url_for("admin.messages"))
