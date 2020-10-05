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

    def __init__(self, url, htmlSoup):
        """
        Constructor class.
        """
        self.url = url
        self.imgPath = "imgs"
        self.imagelinklist = []
        self.htmlSoup = htmlSoup

    def downloadCSS(self, directory="css/"):
        """
        Method traverses soup for for link tags and finds those with css hrefs. It obtains the url and makes a get request in order
        to get the contents of the css file. It creates a new file name and replaces the old file name in the soup. It then creates a new
        directory and locally saves the css files.
        """
        count = 0
        print('Extracting css...')
        for cssFile in self.htmlSoup.find_all("link"):
            if cssFile.attrs.get("href") and '.css' in cssFile['href']:

                completeCssUrl = urljoin(self.url, cssFile.attrs.get("href"))
                fileContent = requests.get(completeCssUrl)

                # Renames the url in the html Soup
                newFileName = directory +"Static_Styling_" + str(count) + ".css"
                cssFile['href'] = newFileName

                ########### This creates a new file directory from scratch. #########
                os.makedirs(os.path.dirname(newFileName), exist_ok=True)

                localCSSFile = open(cssFile['href'], "w")
                localCSSFile.write(fileContent.text)
                localCSSFile.close
                count = count + 1
        print(f'Successfully extracted {count} css files...')

    def downloadScripts(self, directory="js/"):
        """
        Method traverses soup for for link tags and finds those with script hrefs. It obtains the url and makes a get request in order
        to get the contents of the js file. It creates a new file name and replaces the old file name in the soup. It then creates a new
        directory and locally saves the js files.
        """
        count = 0
        print('Extracting scripts...')
        for jsFile in self.htmlSoup.find_all("script"):
            if jsFile.attrs.get("src") and '.js' in jsFile['src']:

                completeJsUrl = urljoin(self.url, jsFile.attrs.get("src"))
                fileContent = requests.get(completeJsUrl)

                # Renames the url in the html Soup
                newFileName = directory+"/Script_" + str(count) + ".js"
                jsFile['src'] = newFileName

                ########### This creates a new file directory from scratch. #########
                os.makedirs(os.path.dirname(newFileName), exist_ok=True)

                localJSFile = open(jsFile['src'], "w")
                localJSFile.write(fileContent.text)
                localJSFile.close
                count = count + 1
        print(f'Successfully extracted {count} js files...')

    def getImageList(self):
        links = []
        print('Getting list of images...')
        images = self.htmlSoup.find_all("img")
        for image in images:
            if(self.linkMaker(image) == ""):
                continue
            else:
                links.append(self.linkMaker(image))
        return links

    def getBGImgList(self):
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

    def getVideoList(self):
        links = []
        print('Getting list of videos...')

        for video in self.htmlSoup.find_all('source', type='video/ogg'):
            links.append(self.linkMaker(video))
        for video in self.htmlSoup.find_all('source', type='video/mp4'):
            links.append(self.linkMaker(video))
        for video in self.htmlSoup.find_all('source', type='video/webm'):
            links.append(self.linkMaker(video))
        return links


# Formats a link into correct form for downloading


    def linkMaker(self, mediaItem):
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

    def getAudioList(self):
        links = []
        print('Getting list of audio files...')

        for audio in self.htmlSoup.find_all('source', type='audio/ogg'):
            links.append(self.linkMaker(audio))
        for audio in self.htmlSoup.find_all('source', type='audio/mpeg'):
            links.append(self.linkMaker(audio))

        return links

# Receives a URL and downloads the file locally

    def downloadMedia(self, media_url, directory="media/"):
        os.makedirs(os.path.dirname(directory), exist_ok=True)

        filename = directory+media_url.split("/")[-1]
        r = requests.get(media_url, stream=True)
        if r.status_code == 200:
            r.raw.decode_content = True
            with open(filename, 'wb') as f:
                shutil.copyfileobj(r.raw, f)


# replaces all old image urls with the new locally saved versions

    def replaceImg(self):
        for image in self.htmlSoup.find_all("img"):
            if self.replaceMedia(image) == "":
                continue
            self.replaceMedia(image)

# Using the html soup, this method replaces the old media url with the new locally saved version

    def replaceMedia(self, media):
        downloadedMedia = os.listdir("media/")
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
                media["src"] = "media/"+downloadedMedia[pos]

        except:
            print("Failed replacing image: ", mediaPart)

    def replaceBgImages(self):
        downloadedMedia = os.listdir("media/")

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
        downloadedMedia = os.listdir("media/")

        for audio in self.htmlSoup.find_all('source', type='audio/ogg'):
            self.replaceMedia(audio)
        for audio in self.htmlSoup.find_all('source', type='audio/mpeg'):
            self.replaceMedia(audio)


# form removal


    def removeForms(self):
        for form in self.htmlSoup.find_all("form"):
            form.replaceWith('')
