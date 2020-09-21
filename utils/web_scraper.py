import requests
from datetime import datetime
from urllib.parse import urlparse, urljoin
from zipfile import ZipFile
from utils.HTML_Localizer import HTML_Localizer
from bs4 import BeautifulSoup as bSoup


class web_scaper():
    base_path = ''
    created_files = []

    def __init__(self, url):
        self.base_path = urlparse(url).hostname
        self.imgPath = "imgs"
    
    """ Method searches through link tags with urls. If the a url contains 'wp-conent' the loop breaks and returns true"""
    def wordPressDetector(self, soup):
        wordPress = False
        
        for wp in soup.find_all('link', href=True):
            url = wp.attrs.get("href")
            if url.find("wp-content") != -1:
                wordPress = True
                break
        
        return wordPress
    

    """ Method creates and saves the html file(s) from a given url """
    def create_html_file(self, url):
        # Variables are created to get the content from a url and create the html soup using the beautiful soup parser
        response = requests.get(url)
        htmlSoup = bSoup(requests.Session().get(url).content, "html.parser")

        #Checks to see if website was built in wordPress
        cmsDetector = self.wordPressDetector(htmlSoup)
        if(cmsDetector):
            print("This website was built in wordPress!")
        else:
            print("This isn't build in WordPress!")

        # Creates a variable called HTML_Localizer to locally save both the css files and images and perform inline
        # editting of the html soup.
        localizeContent = HTML_Localizer(url, htmlSoup)
        localizeContent.extract_css()
        imagelist = localizeContent.get_image_list()
        videolist = localizeContent.get_video_list()
        audioList = localizeContent.get_audio_list()
        print('Downloading images...')
        for img in imagelist:
            localizeContent.download_media(img)
        print('Downloading videos...')
        for video in videolist:
            localizeContent.download_media(video)
        print("Downloading Audio files....")
        for audio in audioList:
            localizeContent.download_media(audio)

        print('Successfully downloaded images...')
        print('Renaming remote image paths to local paths...')
        localizeContent.replaceImg()
        print('Renaming remote video paths to local paths...')
        localizeContent.replaceVideos()
        print('Renaming remote audio paths to local paths...')
        localizeContent.replaceAudio()
        print('Done')

        # Renames the html file to include the date
        now = datetime.now().strftime("%m/%d/%Y-%H:%M:%S").replace('/', '-')
        filename = self.base_path+'-'+now+".html"
       # The HTML soup is converted into a local html file
        html = htmlSoup.prettify("utf-8")
        with open(filename, "wb") as file:
            file.write(html)

        self.created_files.append(filename)
        return filename
    
