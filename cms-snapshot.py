from flask import Flask, render_template, url_for, request, flash, send_file
from utils.web_scraper import web_scaper

app = Flask(__name__)


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/scrape', methods=["GET", "POST"])
def scrape():
    try:
        url = request.args.get('url')
        scraper = web_scaper(url)
        created_file = scraper.create_html_file(url)

        return send_file(created_file, as_attachment=True)

    except:
        return 'Did not work...'
        # flash(f'Failed to get page - did you leave out the "https://?"', 'danger')


if __name__ == '__main__':
    app.run(debug=True)
