#!./env/bin/python3
from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
    return 'Hello oc.at!'


if __name__ == '__main__':
    app.run(debug=True)
