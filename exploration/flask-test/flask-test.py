from flask import Flask
from main import capitalise_name

app = Flask(__name__)


@app.route('/')
def hello_world():
    capital_name = capitalise_name('shai')
    return f"<a href='/home'>Hey {capital_name}</a>"


@app.route('/home')
def home_page():
    return 'home'


app.run(debug=True, port=5000)
