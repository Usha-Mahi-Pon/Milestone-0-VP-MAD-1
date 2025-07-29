from flask import Blueprint, render_template, session, redirect, url_for, request, flash
from models import db, User, ParkingLot, ParkingSpot

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# ---------------- Admin Dashboard ----------------
@admin_bp.route('/dashboard')
def dashboard():
    if 'role' not in session or session['role'] != 'admin':
        return redirect(url_for('auth.login'))

    lots = ParkingLot.query.all()
    users = User.query.filter(User.role != 'admin').all()
    return render_template('admin_dashboard.html', lots=lots, users=users)

# ---------------- Add Parking Lot ----------------
@admin_bp.route('/add_lot', methods=['GET', 'POST'])
def add_lot():
    if 'role' not in session or session['role'] != 'admin':
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        name = request.form['name']
        price = float(request.form['price'])
        address = request.form['address']
        pin_code = request.form['pin_code']
        max_spots = int(request.form['max_spots'])

        if not name or not address or max_spots <= 0:
            flash('All fields are required!', 'danger')
            return redirect(url_for('admin.add_lot'))

        # Create parking lot
        new_lot = ParkingLot(
            prime_location_name=name,
            price_per_hour=price,
            address=address,
            pin_code=pin_code,
            max_spots=max_spots
        )
        db.session.add(new_lot)
        db.session.commit()

        # Auto-create parking spots
        for i in range(1, max_spots + 1):
            spot = ParkingSpot(lot_id=new_lot.id, spot_number=i, status='A')
            db.session.add(spot)
        db.session.commit()

        flash('Parking Lot created successfully!', 'success')
        return redirect(url_for('admin.dashboard'))

    return render_template('add_lot.html')

# ---------------- Delete Parking Lot ----------------
@admin_bp.route('/delete_lot/<int:lot_id>')
def delete_lot(lot_id):
    if 'role' not in session or session['role'] != 'admin':
        return redirect(url_for('auth.login'))

    lot = ParkingLot.query.get(lot_id)
    if not lot:
        flash('Parking Lot not found!', 'danger')
        return redirect(url_for('admin.dashboard'))

    # Only delete if all spots are free
    occupied_spots = ParkingSpot.query.filter_by(lot_id=lot.id, status='O').count()
    if occupied_spots > 0:
        flash('Cannot delete! Some spots are still occupied.', 'danger')
        return redirect(url_for('admin.dashboard'))

    db.session.delete(lot)
    db.session.commit()
    flash('Parking Lot deleted successfully!', 'success')
    return redirect(url_for('admin.dashboard'))
from flask import jsonify

@admin_bp.route('/chart-data')
def chart_data():
    if 'role' not in session or session['role'] != 'admin':
        return redirect(url_for('auth.login'))

    lots = ParkingLot.query.all()
    
    # Prepare data for charts
    lot_names = []
    available_spots = []
    occupied_spots = []
    revenue = []

    for lot in lots:
        lot_names.append(lot.prime_location_name)
        available_count = sum(1 for spot in lot.spots if spot.status == 'A')
        occupied_count = sum(1 for spot in lot.spots if spot.status == 'O')
        available_spots.append(available_count)
        occupied_spots.append(occupied_count)

        # Calculate revenue from reservations
        lot_revenue = sum(res.parking_cost or 0 for spot in lot.spots for res in spot.reservations)
        revenue.append(lot_revenue)

    return jsonify({
        'lots': lot_names,
        'available': available_spots,
        'occupied': occupied_spots,
        'revenue': revenue
    })
