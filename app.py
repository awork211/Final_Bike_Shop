from flask import Flask, render_template, request, url_for, redirect

app = Flask(__name__)

@app.route("/")
def index():
    return render_template('Main-Page.html')


if __name__ == '__main__':
    app.run(Debug=True)