
class WebsiteDownloader():
    def __init__(self, url, recursiveDownloadRequested):
        self.website = Website(url)
        self.recursiveDownloadRequested = recursiveDownloadRequested
    
    def downloadOneWebPage():
        self.website.downloadOneWebPage()

class Website():

    def __init__(self, url):
        """
        Constructor class. Creates url and base path variables. 
        """
        self.baseUrl= url
        self.webPages = []
    
    def downloadOneWebPage():
        webPage = WebPage(self.baseUrl)
        webPage.download()

        

class WebPage():
    
    def __init__(self, url):
        self.pageUrl= url  
        self.images = []
        self.pageHtml = bSoup(requests.Session().get(url, headers=self.headers).content, "html.parser")

    def download():
        self.downloadImages()

    def downloadImages():
        for image in self.images:
            imageFile = File('image',)



class File():

    def __init__(self, fileType, remoteLocation):
        self.fileType = fileType
        self.remoteLocation = remoteLocation
        self.setRelativeLocation()

