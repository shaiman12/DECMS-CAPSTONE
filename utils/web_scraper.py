import requests
from datetime import datetime
from urllib.parse import urlparse
from zipfile import ZipFile
import HTML_Localizer


class web_scaper():
    base_path = ''
    created_files = []

    def __init__(self, url):
        self.base_path = urlparse(url).hostname

    def create_html_file(self, url):
        response = requests.get(url)
        #------------------------------------------------------------------------------------#
        localizeContent = HTML_Localizer(url)
        #------------------------------------------------------------------------------------#
        now = datetime.now().strftime("%m/%d/%Y-%H:%M:%S").replace('/', '-')
        filename = self.base_path+'-'+now+".html"
        f = open(filename, "w")
        f.write(response.text)
        self.created_files.append(filename)
        return filename
