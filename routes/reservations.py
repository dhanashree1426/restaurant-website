from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import current_user
from datetime import date
from extensions import db
from models import Reservation, RestaurantSetting
from forms import ReservationForm

reservations_bp = Blueprint("reservations", __name__)


@reservations_bp.route("/", methods=["GET", "POST"])
def index():
    form = ReservationForm()

    if request.method == "GET" and current_user.is_authenticated:
        form.customer_name.data = current_user.name
        form.customer_email.data = current_user.email
        form.customer_phone.data = current_user.phone

    if form.validate_on_submit():
        res_date = form.reservation_date.data
        res_time = form.reservation_time.data
        guests = form.num_guests.data

        # 1. Past date validation
        if res_date < date.today():
            flash("Reservation date cannot be in the past.", "danger")
            return render_template("reservations.html", form=form)

        # 2. Capacity Check
        max_capacity = int(RestaurantSetting.get_value("max_guests_per_slot", 30))
        existing_bookings = Reservation.query.filter(
            Reservation.reservation_date == res_date,
            Reservation.reservation_time == res_time,
            Reservation.status.in_(["Confirmed", "Pending"]),
        ).all()

        current_guest_count = sum(b.num_guests for b in existing_bookings)

        if current_guest_count + guests > max_capacity:
            remaining = max(0, max_capacity - current_guest_count)
            if remaining > 0:
                flash(
                    f"Sorry! The selected time slot ({res_time}) only has room for {remaining} more guests. Please select another slot or reduce party size.",
                    "warning",
                )
            else:
                flash(
                    f"Sorry! The selected time slot ({res_time}) is fully booked for {res_date.strftime('%d %b %Y')}. Please choose an alternative time.",
                    "warning",
                )
            return render_template("reservations.html", form=form)

        # 3. Create Reservation
        ref_num = Reservation.generate_reference_number()
        reservation = Reservation(
            reference_number=ref_num,
            user_id=current_user.id if current_user.is_authenticated else None,
            customer_name=form.customer_name.data.strip(),
            customer_email=form.customer_email.data.strip().lower(),
            customer_phone=form.customer_phone.data.strip(),
            reservation_date=res_date,
            reservation_time=res_time,
            num_guests=guests,
            special_requests=form.special_requests.data.strip() if form.special_requests.data else None,
            status="Confirmed",
        )
        db.session.add(reservation)
        db.session.commit()

        flash(f"Table reserved successfully! Your booking reference is {ref_num}.", "success")
        return redirect(url_for("reservations.confirmation", reference_number=ref_num))

    return render_template("reservations.html", form=form)


@reservations_bp.route("/<string:reference_number>/confirmation")
def confirmation(reference_number):
    reservation = Reservation.query.filter_by(reference_number=reference_number).first_or_404()
    return render_template("reservation_confirmation.html", reservation=reservation)
