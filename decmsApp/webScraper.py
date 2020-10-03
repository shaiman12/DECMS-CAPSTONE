import requests
from datetime import datetime
from urllib.parse import urlparse, urljoin
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


    def downloadWebPage(self, url):
        """ 
         Method creates the html soup from the given url. 
         It creates an instance of the hmtlLocalizer variable and invokes its methods to download the css and object links. It updates
         the html text and outputs a local html file. 
        """

        htmlSoup = bSoup(requests.Session().get(
            url, headers=self.headers).content, "html.parser")

        localizeContent = htmlLocalizer(url, htmlSoup)
        localizeContent.downloadCSS()
        localizeContent.downloadScripts()
        images = localizeContent.get_image_list()
        for image in images:
            localizeContent.download_media(image)

        bgImages = localizeContent.get_bg_image_list()
        for image in bgImages:
            localizeContent.download_media(image)
        audios = localizeContent.get_audio_list()
        for audio in audios:
            localizeContent.download_media(audio)
        videos = localizeContent.get_video_list()
        for video in videos:
            localizeContent.download_media(video)
        localizeContent.replaceImg()
        localizeContent.replaceBgImages()
        localizeContent.replaceAudio()
        localizeContent.replaceVideos()

        print("Removing unnecessary forms like login boxes, searches...")
        localizeContent.removeForms()

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

# TODO: remove reference https://www.freecodecamp.org/news/how-to-build-a-url-crawler-to-map-a-website-using-python-6a287be1da11/

    def downloadAllWebPages(self):
        newUrls = deque([self.formatUrl(self.homeUrl)])
        brokenUrls = set()


        # process urls one by one until we exhaust the queue 
        while len(newUrls):    
        # move url from the queue to processed url set    
            url = newUrls.popleft()
            htmlSoup = bSoup(requests.Session().get(self.homeUrl).content, "html.parser")
            self.downloadWebPage(url)
            self.processedUrls.add(url)
        # print the current url    
            print(f'Processing {url}')
            try:
                response = requests.get(url)

            except(requests.exceptions.MissingSchema, requests.exceptions.ConnectionError, requests.exceptions.InvalidURL, requests.exceptions.InvalidSchema):    
                # Add broken urls to it’s own set, then continue    
                brokenUrls.add(url)
                continue
            
            for anchorTag in htmlSoup.find_all("a", href=True):
                currentUrl = self.formatUrl(anchorTag['href'])
                
                #If it is explicitely referring to a local page or has a relative path
                if self.basePath in currentUrl or currentUrl.startswith('/'):     

                    if( (not (currentUrl in self.processedUrls)) & (not (currentUrl in newUrls))):

                        newUrls.append(self.formatUrl(currentUrl))


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
