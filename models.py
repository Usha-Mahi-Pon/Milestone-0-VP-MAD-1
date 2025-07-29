from extensions import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100))
    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(50))
    role = db.Column(db.String(10))  # 'admin' or 'user'
    reservations = db.relationship('Reservation', backref='user', lazy=True)


class ParkingLot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    prime_location_name = db.Column(db.String(100))
    price = db.Column(db.Float)
    address = db.Column(db.String(200))
    pincode = db.Column(db.String(10))
    maximum_number_of_spots = db.Column(db.Integer)
    spots = db.relationship('ParkingSpot', backref='lot', lazy=True)


class ParkingSpot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lot_id = db.Column(db.Integer, db.ForeignKey('parking_lot.id'), nullable=False)
    status = db.Column(db.String(1), default='A')  # A=Available, O=Occupied
    reservations = db.relationship('Reservation', backref='spot', lazy=True)


class Reservation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    spot_id = db.Column(db.Integer, db.ForeignKey('parking_spot.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    parking_timestamp = db.Column(db.DateTime)
    leaving_timestamp = db.Column(db.DateTime)
