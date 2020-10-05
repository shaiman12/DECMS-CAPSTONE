import requests
import concurrent.futures
from datetime import datetime
from urllib.parse import urlparse, urljoin, urlsplit
from zipfile import ZipFile
from bs4 import BeautifulSoup as bSoup
from decmsApp.htmlLocalizer import htmlLocalizer
from collections import deque  



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
        self.basePath = urlparse(url).hostname
        self.headers = {'User-Agent': '...', 'referer': 'https://...'}
        self.processedUrls = set()
        self.brokenUrls = set()



    def downloadWebPage(self, url):
        """ 
         Method creates the html soup from the given url. 
         It creates an instance of the hmtlLocalizer variable and invokes its methods to download the css and object links. It updates
         the html text and outputs a local html file. 
        """
        print(f'Downloading {url}')
        htmlSoup = bSoup(requests.Session().get(
            url, headers=self.headers).content, "html.parser")

        localizeContent = htmlLocalizer(url, htmlSoup)

        cssFiles = localizeContent.getAndReplaceCSS()
        jsFiles = localizeContent.getAndReplaceJS()

        with concurrent.futures.ThreadPoolExecutor() as executor:
            executor.map(localizeContent.downloadUrlContent, cssFiles)
            executor.map(localizeContent.downloadUrlContent, jsFiles)
        
        """
        localizeContent.downloadCSS()
        localizeContent.downloadScripts()

        images = localizeContent.get_image_list()
        bgImages = localizeContent.get_bg_image_list()
        audios = localizeContent.get_audio_list()
        videos = localizeContent.get_video_list()

        with concurrent.futures.ThreadPoolExecutor() as executor:
            executor.map(localizeContent.download_media, images)
            executor.map(localizeContent.download_media, bgImages)
            executor.map(localizeContent.download_media, audios)
            executor.map(localizeContent.download_media, videos)
        
        localizeContent.replaceImg()
        localizeContent.replaceBgImages()
        localizeContent.replaceAudio()
        localizeContent.replaceVideos()

        print("Removing unnecessary forms like login boxes, searches...")
        localizeContent.removeForms()
        """
        currentDateTime = datetime.now().strftime(
            "%m/%d/%Y-%H:%M:%S").replace('/', '-')
        filename = self.basePath+'-'+currentDateTime+".html"

        localHtmlFile = htmlSoup.prettify("utf-8")
        with open(filename, "wb") as file:
            file.write(localHtmlFile)

        self.createdFiles.append(filename)
        return filename


    """
    Crawls a website for all local webpages (that are on the same domain) and downloads them recursively,
    until there are no more unique pages.
    """

    def downloadAllWebPages(self):
        print('Starting recursive download...')
        newUrls = deque([self.formatUrl(self.homeUrl)])


        # process urls one by one until we exhaust the queue 
        while len(newUrls):

        # print the current url    
            try:
                url = newUrls.popleft()
                htmlSoup = bSoup(requests.Session().get(url, headers=self.headers).content, "html.parser")
                self.downloadWebPage(url)
                self.processedUrls.add(url)
                for anchorTag in htmlSoup.find_all("a", href=True):
                    currentUrl = self.formatUrl(anchorTag['href'])
                #If it is explicitely referring to a local page or has a relative path
                    if self.basePath in currentUrl or currentUrl.startswith('/'):     

                        if( (not (currentUrl in self.processedUrls)) & (not (currentUrl in newUrls))):

                            newUrls.append(self.formatUrl(currentUrl))


            except(requests.exceptions.MissingSchema, requests.exceptions.ConnectionError, requests.exceptions.InvalidURL, requests.exceptions.InvalidSchema):    
                # Add broken urls to it’s own set, then continue    
                self.brokenUrls.add(url)
                print('Oh no broken link :(')
                continue
            
            


    """
    Converts any string that is designed to describe a web address into a comparable, 
    standardized format of 'http://example.com
    """

    def formatUrl(self,url):
        formattedUrl = url.replace('www.','')
        formattedUrl = formattedUrl.replace('https','http')

        if formattedUrl.startswith('/'):
            formattedUrl = "http://"+self.basePath + formattedUrl
        if formattedUrl.endswith('/'):
            formattedUrl = formattedUrl[:len(formattedUrl)-1]
        if not 'http' in formattedUrl:
            formattedUrl='http://'+formattedUrl
        return formattedUrl
