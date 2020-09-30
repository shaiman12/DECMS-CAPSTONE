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

    def __init__(self, url):
        """
        Constructor class. Creates url and base path variables. 
        """
        self.createdFiles = []
        self.homeUrl = url
        self.basePath = urlparse(url).hostname
        self.headers = {'User-Agent': '...', 'referer': 'https://...'}

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

        localizeContent.get_bg_image_list()
        audios = localizeContent.get_audio_list()
        for audio in audios:
            localizeContent.download_media(audio)
        videos = localizeContent.get_video_list()
        for video in videos:
            localizeContent.download_media(video)
        localizeContent.replaceImg()
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
    def downloadWebsite(self):
        pass

    download website will become the function called from app.py. download webpage will become the recursive function. 
    this method may also be used to call the website validator in the future ,instaed of it being run in app.py. Confused 
    on some flask stuff which I need to clarify first. 
    - Avo  
    """
