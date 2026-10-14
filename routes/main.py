from flask import Blueprint, render_template, request, flash, redirect, url_for
from extensions import db
from models import CarouselSlide, MenuCategory, MenuItem, RestaurantSetting, ContactMessage
from forms import ContactForm

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    # Load dynamic carousel slides
    slides = CarouselSlide.query.filter_by(is_active=True).order_by(CarouselSlide.display_order).all()

    # Dynamic special cuisines for the cards
    special_cuisines = []
    cuisine_slugs = ["italian", "mexican", "chinese", "japanese"]
    for slug in cuisine_slugs:
        cat = MenuCategory.query.filter_by(slug=slug).first()
        if cat:
            items = MenuItem.query.filter_by(category_id=cat.id, is_available=True).all()
            if items:
                prices = [item.price for item in items]
                min_p = min(prices)
                max_p = max(prices)
                price_range = f"₹{int(min_p)} - ₹{int(max_p)}" if min_p != max_p else f"₹{int(min_p)}"
            else:
                price_range = "Starting from ₹199"

            special_cuisines.append({
                "category": cat,
                "name": f"{cat.name} cuisine",
                "price_range": price_range,
                "slug": cat.slug,
                "image": cat.image_url or f"/static/images/dishes/{slug}.jpg",
                "item_count": len(items),
            })

    # Contact form instance for the home contact section
    contact_form = ContactForm()

    return render_template(
        "index.html",
        slides=slides,
        special_cuisines=special_cuisines,
        contact_form=contact_form,
    )


@main_bp.route("/contact", methods=["GET", "POST"])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        msg = ContactMessage(
            name=form.name.data.strip(),
            email=form.email.data.strip(),
            phone=form.phone.data.strip() if form.phone.data else None,
            subject=form.subject.data.strip(),
            message=form.message.data.strip(),
        )
        db.session.add(msg)
        db.session.commit()
        flash("Thank you for contacting Forks & Knife! We have received your message and will respond shortly.", "success")
        return redirect(url_for("main.contact"))

    return render_template("contact.html", form=form)


@main_bp.route("/about")
def about():
    return render_template("about.html")
