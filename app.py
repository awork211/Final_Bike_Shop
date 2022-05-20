from math import prod
import psycopg2
import psycopg2.extras
from flask import Flask, render_template, request, url_for, redirect, session
from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA
from binascii import hexlify

app = Flask(__name__)

app.secret_key = 'bikeshopkey'

# connect database
conn = psycopg2.connect(
    host = 'localhost',
    database = 'user_info'
)



cur = conn.cursor()

# add users table
# cur.execute("""
# CREATE TABLE user_info (
#    email varchar(200),
#    username varchar(200),
#    password BYTEA,
#    phone varchar(10),
#    address varchar(300)
#     );
# """)
# conn.commit()





pr_key = RSA.import_key(open('private.pem', 'r').read())
pu_key = RSA.import_key(open('public.pem', 'r').read())

# # encrypt/decrypt obj
cipher = PKCS1_OAEP.new(key=pu_key)
decrypt = PKCS1_OAEP.new(key=pr_key)
                                                                                                                                        
# add products table
# cur.execute("""
#     CREATE TABLE products (
#         name varchar(100),
#         image varchar(100),
#         category varchar(50),
#         price numeric,
#         quantity int
#     )
# """)
# conn.commit()


@app.route("/", methods=["GET","POST"])
def index():
    # products query here
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("""
        SELECT * FROM products WHERE category = 'complete'
    """)
    conn.commit()
    products = cur.fetchall()
        
    
    if "user" in session:
        user = session['user']
        print(session)
        return render_template('Main-Page.html', user = user, products = products)
    else:
        print(session)
        return render_template('Main-Page.html', products = products)

@app.route('/cart', methods=["GET","POST"])
def addToCart():
    if request.method == 'POST':
        quantity = request.form['quantity']
        itemName = request.form['itemName']
        print(itemName)
        print(session['user'])
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        cur.execute("""
            SELECT * FROM products WHERE name= %s
        """, [itemName])
        conn.commit()
        product = cur.fetchone()

        # creating item for cart
        itemArray = { product['name']: {'quantity': quantity, 'price': product['price'], 'image': product['image'], 'total_price': product['price'] * int(quantity), 'name': product['name']}}
        print(itemArray, 'printed')
        cart_total_quantity = 0
        cart_total_price = 0

        # merge items in cart
        def mergeArr(firstArr, secArr):
            if isinstance(firstArr, list) and isinstance(secArr, list):
                return firstArr + secArr
            elif isinstance(firstArr, dict) and isinstance(secArr, dict):
                return dict(list(firstArr.items()) + list(secArr.items()))
            elif isinstance(firstArr, set) and isinstance(secArr, set):
                return firstArr.union(secArr)
            False
        
        if 'item_cart' in session:
            print('in session')
            if product['name'] in session['item_cart']:
                # add cart properties
                for key, value in session['item_cart'].items():
                    if product['name'] == key:
                        print(session['item_cart'], 'item cart')
                        old_quantity = session['item_cart'][key]['quantity']
                        total_quantity = int(old_quantity) + int(quantity)
                        session['item_cart'][key]['quantity'] = total_quantity
                        session['item_cart'][key]['total_price'] = total_quantity * product['price']
            else:
                # merge new item with cart
                session['item_cart'] = mergeArr(session['item_cart'], itemArray)
            # add individual properties
            for key, value in session['item_cart'].items():
                individual_quantity = int(session['item_cart'][key]['quantity'])
                individual_price = float(session['item_cart'][key]['total_price'])
                cart_total_quantity = cart_total_quantity + individual_quantity
                cart_total_price = cart_total_price + individual_price
        else:
            # add item in cart, add totals
            session['item_cart'] = itemArray
            cart_total_quantity = cart_total_quantity + int(quantity)
            cart_total_price = cart_total_price + int(quantity) * product['price']
        # set totals in session
        session['cart_total_price'] = cart_total_price
        session['cart_total_quantity'] = cart_total_quantity
        print(session['item_cart'])
        return render_template('cart.html')
    elif request.method == 'GET':
        return render_template('cart.html')
    else:
        return 'Error adding item to cart'

@app.route('/clear')
def clear():
    session.clear()
    return redirect(url_for('index'))

@app.route('/delete/<string:name>')
def delete_item(name):
    cart_total_price = 0
    cart_total_quantity = 0

    # casted as list to avoid runtime err
    for item in list(session['item_cart'].items()):
        if name == item[0]:
            # delete item from session
            session['item_cart'].pop(name, None)
            if 'item_cart' in session:
                for key, value in session['item_cart'].items():
                    individual_quantity = int(session['item_cart'][key]['quantity'])
                    individual_price = float(session['item_cart'][key]['total_price'])
                    cart_total_quantity = cart_total_quantity + individual_quantity
                    cart_total_price = cart_total_price + individual_price
    
    # update cart total if not empty
    if cart_total_quantity == 0:
        session.pop('item_cart', None)
    else:
        session['cart_total_quantity'] = cart_total_quantity
        session['cart_total_price'] = float("{:.2f}".format(cart_total_price))
    return redirect(url_for('addToCart')) #change url to cart


@app.route("/prebuilt")
def prebuilt():
     # products query here
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("""
        SELECT * FROM products WHERE category = 'complete'
    """)
    conn.commit()
    products = cur.fetchall()
        
    
    if "user" in session:
        user = session['user']
        print(session)
        return render_template('Prebuilt.html', user = user, products = products)
    else:
        print(session)
        return render_template('Prebuilt.html', products = products)

@app.route("/parts")
def parts():
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("""
        SELECT * FROM products WHERE name LIKE 'Frame%'
    """)
    conn.commit()
    frames = cur.fetchall()
    return render_template('Parts-Page.html', frames = frames)

@app.route("/customize")
def customize():
    return render_template("Customised-Bikes.html")

@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user = request.form['user']
        password = request.form['pasw']
        email = request.form['email']
        phone = request.form['phone']
        address = request.form['address']

        enc_pass = cipher.encrypt(bytes(password, 'utf-8'))

        # insert into db table
        sql = """
            INSERT INTO user_info (email, username, password, phone, address)
            VALUES (%s, %s, %s, %s, %s)
        """
        args = email, user, enc_pass, phone, address

        cur.execute(sql, args)
        conn.commit()
        return redirect(url_for('logMessage', message = 'New Account Created!'))

    return render_template('Registration.html')

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == 'POST':
        # check credentials
        user = request.form['user']
        password = request.form['pasw']

        # query pass
        cur.execute("""
            SELECT username FROM user_info WHERE username = %s
        """, [user])
        conn.commit()
        
        userQuery = cur.fetchone()
        
        cur.execute("""
            SELECT password FROM user_info WHERE username = %s
        """, [user])
        conn.commit()

        if userQuery is not None:
            passQuery = cur.fetchone() 
            bytePass = passQuery[0].tobytes()
            finalPass = decrypt.decrypt(bytePass)
            
            if password == finalPass.decode('utf-8'):
                print('Password matches!')
                session['user'] = user
                return redirect(url_for('index'))
            else:
                print('Password does not match.')
                return redirect(url_for('logMessage', message = 'Incorrect Password'))
        else:
            print('User does not exist.')
            return redirect(url_for('logMessage', message = 'User does not exist'))
    return render_template('Login.html')


@app.route("/login/<message>")
def logMessage(message):
    return render_template('Login.html', message = message)

@app.route("/register/<message>")
def regMessage(message):
    return render_template('Registration.html', message = message)

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for('login'))

@app.route("/admin")
def admin():
    return render_template("admin.html")


if __name__ == '__main__':
    app.run(debug=True)

cur.close()
conn.close()
