import unittest
import requests
from decmsApp.htmlLocalizer import *
from bs4 import BeautifulSoup as bSoup
import shutil



class TestHTMLLocalizer(unittest.TestCase):
    
    def test_getCorrectNumberOfLinks(self):
        url='https://www.dadoagency.com/'
        localizer = htmlLocalizer(url)
        cssLinks=localizer.getAndReplaceCSS()
        self.assertEqual(len(cssLinks),1)
        bgLinks=localizer.getBgImageList()
        self.assertEqual(len(bgLinks),0)
        jsLinks=localizer.getAndReplaceJS()
        self.assertEqual(len(jsLinks),3)
        audioLinks=localizer.getAudioVideolist()
        self.assertEqual(len(audioLinks),1)

        url='https://wordpress-343891-1520087.cloudwaysapps.com/other'
        localizer = htmlLocalizer(url)
        cssLinks=localizer.getAndReplaceCSS()
        self.assertEqual(len(cssLinks),3)
        bgLinks=localizer.getBgImageList()
        self.assertEqual(len(bgLinks),1)
        jsLinks=localizer.getAndReplaceJS()
        self.assertEqual(len(jsLinks),2)
        audioLinks=localizer.getAudioVideolist()
        self.assertEqual(len(audioLinks),0)

    def test_extractLink(self):
        url='https://example.com'
        localizer = htmlLocalizer(url)
        soup = bSoup("<div><a href='/about'>Link</a></div>")
        mediaItem = soup.findAll("a")[0]
        href = localizer.extractLink(mediaItem)
        self.assertEqual(href,'https://example.com/about')

        soup = bSoup("<div><img src='image.jpg'>Link</img></div>")
        mediaItem = soup.findAll("img")[0]
        href = localizer.extractLink(mediaItem)
        self.assertEqual(href,'https://example.com/image.jpg')

               
        soup = bSoup("<div><img data-original='image.jpg'>Link</img></div>")
        mediaItem = soup.findAll("img")[0]
        href = localizer.extractLink(mediaItem)
        self.assertEqual(href,'https://example.com/image.jpg')

    def test_downloadMedia(self):
        randomMedia=["https://woocommerce-343891-1062302.cloudwaysapps.com/wp-content/uploads/2019/12/logo-optimised-0-300x156.png","https://www.weare-creative.com/wp-content/uploads/2018/05/Show-reel-for-home-page-correct-size-edit.mp4","https://uploads-ssl.webflow.com/5e6fc6440ad9f713e1bda812/5e7b784b977c89ce45061ab7_path-179.svg","https://www.obama.org/wp-content/uploads/21-scaled-640x0-c-default.jpg","https://ssl.gstatic.com/dictionary/static/pronunciation/2019-10-21/audio/da/dado_en_us_1.mp3"]
        url='https://dadoagency.com'
        localizer = htmlLocalizer(url)
        for media in randomMedia:
            localizer.downloadMedia(media,"test-media/")
        downloadedMedia = os.listdir("test-media/media")
        self.assertEqual(len(downloadedMedia),len(randomMedia))
        shutil.rmtree("test-media/")

    def test_removeForms(self):
        url='https://dadoagency.com'
        localizer = htmlLocalizer(url)
        localizer.removeForms()
        forms = localizer.getHtmlSoup().find_all("form")
        self.assertEqual(len(forms),0)
        

        url='https://obama.org'
        localizer = htmlLocalizer(url)
        localizer.removeForms()
        forms = localizer.getHtmlSoup().find_all("form")
        self.assertEqual(len(forms),0)

