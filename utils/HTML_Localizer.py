import requests
from bs4 import BeautifulSoup as bSoup
from urllib.parse import urljoin

class HTML_Localizer:
    """
    For now, Localizer recieves the url and creates two variables with the seconf being the htmlSoup used for parsing data 
    """
    def __init__(self, url):
        self.url = url
        self.htmlSoup = bSoup(requests.Session().get(url).content, "html.parser")

    """
    method traverses soup for for link tags and finds those css hrefs. Adds these links to an array and saves them to file
    Need to test to see if I need to save the actaul file content for localizing. 
    """
    def extract_css(self):
        css_files = []
        for css in self.htmlSoup.find_all("link"):
            if css.attrs.get("href"):
                css_url = urljoin(self.url, css.attrs.get("href"))
                css_files.append(css_url)
        
        with open("css_files.txt", "w") as f:
            for css_file in css_files:
                print(css_file, file=f)

