# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import requests

def GetDataFromArrey(data):
    value = data.split(": ")
    return value[len(value) - 1].strip()

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

req = requests.get("https://www.thepiratefilmes.biz/")
data = req.text
soup = BeautifulSoup(data, "html.parser")

for art in soup.find_all('article'):
    id = art.get('id')
    title = art.header.h2.a.string
    category = art.div.find("div", class_="entry-categories").text.strip()
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
    print("------------------------------------------------")