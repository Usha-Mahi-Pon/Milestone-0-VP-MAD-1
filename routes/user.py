from flask import Blueprint, render_template, session, redirect, url_for, request, flash
from datetime import datetime
from models.models import db, ParkingLot, ParkingSpot, Reservation

user_bp = Blueprint('user', __name__, url_prefix='/user')

# ---------------- User Dashboard ----------------
@user_bp.route('/dashboard')
def dashboard():
    if 'role' not in session or session['role'] != 'user':
        return redirect(url_for('auth.login'))

    lots = ParkingLot.query.all()
    # Fetch user reservations to show active spot if any
    reservations = Reservation.query.filter_by(user_id=session['user_id']).all()
    return render_template('user_dashboard.html', lots=lots, reservations=reservations)

# ---------------- Reserve First Available Spot ----------------
@user_bp.route('/reserve/<int:lot_id>')
def reserve_spot(lot_id):
    if 'role' not in session or session['role'] != 'user':
        return redirect(url_for('auth.login'))

    user_id = session['user_id']
    
    # Check if user already has an active spot
    active_res = Reservation.query.filter_by(user_id=user_id, leaving_timestamp=None).first()
    if active_res:
        flash('You already have an active reservation!', 'danger')
        return redirect(url_for('user.dashboard'))

    # Find first available spot
    spot = ParkingSpot.query.filter_by(lot_id=lot_id, status='A').first()
    if not spot:
        flash('No available spots in this lot!', 'danger')
        return redirect(url_for('user.dashboard'))

    # Reserve the spot
    spot.status = 'O'
    reservation = Reservation(user_id=user_id, spot_id=spot.id, parking_timestamp=datetime.utcnow())
    db.session.add(reservation)
    db.session.commit()

    flash(f'Success! Spot {spot.spot_number} reserved in {spot.lot.prime_location_name}.', 'success')
    return redirect(url_for('user.dashboard'))

# ---------------- Release Spot ----------------
@user_bp.route('/release/<int:reservation_id>')
def release_spot(reservation_id):
    if 'role' not in session or session['role'] != 'user':
        return redirect(url_for('auth.login'))

    reservation = Reservation.query.get(reservation_id)
    if reservation and reservation.user_id == session['user_id'] and reservation.leaving_timestamp is None:
        reservation.leaving_timestamp = datetime.utcnow()

        # Calculate duration in hours
        duration_hours = (reservation.leaving_timestamp - reservation.parking_timestamp).total_seconds() / 3600
        reservation.parking_cost = round(duration_hours * reservation.spot.lot.price_per_hour, 2)

        # Free the spot
        reservation.spot.status = 'A'

        db.session.commit()
        flash(f'Spot {reservation.spot.spot_number} released! Cost: ₹{reservation.parking_cost}', 'success')

    return redirect(url_for('user.dashboard'))


@user_bp.route('/history-chart-data')
def history_chart_data():
    if 'role' not in session or session['role'] != 'user':
        return redirect(url_for('auth.login'))

    reservations = Reservation.query.filter_by(user_id=session['user_id']).all()

    # Prepare labels & durations
    labels = []
    durations = []

    for res in reservations:
        labels.append(f"Spot {res.spot.spot_number}")
        if res.leaving_timestamp:
            duration_hours = round((res.leaving_timestamp - res.parking_timestamp).total_seconds() / 3600, 2)
        else:
            duration_hours = 0
        durations.append(duration_hours)

    return jsonify({
        'labels': labels,
        'durations': durations
    })
