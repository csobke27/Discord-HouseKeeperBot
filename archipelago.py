from bs4 import BeautifulSoup
import requests
import re
import datetime

class Archi:
    BASE_URL = 'https://archipelago.gg'
    def __init__(self, room, seed = None):
        #check to see if the text provided is the room number or the room url
        self.roomUrl = self.formatUrl(room, 'room')
        self.roomNum = self.roomUrl[self.roomUrl.rfind('/')+1:]
        response = requests.get(self.roomUrl)
        soup = BeautifulSoup(response.text, 'html.parser')
        #check to see if the text sent is a valid url 
        if soup.title.string == 'Multiworld ' + self.roomNum:
            self.roomValid = True
        else:
            self.roomValid = False
        if self.roomValid == True:
            ip = soup.find(class_='interactive').get_text(strip=True)
            if ip is not None:
                self.ip = ip[ip.find(" ")+1:-1]
            self.worldTable = self.getWorldData(soup)
        #handle seed information
        if seed is not None:
            self.seedUrl = self.formatUrl(seed, 'seed')
            self.seedNum = self.seedUrl[self.seedUrl.rfind('/')+1:]
            response = requests.get(self.seedUrl)
            soup = BeautifulSoup(response.text, 'html.parser')
            #check to see if the text sent is a valid url 
            if soup.title.string == 'View Seed ' + self.seedNum:
                self.seedValid = True
            else:
                self.seedValid = False
            if self.seedValid == True:
                seedDate = soup.find(id='creation-time').get('data-creation-time')
                formatted_time = datetime.datetime.strptime(seedDate, "%Y-%m-%d %H:%M:%S")
                self.seedCreatedDate = formatted_time.strftime('%m/%d/%Y %I:%M:%S %p')
                links = soup.find_all('a', href=lambda href: href and 'dl_spoiler' in href)
                if links:
                    self.spoiler = '[View Spoiler Log](' + self.BASE_URL + links[0].get('href') + ')'

    def formatUrl(self, text, urlType):
        if text.startswith("http"):
            return text
        else:
            return self.BASE_URL + "/" + urlType + "/" + text

    def getWorldData(self, soup):
        table = soup.find('table')
        #get table headers on the page
        headers = [th.get_text(strip=True) for th in table.find_all("th")]
        tbody = soup.find('tbody')
        #table data for the multiworld
        tableData = []
        #set initial append to the list to be the headers
        tableData.append(headers)
        rows = tbody.find_all('tr')
        for row in rows:
            rowData = []
            for index, td in enumerate(row.find_all("td")):
                tdText = td.get_text(strip=True)
                children = td.find_all("a", recursive=False)
                #If the text is the tracker, format the text to be a link
                if children and headers[index] != "Name":
                    rowData.append('['+children[0].get_text(strip=True)+'](' + self.BASE_URL + children[0].get('href') + ')')
                else:
                    rowData.append(td.get_text(strip=True))
            tableData.append(rowData)
        return tableData

    def formatHyperLink(self, text, link):
        return '['+text+']('+link+')'
