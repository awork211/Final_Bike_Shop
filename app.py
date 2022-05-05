import psycopg2
from flask import Flask, render_template, request, url_for, redirect

app = Flask(__name__)

# connect database
# conn = psycopg2.connect(
#     host = 'localhost',
#     database = 'user_info'
# )

# cur = conn.cursor()

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

@app.route("/")
def index():
    return render_template('Login.html')

# @app.route("/register", methods=['GET', 'POST'])
# def register():
#     if request.method == 'POST':
#         email = request.form['email']
#         user = request.form['user']
#         password = request.form['pasw']
#         phone = request.form['phone']
#         address = request.form['address']
#     return render_template('Registration.html')

# @app.route("/login")
# def login():
#     return render_template('Login.html')


if __name__ == '__main__':
    app.run(debug=True)

# cur.close()
# conn.close()