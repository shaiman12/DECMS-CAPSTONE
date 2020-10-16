import unittest
import requests
from decmsApp.htmlLocalizer import *
from decmsApp.webScraper import *

from bs4 import BeautifulSoup as bSoup
import shutil

class TestHTMLLocalizer(unittest.TestCase):

    def test_shouldIgnoreUrl(self):

        url='https://www.dadoagency.com/'
        scraper = webScraper(url)
    
        self.assertFalse(scraper.shouldIgnoreUrl(scraper.formatUrl("/grid")))
        self.assertTrue(scraper.shouldIgnoreUrl(scraper.formatUrl("/#grid")))
        self.assertTrue(scraper.shouldIgnoreUrl(scraper.formatUrl("https://uploads-ssl.webflow.com/5e6fc6440ad9f713e1bda812/5e7b787fa012dc18be8e8f1b_path-purple.svg")))
        self.assertTrue(scraper.shouldIgnoreUrl(scraper.formatUrl("mailto:example@gmail.com")))
        self.assertTrue(scraper.shouldIgnoreUrl(scraper.formatUrl("tel:+27826666666")))
        self.assertTrue(scraper.shouldIgnoreUrl(scraper.formatUrl("http://dadoagency.com/cdn-cgi/l/email-protection#d3b9b6a0a093a3a1b6a7a7aab0b2a0a6b2bffdb0bcfda9b2")))

