# -*- coding: utf-8 -*-
import re
import sys
from bs4 import BeautifulSoup
import requests
import json
import base64

#listas
pages = []

#constantes
URL = "https://www.thepiratefilmes.biz/category/filmes/"
API = "http://movies.api.regifraga.com/api/movie"
#URL_DETAIL = "https://www.thepiratefilmes.biz/magellan-2017-torrent-dublado/"
#URL_DETAIL = "https://www.thepiratefilmes.biz/apos-a-letargia-2019-torrent-dublado/"

#métodos auxiliares
def GetDataFromArrey(data, index):
    if index >= len(data):
        return None

    value = data[index].split(": ")
    return value[len(value) - 1].strip()

def CreateJsonMovie(data):
    #valores padrão
    jsonData = {
        "id": "",
        "title": "",
        "description": "",
        "subtitle": "",
        "ditailLink": "",
        "audio": "",
        "quality": "",
        "size": "",
        "audioQuality": "",
        "videoquality": "",
        "actors": "",
        "directors": "",
        "imdb": "",
        "genres": "",
        "items": "",
        "popularity": "",
        "posterBig": "",
        "posterMed": "",
        "rating": 0,
        "runtime": 0,
        "trailerLink": "",
        "writers": "",
        "year": 0,
        "dubbed": 0,
        "torrents": []
    }

    #atribui os valores ao json a ser enviado
    for d in data:
        parts = d.split(": ")
        name = unicode(parts[0].strip())

        if (len(parts) > 1):
            value = unicode(parts[1].strip())
        else:
            value = ""

        if unicode(name) == u"Título do Filme":
            jsonData["title"] = value
        elif unicode(name) == u"Gênero":
            jsonData["genres"] = value
        elif name == "Legenda":
            jsonData["subtitle"] = value
        elif name == "Formato":
            jsonData["items"] = value
        elif name == "Qualidade":
            jsonData["quality"] = value
        elif name == "Tamanho":
            jsonData["size"] = value
        elif unicode(name) == u"Ano de Lançamento":
            jsonData["year"] = int(value)
        elif name.startswith(u"Duração"):
            totalDuration = 0
            try:
                value = name.strip()
                totalDurations = re.findall(r'\d+', value)

                if len(totalDurations) > 1:
                    totalDuration = (int(totalDurations[0]) * 60) + int(totalDurations[1])
            finally:
                jsonData["runtime"] = int(totalDuration)
        elif name == u"Qualidade de Áudio":
            jsonData["audioQuality"] = value
        elif name == u"Qualidade de Vídeo":
            jsonData["videoquality"] = value
        elif name == "IMDb":
            jsonData["imdb"] = value

    return jsonData

def ExtractValues(pageContent):
    for art in pageContent.find_all('article'):
        id = art.get('id')
        category = art.div.find("div", class_="entry-categories").text.strip()
        img = "https:" + art.find("img", class_="alignleft").get("src")
        info = art.find("div", class_="entry")
        ditailLink = art.find("a", class_="continue-reading")

        movieData = info.text.splitlines()
        jsonData = CreateJsonMovie(movieData)
        jsonData["id"] = id
        jsonData["posterBig"] = img
        jsonData["posterMed"] = img
        jsonData["ditailLink"] = ditailLink.get("href")

        dublado = 1 if "Dublado" in category else 0
        jsonData["dubbed"] = dublado
        
        if isTest:
            print(json.dumps(jsonData, indent=4, sort_keys=True))
        else:
            try:
                print("%s..." %(id)),
                r = requests.post(API, json=jsonData)
            finally:
                print("status_code: %s" %(r.status_code))

def reverse_slicing(s):
    return s[::-1]

def ExtractDetails(jsonMovie, pageContent):
    torrents = []

    for art in pageContent.find_all('article'):
        id = art.get('id')
        print(id)

        sinopse = art.find("div", class_="entry").contents[1].text.replace("SINOPSE: ", "")
        jsonMovie["description"] = sinopse.replace("SINOPSE:", "").strip()

        videoLink = art.find("iframe").get("src")
        jsonMovie["trailerLink"] = videoLink

        idx = 0
        torrentLink = art.find_all("img", src="/img/Download.png")

        for img in torrentLink:
            jsonTorrent = {
                "id": "",
                "movieId": "",
                "quality": "",
                "size": "",
                "torrentMagnet": "",
                "torrentUrl": ""
            }
            
            idx += 1
            jsonTorrent["id"] = id + art.header.h1.a.text + "__" + str(idx)
            jsonTorrent["movieId"] = id

            print(idx)

            if isTest:
                print(img)
                print(jsonTorrent)

            magnet = img.parent.get("href")
            startIndex = magnet.index("id=")
            endIndex = magnet.index("&ref=")

            imgInfo = img.parent.parent.previous_sibling
            imgInfoTitle = ''.join(unicode(caption.string) for caption in imgInfo.previous_sibling.contents)
            imgInfoSize = imgInfo.string.string.replace("|", "")
            jsonTorrent["quality"] = imgInfoTitle.rstrip()
            jsonTorrent["size"] = imgInfoSize.strip()

            #decript the link
            magnetContent = magnet[startIndex + 3 : endIndex].replace("=", "")
            magnetContentReverse = reverse_slicing(magnetContent)
            magnetContentDecode = base64.b64decode(magnetContentReverse + '=' * (-len(magnetContentReverse) % 4))
            jsonTorrent["torrentMagnet"] = str(magnetContentDecode)

            torrents.append(jsonTorrent)

        subtitleLink = art.find_all("strong", string="DOWNLOAD LEGENDA")
        for sub in subtitleLink:
            subLink = sub.parent.get("href")
            jsonMovie["SubtitleLink"] += subLink

        jsonMovie["torrents"] = torrents

        if isTest:
            print(json.dumps(jsonMovie, indent=4, sort_keys=True))
        else:
            putAddress = API + "/" + id
            print("PUT to %s..." %(putAddress))
            headers = {"Content-Type": "application/json"}

            print(json.dumps(jsonMovie, indent=4, sort_keys=True))

            r = requests.put(putAddress, data=json.dumps(jsonMovie, indent=4, sort_keys=True), headers=headers)
            print(r.status_code),

            if r.status_code == 500:
                print(r.text())

#inicializadores
totalArgs = len(sys.argv) - 1
totalPages = int(sys.argv[1]) if totalArgs > 1 else 1
pageEnd = int(sys.argv[2]) + 1 if totalArgs >= 2 else totalPages + 1
isTest = False
isDetail = False

for i in range(1, len(sys.argv)):
    if str(sys.argv[i]).lower() == "test":
        isTest = True
    elif str(sys.argv[i]).lower() == "detail":
        isDetail = True

if totalArgs == 1:
    print("Total Args: %s\nTotal Pages: %s\nTest mode: %s\nDetail: %s\n%s" %(totalArgs, totalPages, isTest, isDetail, "=" * 60))
else:
    print("Total Args: %s\nStart Page: %s\nEnd Page: %s\nTest mode: %s\nDetail: %s\n%s" %(totalArgs, totalPages, pageEnd, isTest, isDetail, "=" * 60))

if totalArgs > 1:
    if isDetail:
        url = "http://movies.api.regifraga.com/api/movie/%s/1"
        pages = [url %(i) for i in range(totalPages, pageEnd)]
    else:
        pages = [URL + "page/" + str(i) for i in range(totalPages, pageEnd)]
elif totalArgs == 1:
    pages.append(URL + "page/" + sys.argv[1])
else:
    pages.append(URL)

#inínio
try:
    print("Total page(s): %s" %(len(pages)))

    for page in pages:
        print("\n%s\nGetting %s..."%('/' * 60, page)),
        res = requests.get(page)

        if res:
            print("status_code: %s" %(res.status_code))

            if isDetail:
                jsonData = res.json()[0]
                detailLink = jsonData['ditailLink']
                
                if isTest:
                    print(json.dumps(jsonData, indent=4, sort_keys=True))

                print("\nGetting detail %s..." %(detailLink))
                res = requests.get(detailLink)
                soup = BeautifulSoup(res.text, "html.parser")

                try:
                    ExtractDetails(jsonData, soup)
                except Exception, e:
                    print("ERROR on ExtractDetails!", str(e))
                    continue
            elif len(res.text) != 0:
                try:
                    soup = BeautifulSoup(res.text, "html.parser")
                    ExtractValues(soup)
                except Exception, e:
                    print("ERROR on ExtractValues!", str(e))
                    continue
except:
    print("ERROR >>> ", sys.exc_info()[0])
