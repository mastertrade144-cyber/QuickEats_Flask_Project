from flask import render_template, request, redirect, url_for, session, flash, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from database import get_db

def register_routes(app):

    def db():
        return get_db(app.config["DATABASE"])

    def current_user():
        if "user_id" not in session:
            return None
        conn = db()
        user = conn.execute("SELECT * FROM users WHERE id=?", (session["user_id"],)).fetchone()
        conn.close()
        return user

    def cart_data():
        cart = session.get("cart", {})
        if not cart:
            return [], 0, 0
        conn = db()
        ids = [int(x) for x in cart.keys()]
        placeholders = ",".join("?" * len(ids))
        foods = conn.execute(
            f"SELECT f.*, r.name AS restaurant_name FROM foods f JOIN restaurants r ON r.id=f.restaurant_id WHERE f.id IN ({placeholders})",
            ids
        ).fetchall()
        conn.close()
        items, subtotal = [], 0
        for food in foods:
            qty = int(cart[str(food["id"])])
            line = food["price"] * qty
            subtotal += line
            items.append({"food": food, "quantity": qty, "line_total": line})
        return items, subtotal, len(items)

    @app.context_processor
    def inject_globals():
        items, subtotal, count = cart_data()
        return {"current_user": current_user(), "cart_count": sum(i["quantity"] for i in items)}

    @app.route("/")
    def splash():
        if session.get("user_id"):
            return redirect(url_for("home"))
        return render_template("splash.html")

    @app.route("/auth", methods=["GET", "POST"])
    def auth():
        if request.method == "POST":
            action = request.form.get("action")
            conn = db()
            email = request.form.get("email", "").strip().lower()
            if action == "signup":
                name = request.form.get("name", "").strip()
                password = request.form.get("password", "")
                if not name or not email or len(password) < 6:
                    flash("Please provide a name, email and password of at least 6 characters.", "error")
                else:
                    try:
                        cur = conn.execute(
                            "INSERT INTO users(name,email,password_hash) VALUES (?,?,?)",
                            (name, email, generate_password_hash(password))
                        )
                        conn.commit()
                        session["user_id"] = cur.lastrowid
                        conn.close()
                        return redirect(url_for("home"))
                    except Exception:
                        flash("An account with this email already exists.", "error")
            else:
                password = request.form.get("password", "")
                user = conn.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
                if user and check_password_hash(user["password_hash"], password):
                    session["user_id"] = user["id"]
                    conn.close()
                    return redirect(url_for("home"))
                flash("Invalid email or password.", "error")
            conn.close()
        return render_template("auth.html")

    @app.route("/logout")
    def logout():
        session.clear()
        return redirect(url_for("splash"))

    @app.route("/home")
    def home():
        conn = db()
        restaurants = conn.execute("SELECT r.*, c.name AS category_name FROM restaurants r LEFT JOIN categories c ON c.id=r.category_id ORDER BY r.rating DESC").fetchall()
        categories = conn.execute("SELECT * FROM categories").fetchall()
        conn.close()
        return render_template("home.html", restaurants=restaurants, categories=categories)

    @app.route("/search")
    def search():
        q = request.args.get("q", "").strip()
        category = request.args.get("category", "")
        conn = db()
        sql = """
            SELECT r.*, c.name AS category_name
            FROM restaurants r LEFT JOIN categories c ON c.id=r.category_id
            WHERE 1=1
        """
        params = []
        if q:
            sql += " AND (r.name LIKE ? OR r.cuisine LIKE ? OR r.description LIKE ?)"
            params += [f"%{q}%", f"%{q}%", f"%{q}%"]
        if category:
            sql += " AND c.name=?"
            params.append(category)
        sql += " ORDER BY r.rating DESC"
        restaurants = conn.execute(sql, params).fetchall()
        categories = conn.execute("SELECT * FROM categories").fetchall()
        conn.close()
        return render_template("search.html", restaurants=restaurants, categories=categories, q=q, selected_category=category)

    @app.route("/categories")
    def categories():
        conn = db()
        rows = conn.execute("SELECT c.*, COUNT(r.id) AS restaurant_count FROM categories c LEFT JOIN restaurants r ON r.category_id=c.id GROUP BY c.id").fetchall()
        conn.close()
        return render_template("categories.html", categories=rows)

    @app.route("/offers")
    def offers():
        conn = db()
        restaurants = conn.execute("SELECT * FROM restaurants ORDER BY rating DESC").fetchall()
        conn.close()
        return render_template("offers.html", restaurants=restaurants)

    @app.route("/restaurants")
    def restaurants():
        conn = db()
        rows = conn.execute("SELECT r.*, c.name AS category_name FROM restaurants r LEFT JOIN categories c ON c.id=r.category_id ORDER BY r.rating DESC").fetchall()
        conn.close()
        return render_template("restaurants.html", restaurants=rows)

    @app.route("/restaurant/<int:restaurant_id>")
    def restaurant_detail(restaurant_id):
        conn = db()
        restaurant = conn.execute("""
            SELECT r.*, c.name AS category_name FROM restaurants r
            LEFT JOIN categories c ON c.id=r.category_id WHERE r.id=?
        """, (restaurant_id,)).fetchone()
        foods = conn.execute("SELECT * FROM foods WHERE restaurant_id=? ORDER BY name", (restaurant_id,)).fetchall()
        reviews = conn.execute("""
            SELECT rv.*, u.name FROM reviews rv JOIN users u ON u.id=rv.user_id
            WHERE rv.restaurant_id=? ORDER BY rv.created_at DESC
        """, (restaurant_id,)).fetchall()
        conn.close()
        if not restaurant:
            return "Restaurant not found", 404
        return render_template("restaurant_detail.html", restaurant=restaurant, foods=foods, reviews=reviews)

    @app.route("/food/<int:food_id>")
    def food_detail(food_id):
        conn = db()
        food = conn.execute("""
            SELECT f.*, r.name AS restaurant_name, r.id AS restaurant_id, r.rating
            FROM foods f JOIN restaurants r ON r.id=f.restaurant_id WHERE f.id=?
        """, (food_id,)).fetchone()
        conn.close()
        if not food:
            return "Food not found", 404
        return render_template("food_detail.html", food=food)

    @app.post("/cart/add/<int:food_id>")
    def add_to_cart(food_id):
        conn = db()
        food = conn.execute("SELECT id FROM foods WHERE id=?", (food_id,)).fetchone()
        conn.close()
        if not food:
            flash("Food item not found.", "error")
            return redirect(request.referrer or url_for("home"))
        cart = session.setdefault("cart", {})
        key = str(food_id)
        cart[key] = int(cart.get(key, 0)) + int(request.form.get("quantity", 1))
        session.modified = True
        flash("Item added to cart.", "success")
        return redirect(request.form.get("next") or request.referrer or url_for("cart"))

    @app.route("/cart")
    def cart():
        items, subtotal, _ = cart_data()
        delivery = 30 if items else 0
        return render_template("cart.html", items=items, subtotal=subtotal, delivery=delivery, total=subtotal+delivery)

    @app.post("/cart/update")
    def update_cart():
        cart = session.get("cart", {})
        for key, value in request.form.items():
            if key.startswith("qty_"):
                food_id = key[4:]
                try:
                    qty = int(value)
                    if qty <= 0:
                        cart.pop(food_id, None)
                    else:
                        cart[food_id] = min(qty, 20)
                except ValueError:
                    pass
        session["cart"] = cart
        return redirect(url_for("cart"))

    @app.post("/cart/remove/<int:food_id>")
    def remove_cart(food_id):
        cart = session.get("cart", {})
        cart.pop(str(food_id), None)
        session["cart"] = cart
        return redirect(url_for("cart"))

    @app.route("/checkout/address", methods=["GET", "POST"])
    def address():
        user = current_user()
        if not user:
            return redirect(url_for("auth"))
        items, subtotal, _ = cart_data()
        if not items:
            return redirect(url_for("cart"))
        if request.method == "POST":
            address_text = request.form.get("address", "").strip()
            if not address_text:
                flash("Please enter a delivery address.", "error")
            else:
                session["checkout_address"] = address_text
                return redirect(url_for("payment"))
        return render_template("address.html", user=user)

    @app.route("/checkout/payment", methods=["GET", "POST"])
    def payment():
        if not current_user():
            return redirect(url_for("auth"))
        items, subtotal, _ = cart_data()
        if not items:
            return redirect(url_for("cart"))
        address_text = session.get("checkout_address", "")
        if not address_text:
            return redirect(url_for("address"))
        delivery = 30
        if request.method == "POST":
            method = request.form.get("payment_method", "Cash on Delivery")
            session["payment_method"] = method
            return redirect(url_for("place_order"))
        return render_template("payment.html", subtotal=subtotal, delivery=delivery, total=subtotal+delivery)

    @app.route("/checkout/place-order", methods=["GET", "POST"])
    def place_order():
        if not current_user():
            return redirect(url_for("auth"))
        items, subtotal, _ = cart_data()
        address_text = session.get("checkout_address")
        payment_method = session.get("payment_method")
        if not items or not address_text or not payment_method:
            return redirect(url_for("cart"))
        delivery = 30
        conn = db()
        cur = conn.execute("""
            INSERT INTO orders(user_id,address,payment_method,subtotal,delivery_fee,total,status)
            VALUES (?,?,?,?,?,?,?)
        """, (session["user_id"], address_text, payment_method, subtotal, delivery, subtotal+delivery, "Order Placed"))
        order_id = cur.lastrowid
        for item in items:
            conn.execute(
                "INSERT INTO order_items(order_id,food_id,quantity,price) VALUES (?,?,?,?)",
                (order_id, item["food"]["id"], item["quantity"], item["food"]["price"])
            )
        conn.commit()
        conn.close()
        session["cart"] = {}
        session.pop("checkout_address", None)
        session.pop("payment_method", None)
        return redirect(url_for("confirmation", order_id=order_id))

    @app.route("/order/<int:order_id>/confirmation")
    def confirmation(order_id):
        if not current_user():
            return redirect(url_for("auth"))
        conn = db()
        order = conn.execute("SELECT * FROM orders WHERE id=? AND user_id=?", (order_id, session["user_id"])).fetchone()
        conn.close()
        if not order:
            return "Order not found", 404
        return render_template("confirmation.html", order=order)

    @app.route("/order/<int:order_id>/track")
    def track_order(order_id):
        if not current_user():
            return redirect(url_for("auth"))
        conn = db()
        order = conn.execute("SELECT * FROM orders WHERE id=? AND user_id=?", (order_id, session["user_id"])).fetchone()
        conn.close()
        if not order:
            return "Order not found", 404
        return render_template("track_order.html", order=order)

    @app.route("/orders")
    def orders():
        if not current_user():
            return redirect(url_for("auth"))
        conn = db()
        rows = conn.execute("SELECT * FROM orders WHERE user_id=? ORDER BY created_at DESC", (session["user_id"],)).fetchall()
        conn.close()
        return render_template("orders.html", orders=rows)

    @app.route("/profile", methods=["GET", "POST"])
    def profile():
        user = current_user()
        if not user:
            return redirect(url_for("auth"))
        if request.method == "POST":
            name = request.form.get("name", "").strip()
            phone = request.form.get("phone", "").strip()
            address_text = request.form.get("address", "").strip()
            conn = db()
            conn.execute("UPDATE users SET name=?, phone=?, address=? WHERE id=?", (name, phone, address_text, user["id"]))
            conn.commit()
            conn.close()
            flash("Profile updated.", "success")
            return redirect(url_for("profile"))
        return render_template("profile.html", user=user)

    @app.route("/settings")
    def settings():
        return render_template("settings.html")

    @app.route("/help")
    def help_center():
        return render_template("help.html")

    @app.post("/restaurant/<int:restaurant_id>/review")
    def review(restaurant_id):
        user = current_user()
        if not user:
            return redirect(url_for("auth"))
        rating = max(1, min(5, int(request.form.get("rating", 5))))
        comment = request.form.get("comment", "").strip()
        conn = db()
        conn.execute("INSERT INTO reviews(user_id,restaurant_id,rating,comment) VALUES (?,?,?,?)",
                     (user["id"], restaurant_id, rating, comment))
        conn.commit()
        conn.close()
        flash("Thank you for your review.", "success")
        return redirect(url_for("restaurant_detail", restaurant_id=restaurant_id))
