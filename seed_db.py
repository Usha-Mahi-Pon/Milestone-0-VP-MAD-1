from datetime import datetime, timedelta
from app import app, db
from models import User, ParkingLot, ParkingSpot, Reservation

with app.app_context():
    # Clear old data
    db.drop_all()
    db.create_all()
    print("✅ Database reset completed")

    # -------------------
    # 1. Admin User
    # -------------------
    admin = User(username="admin", password="admin123", full_name="Administrator", role="admin")
    db.session.add(admin)

    # -------------------
    # 2. Sample Users
    # -------------------
    users = [
        User(username="john", password="1234", full_name="John Doe", role="user"),
        User(username="alice", password="1234", full_name="Alice Smith", role="user"),
        User(username="bob", password="1234", full_name="Bob Williams", role="user")
    ]
    db.session.add_all(users)

    # -------------------
    # 3. Parking Lots & Spots
    # -------------------
    lot1 = ParkingLot(
        prime_location_name="City Center Mall",
        price=50.0,
        address="123 Main Street",
        pincode="600001",
        maximum_number_of_spots=5
    )
    lot2 = ParkingLot(
        prime_location_name="Airport Parking",
        price=80.0,
        address="Airport Road",
        pincode="600027",
        maximum_number_of_spots=3
    )

    db.session.add_all([lot1, lot2])
    db.session.commit()

    # Add spots automatically
    for lot in [lot1, lot2]:
        for i in range(lot.maximum_number_of_spots):
            spot = ParkingSpot(lot_id=lot.id, status='A')  # A = Available
            db.session.add(spot)
    db.session.commit()

    # -------------------
    # 4. Sample Reservations
    # -------------------
    # Assign John a spot in Lot1 (active)
    active_spot = ParkingSpot.query.filter_by(lot_id=lot1.id, status='A').first()
    active_spot.status = 'O'
    reservation1 = Reservation(
        spot_id=active_spot.id,
        user_id=users[0].id,
        parking_timestamp=datetime.now(),
        leaving_timestamp=None
    )

    # Assign Alice a past reservation in Lot2
    past_spot = ParkingSpot.query.filter_by(lot_id=lot2.id, status='A').first()
    past_spot.status = 'A'
    start_time = datetime.now() - timedelta(hours=3)
    end_time = datetime.now() - timedelta(hours=1)
    reservation2 = Reservation(
        spot_id=past_spot.id,
        user_id=users[1].id,
        parking_timestamp=start_time,
        leaving_timestamp=end_time
    )

    db.session.add_all([reservation1, reservation2])
    db.session.commit()

    print("✅ Sample data inserted successfully")
    print(f"Users: {User.query.count()}, Lots: {ParkingLot.query.count()}, Spots: {ParkingSpot.query.count()}, Reservations: {Reservation.query.count()}")
