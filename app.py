from flask import Flask, render_template, url_for, request, flash, send_file, redirect
from utils.web_scraper import web_scaper

app = Flask(__name__)
app.config['SECRET_KEY'] = "b5121df8bab03d4d38d2ebf2c08eebad"


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/scrape', methods=["GET", "POST"])
def scrape():
    url = request.args.get('url')

    try:
        scraper = web_scaper(url)
        created_file = scraper.create_html_file(url)
        send_file(created_file, as_attachment=True)

    except Exception as e:
        flash(str(e), 'danger')

    finally:
        return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)
