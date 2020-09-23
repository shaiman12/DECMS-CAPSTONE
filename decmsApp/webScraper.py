import requests
from datetime import datetime
from urllib.parse import urlparse, urljoin
from zipfile import ZipFile
from bs4 import BeautifulSoup as bSoup
from decmsApp.htmlLocalizer import htmlLocalizer

class webScraper():
    """
    To be Updated fully.
    Class receives url from the flask application. It creates the HTML soup and *runs recurvisely method that downlaods 
    each html file and its contents in given file tree.  
    """
    basePath = ''
    createdFiles = []

    def __init__(self, url):
        """
        Constructor class. Creates url and base path variables. 
        """
        self.url = url
        self.basePath = urlparse(url).hostname
    
    def createHtmlFile(self):
        """ 
         Method creates the html soup from the given url. 
         It creates an instance of the hmtlLocalizer variable and invokes its methods to download the css and object links. It updates
         the html text and outputs a local html file. 
        """

        htmlSoup = bSoup(requests.Session().get(self.url).content, "html.parser")

        localizeContent = htmlLocalizer(self.url, htmlSoup)
        localizeContent.downloadCSS()
        localizeContent.downloadImages()
        
        currentDateTime = datetime.now().strftime("%m/%d/%Y-%H:%M:%S").replace('/', '-')
        filename = self.basePath+'-'+currentDateTime+".html"
       
        localHtmlFile = htmlSoup.prettify("utf-8")
        with open(filename, "wb") as file:
            file.write(localHtmlFile)

        self.createdFiles.append(filename)
        return filename
    
