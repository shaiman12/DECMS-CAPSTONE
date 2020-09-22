import requests
from datetime import datetime
from urllib.parse import urlparse, urljoin
from zipfile import ZipFile
from bs4 import BeautifulSoup as bSoup
from htmlLocalizer import htmlLocalizer

class webScaper():
    basePath = ''
    createdFiles = []

    def __init__(self, url):
        self.url = url
        self.basePath = urlparse(url).hostname
        self.imgPath = "imgs"
    
    """ 
    Returns boolean. True if a wordPress website, False if not. 
    Method searches through link tags with urls. If the a url contains 'wp-conent' the loop breaks and returns true
    """
    def wordPressDetector(self, soup):
        wordPress = False
        
        for wp in soup.find_all('link', href=True):
            url = wp.attrs.get("href")
            if url.find("wp-content") != -1:
                wordPress = True
                break
        
        return wordPress
    

    """ 
    Method creates and saves the html file(s) from a given url.  
    """
    def createHtmlFile(self):
        # Variables are created to get the content from a url and create the html soup using the beautiful soup parser
        response = requests.get(self.url)
        htmlSoup = bSoup(requests.Session().get(self.url).content, "html.parser")

        #Checks to see if website was built in wordPress
        cmsDetector = self.wordPressDetector(htmlSoup)
        if(cmsDetector):
            print("This website was built in wordPress!")
        else:
            print("This isn't build in WordPress!")

        # Creates a variable called HTML_Localizer to locally save both the css files and images and perform inline
        # editting of the html soup.
        localizeContent = htmlLocalizer(self.url, htmlSoup)
        localizeContent.downloadCSS()
        imagelist = localizeContent.getImageList()
        print('Downloading images...')
        for img in imagelist:
            localizeContent.downloadImg(img)
        print('Successfully downloaded images...')
        print('Renaming remote image paths to local paths...')
        localizeContent.replaceImg()
        print('Done')

        # Renames the html file to include the date
        now = datetime.now().strftime("%m/%d/%Y-%H:%M:%S").replace('/', '-')
        filename = self.basePath+'-'+now+".html"
       # The HTML soup is converted into a local html file
        html = htmlSoup.prettify("utf-8")
        with open(filename, "wb") as file:
            file.write(html)

        self.createdFiles.append(filename)
        return filename
    
