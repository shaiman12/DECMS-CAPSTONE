import requests
from bs4 import BeautifulSoup as bSoup

class websiteValidator:
    """
    Parent class. Contains method that finds a webpages HTTP status code. 
    """
    def __init__(self, url):
        """
        Constructor class. Contains variables that stores the inputed URL and headers needed for the get request.
        """
        self.siteUrl = url
        self.headers = {'User-Agent': '...','referer': 'https://...'}

    def isUrlValid(self):
        """
        Method makes a get request on the user inputed url. If the status is 200 website is running, 
        if not it sets the validator to false
        """
        try:
            isOnline = requests.get(self.siteUrl, headers = self.headers)
            if(isOnline.status_code == 200):
                print("Website is up and running!")
                return True
            else:
                print("Website doesn't appear to be up and running...")
                return False
        except requests.RequestException as e:
            return False

class wpValidator(websiteValidator):
    """
    Class inherits websiteValidator. 
    """

    def __init__(self, url):
        """
        Contructor class. When invoked calls the instructor of it's parent class. 
        """
        websiteValidator.__init__(self, url)

    
    def isWordPressSite(self):
        """
        Method adds two wordPress entensions to the user inputed url. If those pages exist its a WP website. If not it creates
        html soup and looks for an instance of the word "wp-" in an href indicating a WP content. 
        If any checks pass it returns true, else it returns false.   
        """
        wpLoginPage = requests.head(self.siteUrl + '/wp-login.php', headers = self.headers)
        wpAdminPage = requests.head(self.siteUrl + '/wp-admin', headers = self.headers)
        
        if wpLoginPage.status_code == 200: 
            print("This is a wordpress website! It has a WP login page!")
            return True 
            
        elif wpAdminPage.status_code == 200:
            print("This is a wordpress website! It has a WP admin page!")
            return True

        else:
            homeSoup = bSoup(requests.Session().get(self.siteUrl, headers = self.headers).content, "html.parser")
            for wpContent in homeSoup.find_all("link", href = True):
                url = wpContent["href"]
                if url.find("wp-") != -1:
                    print("This is a WordPress website! It has WP content")
                    
                    return True

            print("This isn't a WordPress Website!")
            return False
    
    def runWebsiteChecks(self):
        """
        Returns a boolean. True if website is up and running and was built in WP. False if not.
        Calls class member functions to perform checks. 
        """
        print("Checking if this is a WordPress site...")
        if self.isUrlValid() == True:
            return self.isWordPressSite()
        else:
            return False


class drupalValidator(websiteValidator):
    """
    Class inherits websiteValidator. 
    """
    
    def __init__(self, url):
        """
        Contructor class. When invoked calls the instructor of it's parent class. 
        """
        websiteValidator.__init__(self, url)
    

    def isDrupalSite(self):
        """
        Method checks if two drupal entensions to the user inputed url work. If those pages exist its a drupal website. If not it checks the text 
        of the url's html for an instance of the word "drupal" indicating a WP content. If any checks pass it sets validator to true. 
        """
        drpalReadMe = requests.head(self.siteUrl + '/readme.txt', headers = self.headers)
        drupalMReadMe = requests.head(self.siteUrl + '/modules/README.txt', headers = self.headers)
        drupalLinks = requests.get(self.siteUrl, headers = self.headers)

        if drpalReadMe.status_code == 200: 
            print("This is a drupal website! It has a drupal README page!")
            return True

        elif drpalReadMe.status_code == 200:
            print("This is a drupal website! It has a drupal modules README page!")
            return True

        elif 'drupal' in drupalLinks.text:
            print("This is a drupal website! It has drupal content")
            return True

        else:
            print("This isn't a Drupal Website!")
            return False


    def runWebsiteChecks(self):
        """
        Returns boolean. True if website is up and running and was built in drupal. False if not.
        Calls class member functions to perform checks. 
        """
        print("Checking if this is a drupal site...")
        if self.isUrlValid():
            return self.isDrupalSite()
        else:
            return False

    