import unittest
from decmsApp.websiteValidator import websiteValidator, wpValidator, drupalValidator
from decmsApp.webScraper import *
class TestWebsiteValidator(unittest.TestCase):

    # def test_isUrlValid(self):

    #     #invalid url
    #     offlineSite = "http://sdjvhjdsa.com/"
    #     result = websiteValidator(offlineSite).isUrlValid()
    #     self.assertFalse(result)

    #     #invalid url
    #     offlineSite = "https://techcrunch.co"
    #     result = websiteValidator(offlineSite).isUrlValid()
    #     self.assertFalse(result)

    #     #valid url
    #     onlineSite = "https://www.reddbar.com/"
    #     result = websiteValidator(onlineSite).isUrlValid()
    #     self.assertTrue(result)

    #     #valid url
    #     onlineSite = "https://techcrunch.com/"
    #     result = websiteValidator(onlineSite).isUrlValid()
    #     self.assertTrue(result)

    # def test_isWordPressSite(self):

    #     #other url
    #     otherSite = "https://shawpremierbrands.co.za/"
    #     result = wpValidator(otherSite).isWordPressSite()
    #     self.assertFalse(result)

    #     #other url
    #     otherSite = "https://sports.sportingbet.co.za/en/sports?q=1"
    #     result = wpValidator(otherSite).isWordPressSite()
    #     self.assertFalse(result)

    #     #wordpress url
    #     wpSite = "https://techcrunch.com/"
    #     result = wpValidator(wpSite).isWordPressSite()
    #     self.assertTrue(result)

    #     #wordpress url
    #     wpSite = "https://www.angrybirds.com/"
    #     result = wpValidator(wpSite).isWordPressSite()
    #     self.assertTrue(result)

    # def test_DrupalSite(self):

    #     #other url
    #     otherSite = "https://techcrunch.com/"
    #     result = drupalValidator(otherSite).isDrupalSite()
    #     self.assertFalse(result)

    #     #other url
    #     otherSite = "https://www.katyperry.com/"
    #     result = drupalValidator(otherSite).isDrupalSite()
    #     self.assertFalse(result)

    #     #drupal url
    #     drupalSite = "https://www.arsenal.com/"
    #     result = drupalValidator(drupalSite).isDrupalSite()
    #     self.assertTrue(result)

    #     #drupal url
    #     drupalSite = "https://www.tesla.com/"
    #     result = drupalValidator(drupalSite).isDrupalSite()
    #     self.assertTrue(result)

    def test_isWebPage(self):
        scraper = webScraper('http://prettycasual.co.za')
        scraper.getWebPageIfWebPage("http://prettycasual.co.za/cdn-cgi/l/email-protection#254f4056566555574051515c4644565044490b464a0b5f44")