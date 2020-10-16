import unittest
import requests
from decmsApp.htmlLocalizer import *
from bs4 import BeautifulSoup as bSoup
import shutil



class TestHTMLLocalizer(unittest.TestCase):
    # randomMedia=["https://woocommerce-343891-1062302.cloudwaysapps.com/wp-content/uploads/2019/12/logo-optimised-0-300x156.png","https://www.weare-creative.com/wp-content/uploads/2018/05/Show-reel-for-home-page-correct-size-edit.mp4","https://uploads-ssl.webflow.com/5e6fc6440ad9f713e1bda812/5e7b784b977c89ce45061ab7_path-179.svg","https://www.obama.org/wp-content/uploads/21-scaled-640x0-c-default.jpg","https://ssl.gstatic.com/dictionary/static/pronunciation/2019-10-21/audio/da/dado_en_us_1.mp3"]

    def test_getCorrectNumberOfLinks(self):
        url='https://www.dadoagency.com/'
        response = requests.Session().get(url, headers={'User-Agent': '...', 'referer': 'https://...'})
        localizer = htmlLocalizer(url)
        cssLinks=localizer.getAndReplaceCSS()
        self.assertEqual(len(cssLinks),1)
        bgLinks=localizer.getBgImageList()
        self.assertEqual(len(bgLinks),0)
        jsLinks=localizer.getAndReplaceJS()
        self.assertEqual(len(jsLinks),3)
        audioLinks=localizer.getAudioVideolist()
        print(audioLinks)
        self.assertEqual(len(audioLinks),1)


        url='https://wordpress-343891-1520087.cloudwaysapps.com/other'
        response = requests.Session().get(url, headers={'User-Agent': '...', 'referer': 'https://...'})
        localizer = htmlLocalizer(url,response)
        cssLinks=localizer.getAndReplaceCSS()
        self.assertEqual(len(cssLinks),3)
        bgLinks=localizer.getBgImageList()
        self.assertEqual(len(bgLinks),1)
        jsLinks=localizer.getAndReplaceJS()
        self.assertEqual(len(jsLinks),2)
        audioLinks=localizer.getAudioVideolist()
        self.assertEqual(len(audioLinks),0)

        

        