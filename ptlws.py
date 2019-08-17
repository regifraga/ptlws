# -*- coding: utf-8 -*-
import sys
from bs4 import BeautifulSoup
import requests

pages = []
contents = []

#constantes
TITLE = 1
GENRE = 2
AUDIO = 3
SUBTITLE = 4
FORMAT = 5
QUALITY = 6
SIZE = 7
YEAR = 8
DURATION = 9
AUDIO_QUALITY = 10
VIDEO_QUALITY = 11
URL = "https://www.thepiratefilmes.biz/category/filmes/"

def GetDataFromArrey(data):
    value = data.split(": ")
    return value[len(value) - 1].strip()

def extractValues(pageContent):
    for art in pageContent.find_all('article'):
        id = art.get('id')
        title = art.header.h2.a.string
        #category = art.div.find("div", class_="entry-categories").text.strip()
        img = "https:" + art.find("img", class_="alignleft").get("src")
        info = art.find("div", class_="entry")

        movieData = info.text.splitlines()
        title = GetDataFromArrey(movieData[TITLE])
        genre = GetDataFromArrey(movieData[GENRE])
        audio = GetDataFromArrey(movieData[AUDIO])
        subtitle = GetDataFromArrey(movieData[SUBTITLE])
        format = GetDataFromArrey(movieData[FORMAT])
        quality = GetDataFromArrey(movieData[QUALITY])
        size = GetDataFromArrey(movieData[SIZE])
        year = GetDataFromArrey(movieData[YEAR])
        duration = GetDataFromArrey(movieData[DURATION])
        audioQuality = GetDataFromArrey(movieData[AUDIO_QUALITY])
        videoquality = GetDataFromArrey(movieData[VIDEO_QUALITY])

        print(id)
        print(title)
        print(genre)
        print(audio)
        print(subtitle)
        print(format)
        print(quality)
        print(size)
        print(year)
        print(duration)
        print(audioQuality)
        print(videoquality)
        print(img)
        print("--------------------------------------------")

totalArgs = len(sys.argv) - 1
totalPages = int(sys.argv[1]) if totalArgs > 0 else 1

print("Total Args: %s\nTotal Pages: %s\n********************************************" %(totalArgs, totalPages))

if totalArgs > 0:
    for i in range(1, totalPages + 1):
        pages.append(URL + "page/" + str(i))
else:
    pages.append(URL)

try:
    for page in pages:
        res = requests.get(page)
        contents.append(res.text)
except:
    print("ERROR >>> ", sys.exc_info()[0])
else:
    for content in contents:
        soup = BeautifulSoup(content, "html.parser")

        if len(content) == 0:
            print("No content found!")
        else:
            extractValues(soup)
