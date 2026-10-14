from flask import Blueprint, render_template, request, session, redirect, url_for, flash, jsonify
from extensions import db
from models import MenuItem, RestaurantSetting

cart_bp = Blueprint("cart", __name__)


def get_cart_details():
    """Calculates valid cart items, subtotals, delivery fee, and grand total from the database."""
    cart_dict = session.get("cart", {})
    cart_items = []
    subtotal = 0.0
    total_quantity = 0

    to_remove = []
    for item_id_str, qty in cart_dict.items():
        try:
            item_id = int(item_id_str)
            qty = int(qty)
            if qty <= 0:
                to_remove.append(item_id_str)
                continue
            item = db.session.get(MenuItem, item_id)
            if not item or not item.is_available:
                to_remove.append(item_id_str)
                continue

            item_total = item.price * qty
            subtotal += item_total
            total_quantity += qty

            cart_items.append({
                "item": item,
                "quantity": qty,
                "item_total": item_total,
            })
        except (ValueError, TypeError):
            to_remove.append(item_id_str)

    # Clean up any invalid items from session
    if to_remove:
        for k in to_remove:
            cart_dict.pop(k, None)
        session["cart"] = cart_dict
        session.modified = True

    # Compute delivery fee
    fee_setting = float(RestaurantSetting.get_value("delivery_fee", 40.0))
    free_threshold = float(RestaurantSetting.get_value("free_delivery_threshold", 500.0))

    if subtotal == 0 or subtotal >= free_threshold:
        delivery_fee = 0.0
    else:
        delivery_fee = fee_setting

    grand_total = subtotal + delivery_fee

    return {
        "items": cart_items,
        "cart_items": cart_items,
        "subtotal": round(subtotal, 2),
        "delivery_fee": round(delivery_fee, 2),
        "free_threshold": free_threshold,
        "grand_total": round(grand_total, 2),
        "total_quantity": total_quantity,
    }


@cart_bp.route("/")
def index():
    cart_data = get_cart_details()
    return render_template("cart.html", cart=cart_data)


@cart_bp.route("/add", methods=["POST"])
def add_item():
    is_json = request.is_json
    data = request.get_json(silent=True) or request.form

    try:
        item_id = int(data.get("item_id", 0))
        quantity = int(data.get("quantity", 1))
    except (ValueError, TypeError):
        if is_json:
            return jsonify({"success": False, "message": "Invalid item or quantity."}), 400
        flash("Invalid request parameters.", "danger")
        return redirect(request.referrer or url_for("menu.index"))

    item = db.session.get(MenuItem, item_id)
    if not item or not item.is_available:
        if is_json:
            return jsonify({"success": False, "message": "Item is not currently available."}), 404
        flash("This dish is currently unavailable.", "warning")
        return redirect(request.referrer or url_for("menu.index"))

    cart = session.get("cart", {})
    item_key = str(item_id)
    cart[item_key] = cart.get(item_key, 0) + max(1, quantity)
    session["cart"] = cart
    session.modified = True

    cart_data = get_cart_details()

    if is_json:
        return jsonify({
            "success": True,
            "message": f"Added {item.name} to your cart!",
            "cart_count": cart_data["total_quantity"],
            "cart_subtotal": cart_data["subtotal"],
        })

    flash(f"Added {item.name} to your cart!", "success")
    return redirect(request.referrer or url_for("cart.index"))


@cart_bp.route("/update", methods=["POST"])
def update_item():
    is_json = request.is_json
    data = request.get_json(silent=True) or request.form

    try:
        item_id = int(data.get("item_id", 0))
        quantity = int(data.get("quantity", 0))
    except (ValueError, TypeError):
        if is_json:
            return jsonify({"success": False, "message": "Invalid values."}), 400
        return redirect(url_for("cart.index"))

    cart = session.get("cart", {})
    item_key = str(item_id)

    if quantity <= 0:
        cart.pop(item_key, None)
    else:
        cart[item_key] = quantity

    session["cart"] = cart
    session.modified = True

    cart_data = get_cart_details()

    if is_json:
        return jsonify({
            "success": True,
            "cart_count": cart_data["total_quantity"],
            "subtotal": cart_data["subtotal"],
            "delivery_fee": cart_data["delivery_fee"],
            "grand_total": cart_data["grand_total"],
        })

    return redirect(url_for("cart.index"))


@cart_bp.route("/remove/<int:item_id>", methods=["POST"])
def remove_item(item_id):
    cart = session.get("cart", {})
    item_key = str(item_id)
    if item_key in cart:
        cart.pop(item_key)
        session["cart"] = cart
        session.modified = True
        flash("Item removed from your cart.", "info")

    if request.is_json:
        cart_data = get_cart_details()
        return jsonify({
            "success": True,
            "cart_count": cart_data["total_quantity"],
            "subtotal": cart_data["subtotal"],
            "grand_total": cart_data["grand_total"],
        })

    return redirect(url_for("cart.index"))


@cart_bp.route("/clear", methods=["POST"])
def clear_cart():
    session["cart"] = {}
    session.modified = True
    flash("Your cart has been cleared.", "info")
    return redirect(url_for("cart.index"))
