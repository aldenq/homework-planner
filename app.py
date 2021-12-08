from flask import Flask, redirect, url_for

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    return redirect("www.google.com")

if __name__ == '__main__':
    app.run(debug=True)