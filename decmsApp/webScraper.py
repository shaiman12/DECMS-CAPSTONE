import requests
import os
import concurrent.futures
from datetime import datetime
from urllib.parse import urlparse, urljoin, urlsplit
from zipfile import ZipFile
from bs4 import BeautifulSoup as bSoup
from decmsApp.htmlLocalizer import htmlLocalizer
from collections import deque
import urllib
import mimetypes
import pdb

class webScraper():
    """
    To be Updated fully.
    Class receives url from the flask application. It creates the HTML soup and *runs recurvisely method that downlaods 
    each html file and its contents in given file tree.  
    """

    def __init__(self, url):
        """
        Constructor class. Creates url and base path variables. 
        """
        self.createdFiles = []
        self.homeUrl = url
        self.basePath = self.formatUrl(urlparse(url).hostname)
        self.headers = {'User-Agent': '...', 'referer': 'https://...'}
        self.processedUrls = set()
        self.brokenUrls = set()

    def downloadWebPage(self, url):
        """ 
        Returns filename that... shaikus can you write this sentence. not actually sure what/why this returns something lol 
        Method creates html soup from a parsed in url. It creates an instance of of the htmlLocalizer class and retrieves a list 
        of css, js and media files to be downloading. These files are then downloaded in parallel using the concurrent.futures lib. (A thread is created for each file in the list). 
        The html soup is updated with all embeded object links to point to the local saved data. Html soup is then saved into a local html file. 
        """
        directory = url[7:] 
        if not os.path.exists(url[7:]):
            os.makedirs(url[7:])
            

        print(f'Downloading {url}')
        htmlSoup = bSoup(requests.Session().get(
            url, headers=self.headers).content, "html.parser")

        
        localizeContent = htmlLocalizer(url, htmlSoup, directory)

        cssFiles = localizeContent.getAndReplaceCSS()
        jsFiles = localizeContent.getAndReplaceJS()
        mediaFiles = localizeContent.getAllMediaLists()
       
        with concurrent.futures.ThreadPoolExecutor(max_workers = 20) as executor:
            print("Downloading CSS files...")
            executor.map(localizeContent.downloadUrlContent, cssFiles)

            print("Downloading JS files...")
            executor.map(localizeContent.downloadUrlContent, jsFiles)

            print("Downloading Media files...")
            executor.map(localizeContent.downloadMedia, mediaFiles, timeout = 200)
            
            print("Removing unnecessary forms such as login boxes, searches...")
            executor.map(localizeContent.removeForms()) 
        
        localizeContent.replaceAllMedia()
      
        currentDateTime = datetime.now().strftime(
            "%m/%d/%Y-%H:%M:%S").replace('/', '-')
        filename = os.path.join(directory, url[url.rfind("/")+1:] + currentDateTime+".html")


        localHtmlFile = htmlSoup.prettify("utf-8")
        with open(filename, "wb") as file:
            file.write(localHtmlFile)

        self.createdFiles.append(filename)
        return filename

    def downloadAllWebPages(self, pathsToIgnore=['cdn-cgi','wp-content']):
        """
        Crawls a website for all local webpages (that are on the same domain) and downloads them recursively,
        until there are no more unique pages.
        """
        print('Starting recursive download...')
        newUrls = deque([self.formatUrl(self.homeUrl)])
        # process urls one by one until we exhaust the queue
        while len(newUrls):

            # print the current url
            try:
                url = newUrls.popleft()
                response = requests.Session().get(url, headers=self.headers)

                htmlSoup = bSoup(response.content, "html.parser")
                self.downloadWebPage(url)
                self.processedUrls.add(url)
                for anchorTag in htmlSoup.find_all("a", href=True):
                    currentUrl = self.formatUrl(anchorTag['href'])
                    formattedBasePath = self.formatUrl(self.basePath)
                # If it is explicitely referring to a local page or has a relative path
                    if formattedBasePath in currentUrl or currentUrl.startswith('/'):
                        ignoreUrl = self.shouldIgnoreUrl(currentUrl, pathsToIgnore)
                        #confirm we haven't processed the url, it's not in the queue to be processed and we shouldn't ignore it
                        if (not ignoreUrl) & (not((currentUrl in self.processedUrls))) & (not (currentUrl in newUrls)) :
                            newUrls.append(self.formatUrl(currentUrl))
                

            except(requests.exceptions.MissingSchema, requests.exceptions.ConnectionError, requests.exceptions.InvalidURL, requests.exceptions.InvalidSchema):
                # Add broken urls to it’s own set, then continue
                self.brokenUrls.add(url)
                print('Oh no broken link :(')
                print(url)
                continue
    
    def shouldIgnoreUrl(self, url, pathsToIgnore, acceptableType="text/html"):
        """
        Checks if a url should be ignored according to whether it;
        A) contains any paths to ignore, or 
        B) is not of the acceptable content type
        """
        for pathToIgnore in pathsToIgnore:
            if pathToIgnore in url:
                return True
        response = requests.Session().get(url, headers=self.headers)
        contentType = response.headers["content-type"]
        isAcceptable = acceptableType in contentType
        if not(isAcceptable):
            return True
        return False
    
                                    
    def formatUrl(self, url):
        """
        Converts any string that is designed to describe a web address into a comparable, 
        standardized format of 'http://example.com
        """
        formattedUrl = url.replace('www.', '')
        formattedUrl = formattedUrl.replace('https', 'http')

        if formattedUrl.startswith('/'):
            formattedUrl = self.basePath + formattedUrl
        if formattedUrl.endswith('/'):
            formattedUrl = formattedUrl[:len(formattedUrl)-1]
        if not 'http' in formattedUrl:
            formattedUrl = 'http://'+formattedUrl
        return formattedUrl

