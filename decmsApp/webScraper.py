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
    Class receives url from the flask application. It contains various methods to download and or recursively download the contents 
    of a webpage(s). 
    """

    def __init__(self, url):
        """
        Constructor class. Variables: homeURL - the url the user 
        inputed into the GUI. basePath - the base directory path of the user inputed url. headers - headers required for making a succesful
        get request. processUrls - deque used for storing already downloaded urls. brokenUrls - set used for storing URL's that couldn't be downloaded. 
        """
        self.homeUrl = url
        self.basePath = self.formatUrl(urlparse(url).hostname)
        self.headers = {'User-Agent': '...', 'referer': 'https://...'}
        self.processedUrls = []
        self.brokenUrls = set()
        self.rootDirectory = self.basePath[7:]
        self.ignoredPages=[]


    def downloadWebPage(self, htmlLocalizer):
        """ 
        Returns string - needed for the flask application to function correctly. 
        Method creates a folder directory if it doesn't already exist. Does so according to HTML dom tree. Creates html soup from a parsed in url. 
        It creates an instance of of the htmlLocalizer class and retrieves a list of css, js and media files to be downloaded. 
        These files are then downloaded in parallel using the concurrent.futures lib. (A thread is created for each file in the list). 
        The html soup is updated with all embeded object links to point to the local saved data. Html soup is then saved into a local html file. 
        """
        htmlFile = htmlLocalizer.getHtmlFile()
        directory = htmlFile.localDirectory
        url = htmlFile.remoteDirectory
        if not os.path.exists(directory):
            os.makedirs(directory)
            
        print(f'Downloading {url}')
    
        
        htmlSoup = htmlLocalizer.getHtmlSoup()
        cssFiles = htmlLocalizer.getAndReplaceCSS()
        jsFiles = htmlLocalizer.getAndReplaceJS()
        mediaFiles = htmlLocalizer.getAllMediaLists()
       
        with concurrent.futures.ThreadPoolExecutor(max_workers = 20) as executor:
            print("Downloading CSS files...")
            executor.map(htmlLocalizer.downloadRemoteFile, cssFiles)

            print("Downloading JS files...")
            executor.map(htmlLocalizer.downloadRemoteFile, jsFiles)

            print("Downloading Media files...")
            executor.map(htmlLocalizer.downloadMedia, mediaFiles, timeout = 200)
            
            print("Removing unnecessary forms such as login boxes, searches...")
            executor.map(htmlLocalizer.removeForms()) 
        
        htmlLocalizer.replaceAllMedia()

        filename = htmlFile.newFilename


        localHtmlFile = htmlSoup.prettify("utf-8")
        with open(filename, "wb") as file:
            file.write(localHtmlFile)

        return filename

    def downloadAllWebPages(self,url,pathsToIgnore=['cdn-cgi']):
        """
        Crawls a website for all local webpages (that are on the same domain) and downloads them recursively,
        until there are no more unique pages. If a url does not work, method catches and saves the url in brokenUrls. 
        """
        print(f'Starting recursive download on {url} ...')
        
        try:
            
            url = self.formatUrl(url)
            response = requests.Session().get(url, headers=self.headers)
            htmlLocalize = htmlLocalizer(url, response)

            if(url not in self.processedUrls):
                self.processedUrls.append(self.formatUrl(url))

            
            for anchorTag in htmlLocalize.getHtmlSoup().find_all("a", href=True):
                currentUrl = self.formatUrl(anchorTag['href'])
                formattedBasePath = self.formatUrl(self.basePath)

                # If it is explicitely referring to a local page or has a relative path
                if formattedBasePath in currentUrl or currentUrl.startswith('/'):
                    #confirm we haven't processed the url, it's not in the queue to be processed and we shouldn't ignore it
                    if (not((currentUrl in self.processedUrls))):
                        ignoreUrl = self.shouldIgnoreUrl(currentUrl, pathsToIgnore)
                        if (not ignoreUrl):
                            self.processedUrls.append(self.formatUrl(currentUrl))
                            self.replaceHrefWithLocalPath(currentUrl,anchorTag)
                            self.downloadAllWebPages(currentUrl)
                        else:
                            self.ignoredPages.append(self.formatUrl(currentUrl))
                            self.processedUrls.append(self.formatUrl(currentUrl))
                    else:
                        if(not(currentUrl in self.ignoredPages)):
                            self.replaceHrefWithLocalPath(currentUrl,anchorTag)


            self.downloadWebPage(htmlLocalize)

                        
        except(requests.exceptions.MissingSchema, requests.exceptions.ConnectionError, requests.exceptions.InvalidURL, requests.exceptions.InvalidSchema):
            # Add broken urls to it’s own set, then continue
            self.brokenUrls.add(url)
            print('Oh no broken link :(')
            print(url)
            
    
    def shouldIgnoreUrl(self, url, pathsToIgnore, acceptableType="text/html"):
        """
        Checks if a url should be ignored according to whether it;
        A) contains any paths to ignore, or 
        B) is not of the acceptable content type
        """
        for pathToIgnore in pathsToIgnore:
            if pathToIgnore in url:
                return True

        #check for on-page links that use ids
        if url[url.rfind('/')+1:].startswith('#'):
            return True
        response = requests.Session().get(url, headers=self.headers)
        try:
            contentType = response.headers["content-type"]
            isAcceptable = acceptableType in contentType
            if not(isAcceptable):
                return True
            return False
        except Exception as e:
            print("HTML headers did not contain a content-type")
        

    
    def replaceHrefWithLocalPath(self, currentUrl, anchorTag):

        futureFileName = currentUrl[currentUrl.rfind("/")+1:]
        completePath = currentUrl[len(self.basePath):]

        if(currentUrl==self.basePath):
            anchorTag['href'] = "/"+futureFileName+".html"
        else:
            anchorTag['href'] =  os.path.join(completePath, futureFileName+".html")
        

    
                                    
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

    