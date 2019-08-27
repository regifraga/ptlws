# -*- coding: utf-8 -*-
import re
import sys
from bs4 import BeautifulSoup
import requests
import json

#listas
pages = []

#constantes
URL = "https://www.thepiratefilmes.biz/category/filmes/"
API = "http://movies.api.regifraga.com/api/movie"

#métodos auxiliares
def GetDataFromArrey(data, index):
    if index >= len(data):
        return None

    value = data[index].split(": ")
    return value[len(value) - 1].strip()

def CreateJSON(data):
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

    #Título do Filme: Duendes e Dragões
    #Gênero: Fantasia, Terror, Thriller
    #Áudio:  Português, Inglês
    #Legenda: S/ L.
    #Formato: MKV
    #Qualidade: WEB-DL 720p, 1080p
    #Tamanho: 1 GB, 1.7 GB
    #Ano de Lançamento: 2019
    #Duração: 1h 30Min.
    #Qualidade de Áudio:  10
    #Qualidade de Vídeo: 10
    #IMDb: 3.5/10

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
        jsonData = CreateJSON(movieData)
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
                print(id)
                r = requests.post(API, json=jsonData)
            finally:
                print(r.status_code)

#inicializadores
totalArgs = len(sys.argv) - 1
totalPages = int(sys.argv[1]) if totalArgs > 1 else 1
pageEnd = int(sys.argv[2]) + 1 if totalArgs > 2 else totalPages + 1
isTest = False

for i in range(1, len(sys.argv)):
    if str(sys.argv[i]).lower() == "test":
        isTest = True
        break

if totalArgs == 1:
    print("Total Args: %s\nTotal Pages: %s\nTest mode: %s\n%s" %(totalArgs, totalPages, isTest, "=" * 60))
else:
    print("Total Args: %s\nStart Page: %s\nEnd PAge: %s\nTest mode: %s\n%s" %(totalArgs, totalPages, pageEnd, isTest, "=" * 60))

if totalArgs > 0:
    pages = [URL + "page/" + str(i) for i in range(totalPages, pageEnd)]
else:
    pages.append(URL)

#inínio
try:
    for page in pages:
        print("Getting %s..."%(page))
        res = requests.get(page)

        if res.status_code == 200:
            print("status_code == 200")
            soup = BeautifulSoup(res.text, "html.parser")

            if len(res.text) == 0:
                print("No content found!")
            else:
                try:
                    ExtractValues(soup)
                except Exception, e:
                    print("ERROR > ", str(e))
except:
    print("ERROR >>> ", sys.exc_info()[0])
