from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import current_user
from extensions import db
from models import Order, OrderItem, MenuItem
from forms import CheckoutForm
from routes.cart import get_cart_details

orders_bp = Blueprint("orders", __name__)


@orders_bp.route("/checkout", methods=["GET", "POST"])
def checkout():
    cart_data = get_cart_details()
    if not cart_data["items"]:
        flash("Your shopping cart is currently empty. Please add items before checking out.", "info")
        return redirect(url_for("menu.index"))

    form = CheckoutForm()

    # Pre-fill customer details if logged in and form is not submitted
    if request.method == "GET" and current_user.is_authenticated:
        form.customer_name.data = current_user.name
        form.customer_email.data = current_user.email
        form.customer_phone.data = current_user.phone

    if form.validate_on_submit():
        order_num = Order.generate_order_number()

        new_order = Order(
            order_number=order_num,
            user_id=current_user.id if current_user.is_authenticated else None,
            customer_name=form.customer_name.data.strip(),
            customer_email=form.customer_email.data.strip().lower(),
            customer_phone=form.customer_phone.data.strip(),
            delivery_address=form.delivery_address.data.strip(),
            order_notes=form.order_notes.data.strip() if form.order_notes.data else None,
            subtotal=cart_data["subtotal"],
            delivery_fee=cart_data["delivery_fee"],
            total_amount=cart_data["grand_total"],
            payment_method=form.payment_method.data,
            status="Pending",
        )
        db.session.add(new_order)
        db.session.flush()  # assign ID to new_order

        # Create OrderItems
        for c_item in cart_data["items"]:
            order_item = OrderItem(
                order_id=new_order.id,
                menu_item_id=c_item["item"].id,
                item_name=c_item["item"].name,
                item_price=c_item["item"].price,
                quantity=c_item["quantity"],
                subtotal=c_item["item_total"],
            )
            db.session.add(order_item)

        db.session.commit()

        # Clear cart
        session["cart"] = {}
        session.modified = True

        flash(f"Order #{order_num} has been successfully placed!", "success")
        return redirect(url_for("orders.confirmation", order_number=order_num))

    return render_template("checkout.html", form=form, cart=cart_data)


@orders_bp.route("/<string:order_number>/confirmation")
def confirmation(order_number):
    order = Order.query.filter_by(order_number=order_number).first_or_404()
    return render_template("order_confirmation.html", order=order)


@orders_bp.route("/track", methods=["GET", "POST"])
def track():
    order = None
    searched = False
    if request.method == "POST":
        searched = True
        order_number = request.form.get("order_number", "").strip().upper()
        phone = request.form.get("phone", "").strip()

        query = Order.query.filter_by(order_number=order_number)
        if phone:
            query = query.filter_by(customer_phone=phone)
        order = query.first()

        if not order:
            flash("No order found with the provided details. Please check your order number.", "warning")

    return render_template("order_track.html", order=order, searched=searched)
