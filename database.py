import sqlite3
from werkzeug.security import generate_password_hash

def get_db(db_path):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db(db_path):
    conn = get_db(db_path)
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        phone TEXT DEFAULT '',
        address TEXT DEFAULT '',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        icon TEXT DEFAULT '🍽️'
    );

    CREATE TABLE IF NOT EXISTS restaurants (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        category_id INTEGER,
        cuisine TEXT NOT NULL,
        rating REAL DEFAULT 4.0,
        delivery_time TEXT DEFAULT '25-35 min',
        delivery_fee REAL DEFAULT 0,
        description TEXT DEFAULT '',
        image_url TEXT DEFAULT '',
        FOREIGN KEY(category_id) REFERENCES categories(id)
    );

    CREATE TABLE IF NOT EXISTS foods (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        restaurant_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        description TEXT DEFAULT '',
        price REAL NOT NULL,
        veg INTEGER DEFAULT 1,
        image_url TEXT DEFAULT '',
        FOREIGN KEY(restaurant_id) REFERENCES restaurants(id)
    );

    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        address TEXT NOT NULL,
        payment_method TEXT NOT NULL,
        subtotal REAL NOT NULL,
        delivery_fee REAL DEFAULT 0,
        total REAL NOT NULL,
        status TEXT DEFAULT 'Order Placed',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(id)
    );

    CREATE TABLE IF NOT EXISTS order_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER NOT NULL,
        food_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        price REAL NOT NULL,
        FOREIGN KEY(order_id) REFERENCES orders(id),
        FOREIGN KEY(food_id) REFERENCES foods(id)
    );

    CREATE TABLE IF NOT EXISTS reviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        restaurant_id INTEGER NOT NULL,
        rating INTEGER NOT NULL,
        comment TEXT DEFAULT '',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(id),
        FOREIGN KEY(restaurant_id) REFERENCES restaurants(id)
    );
    """)
    conn.commit()
    conn.close()

def seed_db(db_path):
    conn = get_db(db_path)

    if conn.execute("SELECT COUNT(*) FROM categories").fetchone()[0] == 0:
        categories = [
            ("Pizza", "🍕"), ("Burger", "🍔"), ("Indian", "🍛"),
            ("Chinese", "🥡"), ("Biryani", "🍗"), ("Desserts", "🍰"),
            ("Healthy", "🥗"), ("Drinks", "🥤")
        ]
        conn.executemany("INSERT INTO categories(name, icon) VALUES (?, ?)", categories)

    if conn.execute("SELECT COUNT(*) FROM restaurants").fetchone()[0] == 0:
        cat = {r["name"]: r["id"] for r in conn.execute("SELECT id,name FROM categories")}
        restaurants = [
            ("Spice Garden", cat["Indian"], "North Indian", 4.7, "25-30 min", 30, "Authentic Indian dishes prepared fresh every day.", "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?auto=format&fit=crop&w=900&q=80"),
            ("Pizza Planet", cat["Pizza"], "Italian", 4.5, "20-25 min", 25, "Wood-fired pizzas, pasta and Italian favourites.", "https://images.unsplash.com/photo-1513104890138-7c749659a591?auto=format&fit=crop&w=900&q=80"),
            ("Burger House", cat["Burger"], "American", 4.6, "20-30 min", 20, "Juicy burgers, crispy fries and cold drinks.", "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?auto=format&fit=crop&w=900&q=80"),
            ("Dragon Bowl", cat["Chinese"], "Chinese", 4.4, "30-35 min", 35, "Noodles, fried rice and classic Asian flavours.", "https://images.unsplash.com/photo-1563245372-f21724e3856d?auto=format&fit=crop&w=900&q=80"),
            ("Royal Biryani", cat["Biryani"], "Indian", 4.8, "30-40 min", 30, "Fragrant dum biryani and traditional sides.", "https://images.unsplash.com/photo-1589302168068-964664d93dc0?auto=format&fit=crop&w=900&q=80"),
        ]
        conn.executemany("""
            INSERT INTO restaurants
            (name,category_id,cuisine,rating,delivery_time,delivery_fee,description,image_url)
            VALUES (?,?,?,?,?,?,?,?)
        """, restaurants)

    if conn.execute("SELECT COUNT(*) FROM foods").fetchone()[0] == 0:
        rest = {r["name"]: r["id"] for r in conn.execute("SELECT id,name FROM restaurants")}
        foods = [
            (rest["Spice Garden"], "Butter Chicken", "Creamy tomato gravy with tender chicken.", 260, 0, "https://images.unsplash.com/photo-1603894584373-5ac82b2ae398?auto=format&fit=crop&w=700&q=80"),
            (rest["Spice Garden"], "Paneer Tikka", "Char-grilled cottage cheese with spices.", 220, 1, "https://images.unsplash.com/photo-1567188040759-fb8a883dc6d8?auto=format&fit=crop&w=700&q=80"),
            (rest["Spice Garden"], "Garlic Naan", "Soft naan topped with garlic and butter.", 70, 1, "https://images.unsplash.com/photo-1601050690597-df0568f70950?auto=format&fit=crop&w=700&q=80"),
            (rest["Pizza Planet"], "Margherita Pizza", "Classic tomato, mozzarella and basil.", 299, 1, "https://images.unsplash.com/photo-1574071318508-1cdbab80d002?auto=format&fit=crop&w=700&q=80"),
            (rest["Pizza Planet"], "Farmhouse Pizza", "Loaded with fresh vegetables and cheese.", 399, 1, "https://images.unsplash.com/photo-1579751626657-72bc17010498?auto=format&fit=crop&w=700&q=80"),
            (rest["Burger House"], "Classic Chicken Burger", "Crispy chicken, lettuce and house sauce.", 249, 0, "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?auto=format&fit=crop&w=700&q=80"),
            (rest["Burger House"], "Veggie Burger", "Crispy vegetable patty with fresh salad.", 199, 1, "https://images.unsplash.com/photo-1520072959219-c595dc870360?auto=format&fit=crop&w=700&q=80"),
            (rest["Dragon Bowl"], "Hakka Noodles", "Wok-tossed noodles with vegetables.", 210, 1, "https://images.unsplash.com/photo-1585032226651-759b368d7246?auto=format&fit=crop&w=700&q=80"),
            (rest["Dragon Bowl"], "Chicken Fried Rice", "Wok-fried rice with chicken and vegetables.", 240, 0, "https://images.unsplash.com/photo-1603133872878-684f208fb84b?auto=format&fit=crop&w=700&q=80"),
            (rest["Royal Biryani"], "Chicken Dum Biryani", "Long-grain basmati rice slow-cooked with chicken.", 289, 0, "https://images.unsplash.com/photo-1563379091339-03246963d96c?auto=format&fit=crop&w=700&q=80"),
            (rest["Royal Biryani"], "Veg Biryani", "Aromatic rice cooked with seasonal vegetables.", 229, 1, "https://images.unsplash.com/photo-1631515243349-e0cb75fb8d0d?auto=format&fit=crop&w=700&q=80"),
        ]
        conn.executemany("""
            INSERT INTO foods(restaurant_id,name,description,price,veg,image_url)
            VALUES (?,?,?,?,?,?)
        """, foods)

    # Demo account
    if conn.execute("SELECT COUNT(*) FROM users WHERE email='demo@quickeats.local'").fetchone()[0] == 0:
        conn.execute("""
            INSERT INTO users(name,email,password_hash,phone,address)
            VALUES (?,?,?,?,?)
        """, ("Demo User", "demo@quickeats.local",
              generate_password_hash("demo123"), "+91 90000 00000",
              "Andherighat, Assam, India"))

    conn.commit()
    conn.close()
