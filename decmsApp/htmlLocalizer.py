import requests
import os
from bs4 import BeautifulSoup as bSoup
from urllib.parse import urljoin, urlparse
import shutil


class htmlLocalizer:
    """
    Class receives the url and html soup from the webScraper. Contains methods to locate, download, and inline edit the css files and
    embeded object links from the html soup. 
    """

    def __init__(self, url, htmlSoup):
        """
        Constructor class. 
        """
        self.url = url
        self.imgPath = "imgs"
        self.imagelinklist = []
        self.htmlSoup = htmlSoup


    def downloadCSS(self):
        """
        Method traverses soup for for link tags and finds those with css hrefs. It adds these links to an array and then creates and saves
        the contents of the files locally in a folder. 
        """
        count = 0
        print('Extracting css...')
        for cssFile in self.htmlSoup.find_all("link"):
            if cssFile.attrs.get("href") and '.css' in cssFile['href']:
                
                completeCssUrl = urljoin(self.url, cssFile.attrs.get("href"))
                fileContent = requests.get(completeCssUrl)

                # Renames the url in the html Soup
                newFileName = "css/Static_Styling_" + str(count) + ".css"
                cssFile['href'] = newFileName

                ########### This creates a new file directory from scratch. #########
                os.makedirs(os.path.dirname(newFileName), exist_ok=True)

                localCSSFile = open(cssFile['href'], "w")
                localCSSFile.write(fileContent.text)
                localCSSFile.close
                count = count + 1
        print(f'Successfully extracted {count} css files...')

    """ Returns a list of all links of images from a URL"""

    def getImageList(self):
        links = []
        print('Getting list of images...')

        for image in self.htmlSoup.find_all("img"):
            imageurl = image.attrs.get("src")
            if not imageurl:
                continue
            imageurl = urljoin(self.url, imageurl)
            try:
                # removing "?" from imgs
                x = imageurl.index("?")
                imageurl = imageurl[:x]
            except:
                pass
            links.append(imageurl)
        return links

    """ Receives a list of image urls and downloads them locally  """

    def downloadImg(self, image_url):

        filename = "imgs/"+image_url.split("/")[-1]
        r = requests.get(image_url, stream=True)
        if r.status_code == 200:
            r.raw.decode_content = True
            with open(filename, 'wb') as f:
                shutil.copyfileobj(r.raw, f)

    """ Using the html soup, this method replaces the old image url with the new locally saved version """

    def replaceImg(self):
        downloadedImages = os.listdir("imgs/")

        for image in self.htmlSoup.find_all("img"):

            imageLink = image.attrs.get("src")
            if not imageLink:
                continue
            dissasembled = urlparse(imageLink)
            filename, file_ext = os.path.splitext(
                os.path.basename(dissasembled.path))
            imagePart = filename+file_ext
            pos = downloadedImages.index(imagePart)
            if(pos > -1):
                image["src"] = "imgs/"+downloadedImages[pos]
