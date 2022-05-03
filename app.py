from flask import Flask, render_template, request, url_for, redirect

app = Flask(__name__)

@app.route("/")
def index():
    return render_template('Main-Page.html')

@app.route("/registration")
def register():
    return render_template('Registration.html')

@app.route("/login")
def login():
    return render_template('Login.html')

if __name__ == '__main__':
    app.run(Debug=True)