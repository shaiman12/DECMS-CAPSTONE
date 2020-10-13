from flask import Flask, render_template, url_for, request, flash, send_file, redirect, send_from_directory
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
    return render_template('home.html')


@app.route('/success/<directory>')
def success(directory):
    """
    returns the html for the success page after downloading a website 
    and saving it in a directory. eg. after downloading obama.org the enpoint hit will be 
    localhost:5000/success/obama.org - obama.org will be the directory in which the 
    site was saved
    """
    return render_template('success.html',directory=directory)


@app.route('/scrape', methods=["GET", "POST"])
def scrape():
    """
    returns the html for the home page of the local GUI

    Method receives the url from the user input. In the try, It first makes use of the websiteValidator class. This ensures the website 
    returns a HTTP status code of 200 (up and running) and then perfroms various checks to determine if it was built with wordPress or Drupal. The 
    method then attempts to make a webscraper variable and then depending on user input it a) recursively downloads the entire website b) downloads
    the singular inputed webpage. 
    If unssuccessful catches and prints the error. 
    """
    url = request.args.get('url')
    allPagesRequested = request.args.get('all-pages') == 'on'

    try:
        
        wpSiteValidator = wpValidator(url)

        #Performing wordPress Checks
        isValid = wpSiteValidator.runWebsiteChecks()
        if isValid == False:
            print("Failed WordPress Checks.... Trying Drupal")

            #Performing Drupal Checks
            drupSiteValidator = drupalValidator(url)
            isValid = drupSiteValidator.runWebsiteChecks()
            if isValid == False:
                print("Failed Drupal Checks...")
                print("Attempting to download other webite - this was built with Drupal and Wordpress in mind, but should still work as expected...")

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

def zipdir(path, zipFileHandler):
    """
    This method create a zip file of a given path, 
    recursively zipping it's sub folders
    """

    # zipFileHandler is zipfile handle
    for root, dirs, files in os.walk(path):
        for file in files:
            zipFileHandler.write(os.path.join(root, file))


@app.route('/download-zip', methods=["GET", "POST"])

def request_zip():
    """
    This endpoint expects a directory as a query param
    it returns a zip file of the directory (found in the file system 
    wherever this application is running from) to the user
    """
    filePath = request.args.get('directory')

    basePath = pathlib.Path('./'+filePath+'.zip')
    zipFileHandler = zipfile.ZipFile(f'{filePath}.zip', 'w', zipfile.ZIP_DEFLATED)
    zipdir(f'./{filePath}', zipFileHandler)
    zipFileHandler.close()
    return send_from_directory('./',filePath+".zip", as_attachment=True)


@app.route('/delete-directory', methods=["GET", "POST"])

def delete_directory():
    """
    This endpoint expects a directory as a query param
    it then deletes the entire directory and its contents
    """
    directory = request.args.get('directory')
    path = "./"+directory
    shutil.rmtree(path, ignore_errors=True)
    flash(f'Successfully deleted the local snapshot of: {directory}', 'success')
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)
