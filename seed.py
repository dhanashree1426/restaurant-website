import os
from datetime import datetime, date, timedelta
from app import create_app
from extensions import db
from models import (
    User,
    MenuCategory,
    MenuItem,
    CarouselSlide,
    RestaurantSetting,
    Order,
    OrderItem,
    Reservation,
    ContactMessage,
)


def seed_database():
    db.create_all()

    # 1. Seed Restaurant Settings
    settings = {
        "restaurant_name": "FORKS & KNIFE",
        "tagline": "A Symphony of Global Flavors",
        "phone": "+91 98971 23456",
        "email": "forks.knife.dining@gmail.com",
        "address": "42 Gourmet Avenue, Connaught Place, New Delhi - 110001",
        "weekday_hours": "Monday - Friday: 11:00 AM - 11:00 PM",
        "weekend_hours": "Saturday - Sunday: 10:00 AM - 12:00 AM",
        "currency_symbol": "₹",
        "delivery_fee": "40.0",
        "free_delivery_threshold": "500.0",
        "max_guests_per_slot": "30",
    }
    for key, value in settings.items():
        RestaurantSetting.set_value(key, value)

    # 2. Seed Carousel Slides
    slides_data = [
        {
            "title": "Welcome to Our Restaurant",
            "subtitle": "Enjoy the best food in town!",
            "image_url": "/static/images/slider/slider-1.png",
            "button_text": "Explore Menu",
            "button_url": "/menu",
            "display_order": 1,
        },
        {
            "title": "Special Offers",
            "subtitle": "Check out our daily chef specials & sizzling platters!",
            "image_url": "/static/images/slider/slider-2.png",
            "button_text": "View Specials",
            "button_url": "/#specials",
            "display_order": 2,
        },
        {
            "title": "Great Taste",
            "subtitle": "Experience the finest handcrafted international flavors.",
            "image_url": "/static/images/slider/slider-3.png",
            "button_text": "Book a Table",
            "button_url": "/reservations",
            "display_order": 3,
        },
        {
            "title": "Delicious Meals",
            "subtitle": "Try our award-winning signature dishes made fresh to order!",
            "image_url": "/static/images/slider/slider-4.jpg",
            "button_text": "Order Online",
            "button_url": "/menu",
            "display_order": 4,
        },
    ]

    for s in slides_data:
        existing_slide = CarouselSlide.query.filter_by(title=s["title"]).first()
        if not existing_slide:
            slide = CarouselSlide(**s)
            db.session.add(slide)

    # 3. Seed Menu Categories
    categories_data = [
        {
            "name": "Italian",
            "slug": "italian",
            "description": "Authentic Italian handmade pasta, wood-fired pizzas, and creamy risottos.",
            "image_url": "/static/images/dishes/italian.jpg",
            "display_order": 1,
        },
        {
            "name": "Mexican",
            "slug": "mexican",
            "description": "Bold Mexican street tacos, cheesy burritos, quesadillas, and loaded nachos.",
            "image_url": "/static/images/dishes/mexican_tacos.jpg",
            "display_order": 2,
        },
        {
            "name": "Chinese",
            "slug": "chinese",
            "description": "Savory wok-tossed noodles, handcrafted dim sum, and aromatic gravies.",
            "image_url": "/static/images/dishes/chinese_noodles.jpg",
            "display_order": 3,
        },
        {
            "name": "Japanese",
            "slug": "japanese",
            "description": "Artful sushi rolls, fresh nigiri, rich ramen bowls, and tempura.",
            "image_url": "/static/images/dishes/japanese_sushi.jpg",
            "display_order": 4,
        },
        {
            "name": "Beverages",
            "slug": "beverages",
            "description": "Artisan mocktails, handcrafted coolers, iced teas, and thick shakes.",
            "image_url": "/static/images/dishes/virgin_mojito.jpg",
            "display_order": 5,
        },
        {
            "name": "Desserts",
            "slug": "desserts",
            "description": "Decadent Italian tiramisu, warm molten lava cakes, and gourmet treats.",
            "image_url": "/static/images/dishes/tiramisu.jpg",
            "display_order": 6,
        },
    ]

    cat_map = {}
    for c in categories_data:
        cat = MenuCategory.query.filter_by(slug=c["slug"]).first()
        if not cat:
            cat = MenuCategory(**c)
            db.session.add(cat)
            db.session.flush()
        cat_map[c["slug"]] = cat

    # 4. Seed Menu Items
    dishes = [
        # Italian
        {
            "category": "italian",
            "name": "Classic Margherita Pizza",
            "description": "Stone-baked sourdough topped with San Marzano tomato sauce, fresh buffalo mozzarella, and basil.",
            "price": 280.0,
            "is_veg": True,
            "is_special": True,
            "image_url": "/static/images/dishes/margherita_pizza.jpg",
            "prep_time_minutes": 20,
        },
        {
            "category": "italian",
            "name": "Truffle Fettuccine Alfredo",
            "description": "Handmade fettuccine tossed in rich parmesan cream sauce, black truffle oil, and herbs.",
            "price": 320.0,
            "is_veg": True,
            "is_special": True,
            "image_url": "/static/images/dishes/pasta_alfredo.jpg",
            "prep_time_minutes": 18,
        },
        {
            "category": "italian",
            "name": "Penne Arbiatta Piccante",
            "description": "Al dente penne pasta simmered in spicy garlic and ripe tomato sauce with black olives.",
            "price": 240.0,
            "is_veg": True,
            "is_special": False,
            "image_url": "/static/images/dishes/italian.jpg",
            "prep_time_minutes": 15,
        },
        {
            "category": "italian",
            "name": "Grilled Chicken Pesto Pizza",
            "description": "Crisp pizza crust topped with basil pesto, marinated herb chicken, sun-dried tomatoes, and mozzarella.",
            "price": 350.0,
            "is_veg": False,
            "is_special": False,
            "image_url": "/static/images/dishes/margherita_pizza.jpg",
            "prep_time_minutes": 22,
        },

        # Mexican
        {
            "category": "mexican",
            "name": "Crispy Veg Street Tacos (3 Pcs)",
            "description": "Crispy corn tortillas packed with spiced beans, roasted corn, guacamole, pico de gallo, and cotija cheese.",
            "price": 190.0,
            "is_veg": True,
            "is_special": True,
            "image_url": "/static/images/dishes/mexican_tacos.jpg",
            "prep_time_minutes": 15,
        },
        {
            "category": "mexican",
            "name": "Loaded Barbacoa Burrito",
            "description": "Large flour tortilla stuffed with cilantro lime rice, pinto beans, tender shredded meat, melted cheddar, and sour cream.",
            "price": 250.0,
            "is_veg": False,
            "is_special": True,
            "image_url": "/static/images/dishes/mexican_burrito.jpg",
            "prep_time_minutes": 18,
        },
        {
            "category": "mexican",
            "name": "Fiesta Quesadilla Grande",
            "description": "Golden grilled tortilla filled with Monterey Jack, sauteed bell peppers, jalapeños, and house salsa.",
            "price": 210.0,
            "is_veg": True,
            "is_special": False,
            "image_url": "/static/images/dishes/mexican_tacos.jpg",
            "prep_time_minutes": 14,
        },

        # Chinese
        {
            "category": "chinese",
            "name": "Sichuan Chili Garlic Noodles",
            "description": "Wok-tossed egg noodles with crisp julienned vegetables, fiery Sichuan chili oil, and toasted sesame.",
            "price": 180.0,
            "is_veg": True,
            "is_special": True,
            "image_url": "/static/images/dishes/chinese_noodles.jpg",
            "prep_time_minutes": 15,
        },
        {
            "category": "chinese",
            "name": "Steamed Crystal Dim Sum (6 Pcs)",
            "description": "Hand-folded translucent dumplings filled with water chestnuts, mushrooms, and scallions, served with spicy dip.",
            "price": 210.0,
            "is_veg": True,
            "is_special": True,
            "image_url": "/static/images/dishes/chinese_dimsum.jpg",
            "prep_time_minutes": 16,
        },
        {
            "category": "chinese",
            "name": "Kung Pao Chicken Wok Bowl",
            "description": "Succulent chicken morsels wok-fried with dry red chilies, roasted peanuts, and scallions in tangy brown sauce.",
            "price": 220.0,
            "is_veg": False,
            "is_special": False,
            "image_url": "/static/images/dishes/chinese_noodles.jpg",
            "prep_time_minutes": 20,
        },

        # Japanese
        {
            "category": "japanese",
            "name": "Signature Salmon Sushi Platter (8 Pcs)",
            "description": "Fresh Atlantic salmon nigiri, avocado maki, and spicy salmon rolls prepared with premium seasoned sushi rice.",
            "price": 490.0,
            "is_veg": False,
            "is_special": True,
            "image_url": "/static/images/dishes/japanese_sushi.jpg",
            "prep_time_minutes": 25,
        },
        {
            "category": "japanese",
            "name": "Tokyo Shoyu Ramen",
            "description": "Rich 12-hour simmered savory broth, springy ramen noodles, marinated soft-boiled egg, nori, bamboo shoots, and scallions.",
            "price": 380.0,
            "is_veg": False,
            "is_special": True,
            "image_url": "/static/images/dishes/japanese_ramen.jpg",
            "prep_time_minutes": 20,
        },
        {
            "category": "japanese",
            "name": "Vegetarian California Roll (8 Pcs)",
            "description": "Sushi roll filled with creamy ripe avocado, crisp cucumber, cream cheese, and toasted sesame seeds.",
            "price": 360.0,
            "is_veg": True,
            "is_special": False,
            "image_url": "/static/images/dishes/japanese_sushi.jpg",
            "prep_time_minutes": 20,
        },

        # Beverages
        {
            "category": "beverages",
            "name": "Fresh Mint Virgin Mojito",
            "description": "Crushed garden fresh mint leaves, zesty lime wedges, simple syrup, and sparkling soda over crushed ice.",
            "price": 140.0,
            "is_veg": True,
            "is_special": False,
            "image_url": "/static/images/dishes/virgin_mojito.jpg",
            "prep_time_minutes": 8,
        },
        {
            "category": "beverages",
            "name": "Passion Fruit Tropical Cooler",
            "description": "Vibrant passion fruit puree shaken with orange juice, crushed ice, and mint garnish.",
            "price": 160.0,
            "is_veg": True,
            "is_special": False,
            "image_url": "/static/images/dishes/virgin_mojito.jpg",
            "prep_time_minutes": 8,
        },

        # Desserts
        {
            "category": "desserts",
            "name": "Classic Venetian Tiramisu",
            "description": "Espresso-soaked savoiardi ladyfingers layered with silky mascarpone cream and dusted with dark cocoa.",
            "price": 220.0,
            "is_veg": True,
            "is_special": True,
            "image_url": "/static/images/dishes/tiramisu.jpg",
            "prep_time_minutes": 10,
        },
    ]

    for d in dishes:
        existing_item = MenuItem.query.filter_by(name=d["name"]).first()
        if not existing_item:
            cat = cat_map.get(d["category"])
            if cat:
                item = MenuItem(
                    category_id=cat.id,
                    name=d["name"],
                    description=d["description"],
                    price=d["price"],
                    is_veg=d["is_veg"],
                    is_special=d["is_special"],
                    image_url=d["image_url"],
                    prep_time_minutes=d["prep_time_minutes"],
                    is_available=True,
                )
                db.session.add(item)

    # 5. Seed Admin User
    admin_email = os.environ.get("ADMIN_EMAIL", "admin@forksandknife.com").lower()
    admin_password = os.environ.get("ADMIN_PASSWORD", "AdminPassword123!")

    admin_user = User.query.filter_by(email=admin_email).first()
    if not admin_user:
        admin_user = User(
            name="Executive Chef & Admin",
            email=admin_email,
            phone="+91 98971 00000",
            is_admin=True,
        )
        admin_user.set_password(admin_password)
        db.session.add(admin_user)
        print(f"Created default admin account: {admin_email}")

    # 6. Seed Demo Customer User
    customer_email = "customer@example.com"
    customer_user = User.query.filter_by(email=customer_email).first()
    if not customer_user:
        customer_user = User(
            name="Rahul Sharma",
            email=customer_email,
            phone="+91 98111 22334",
            is_admin=False,
        )
        customer_user.set_password("Customer123!")
        db.session.add(customer_user)
        db.session.flush()

        # Seed sample order for demonstration
        sample_order = Order(
            order_number=Order.generate_order_number(),
            user_id=customer_user.id,
            customer_name=customer_user.name,
            customer_email=customer_user.email,
            customer_phone=customer_user.phone,
            delivery_address="Flat 402, Royal Palms, Connaught Place, New Delhi",
            order_notes="Please include extra napkins and cutlery.",
            subtotal=600.0,
            delivery_fee=0.0,
            total_amount=600.0,
            payment_method="Cash on Delivery",
            status="Delivered",
        )
        db.session.add(sample_order)
        db.session.flush()

        # Sample reservation for demonstration
        tomorrow = date.today() + timedelta(days=1)
        sample_res = Reservation(
            reference_number=Reservation.generate_reference_number(),
            user_id=customer_user.id,
            customer_name=customer_user.name,
            customer_email=customer_user.email,
            customer_phone=customer_user.phone,
            reservation_date=tomorrow,
            reservation_time="19:30",
            num_guests=4,
            special_requests="Corner booth table by the window please.",
            status="Confirmed",
        )
        db.session.add(sample_res)

        # Sample contact inquiry
        sample_msg = ContactMessage(
            name="Priya Patel",
            email="priya.patel@example.com",
            phone="+91 98222 33445",
            subject="Private Birthday Dinner Inquiry",
            message="Hi, I would like to inquire about booking the mezzanine floor for a private birthday dinner for 15 guests next month. Do you have a set banquet menu?",
            is_read=False,
        )
        db.session.add(sample_msg)

    db.session.commit()
    print("Database seeding completed.")


if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        seed_database()
