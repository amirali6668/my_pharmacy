from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # برای session

# نام کاربری و رمز ادمین
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = '1234'

# اتصال به دیتابیس
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

# صفحه اصلی فروشگاه
@app.route('/')
def index():
    conn = get_db_connection()
    products = conn.execute('SELECT * FROM products').fetchall()
    conn.close()
    return render_template('index.html', products=products)

# صفحه ورود ادمین
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            return redirect(url_for('admin'))
        else:
            return "<h3>نام کاربری یا رمز اشتباه است!</h3>"
    return '''
    <h2>ورود ادمین</h2>
    <form method="POST">
        <input type="text" name="username" placeholder="نام کاربری" required>
        <input type="password" name="password" placeholder="رمز عبور" required>
        <button type="submit">ورود</button>
    </form>
    '''

# پنل ادمین
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if not session.get('admin_logged_in'):
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = request.form['price']
        image = request.form['image']
        if name and price:
            conn.execute('INSERT INTO products (name, description, price, image) VALUES (?, ?, ?, ?)',
                         (name, description, price, image))
            conn.commit()
            return redirect(url_for('admin'))
    products = conn.execute('SELECT * FROM products').fetchall()
    conn.close()
    return render_template('admin.html', products=products)

# حذف محصول
@app.route('/delete/<int:id>')
def delete(id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('login'))
    conn = get_db_connection()
    conn.execute('DELETE FROM products WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin'))

# خروج ادمین
@app.route('/logout')
def logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('login'))

# اضافه کردن محصول به سبد خرید
@app.route('/add_to_cart/<int:product_id>')
def add_to_cart(product_id):
    if 'cart' not in session:
        session['cart'] = {}
    
    cart = session['cart']
    if str(product_id) in cart:
        cart[str(product_id)] += 1  # افزایش تعداد
    else:
        cart[str(product_id)] = 1  # اضافه کردن محصول جدید

    session['cart'] = cart
    return redirect(url_for('index'))

# نمایش سبد خرید
@app.route('/cart')
def cart():
    if 'cart' not in session or not session['cart']:
        return "<h3>سبد خرید خالی است!</h3><a href='/'>بازگشت به فروشگاه</a>"

    conn = get_db_connection()
    products_in_cart = []
    total = 0

    for product_id, quantity in session['cart'].items():
        product = conn.execute('SELECT * FROM products WHERE id = ?', (product_id,)).fetchone()
        if product:
            subtotal = product['price'] * quantity
            total += subtotal
            products_in_cart.append({
                'id': product['id'],
                'name': product['name'],
                'price': product['price'],
                'quantity': quantity,
                'subtotal': subtotal
            })
    conn.close()
    return render_template('cart.html', products=products_in_cart, total=total)

# حذف محصول از سبد خرید
@app.route('/remove_from_cart/<int:product_id>')
def remove_from_cart(product_id):
    if 'cart' in session:
        cart = session['cart']
        cart.pop(str(product_id), None)
        session['cart'] = cart
    return redirect(url_for('cart'))

if __name__ == '__main__':
    app.run(debug=True)
