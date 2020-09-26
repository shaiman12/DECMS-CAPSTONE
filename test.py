import unittest
from decmsApp.websiteValidator import websiteValidator, wpValidator

class TestWebsiteValidator(unittest.TestCase):

    def test_isUrlValid(self):

        #invalid url
        offlineSite = "http://sdjvhjdsa.com/"
        result = websiteValidator(offlineSite).isUrlValid()
        self.assertFalse(result)

        #valid url
        onlineSite = "https://www.reddbar.com/"
        result = websiteValidator(onlineSite).isUrlValid()
        self.assertTrue(result)

    def test_isWordPressSite(self):

        #other url
        otherSite = "https://shawpremierbrands.co.za/"
        result = wpValidator(otherSite).isWordPressSite()
        self.assertFalse(result)

        #wordpress url
        wpSite = "https://www.reddbar.com/"
        result = wpValidator(wpSite).isWordPressSite()
        self.assertTrue(result)

      