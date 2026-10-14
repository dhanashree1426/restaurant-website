from flask import Blueprint, render_template, request, jsonify
from extensions import db
from models import MenuCategory, MenuItem

menu_bp = Blueprint("menu", __name__)


@menu_bp.route("/")
def index():
    categories = MenuCategory.query.filter_by(is_active=True).order_by(MenuCategory.display_order).all()

    # Query params
    active_category = request.args.get("category", "all")
    search_query = request.args.get("q", "").strip()
    diet_filter = request.args.get("diet", "all")  # all, veg, non-veg
    sort_option = request.args.get("sort", "default")

    query = MenuItem.query.filter_by(is_available=True)

    # Filter by category
    selected_category_obj = None
    if active_category != "all":
        selected_category_obj = MenuCategory.query.filter_by(slug=active_category).first()
        if selected_category_obj:
            query = query.filter_by(category_id=selected_category_obj.id)

    # Filter by search term
    if search_query:
        search_pattern = f"%{search_query}%"
        query = query.filter(
            (MenuItem.name.ilike(search_pattern)) | (MenuItem.description.ilike(search_pattern))
        )

    # Filter by dietary preference
    if diet_filter == "veg":
        query = query.filter_by(is_veg=True)
    elif diet_filter == "non-veg":
        query = query.filter_by(is_veg=False)

    # Sort
    if sort_option == "price_asc":
        query = query.order_by(MenuItem.price.asc())
    elif sort_option == "price_desc":
        query = query.order_by(MenuItem.price.desc())
    elif sort_option == "name_asc":
        query = query.order_by(MenuItem.name.asc())
    else:
        query = query.order_by(MenuItem.display_order.asc(), MenuItem.name.asc())

    items = query.all()

    return render_template(
        "menu.html",
        categories=categories,
        items=items,
        active_category=active_category,
        selected_category=selected_category_obj,
        search_query=search_query,
        diet_filter=diet_filter,
        sort_option=sort_option,
    )


@menu_bp.route("/item/<int:item_id>")
def item_detail(item_id):
    item = MenuItem.query.get_or_404(item_id)
    return jsonify(item.to_dict())
