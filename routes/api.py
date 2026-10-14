from flask import Blueprint, jsonify, request
from datetime import datetime, date
from extensions import db, csrf
from models import MenuItem, MenuCategory, Reservation, ContactMessage, RestaurantSetting
from routes.cart import get_cart_details

api_bp = Blueprint("api", __name__, url_prefix="/api")


@api_bp.route("/menu", methods=["GET"])
def get_menu():
    """Retrieve list of menu items with optional filtering."""
    category_slug = request.args.get("category")
    search = request.args.get("search", "").strip()
    is_veg = request.args.get("is_veg")

    query = MenuItem.query.filter_by(is_available=True)

    if category_slug:
        cat = MenuCategory.query.filter_by(slug=category_slug).first()
        if cat:
            query = query.filter_by(category_id=cat.id)
        else:
            return jsonify({"status": "error", "message": "Category not found"}), 404

    if search:
        query = query.filter(
            (MenuItem.name.ilike(f"%{search}%")) | (MenuItem.description.ilike(f"%{search}%"))
        )

    if is_veg is not None:
        if is_veg.lower() in ["true", "1", "yes"]:
            query = query.filter_by(is_veg=True)
        elif is_veg.lower() in ["false", "0", "no"]:
            query = query.filter_by(is_veg=False)

    items = query.order_by(MenuItem.display_order.asc(), MenuItem.name.asc()).all()
    return jsonify({
        "status": "success",
        "count": len(items),
        "data": [item.to_dict() for item in items],
    })


@api_bp.route("/categories", methods=["GET"])
def get_categories():
    """Retrieve all active cuisine categories."""
    categories = MenuCategory.query.filter_by(is_active=True).order_by(MenuCategory.display_order).all()
    return jsonify({
        "status": "success",
        "count": len(categories),
        "data": [
            {
                "id": c.id,
                "name": c.name,
                "slug": c.slug,
                "description": c.description,
                "image_url": c.image_url,
            }
            for c in categories
        ],
    })


@api_bp.route("/menu/<int:item_id>", methods=["GET"])
def get_menu_item(item_id):
    """Retrieve details for a single menu item."""
    item = MenuItem.query.get(item_id)
    if not item:
        return jsonify({"status": "error", "message": "Menu item not found"}), 404
    return jsonify({"status": "success", "data": item.to_dict()})


@api_bp.route("/cart", methods=["GET"])
def get_cart():
    """Retrieve current shopping cart status."""
    cart_data = get_cart_details()
    serializable_items = [
        {
            "id": ci["item"].id,
            "name": ci["item"].name,
            "price": ci["item"].price,
            "quantity": ci["quantity"],
            "subtotal": ci["item_total"],
            "is_veg": ci["item"].is_veg,
            "image_url": ci["item"].image_url,
        }
        for ci in cart_data["items"]
    ]
    return jsonify({
        "status": "success",
        "items": serializable_items,
        "subtotal": cart_data["subtotal"],
        "delivery_fee": cart_data["delivery_fee"],
        "grand_total": cart_data["grand_total"],
        "total_quantity": cart_data["total_quantity"],
    })


@api_bp.route("/reservations", methods=["POST"])
@csrf.exempt
def create_reservation_api():
    """Create a table reservation via JSON API."""
    data = request.get_json(silent=True) or {}

    required_fields = ["customer_name", "customer_email", "customer_phone", "reservation_date", "reservation_time", "num_guests"]
    missing = [f for f in required_fields if not data.get(f)]
    if missing:
        return jsonify({"status": "error", "message": f"Missing required fields: {', '.join(missing)}"}), 400

    try:
        res_date = datetime.strptime(data["reservation_date"], "%Y-%m-%d").date()
    except ValueError:
        return jsonify({"status": "error", "message": "Invalid date format. Use YYYY-MM-DD"}), 400

    if res_date < date.today():
        return jsonify({"status": "error", "message": "Reservation date cannot be in the past"}), 400

    try:
        guests = int(data["num_guests"])
        if guests < 1 or guests > 20:
            return jsonify({"status": "error", "message": "Party size must be between 1 and 20"}), 400
    except (ValueError, TypeError):
        return jsonify({"status": "error", "message": "Invalid number of guests"}), 400

    res_time = str(data["reservation_time"]).strip()

    # Slot capacity check
    max_capacity = int(RestaurantSetting.get_value("max_guests_per_slot", 30))
    existing = Reservation.query.filter(
        Reservation.reservation_date == res_date,
        Reservation.reservation_time == res_time,
        Reservation.status.in_(["Confirmed", "Pending"]),
    ).all()
    booked = sum(b.num_guests for b in existing)

    if booked + guests > max_capacity:
        remaining = max(0, max_capacity - booked)
        return jsonify({
            "status": "error",
            "message": f"Time slot capacity exceeded. Only {remaining} seats remaining.",
            "remaining_capacity": remaining,
        }), 409

    ref = Reservation.generate_reference_number()
    res = Reservation(
        reference_number=ref,
        customer_name=data["customer_name"].strip(),
        customer_email=data["customer_email"].strip().lower(),
        customer_phone=data["customer_phone"].strip(),
        reservation_date=res_date,
        reservation_time=res_time,
        num_guests=guests,
        special_requests=data.get("special_requests", "").strip() or None,
        status="Confirmed",
    )
    db.session.add(res)
    db.session.commit()

    return jsonify({
        "status": "success",
        "message": "Reservation confirmed",
        "data": {
            "reference_number": ref,
            "date": str(res_date),
            "time": res_time,
            "guests": guests,
            "customer_name": res.customer_name,
        },
    }), 201


@api_bp.route("/contact", methods=["POST"])
@csrf.exempt
def create_contact_message_api():
    """Submit a contact inquiry via JSON API."""
    data = request.get_json(silent=True) or {}

    required_fields = ["name", "email", "subject", "message"]
    missing = [f for f in required_fields if not data.get(f)]
    if missing:
        return jsonify({"status": "error", "message": f"Missing required fields: {', '.join(missing)}"}), 400

    msg = ContactMessage(
        name=data["name"].strip(),
        email=data["email"].strip().lower(),
        phone=data.get("phone", "").strip() or None,
        subject=data["subject"].strip(),
        message=data["message"].strip(),
    )
    db.session.add(msg)
    db.session.commit()

    return jsonify({
        "status": "success",
        "message": "Your message has been received. Thank you!",
    }), 201
