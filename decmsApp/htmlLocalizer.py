import requests
import os
from bs4 import BeautifulSoup as bSoup
from urllib.parse import urljoin, urlparse
import shutil
from cssutils import parseStyle


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
                newFileName = os.path.join(self.directory, "css/Static_Styling_" + str(count) + ".css")
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
                newFileName = os.path.join(self.directory,"js/Script_" + str(count) + ".js")
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
        fileContent = requests.get(listOfFiles[0])

        os.makedirs(os.path.dirname(listOfFiles[1]), exist_ok=True)

        localFile = open(listOfFiles[1], "w")
        localFile.write(fileContent.text)
        localFile.close

    def get_image_list(self):
        links = []
        print('Getting list of images...')
        for image in self.htmlSoup.find_all("img"):
            if(self.link_maker(image) == ""):
                continue
            else:
                links.append(self.link_maker(image))
        return links

    def get_bg_image_list(self):
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


# Returns a list of all links of videos from a URL

    def get_video_list(self):
        links = []
        print('Getting list of videos...')

        for video in self.htmlSoup.find_all('source', type='video/ogg'):
            links.append(self.link_maker(video))
        for video in self.htmlSoup.find_all('source', type='video/mp4'):
            links.append(self.link_maker(video))
        for video in self.htmlSoup.find_all('source', type='video/webm'):
            links.append(self.link_maker(video))
        return links


# Formats a link into correct form for downloading


    def link_maker(self, mediaItem):
        if mediaItem.has_attr('data-original'):
            mediaurl = mediaItem.attrs.get("data-original")
        else:
            mediaurl = mediaItem.attrs.get("src")
        if mediaurl.find("svg+xml") > -1:
            return ""
        mediaurl = urljoin(self.url, mediaurl)
        try:
            # removing "?" from imgs
            x = mediaurl.index("?")
            mediaurl = mediaurl[:x]
        except:
            pass
        return mediaurl


# Returns a list of all links of videos from a URL

    def get_audio_list(self):
        links = []
        print('Getting list of audio files...')

        for audio in self.htmlSoup.find_all('source', type='audio/ogg'):
            links.append(self.link_maker(audio))
        for audio in self.htmlSoup.find_all('source', type='audio/mpeg'):
            links.append(self.link_maker(audio))

        return links

# Receives a URL and downloads the file locally

    def downloadMedia(self, media_url):

        filename = os.path.join(self.directory,"media/"+media_url.split("/")[-1])
        os.makedirs(os.path.dirname(filename), exist_ok=True)

        mediaContent = requests.get(media_url, stream=True)
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
        downloadedMedia = os.listdir(self.directory+"/media/")
        mediaLink = ""
        if(media.has_attr('data-original')):
            mediaLink = media.attrs.get("data-original")
        else:
            mediaLink = media.attrs.get("src")
        if mediaLink.find("svg+xml") > -1:
            return ""
        dissasembled = urlparse(mediaLink)
        filename, file_ext = os.path.splitext(
            os.path.basename(dissasembled.path))
        mediaPart = filename+file_ext
        try:
            pos = downloadedMedia.index(mediaPart)
            if(pos > -1):
                media["src"] = self.directory+"/media/"+downloadedMedia[pos]

        except:
            print("Failed replacing image: ", mediaPart)

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
                toReplace = self.directory+"/media/"+downloadedMedia[pos]
                strStyle = strStyle.replace(link, toReplace)

                element["style"] = strStyle


# replaces all old video urls with the new locally saved versions


    def replaceVideos(self):
        for video in self.htmlSoup.find_all('source', type='video/mp4'):
            self.replaceMedia(video)
        for video in self.htmlSoup.find_all('source', type='video/ogg'):
            self.replaceMedia(video)
        for video in self.htmlSoup.find_all('source', type='video/webm'):
            self.replaceMedia(video)


# replaces all old audio urls with the new locally saved versions

    def replaceAudio(self):
       
        for audio in self.htmlSoup.find_all('source', type='audio/ogg'):
            self.replaceMedia(audio)
        for audio in self.htmlSoup.find_all('source', type='audio/mpeg'):
            self.replaceMedia(audio)


# form removal

    def removeForms(self):
        for form in self.htmlSoup.find_all("form"):
            form.replaceWith('')

    def getAllMediaLists(self):
        """
        Returns single list containing all media urls to be downloaded. 
        Method makes get {media} list methods within localizer class.
        """
        images = self.get_image_list()
        bgImages = self.get_bg_image_list()
        audios = self.get_audio_list()
        videos = self.get_video_list()
        mediaList = images+ bgImages + audios + videos
        return mediaList

    def replaceAllMedia(self):
        """
        Method makes use of all replace 'media' methods for cleaner code. 
        """
        pathname = self.directory+"/media"
        os.makedirs(pathname, exist_ok=True)

        self.replaceImg()

        self.replaceBgImages()
        
        self.replaceAudio()
        
        self.replaceVideos()