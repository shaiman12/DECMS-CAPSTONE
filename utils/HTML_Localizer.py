import requests
from bs4 import BeautifulSoup as bs
from urllib.parse import urljoine

class HTML_Localizer:
    def __init__(self, url):
        self.url = url
        
