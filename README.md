# QuickEats — Flask Food Delivery Demo

A complete starter food-delivery web application based on the supplied QuickEats blueprint.

## Blueprint coverage

1. Splash Screen
2. Login / Sign Up
3. Home Screen
4. Search Screen
5. Categories Screen
6. Restaurant List
7. Restaurant Details
8. Menu / Food List
9. Food Details
10. Cart
11. Address / Location
12. Payment Method
13. Order Confirmation
14. Track Order
15. My Orders
16. Profile
17. Settings / Help

## Key features implemented

- User registration and login
- Password hashing
- Restaurant/category browsing
- Search and category filtering
- Restaurant menu and food details
- Session-based shopping cart
- Quantity update/remove
- Address checkout
- Payment-method selection (demo flow)
- Order placement
- Order confirmation
- Order tracking UI
- Order history
- Profile editing
- Restaurant ratings/reviews
- Responsive mobile-first interface
- SQLite database with automatic seed data

## Requirements

- Python 3.10+ recommended
- Flask
- A modern browser

## Run on Windows

```text
cd QuickEats_Flask_Project
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Open:

http://127.0.0.1:5000

## Demo login

Email: demo@quickeats.local
Password: demo123

## Project structure

```text
QuickEats_Flask_Project/
├── app.py
├── database.py
├── routes.py
├── requirements.txt
├── README.md
├── instance/
│   └── quickeats.db          # generated automatically
├── templates/
│   ├── base.html
│   ├── splash.html
│   ├── auth.html
│   ├── home.html
│   ├── search.html
│   ├── categories.html
│   ├── offers.html
│   ├── restaurants.html
│   ├── restaurant_detail.html
│   ├── food_detail.html
│   ├── cart.html
│   ├── address.html
│   ├── payment.html
│   ├── confirmation.html
│   ├── track_order.html
│   ├── orders.html
│   ├── profile.html
│   ├── settings.html
│   └── help.html
└── static/
    ├── css/style.css
    └── js/app.js
```

## Notes

This is a functional development/demo application, not a production payment or delivery platform. Payment is represented by a selection screen and no real payment gateway is charged.

For production, add CSRF protection, secure production secrets, server-side cart storage, PostgreSQL/MySQL, real payment integration, real-time courier location, push notifications, image storage, validation, rate limiting and deployment configuration.
