import requests
import os
from bs4 import BeautifulSoup as bSoup
from urllib.parse import urljoin, urlparse
import os
import shutil


class HTML_Localizer:
    """
    For now, Localizer recieves the url and creates two variables with the seconf being the htmlSoup used for parsing data
    """

    def __init__(self, url):
        self.url = url
        self.imgPath = "imgs"
        self.imagelinklist = []
        self.htmlSoup = bSoup(
            requests.Session().get(url).content, "html.parser")

    """
    method traverses soup for for link tags and finds those css hrefs. Adds these links to an array and saves them to file
    Need to test to see if I need to save the actual file content for localizing.
    """

    def extract_css(self):
        css_files = []
        for css in self.htmlSoup.find_all(type='text/css'):
            if css.attrs.get("href"):
                css_url = urljoin(self.url, css.attrs.get("href"))
                css_files.append(css_url)
<<<<<<< HEAD

        with open("css_files.txt", "w") as f:
            for css_file in css_files:
                print(css_file, file=f)
=======
        
        count = 0 
        for css_file_name in css_files:
            fileContent = requests.get(css_file_name)
            completFilename = "css/staticStyling" + str(count) + ".css"
            f = open(completFilename, "w")
            f.write(fileContent.text)
            f.close
            count = count +1 
        
>>>>>>> 49cf94a... Css extractor now saves each css file locally as opposed to just collating the url's in a text file

    def get_image_list(self, url):
        """Returns a list of all links of images from a URL"""
        links = []
        for image in self.htmlSoup.find_all("img"):
            imageurl = image.attrs.get("src")
            if not imageurl:
                continue
            imageurl = urljoin(url, imageurl)
            try:
                # removing "?" from imgs
                x = imageurl.index("?")
                imageurl = imageurl[:x]
            except:
                pass
            links.append(imageurl)
        return links

    def download_img(self, image_url):
        filename = "imgs/"+image_url.split("/")[-1]
        r = requests.get(image_url, stream=True)
        if r.status_code == 200:
            r.raw.decode_content = True
            with open(filename, 'wb') as f:
                shutil.copyfileobj(r.raw, f)

    def replaceImg(self, htmlfilename):
        downloadedImages = os.listdir("imgs/")
        with open(htmlfilename) as fp:
            newsoup = bSoup(fp, "lxml")
        for image in newsoup.find_all("img"):

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
        fp.close()
        html = newsoup.prettify("utf-8")
        with open(htmlfilename, "wb") as file:
            file.write(html)