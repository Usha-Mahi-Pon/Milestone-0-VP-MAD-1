from flask import Flask, render_template, request, redirect, url_for, session, flash
from datetime import datetime
from extensions import db
from models.models import User, ParkingLot, ParkingSpot, Reservation

app = Flask(__name__)
app.secret_key = "supersecretkey"

# ------------------------ DATABASE CONFIG ------------------------
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# ------------------------ INIT DB & ADMIN ------------------------
with app.app_context():
    db.create_all()
    if not User.query.filter_by(role='admin').first():
        admin = User(username="admin", password="admin123", full_name="Administrator", role="admin")
        db.session.add(admin)
        db.session.commit()
        print("✅ Admin user created: admin/admin123")


# ------------------------ HOME ------------------------
@app.route('/')
def home():
    return redirect(url_for('login'))


# ------------------------ AUTH ------------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            flash(f"Welcome {user.full_name}!", "success")

            return redirect(url_for('admin_dashboard' if user.role == 'admin' else 'user_dashboard'))
        else:
            flash("Invalid username or password", "danger")

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        full_name = request.form['full_name']
        username = request.form['username']
        password = request.form['password']

        if User.query.filter_by(username=username).first():
            flash("Username already exists!", "danger")
        else:
            new_user = User(full_name=full_name, username=username, password=password, role='user')
            db.session.add(new_user)
            db.session.commit()
            flash("Registration successful! Please log in.", "success")
            return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for('login'))


# ------------------------ ADMIN DASHBOARD ------------------------
@app.route('/admin/dashboard')
def admin_dashboard():
    if 'role' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))

    lots = ParkingLot.query.all()
    users = User.query.filter_by(role='user').all()
    return render_template('admin_dashboard.html', lots=lots, users=users)


# ------------------------ ADD PARKING LOT ------------------------
@app.route('/admin/add_lot', methods=['GET', 'POST'])
def add_lot():
    if 'role' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))

    if request.method == 'POST':
        name = request.form['name']
        price = float(request.form['price'])
        address = request.form['address']
        pincode = request.form['pincode']
        max_spots = int(request.form['max_spots'])

        new_lot = ParkingLot(
            prime_location_name=name,
            price=price,
            address=address,
            pincode=pincode,
            maximum_number_of_spots=max_spots
        )
        db.session.add(new_lot)
        db.session.commit()

        # Create Parking Spots
        for _ in range(max_spots):
            spot = ParkingSpot(lot_id=new_lot.id, status='A')
            db.session.add(spot)
        db.session.commit()

        flash("Parking lot created successfully!", "success")
        return redirect(url_for('admin_dashboard'))

    return render_template('add_lot.html')


# ------------------------ EDIT PARKING LOT ------------------------
@app.route('/admin/edit_lot/<int:lot_id>', methods=['GET', 'POST'])
def edit_lot(lot_id):
    if 'role' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))

    lot = ParkingLot.query.get_or_404(lot_id)

    if request.method == 'POST':
        lot.prime_location_name = request.form['name']
        lot.price = float(request.form['price'])
        lot.address = request.form['address']
        lot.pincode = request.form['pincode']
        new_max_spots = int(request.form['max_spots'])

        # Adjust parking spots
        current_spots = ParkingSpot.query.filter_by(lot_id=lot_id).count()

        if new_max_spots > current_spots:
            # Add new spots
            for _ in range(new_max_spots - current_spots):
                spot = ParkingSpot(lot_id=lot.id, status='A')
                db.session.add(spot)
        elif new_max_spots < current_spots:
            # Remove only available spots if reducing
            removable_spots = ParkingSpot.query.filter_by(lot_id=lot.id, status='A').limit(current_spots - new_max_spots).all()
            if len(removable_spots) < (current_spots - new_max_spots):
                flash("Cannot reduce spots: some are occupied!", "danger")
                return redirect(url_for('admin_dashboard'))

            for spot in removable_spots:
                db.session.delete(spot)

        lot.maximum_number_of_spots = new_max_spots
        db.session.commit()
        flash("Parking lot updated successfully!", "success")
        return redirect(url_for('admin_dashboard'))

    return render_template('edit_lot.html', lot=lot)


# ------------------------ DELETE LOT ------------------------
@app.route('/admin/delete_lot/<int:lot_id>', methods=['POST'])
def delete_lot(lot_id):
    if 'role' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))

    lot = ParkingLot.query.get_or_404(lot_id)
    occupied = ParkingSpot.query.filter_by(lot_id=lot_id, status='O').count()

    if occupied > 0:
        flash("Cannot delete lot with active reservations!", "danger")
        return redirect(url_for('admin_dashboard'))

    ParkingSpot.query.filter_by(lot_id=lot_id).delete()
    db.session.delete(lot)
    db.session.commit()
    flash("Parking lot deleted successfully!", "success")
    return redirect(url_for('admin_dashboard'))


# ------------------------ USER DASHBOARD ------------------------
@app.route('/user/dashboard')
def user_dashboard():
    if 'role' not in session or session['role'] != 'user':
        return redirect(url_for('login'))

    lots = ParkingLot.query.all()
    reservations = Reservation.query.filter_by(user_id=session['user_id']).all()
    return render_template('user_dashboard.html', lots=lots, reservations=reservations)


# ------------------------ RESERVATION ------------------------
@app.route('/reserve/<int:lot_id>', methods=['POST'])
def reserve_spot(lot_id):
    if 'role' not in session or session['role'] != 'user':
        return redirect(url_for('login'))

    spot = ParkingSpot.query.filter_by(lot_id=lot_id, status='A').first()
    if not spot:
        flash("No available spots in this lot.", "danger")
        return redirect(url_for('user_dashboard'))

    spot.status = 'O'
    reservation = Reservation(
        spot_id=spot.id,
        user_id=session['user_id'],
        parking_timestamp=datetime.now(),
        leaving_timestamp=None
    )
    db.session.add(reservation)
    db.session.commit()
    flash("Spot reserved successfully!", "success")
    return redirect(url_for('user_dashboard'))


@app.route('/release/<int:res_id>', methods=['POST'])
def release_spot(res_id):
    if 'role' not in session or session['role'] != 'user':
        return redirect(url_for('login'))

    reservation = Reservation.query.get(res_id)
    if reservation and reservation.user_id == session['user_id'] and reservation.leaving_timestamp is None:
        reservation.leaving_timestamp = datetime.now()
        
        # Calculate parking duration in hours
        duration = reservation.leaving_timestamp - reservation.parking_timestamp
        duration_hours = duration.total_seconds() / 3600
        
        # Calculate cost based on lot price per hour
        lot_price = reservation.spot.lot.price
        reservation.parking_cost = round(duration_hours * lot_price, 2)
        
        # Release the spot
        reservation.spot.status = 'A'
        db.session.commit()
        
        flash(f"Spot released successfully! Total cost: ₹{reservation.parking_cost}", "success")

    return redirect(url_for('user_dashboard'))


if __name__ == '__main__':
    app.run(debug=True)