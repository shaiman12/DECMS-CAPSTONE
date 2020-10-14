import unittest
import requests
from decmsApp.htmlLocalizer import *
from bs4 import BeautifulSoup as bSoup
import shutil



class TestHTMLLocalizer(unittest.TestCase):
    # randomMedia=["https://woocommerce-343891-1062302.cloudwaysapps.com/wp-content/uploads/2019/12/logo-optimised-0-300x156.png","https://www.weare-creative.com/wp-content/uploads/2018/05/Show-reel-for-home-page-correct-size-edit.mp4","https://uploads-ssl.webflow.com/5e6fc6440ad9f713e1bda812/5e7b784b977c89ce45061ab7_path-179.svg","https://www.obama.org/wp-content/uploads/21-scaled-640x0-c-default.jpg","https://ssl.gstatic.com/dictionary/static/pronunciation/2019-10-21/audio/da/dado_en_us_1.mp3"]

    # def test_downloadCSS(self):
    #     url='https://www.reddbar.com/'
    #     htmlSoup = bSoup(requests.Session().get(url, headers={'User-Agent': '...', 'referer': 'https://...'}).content, "html.parser")
    #     localizer = htmlLocalizer(url,htmlSoup)
    #     localizer.downloadCSS('test-css/testCSS_')
    #     downloadedCSS= os.listdir("test-css/")
    #     expectedNumberOfFiles=3
    #     self.assertEqual(len(downloadedCSS),expectedNumberOfFiles)
    #     shutil.rmtree("test-css/")

    # def test_getImgList(self):
    #     url='https://woocommerce-343891-1062302.cloudwaysapps.com/coming-soon/'
    #     htmlSoup = bSoup(requests.Session().get(url, headers={'User-Agent': '...', 'referer': 'https://...'}).content, "html.parser")
    #     localizer = htmlLocalizer(url,htmlSoup)
    #     images=localizer.getImageList()
    #     expectedNumberOfImages=2
    #     self.assertEqual(len(images),expectedNumberOfImages)

    # def test_downloadMedia(self):
    #     url='https://woocommerce-343891-1062302.cloudwaysapps.com/coming-soon/'
    #     htmlSoup = bSoup(requests.Session().get(url, headers={'User-Agent': '...', 'referer': 'https://...'}).content, "html.parser")
    #     localizer = htmlLocalizer(url,htmlSoup)

    #     for mediaItem in self.randomMedia:
    #         localizer.downloadMedia(mediaItem, "test-media/")
        
    #     downloadedMedia = os.listdir("test-media/")
    #     self.assertEqual(len(self.randomMedia), len(downloadedMedia))
    #     shutil.rmtree("test-media/")


    # def test_replaceImg(self):
    #     url='https://wordpress-343891-1520087.cloudwaysapps.com/other'
    #     htmlSoup = bSoup(requests.Session().get(url, headers={'User-Agent': '...', 'referer': 'https://...'}).content, "html.parser")
    #     localizer = htmlLocalizer(url,htmlSoup)
    #     imagesBefore = localizer.getImageList()
    #     localizer.replaceImg()
    #     imagesAfter = localizer.getImageList()
    #     print(f'Before: {imagesBefore}')
    #     print(f'After: {imagesAfter}')




        

        