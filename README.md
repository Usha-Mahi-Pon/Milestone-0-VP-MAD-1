# Milestone-0-VP-MAD-1

The platform will have two roles:


Admin - root access - It is the superuser of the app and requires no registration

Admin is also known as the superuser
Admin can create a new parking lot
Each parking lot can have any number of parking spots for 4-wheeler parking
Each parking lot can have a different price
Admin can view the status of all available parking spots on his/her dashboard
Admin can edit/delete any number of parking lots, i.e., admin can increase or decrease the number of parking spots inside the lot.

User - Can reserve a parking space
Register/Login
Choose an available parking lot
Book the spot (automatically allotted by the app after booking)
Release or vacate the spot
Terminologies

User: The user will register/login and reserve any parking spot.


Admin: The superuser with full control over other users and data. No

registration is required, i.e. the admin should exist whenever the database is

created.


Parking lot: It’s the physical space where the collection of parking spots are available for an area. The parking lot may contain the following attributes.


id - primary key
prime_location_name
Price
Address
Pin code
maximum_number_of_spots
etc: Additional fields (if any)

Parking spot: The physical space for parking a 4-wheeler parking. The parking spot may contain the following attributes.


id - primary key
lot_id (foreign key-parking lot)
status(O-occupied/A-available)
etc: Additional fields (if any)

Reserve parking spot: Allocates parking spot as per the user requests.

This may contain the following attributes.


id - primary key
spot_id (foreign key-parking spot)
user_id(foreign key-users)
Parking_timestamp
Leaving_timestamp
parking_cost / unit time