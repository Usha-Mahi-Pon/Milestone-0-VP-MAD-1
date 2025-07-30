#!/usr/bin/env python3
"""
Initialize database with test data
"""

from app import app
from extensions import db
from models.models import User, ParkingLot, ParkingSpot, Reservation
from datetime import datetime, timedelta

def init_database():
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Create admin user (if not exists)
        if not User.query.filter_by(role='admin').first():
            admin = User(username="admin", password="admin123", full_name="Administrator", role="admin")
            db.session.add(admin)
        
        # Create a test user
        if not User.query.filter_by(username='testuser').first():
            test_user = User(username="testuser", password="test123", full_name="Test User", role="user")
            db.session.add(test_user)
        
        # Create a test parking lot
        if not ParkingLot.query.first():
            lot = ParkingLot(
                prime_location_name="Downtown Mall",
                price=50.0,  # ₹50 per hour
                address="123 Main Street",
                pincode="12345",
                maximum_number_of_spots=5
            )
            db.session.add(lot)
            db.session.commit()
            
            # Create parking spots for the lot
            for i in range(5):
                spot = ParkingSpot(lot_id=lot.id, status='A')
                db.session.add(spot)
        
        db.session.commit()
        print("✅ Database initialized with test data")
        print("✅ Admin login: admin/admin123")
        print("✅ Test user login: testuser/test123")

if __name__ == '__main__':
    init_database()