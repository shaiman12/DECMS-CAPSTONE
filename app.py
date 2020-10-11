from flask import Flask, render_template, url_for, request, flash, send_file, redirect
import pathlib
import zipfile
import io
import os
import shutil
from decmsApp.webScraper import webScraper
from decmsApp.websiteValidator import *
import traceback

app = Flask(__name__)
app.config['SECRET_KEY'] = "b5121df8bab03d4d38d2ebf2c08eebad"


@app.route('/')
def home():
    """
    returns the html for the home page of the local GUI
    """
    text="hiii"
    return render_template('home.html')


@app.route('/success/<directory>')
def success(directory):
    """
    returns the html for the home page of the local GUI
    """
    text=directory
    return render_template('success.html',directory=directory)


@app.route('/scrape', methods=["GET", "POST"])
def scrape():
    """
    returns the html for the home page of the local GUI

    Method receives the url from the user input. In the try, attempts to create a webScraper variable.
    If unssuccessful catches and prints the error. 
    """
    url = request.args.get('url')
    allPagesRequested = request.args.get('all-pages') == 'on'

    try:
        
        wpSiteValidator = wpValidator(url)
        isValid = wpSiteValidator.runWebsiteChecks()

        if isValid == False:
            print("Failed WordPress Checks.... Trying Drupal")
            drupSiteValidator = drupalValidator(url)
            isValid = drupSiteValidator.runWebsiteChecks()
            if isValid == False:
                print("Failed Drupal Checks...")
                return
        
        scraper = webScraper(url)
        
        if(allPagesRequested):
            scraper.downloadAllWebPages(url)
            processedUrls = scraper.processedUrls
            brokenUrls = scraper.brokenUrls
            flash(
                f'Successfully downloaded recursively: {processedUrls} but the following were broken: {brokenUrls}', 'success')
            return redirect(url_for('success',directory=scraper.rootDirectory))


        else:
            url = scraper.formatUrl(url)
            scraper.downloadWebPage(url)
            flash(f'Successfully downloaded: {url}', 'success')
            return redirect(url_for('success',directory=scraper.rootDirectory))

    except Exception as e:
        flash(f'Failed to download a snapshot of {url}. Error: {e}', 'danger')
        print(e)
        traceback.print_exc()

    return redirect(url_for('home'))

@app.route('/download-zip', methods=["GET", "POST"])
def request_zip():
    filePath = request.args.get('directory')

    base_path = pathlib.Path('./'+filePath)
    data = io.BytesIO()
    with zipfile.ZipFile(data, mode='w') as z:
        for f_name in base_path.iterdir():
            z.write(f_name)
    data.seek(0)

    return   send_file(
        data,
        mimetype='application/zip',
        as_attachment=True,
        attachment_filename= filePath+'.zip')

@app.route('/delete-directory', methods=["GET", "POST"])
def delete_directory():
    directory = request.args.get('directory')
    path = "./"+directory
    shutil.rmtree(path, ignore_errors=True)
    flash(f'Successfully deleted the local snapshot of: {directory}', 'success')
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)
