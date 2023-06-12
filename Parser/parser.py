import requests
from bs4 import BeautifulSoup as bs
import json


class Parser:
    def __init__(self, partCode):
        self.session = requests.Session()

        self.itradeURL = "https://itrade.forum-auto.ru/shop/index.html"
        self.shateLoginURL = "https://shate-m.ru/Account/LogOn"
        self.shateIDsParts = "https://shate-m.ru/api/searchPart/GetOriginalsInternalPrices?agreement="
        self.shateSearchIDs = "https://shate-m.ru/api/SearchPart/PartsByNumber?number="

        self.itradeLogin = "forddetal@yandex.ru"
        self.shateLogin = "CHUPRINIA"

        self.itradePassword = "3b02f43b98e8c52f"
        self.shatePassword = "123456789"

        self.partCode = partCode

    def parseItrade(self) -> list:
        request = self.session.get(self.itradeURL)
        html = bs(request.content, 'html.parser')
        if "Вход для клиентов" in html.text:
            self.loginItrade()

        request = self.findPart(self.partCode)
        html = bs(request.content, 'html.parser')
        table = html.find('table', {'id': 'search'})
        availableParts = []
        if table:
            rows = table.find_all('tr')

            for row in rows:
                columns = row.find_all('td')
                if 'tr_sa' not in row.get('class', []) and len(columns)>1:
                    availableParts.append(columns[1:])

        return availableParts

    def parseShate(self):
        self.loginShate()
        request = self.session.get(self.shateSearchIDs+ ''.join(self.partCode.split()))
        html = bs(request.content, 'html.parser')
        ids = self.getIDs(html.text)
        return self.findShatePart(self.partCode, ids)

    def findShatePart(self, partCode, ids):
        parts = []
        for id in ids:
            url = self.shateIDsParts + ''.join(partCode.split()) + '&partId=' + id
            urls = [url, url.replace("Internal", "External")]
            for url in urls:
                request = self.session.get(url)
                html = bs(request.content, 'html.parser')
                parts.append(html.text)

        return self.polishPartsInfo(parts)

    def getIDs(self, content):
        ids = []
        for line in content.split("\n"):
            line = line.strip()
            if "id" in line:
                ids.append(line.split()[-1][:-1])

        return ids

    def polishPartsInfo(self, parts):
        totalParts = []
        for part in parts:
            objs = json.loads(part)
            for obj in objs:
                for price in obj['prices']:
                    try:
                        available = price['availability']
                        if available not in ["-", "0"]:
                            totalParts.append(self.collectPartInfo(obj["partInfo"], price))
                    except:
                        pass

        return totalParts

    def collectPartInfo(self, partInfo1, partInfo2):
        info = []
        info.append(partInfo1["tradeMarkName"])
        info.append(partInfo1["description"])
        info.append(partInfo2["city"] if partInfo2["city"] else "Под заказ")
        info.append(partInfo2["availability"])
        try:
            info.append(partInfo2["deliveryProbability"])
        except:
            info.append("-")

        info.append(partInfo2["deliveryInfo"]["deliveryDateTimes"][1]["deliveryDate"])
        info.append(partInfo2["price"])

        return info

    def loginShate(self):
        self.session.post(self.shateLoginURL, data={
            'Login': self.shateLogin,
            'Password': self.shatePassword,
            'RememberMe': 'true',
            'ReturnUrl': ''
        })

    def loginItrade(self):
        self.session.post(self.itradeURL, data={
            'login': self.itradeLogin,
            'password': self.itradePassword,
            'enter': "Войти",
            'check': "stopSpam"
        })

    def findPart(self, partCode):
        r = self.session.post(self.itradeURL, data={
            "jspt": "1",
            "cat_num": partCode,
            "search": "Найти",
            "gr1": "600",
            "gr2": "0"
        })

        return r

    def getAvailableParts(self):
        parts = self.parseItrade()

        totalParts = []
        if parts:
            for part in parts:
                currentPart = []
                for column in part:
                    text = self.polishRow(column.text)
                    if text:
                        currentPart.append(text)
                totalParts.append(currentPart)

        return (totalParts, self.parseShate())

    def polishRow(self, row):
        row = row.strip()
        if not row:
            return ""

        res = ""
        for c in row:
            if c not in ["\n", "\r"]:
                res += c
            else:
                res += " "

        recommend = res.find("ФОРУМ-АВТО")
        if recommend != -1:
            res = res[:recommend-2]

        sale = res.find("Акция")
        if sale != -1:
            res = res[:sale - 2]

        return res