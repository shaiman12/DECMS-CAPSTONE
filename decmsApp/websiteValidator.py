import requests

class websiteValidator:
    """
    Class checks if the website is currently online and if it uses WP. (Future drupal method to be added)
    """
    def __init__(self, url):
        self.siteUrl = url
        self.siteValidator = True

    def isUrlValid(self):
        """
        Method makes a get request on the user inputed url. If the status is 200 website is running, 
        if not it sets the validator to false
        """
        try:
            isOnline = requests.get(self.siteUrl)
            if(isOnline.status_code == 200):
                print("Website is up and running!")
        except requests.ConnectionError as e:
            print (e + "Cannot connect to website")
            self.siteValidator = False
    
    def wordPressDetector(self):
        """
        Method added two wp entensions to the user inputed url. If those pages exist its a WP website. If not it checks the text 
        of the url's html for an instance of the word "wp-" indicating a WP content. If all checks fail it sets validator to false. 
        """
        wpLoginPage = requests.get(self.siteUrl + '/wp-login.php')
        wpAdminPage = requests.get(self.siteUrl + '/wp-admin')
        wpLinks = requests.get(self.siteUrl)
        #can make messages more robust in future refactor
        if wpLoginPage.status_code == 200 or wpAdminPage.status_code == 200:
            print("This is a wordpress website! It has a WP admin page!")
        elif 'wp-' in wpLinks.text:
            print("This is a wordpress website!")
        else:
            print("This isn't built in WordPress!")
            self.siteValidator = False

    def runWebsiteChecks(self):
        """
        Returns boolean. True if website is up and running and was built in WP (drupal). False if not.
        Calls class member functions to perform checks. 
        """
        print("Performing checks...")
        self.isUrlValid()
        self.wordPressDetector()
        return self.siteValidator
