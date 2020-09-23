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
        Method traverses soup for for link tags and finds those with css hrefs. It obtains the url and makes a get request in order 
        to get the contents of the css file. It creates a new file name and replaces the old file name in the soup. It then creates a new 
        directory and locally saves the css files. 
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

    def downloadImages(self):
        """ 
         Method traverses soup for for img tags and finds those with valid src's. It obtains the url and makes a get request in order 
        to get the contents of the images. It replaces the old file name in the soup to the local file name. It then creates a new 
        directory and locally saves the image files. 
        """
        count = 0 
        print('Downloading images...')
        for image in self.htmlSoup.find_all("img"):
            if image.attrs.get("src"):
                imageUrl = urljoin(self.url, image.attrs.get("src"))
                if imageUrl.__contains__("?"):
                    shortenUrl = imageUrl.index("?")
                    imageUrl = imageUrl[:shortenUrl]
                
                imgFilename = "imgs/"+imageUrl.split("/")[-1]
                image['src'] = imgFilename
                os.makedirs(os.path.dirname(imgFilename), exist_ok=True)

                imageContent = requests.get(imageUrl, stream=True)
                if imageContent.status_code == 200:
                    imageContent.raw.decode_content = True
                    with open(imgFilename, 'wb') as f:
                        shutil.copyfileobj(imageContent.raw, f)
                        count = count + 1

        print(f'Successfully extracted {count} images files...')

"""
    def downloadImg(self, image_url):
        

        filename = "imgs/"+image_url.split("/")[-1]
        r = requests.get(image_url, stream=True)
        if r.status_code == 200:
            r.raw.decode_content = True
            with open(filename, 'wb') as f:
                shutil.copyfileobj(r.raw, f)


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
"""
