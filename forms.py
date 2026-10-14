from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    PasswordField,
    BooleanField,
    TextAreaField,
    FloatField,
    IntegerField,
    SelectField,
    DateField,
    SubmitField,
)
from wtforms.validators import (
    DataRequired,
    Email,
    Length,
    EqualTo,
    NumberRange,
    Optional,
    ValidationError,
)
from datetime import date


class LoginForm(FlaskForm):
    email = StringField("Email Address", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember = BooleanField("Remember Me")
    submit = SubmitField("Log In")


class RegisterForm(FlaskForm):
    name = StringField("Full Name", validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField("Email Address", validators=[DataRequired(), Email(), Length(max=120)])
    phone = StringField("Phone Number", validators=[DataRequired(), Length(min=10, max=15)])
    password = PasswordField(
        "Password",
        validators=[
            DataRequired(),
            Length(min=6, message="Password must be at least 6 characters long"),
        ],
    )
    confirm_password = PasswordField(
        "Confirm Password",
        validators=[
            DataRequired(),
            EqualTo("password", message="Passwords must match"),
        ],
    )
    submit = SubmitField("Create Account")


class ProfileForm(FlaskForm):
    name = StringField("Full Name", validators=[DataRequired(), Length(min=2, max=100)])
    phone = StringField("Phone Number", validators=[DataRequired(), Length(min=10, max=15)])
    current_password = PasswordField("Current Password (required to change password)", validators=[Optional()])
    new_password = PasswordField("New Password", validators=[Optional(), Length(min=6)])
    confirm_new_password = PasswordField(
        "Confirm New Password",
        validators=[
            EqualTo("new_password", message="New passwords must match"),
        ],
    )
    submit = SubmitField("Update Profile")


class ReservationForm(FlaskForm):
    customer_name = StringField("Full Name", validators=[DataRequired(), Length(min=2, max=100)])
    customer_email = StringField("Email Address", validators=[DataRequired(), Email()])
    customer_phone = StringField("Phone Number", validators=[DataRequired(), Length(min=10, max=15)])
    reservation_date = DateField("Date", validators=[DataRequired()], format="%Y-%m-%d")
    reservation_time = SelectField(
        "Time Slot",
        validators=[DataRequired()],
        choices=[
            ("11:30", "11:30 AM"),
            ("12:00", "12:00 PM"),
            ("12:30", "12:30 PM"),
            ("13:00", "01:00 PM"),
            ("13:30", "01:30 PM"),
            ("14:00", "02:00 PM"),
            ("18:00", "06:00 PM"),
            ("18:30", "06:30 PM"),
            ("19:00", "07:00 PM"),
            ("19:30", "07:30 PM"),
            ("20:00", "08:00 PM"),
            ("20:30", "08:30 PM"),
            ("21:00", "09:00 PM"),
            ("21:30", "09:30 PM"),
            ("22:00", "10:00 PM"),
        ],
    )
    num_guests = IntegerField(
        "Number of Guests",
        validators=[DataRequired(), NumberRange(min=1, max=20, message="Guests must be between 1 and 20")],
        default=2,
    )
    special_requests = TextAreaField("Special Requests / Dietary Notes", validators=[Optional(), Length(max=500)])
    submit = SubmitField("Confirm Reservation")

    def validate_reservation_date(self, field):
        if field.data and field.data < date.today():
            raise ValidationError("Reservation date cannot be in the past.")


class CheckoutForm(FlaskForm):
    customer_name = StringField("Full Name", validators=[DataRequired(), Length(min=2, max=100)])
    customer_email = StringField("Email Address", validators=[DataRequired(), Email()])
    customer_phone = StringField("Phone Number", validators=[DataRequired(), Length(min=10, max=15)])
    delivery_address = TextAreaField("Complete Delivery Address", validators=[DataRequired(), Length(min=10, max=300)])
    order_notes = TextAreaField("Cooking / Delivery Instructions", validators=[Optional(), Length(max=300)])
    payment_method = SelectField(
        "Payment Method",
        choices=[
            ("Cash on Delivery", "Cash on Delivery (CoD)"),
            ("Pay at Restaurant", "Pay at Restaurant / Counter"),
        ],
        default="Cash on Delivery",
    )
    submit = SubmitField("Place Order")


class ContactForm(FlaskForm):
    name = StringField("Your Name", validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField("Your Email", validators=[DataRequired(), Email()])
    phone = StringField("Phone Number", validators=[Optional(), Length(min=10, max=15)])
    subject = StringField("Subject", validators=[DataRequired(), Length(min=3, max=150)])
    message = TextAreaField("Your Message", validators=[DataRequired(), Length(min=10, max=1000)])
    submit = SubmitField("Send Message")


class MenuItemForm(FlaskForm):
    name = StringField("Dish Name", validators=[DataRequired(), Length(min=2, max=120)])
    category_id = SelectField("Category", coerce=int, validators=[DataRequired()])
    description = TextAreaField("Description", validators=[Optional(), Length(max=500)])
    price = FloatField("Price (₹)", validators=[DataRequired(), NumberRange(min=1.0, message="Price must be positive")])
    is_veg = BooleanField("Vegetarian Dish", default=True)
    is_available = BooleanField("Available in Stock", default=True)
    is_special = BooleanField("Highlight in Chef Specials", default=False)
    image_url = StringField("Image URL or Path", validators=[Optional(), Length(max=255)])
    prep_time_minutes = IntegerField("Prep Time (minutes)", default=20, validators=[NumberRange(min=5, max=120)])
    display_order = IntegerField("Display Order", default=0)
    submit = SubmitField("Save Item")


class CategoryForm(FlaskForm):
    name = StringField("Category Name", validators=[DataRequired(), Length(min=2, max=80)])
    slug = StringField("URL Slug (e.g. italian, chinese)", validators=[DataRequired(), Length(min=2, max=80)])
    description = StringField("Short Description", validators=[Optional(), Length(max=255)])
    image_url = StringField("Image URL or Path", validators=[Optional(), Length(max=255)])
    display_order = IntegerField("Display Order", default=0)
    submit = SubmitField("Save Category")


class SlideForm(FlaskForm):
    title = StringField("Slide Title", validators=[DataRequired(), Length(min=2, max=120)])
    subtitle = StringField("Subtitle / Tagline", validators=[DataRequired(), Length(min=2, max=200)])
    image_url = StringField("Image URL or Path", validators=[DataRequired(), Length(max=255)])
    button_text = StringField("Button Text", default="Explore Menu", validators=[Optional(), Length(max=50)])
    button_url = StringField("Button URL", default="/menu", validators=[Optional(), Length(max=255)])
    display_order = IntegerField("Display Order", default=0)
    is_active = BooleanField("Active Slide", default=True)
    submit = SubmitField("Save Slide")


class RestaurantSettingsForm(FlaskForm):
    restaurant_name = StringField("Restaurant Name", validators=[DataRequired()])
    tagline = StringField("Tagline / Motto", validators=[DataRequired()])
    phone = StringField("Contact Phone", validators=[DataRequired()])
    email = StringField("Contact Email", validators=[DataRequired(), Email()])
    address = StringField("Address", validators=[DataRequired()])
    weekday_hours = StringField("Weekday Hours", validators=[DataRequired()])
    weekend_hours = StringField("Weekend Hours", validators=[DataRequired()])
    delivery_fee = FloatField("Delivery Fee (₹)", validators=[NumberRange(min=0)])
    free_delivery_threshold = FloatField("Free Delivery Order Threshold (₹)", validators=[NumberRange(min=0)])
    max_guests_per_slot = IntegerField("Max Capacity per Time Slot", validators=[NumberRange(min=5, max=200)])
    submit = SubmitField("Update Settings")
