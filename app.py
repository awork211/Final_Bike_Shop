from flask import Flask, render_template, request, url_for, redirect

app = Flask(__name__)

@app.route("/Login")
def login():
    return render_template('Login.html')

@app.route("/")
def index():
    return render_template('Main-Page.html')

@app.route("/register")
def register():
    return render_template('Registration.html')

if __name__ == '__main__':
    app.run(debug=True)