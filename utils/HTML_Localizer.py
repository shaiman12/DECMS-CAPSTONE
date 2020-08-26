import requests
from bs4 import BeautifulSoup as bSoup
from urllib.parse import urljoin, urlparse
import os
from tqdm import tqdm
import shutil
from requests_html import HTMLSession


class HTML_Localizer:
    """
    For now, Localizer recieves the url and creates two variables with the seconf being the htmlSoup used for parsing data
    """

    def __init__(self, url):
        self.url = url
        self.imgPath = "imgs"
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

        with open("css_files.txt", "w") as f:
            for css_file in css_files:
                print(css_file, file=f)

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
