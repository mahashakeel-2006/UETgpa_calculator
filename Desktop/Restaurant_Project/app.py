import sqlite3
import os
import csv
from collections import defaultdict
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'super_secret_restaurant_key_v2'

DB = 'kitchen.db'
orders = {} 
token_counter = 100

def init_db():
    """Create DB and table if they don't exist"""
    conn = sqlite3.connect(DB)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS timers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            dish TEXT NOT NULL,
            end_time TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Initialize database tables on server startup
init_db()

def get_menu():
    menu = defaultdict(list)
    try:
        with open('data.csv', mode='r', encoding='utf-8-sig') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if not row.get('Item'):
                    continue
                category = row['Category'].strip()
                item = row['Item'].strip()
                price = float(row['Price'].strip())
                cook_time = int(row.get('CookTime', 10).strip() or 10)
                
                menu[category].append({
                    'name': item, 
                    'price': price, 
                    'cook_time': cook_time
                })
    except FileNotFoundError:
        print("Error: data.csv not found!")
    return dict(menu)

def get_item_price(item_name):
    menu = get_menu()
    for category, items in menu.items():
        for item in items:
            if item['name'] == item_name:
                return item['price']
    return 0

def get_item_details(item_name):
    """Looks up an item in the menu and returns its (price, cook_time)"""
    menu = get_menu()
    for category, items in menu.items():
        for item in items:
            if item['name'] == item_name:
                return item['price'], item['cook_time']
    return 0, 10

def calculate_split(total_amount, num_people):
    if num_people <= 0:
        return total_amount
    return total_amount / num_people

def calculate_total(cart_dict):
    total = 0
    items_list = list(cart_dict.keys())
    i = 0
    while i < len(items_list):
        item = items_list[i]
        qty = cart_dict[item]
        total += get_item_price(item) * qty
        i += 1
    return total

@app.route('/', methods=['GET', 'POST'])
def index():
    """Main page: shows menu, bill splitting, and kitchen timers"""
    if 'cart' not in session:
        session['cart'] = {}
    
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    
    if request.method == 'POST' and 'dish' in request.form:
        dish = request.form['dish']
        mins = int(request.form['minutes'])
        end_time = datetime.now() + timedelta(minutes=mins)
        conn.execute('INSERT INTO timers (dish, end_time) VALUES (?, ?)', 
                     (dish, end_time.isoformat()))
        conn.commit()
    
    # Clean out old timers (older than 5 mins) automatically
    old_timers = (datetime.now() - timedelta(minutes=5)).isoformat()
    conn.execute('DELETE FROM timers WHERE end_time <= ?', (old_timers,))
    conn.commit()
    
    timers = conn.execute('SELECT * FROM timers ORDER BY end_time ASC').fetchall()
    conn.close()
    
    cart_count = sum(session['cart'].values()) if session['cart'] else 0
    menu_items = get_menu()
    
    return render_template('index.html', timers=timers, now=datetime.now(), menu=menu_items, cart_count=cart_count)

@app.route('/add', methods=['POST'])
def add_to_cart():
    """Handles items added to cart and automatically starts their cooking timers"""
    if 'cart' not in session:
        session['cart'] = {}
        
    conn = sqlite3.connect(DB)
    
    for key, value in request.form.items():
        if key.startswith('qty_') and value.strip() and int(value) > 0:
            item_name = key[4:]  
            qty = int(value)
            
            if item_name in session['cart']:
                session['cart'][item_name] += qty
            else:
                session['cart'][item_name] = qty
            
            _, cook_time = get_item_details(item_name)
            
            if cook_time == 0:
                spaced_name = item_name.replace('_', ' ')
                _, cook_time = get_item_details(spaced_name)
                if cook_time > 0:
                    item_name = spaced_name
            
            if cook_time == 0:
                cook_time = 10
            
            end_time = datetime.now() + timedelta(minutes=cook_time)
            
            for _ in range(qty):
                conn.execute(
                    'INSERT INTO timers (dish, end_time) VALUES (?, ?)', 
                    (item_name, end_time.isoformat())
                )
                
    conn.commit()
    conn.close()
    session.modified = True
    return redirect(url_for('view_cart'))

@app.route('/cart', methods=['GET', 'POST'])
def view_cart():
    cart_dict = session.get('cart', {})
    total_bill = calculate_total(cart_dict)
    split_amount = total_bill
    people = 1

    if request.method == 'POST' and 'people' in request.form:
        people = int(request.form.get('people', 1))
        split_amount = calculate_split(total_bill, people)

    cart_details = []
    for item, qty in cart_dict.items():
        price = get_item_price(item)
        cart_details.append({
            'name': item,
            'qty': qty,
            'price': price,
            'subtotal': price * qty
        })

    return render_template('cart.html', cart_details=cart_details, total=total_bill, split=split_amount, people=people)

@app.route('/checkout')
def checkout():
    global token_counter
    cart_dict = session.get('cart', {})
    if len(cart_dict) > 0:
        token_counter += 1
        current_token = str(token_counter)
        orders[current_token] = "Pending ⏳"
        session.pop('cart', None) 
    return redirect(url_for('tracker'))

@app.route('/tracker')
def tracker():
    return render_template('tracker.html', orders=orders)

@app.route('/kitchen')
def kitchen():
    return render_template('kitchen.html', orders=orders)

@app.route('/update/<token>')
def update_status(token):
    if token in orders:
        status = orders[token]
        if status == "Pending ⏳":
            orders[token] = "In Preparation 🍳"
        elif status == "In Preparation 🍳":
            orders[token] = "Out for Delivery 🛵"
        elif status == "Out for Delivery 🛵":
            orders[token] = "Delivered ✅"
        else:
            del orders[token]
    return redirect(url_for('kitchen'))

@app.template_filter('as_datetime')
def as_datetime(s):
    """Safely convert ISO string or object to datetime for template rendering"""
    if isinstance(s, datetime):
        return s
    if not s:
        return datetime.now()
    try:
        return datetime.fromisoformat(str(s))
    except ValueError:
        return datetime.now()

if __name__ == '__main__':
    app.run(debug=True)
