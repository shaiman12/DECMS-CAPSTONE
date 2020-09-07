import requests
import os
from bs4 import BeautifulSoup as bSoup
from urllib.parse import urljoin, urlparse
import os
import shutil


class HTML_Localizer:
    """
    For prototype, Localizer receives the url and html soup from the web_scrapper
    """

    def __init__(self, url, htmlSoup):
        self.url = url
        self.imgPath = "imgs"
        self.imagelinklist = []
        self.htmlSoup = htmlSoup

    """
    Method traverses soup for for link tags and finds those with css hrefs. It adds these links to an array and then creates and saves
    the contents of the files locally in a folder.
    """

    def extract_css(self):
        count = 0
        print('Extracting css...')
        for css in self.htmlSoup.find_all(type='text/css'):
            if css.attrs.get("href"):
                # makes url complete and requests the data
                css_url = urljoin(self.url, css.attrs.get("href"))

                fileContent = requests.get(css_url)

                # renames the url in the html Soup
                css['href'] = "css/Static_Styling_" + str(count) + ".css"

                # saves the css file locally
                f = open(css['href'], "w")
                f.write(fileContent.text)
                f.close
                count = count + 1
        print(f'Successfully extracted {count} css files...')

    """ Returns a list of all links of images from a URL"""

    def get_image_list(self):
        links = []
        print('Getting list of images...')
        for image in self.htmlSoup.find_all("img"):
            print(image)
            print("----------")
            links.append(self.link_maker(image))
        return links

    def get_video_list(self):
        links = []
        print('Getting list of videos...')

        for video in self.htmlSoup.find_all('source', type='video/mp4'):
            links.append(self.link_maker(video))
        for video in self.htmlSoup.find_all('source', type='video/mp4'):
            links.append(self.link_maker(video))
        return links

    def link_maker(self, mediaItem):
        mediaurl = mediaItem.attrs.get("src")
        mediaurl = urljoin(self.url, mediaurl)
        try:
            # removing "?" from imgs
            x = mediaurl.index("?")
            mediaurl = mediaurl[:x]
        except:
            pass
        return mediaurl

    def get_audio_list(self):
        links = []
        print('Getting list of videos...')

        for audio in self.htmlSoup.find_all('source', type='audio/ogg'):
            links.append(self.link_maker(audio))
        for audio in self.htmlSoup.find_all('source', type='audio/mpeg'):
            links.append(self.link_maker(audio))

        return links

    """ Receives a list of image urls and downloads them locally  """

    def download_media(self, media_url):

        filename = "media/"+media_url.split("/")[-1]
        r = requests.get(media_url, stream=True)
        if r.status_code == 200:
            r.raw.decode_content = True
            with open(filename, 'wb') as f:
                shutil.copyfileobj(r.raw, f)

    """ Using the html soup, this method replaces the old image url with the new locally saved version """

    def replaceImg(self):
        for image in self.htmlSoup.find_all("img"):
            self.replaceMedia(image)

    def replaceMedia(self, media):
        downloadedMedia = os.listdir("media/")
        mediaLink = media.attrs.get("src")
        dissasembled = urlparse(mediaLink)
        filename, file_ext = os.path.splitext(
            os.path.basename(dissasembled.path))
        mediaPart = filename+file_ext
        pos = downloadedMedia.index(mediaPart)
        if(pos > -1):
            media["src"] = "media/"+downloadedMedia[pos]

    def replaceVideos(self):
        downloadedVideos = os.listdir("media/")

        for video in self.htmlSoup.find_all('source', type='video/mp4'):

            videoLink = video.attrs.get("src")
            if not videoLink:
                continue
            dissasembled = urlparse(videoLink)
            filename, file_ext = os.path.splitext(
                os.path.basename(dissasembled.path))
            videoPart = filename+file_ext
            pos = downloadedVideos.index(videoPart)
            if(pos > -1):
                video["src"] = "media/"+downloadedVideos[pos]

    def replaceAudio(self):
        downloadedMedia = os.listdir("media/")

        for audio in self.htmlSoup.find_all('source', type='audio/ogg'):

            audioLink = audio.attrs.get("src")
            if not audioLink:
                continue
            dissasembled = urlparse(audioLink)
            filename, file_ext = os.path.splitext(
                os.path.basename(dissasembled.path))
            audioPart = filename+file_ext
            pos = downloadedMedia.index(audioPart)
            if(pos > -1):
                audio["src"] = "media/"+downloadedMedia[pos]
        for audio in self.htmlSoup.find_all('source', type='audio/mpeg'):

            audioLink = audio.attrs.get("src")
            if not audioLink:
                continue
            dissasembled = urlparse(audioLink)
            filename, file_ext = os.path.splitext(
                os.path.basename(dissasembled.path))
            audioPart = filename+file_ext
            pos = downloadedMedia.index(audioPart)
            if(pos > -1):
                audio["src"] = "media/"+downloadedMedia[pos]
