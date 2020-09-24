from flask import Flask, render_template, url_for, request, flash, send_file, redirect
from decmsApp.webScraper import webScraper
from decmsApp.websiteValidator import *

app = Flask(__name__)
app.config['SECRET_KEY'] = "b5121df8bab03d4d38d2ebf2c08eebad"


@app.route('/')
def home():
    """
    returns the html for the home page of the local GUI
    """
    return render_template('home.html')


@app.route('/scrape', methods=["GET", "POST"])
def scrape():
    """
    returns the html for the home page of the local GUI

    Method receives the url from the user input. In the try, attempts to create a webScraper variable.
    If unssuccessful catches and prints the error. 
    """
    url = request.args.get('url')

    try:
        wpSiteValidator = wpValidator(url)
        isValid = wpSiteValidator.runWebsiteChecks()
        if  isValid == False:
            print("Failed WordPress Checks.... Trying Drupal")
            drupSiteValidator = drupalValidator(url)
            isValid = drupSiteValidator.runWebsiteChecks()
            if  isValid == False:
                print("Failed Drupal Checks.... Trying Drupal")
                return
        
        scraper = webScraper(url)
        createdFile = scraper.downloadWebPage(url)
        send_file(createdFile, as_attachment=True)
        
        

    except Exception as e:
        flash(f'Failed to download a snapshot of {url}', 'danger')
        print(e)

    finally:
        return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)
