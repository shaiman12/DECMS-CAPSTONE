import requests
from datetime import datetime
from urllib.parse import urlparse, urljoin
from zipfile import ZipFile
from utils.HTML_Localizer import HTML_Localizer


class web_scaper():
    base_path = ''
    created_files = []

    def __init__(self, url):
        self.base_path = urlparse(url).hostname
        self.imgPath = "imgs"

    def create_html_file(self, url):
        response = requests.get(url)
        #------------------------------------------------------------------------------------#
        localizeContent = HTML_Localizer(url)
        localizeContent.extract_css()
        imagelist = localizeContent.get_image_list(url)
        for img in imagelist:
            localizeContent.download_img(img)

        #------------------------------------------------------------------------------------#
        now = datetime.now().strftime("%m/%d/%Y-%H:%M:%S").replace('/', '-')
        filename = self.base_path+'-'+now+".html"
        f = open(filename, "w")
        f.write(response.text)
        self.created_files.append(filename)
        localizeContent.replaceImg(filename)
        return filename
