import psycopg2
import re
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

# encrypt/decrypt obj
cipher = PKCS1_OAEP.new(key=pu_key)
decrypt = PKCS1_OAEP.new(key=pr_key)
                                                                                                                                        

# decrypt message
@app.route("/")
def index():
    # products query here
    if "user" in session:
        user = session['user']
        print(session)
        return render_template('Main-Page.html', user = user)
    else:
        print(session)
        return render_template('Main-Page.html')

@app.route("/purchase")
def purchase():
    return render_template('Purchase.html')

@app.route("/parts")
def parts():
    return render_template('Parts-Page.html')

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


if __name__ == '__main__':
    app.run(debug=True)

cur.close()
conn.close()