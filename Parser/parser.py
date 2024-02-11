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

        self.itradeLogin = ""
        self.shateLogin = ""

        self.itradePassword = ""
        self.shatePassword = ""

        self.partCode = partCode

    def parseItrade(self) -> list:
        # запрашиваем html страницу магазина
        request = self.session.get(self.itradeURL)
        html = bs(request.content, 'html.parser')
        if "Вход для клиентов" in html.text: # если не залогинены
            self.loginItrade()

        request = self.findPart(self.partCode) # отправляем запрос поиска детали
        html = bs(request.content, 'html.parser')   # получаем html страницу с результатами поиска
        table = html.find('table', {'id': 'search'})  # ищем таблицу в странице
        availableParts = []
        if table:
            rows = table.find_all('tr')

            for row in rows:
                columns = row.find_all('td')
                if 'tr_sa' not in row.get('class', []) and len(columns)>1: # если поле зеленого цвета (в наличии)
                    availableParts.append(columns[1:])

        return availableParts

    def parseShate(self):
        self.loginShate()  # логинимся
        request = self.session.get(self.shateSearchIDs+ ''.join(self.partCode.split()))  # заходим на страницу
                                                                             # детали с разделами
        html = bs(request.content, 'html.parser')
        ids = self.getIDs(html.text)  # вытаскиваем id разделов
        return self.findShatePart(self.partCode, ids)  # парсим результаты поиска в каждом разделе

    def findShatePart(self, partCode, ids):
        parts = []
        for id in ids:
            # каждая таблица разделов имеет свой url
            url = self.shateIDsParts + ''.join(partCode.split()) + '&partId=' + id
            urls = [url, url.replace("Internal", "External")]  # два типа деталей - в России и зарубежом
            for url in urls:
                # в качестве ответа на запрос будет словарь со всеми данными таблицы
                request = self.session.get(url)
                html = bs(request.content, 'html.parser')
                parts.append(html.text)  # сохраняем данные в необработанном виде

        return self.polishPartsInfo(parts)  # возвращаем отполированные данные

    def getIDs(self, content):  # вытаскиваем id разделов из строки данных
        ids = []
        for line in content.split("\n"):
            line = line.strip()
            if "id" in line:
                ids.append(line.split()[-1][:-1])

        return ids

    def polishPartsInfo(self, parts):  # вытаскиваем только необходимые для рендеринга данные таблицы
        totalParts = []
        for part in parts:
            # в качестве ответа приходит список из словарей, которые тоже содержат различные структуры данных
            # парсим и ищем нужные данные
            objs = json.loads(part)  # сохраняем данные из json
            for obj in objs:
                for price in obj['prices']:
                    try:
                        available = price['availability']
                        if available not in ["-", "0"]:
                            totalParts.append(self.collectPartInfo(obj["partInfo"], price))  # вытаскиваем нужные
                            # структуры данных и передаем их для выделения нужных полей
                    except:
                        pass

        return totalParts

    def collectPartInfo(self, partInfo1, partInfo2):
        info = []
        info.append(partInfo1["tradeMarkName"])  # бренд
        info.append(partInfo1["description"])
        info.append(partInfo2["city"] if partInfo2["city"] else "Под заказ")
        info.append(partInfo2["availability"])
        try:
            info.append(partInfo2["deliveryProbability"])  # не у всех указана возможность доставки
        except:
            info.append("-")

        info.append(partInfo2["deliveryInfo"]["deliveryDateTimes"][1]["deliveryDate"])
        info.append(partInfo2["price"])

        return info

    def loginShate(self):
        self.session.post(self.shateLoginURL, data={  # отправляем http запросом с payload для логина
            'Login': self.shateLogin,
            'Password': self.shatePassword,
            'RememberMe': 'true',
            'ReturnUrl': ''
        })

    def loginItrade(self):
        self.session.post(self.itradeURL, data={  # отправляем http запросом с payload для логина
            'login': self.itradeLogin,
            'password': self.itradePassword,
            'enter': "Войти",
            'check': "stopSpam"
        })

    def findPart(self, partCode):
        r = self.session.post(self.itradeURL, data={ #  отправляем http запросом с payload для поиска детали
            "jspt": "1",
            "cat_num": partCode,
            "search": "Найти",
            "gr1": "600",
            "gr2": "0"
        })

        return r

    def getAvailableParts(self):  # функция, которую вызывают извне, ищет детали и возвращает кортеж из двух
        # списков для каждого магазина отдельно
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

    def polishRow(self, row):  # убираем из данных ненужную информацию, пробелы и тп.
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
