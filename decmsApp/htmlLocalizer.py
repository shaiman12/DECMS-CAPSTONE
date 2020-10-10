import requests
import os
from bs4 import BeautifulSoup as bSoup
from urllib.parse import urljoin, urlparse
import shutil
from cssutils import parseStyle
import pdb


class htmlLocalizer:
    """
    Class receives the url and html soup from the webScraper. Contains methods to locate, download, and inline edit the css files and
    embeded object links from the html soup.
    """

    def __init__(self, url, htmlSoup, directory):
        """
        Constructor class.
        """
        self.url = url
        self.imgPath = "imgs"
        self.imagelinklist = []
        self.htmlSoup = htmlSoup
        self.directory = directory 
        self.headers = {'User-Agent': '...', 'referer': 'https://...'}

    def getAndReplaceCSS(self):
        """
         Returns 2xN array with the css url and its pair new file name as its contents 
         Method traverses soup for for link tags and finds those with script hrefs. It creates a new file name 
         and replaces the old file name in the soup. Both the original url and new file name is appended to a list.
        """
        cssLinks = []
        count = 0
        print('Getting list of css files ...')
        for cssFile in self.htmlSoup.find_all("link"):
            if cssFile.attrs.get("href") and '.css' in cssFile['href']:

                completeCssUrl = urljoin(self.url, cssFile.attrs.get("href"))

                # Renames the url in the html Soup
                newFileName =  "css/staticStyling_" + str(count) + ".css"
                cssFile['href'] = newFileName

                fileNames = [completeCssUrl, newFileName]
                cssLinks.append(fileNames)
                count += 1

        return cssLinks

    def getAndReplaceJS(self):
        """
         Returns 2xN array with the js url and its pair new file name as its contents 
         Method traverses soup for for script tags and finds those with src attributes. It creates a new file name 
         and replaces the old file name in the soup. Both the original url and new file name is appended to a list.
        """
        jsLinks = []
        count = 0
        print('Getting list of js files ...')
        for jsFile in self.htmlSoup.find_all("script"):
            if jsFile.attrs.get("src") and '.js' in jsFile['src']:

                completeJsUrl = urljoin(self.url, jsFile.attrs.get("src"))

                # Renames the url in the html Soup
                newFileName = "js/Script_" + str(count) + ".js"
                jsFile['src'] = newFileName

                fileNames = [completeJsUrl, newFileName]
                jsLinks.append(fileNames)
                count += 1

        return jsLinks

    def downloadUrlContent(self, listOfFiles):
        """
        Method receives a 2xN array. The first element contains a url in which the request lib retrieves its contents. The second element
        contains the local file name in which the content is saved. 
        """
        fileContent = requests.get(listOfFiles[0], headers = self.headers)
        directoryName = os.path.join(self.directory,listOfFiles[1])
        os.makedirs(os.path.dirname(directoryName), exist_ok=True)
        
        localFile = open(directoryName, "w")
        localFile.write(fileContent.text)
        localFile.close

    def getImageList(self):
        links = []
       
        print('Getting list of images...')
        for image in self.htmlSoup.find_all("img"):
            if(self.linkMaker(image) == ""):
                continue
            else:
                links.append(self.linkMaker(image))
        
        return links

    def getBgImageList(self):
        print('Getting list of background images...')
        links = []
        styles = []
        for element in self.htmlSoup.find_all(style=True):
            if(element["style"]).find("background-image: url") > -1:
                styles.append(element["style"])
        for style in styles:
            start = style.find("url(")+4
            end = style.find(")")
            links.append(style[start:end])
        return links

    def imagesFromOtherHrefs(self):
        links = []
        for element in self.htmlSoup.find_all(href=True):
            href = element["href"]
            if ".png" in href or ".jpg" in href or ".jpeg" in href or ".gif" in href or ".JPEG" in href or ".svg" in href:
                links.append(element)
        newLinks = []
        for link in links:
            newLinks.append(self.linkMaker(link))
        return newLinks
# Returns a list of all links of videos from a URL

    def getAudioVideolist(self):
        audioVideoLinks = []
        print('Getting list of videos...')

        for audioVideo in self.htmlSoup.find_all('source', type=['video/ogg','video/mp4','video/webm', 'audio/ogg', 'audio/mpeg']):
            audioVideoLinks.append(self.linkMaker(audioVideo))

        return audioVideoLinks

# Formats a link into correct form for downloading


    def linkMaker(self, mediaItem):
        mediaurl = ""
        if mediaItem.has_attr('href'):
            mediaurl = mediaItem.attrs.get("href")
        elif mediaItem.has_attr('data-original'):
            mediaurl = mediaItem.attrs.get("data-original")
        elif mediaItem.has_attr('src'):
            mediaurl = mediaItem.attrs.get("src")
        elif(mediaItem.has_attr('data-src')):
            mediaLink = mediaItem.attrs.get("data-src")
        else:
            mediaurl = ""
            #print(mediaItem)
        if mediaurl.find("svg+xml") > -1 or mediaurl == "":
            return ""
        mediaurl = urljoin(self.url, mediaurl)
        try:
            # removing "?" from imgs #potential flag
            x = mediaurl.index("?")
            mediaurl = mediaurl[:x]
        except:
            pass
        return mediaurl

# Receives a URL and downloads the file locally

    def downloadMedia(self, media_url):
        filename = os.path.join(self.directory,"media/"+media_url.split("/")[-1])
        os.makedirs(os.path.dirname(filename), exist_ok=True)

        mediaContent = requests.get(media_url, stream=True, headers = self.headers)
        if mediaContent.status_code == 200:
            mediaContent.raw.decode_content = True
            with open(filename, 'wb') as f:
                shutil.copyfileobj(mediaContent.raw, f)


# replaces all old image urls with the new locally saved versions

    def replaceImg(self):
        for image in self.htmlSoup.find_all("img"):
            if self.replaceMedia(image) == "":
                continue
            self.replaceMedia(image)
            

# Using the html soup, this method replaces the old media url with the new locally saved version

    def replaceMedia(self, media):
        
        downloadedMedia = os.listdir(os.path.join(self.directory,"media/"))
        mediaLink = ""
        if(media.has_attr('href')):
            mediaLink = media.attrs.get("href")
            attType = "href"
        elif(media.has_attr('data-original')):
            mediaLink = media.attrs.get("data-original")
            attType = "data-original"
        elif(media.has_attr('src')):
            mediaLink = media.attrs.get("src")
            attType = "src"
        elif(media.has_attr('data-src')):
            mediaLink = media.attrs.get("data-src")
            attType = "data-src"
        else:
            #print(media)
            mediaLink = ""
        if (mediaLink.find("svg+xml") > -1) or (mediaLink == ""):
            return ""
        dissasembled = urlparse(mediaLink)
        filename, file_ext = os.path.splitext(
            os.path.basename(dissasembled.path))
        mediaPart = filename+file_ext
        try:
            pos = downloadedMedia.index(mediaPart)
            if(pos > -1):
                media[attType] = "media/"+downloadedMedia[pos]

        except Exception as e:
            print("Failed replacing image: ", mediaPart)
            print(e)

    def replaceBgImages(self):
        downloadedMedia = os.listdir(self.directory+"/media/")

        elementsToReplace = []
        for element in self.htmlSoup.find_all(style=True):
            if(element["style"]).find("background-image: url") > -1:
                elementsToReplace.append(element)

        for element in elementsToReplace:
            strStyle = element["style"]
            start = strStyle.find("url(")+4
            end = strStyle.find(")")
            link = strStyle[start:end]

            dissasembled = urlparse(link)
            filename, file_ext = os.path.splitext(
                os.path.basename(dissasembled.path))
            mediaPart = filename+file_ext
            pos = downloadedMedia.index(mediaPart)
            if(pos > -1):
                toReplace = "media/"+downloadedMedia[pos]
                strStyle = strStyle.replace(link, toReplace)

                element["style"] = strStyle

    def replaceHrefImages(self):
        for element in self.htmlSoup.find_all(href=True):
            href = element["href"]
            if ".png" in href or ".jpg" in href or ".jpeg" in href or ".gif" in href or ".JPEG" in href or ".svg" in href:
                self.replaceMedia(element)

# replaces all old video urls with the new locally saved versions

    def replaceAudioVideos(self):
        for audioVideo in self.htmlSoup.find_all('source', type=['video/mp4','video/ogg','video/webm', 'audio/ogg', 'audio/mpeg']):
            self.replaceMedia(audioVideo)

# form removal

    def removeForms(self):
        for form in self.htmlSoup.find_all("form"):
            form.replaceWith('')

    def getAllMediaLists(self):
        """
        Returns single list containing all media urls to be downloaded. 
        Method makes get {media} list methods within localizer class.
        """
        images = self.getImageList()
        bgImages = self.getBgImageList()
        hrefImages = self.imagesFromOtherHrefs()
        audioVidio = self.getAudioVideolist()
        
        mediaList = images + bgImages + hrefImages + audioVidio
        return mediaList

    def replaceAllMedia(self):
        """
        Method makes use of all replace 'media' methods for cleaner code. 
        """
        pathname = os.path.join(self.directory,"media/")
        os.makedirs(pathname, exist_ok=True)

        self.replaceImg()
        self.replaceBgImages()
        self.replaceHrefImages()
        self.replaceAudioVideos()
        