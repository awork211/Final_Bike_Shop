import psycopg2
from flask import Flask, render_template, request, url_for, redirect
from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA
from binascii import hexlify

app = Flask(__name__)

# connect database
conn = psycopg2.connect(
    host = 'localhost',
    database = 'user_info'
)

cur = conn.cursor()

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

# encrypt obj
cipher = PKCS1_OAEP.new(key=pu_key)

# decrypt message
# decrypted_message = decrypt.decrypt(cipher_text)
@app.route("/")
def index():
    return render_template('Purchase.html')

@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user = request.form['user']
        password = request.form['pasw']
        email = request.form['email']
        phone = request.form['phone']
        address = request.form['address']

        enc_pass = cipher.encrypt(bytes(password, 'utf-8'))
        print(email, user, phone, address, enc_pass)
        # insert into db table
        sql = """
            INSERT INTO user_info (email, username, password, phone, address)
            VALUES (%s, %s, %s, %s, %s)
        """
        args = email, user, enc_pass, phone, address

        cur.execute(sql, args)
        conn.commit()

    return render_template('Registration.html')

@app.route("/login")
def login():
    # decrypt = PKCS1_OAEP.new(key=pr_key)
    return render_template('Login.html')


if __name__ == '__main__':
    app.run(debug=True)

cur.close()
conn.close()