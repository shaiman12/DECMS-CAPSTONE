import requests
from bs4 import BeautifulSoup as bSoup

class websiteValidator:
    """
    Class checks if the website is currently online and if it uses WP. (Future drupal method to be added)
    """
    def __init__(self, url):
        self.siteUrl = url
        self.siteValidator = False
        #homeSoup = bSoup(requests.Session().get(url).content, "html.parser")

    def isUrlValid(self):
        """
        Method makes a get request on the user inputed url. If the status is 200 website is running, 
        if not it sets the validator to false
        """
        try:
            isOnline = requests.get(self.siteUrl)
            if(isOnline.status_code == 200):
                print("Website is up and running!")
                return True
        except requests.RequestException as e:
            print(e)
            return False

class wpValidator(websiteValidator):

    def __init__(self, url):
        websiteValidator.__init__(self, url)

    
    def isWordPressSite(self):
        """
        Method added two wp entensions to the user inputed url. If those pages exist its a WP website. If not it checks the text 
        of the url's html for an instance of the word "wp-" indicating a WP content. If any checks pass it sets validator to true.  
        """
        wpLoginPage = requests.get(self.siteUrl + '/wp-login.php')
        wpAdminPage = requests.get(self.siteUrl + '/wp-admin')
        wpLinks = requests.get(self.siteUrl)

        #can make messages more robust in future refactor
        if wpLoginPage.status_code == 200: 
            print("This is a wordpress website! It has a WP login page!")
            self.siteValidator = True 
            return True
        elif wpAdminPage.status_code == 200:
            print("This is a wordpress website! It has a WP admin page!")
            self.siteValidator = True
            return True

        elif 'wp-' in wpLinks.text:
            print("This is a wordpress website! It has WP content")
            self.siteValidator = True
            return True

        else:
            print("This isn't a WordPress Website!")
            return False
    
    def runWebsiteChecks(self):
        """
        Returns boolean. True if website is up and running and was built in WP (drupal). False if not.
        Calls class member functions to perform checks. 
        """
        print("Performing WordPress Checks...")
        if self.isUrlValid() == True:
            self.isWordPressSite()

        return self.siteValidator


class drupalValidator(websiteValidator):
    
    def __init__(self, url):
        websiteValidator.__init__(self, url)

    def isDrupalSite(self):
        """
        Method checks if two drupal entensions to the user inputed url work. If those pages exist its a drupal website. If not it checks the text 
        of the url's html for an instance of the word "drupal" indicating a WP content. If any checks pass it sets validator to true. 
        """
        drpalReadMe = requests.get(self.siteUrl + '/readme.txt')
        drupalMReadMe = requests.get(self.siteUrl + '/modules/README.txt')
        drupalLinks = requests.get(self.siteUrl)

        if drpalReadMe.status_code == 200: 
            print("This is a drupal website! It has a drupal README page!")
            self.siteValidator = True 
            return True
        elif drpalReadMe.status_code == 200:
            print("This is a drupal website! It has a drupal modules README page!")
            self.siteValidator = True
            return True

        elif 'drupal' in drupalLinks.text:
            print("This is a drupal website! It has drupal content")
            self.siteValidator = True
            return True

        else:
            print("This isn't a Drupal Website!")
            return False


    def runWebsiteChecks(self):
        """
        Returns boolean. True if website is up and running and was built in WP (drupal). False if not.
        Calls class member functions to perform checks. 
        """
        print("Performing Drupal Checks...")
        if self.isUrlValid():
            self.isDrupalSite()
        return self.siteValidator

    