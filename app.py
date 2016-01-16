from flask import Flask, render_template, request
import urllib2
from bs4 import BeautifulSoup
import re
from fuzzywuzzy import fuzz
import json

app = Flask(__name__)

def lyricscraper(artist_name, song_name):
    base_url = "http://search.azlyrics.com/search.php?q="

    artist = artist_name.lower()
    newartist = artist.replace(" ", "+")
    song_choice = song_name.lower();
    newsong_name = song_choice.replace(" ", "+")

    url = base_url + newartist + "+" + newsong_name
    url_parse = urllib2.urlopen(url)
    soup = BeautifulSoup(url_parse, "html.parser")

    listoftables = soup.find_all("td")
    listoftables[0] = str(listoftables[0])
    maincheck = listoftables[0]
    soup2 = BeautifulSoup(maincheck, "html.parser")

    checklist = soup2.find_all('b')

    link = ""

    song_name_check = str(checklist[0])
    song_name_check = song_name_check.replace("<b>", "")
    song_name_check = song_name_check.replace("</b>", "")
    artist_check = str(checklist[1])
    artist_check = artist_check.replace("<b>", "")
    artist_check = artist_check.replace("</b>", "")

    if(fuzz.ratio(artist, artist_check.lower()) > 70 and fuzz.ratio(song_name, song_name_check.lower()) > 70):
        link = soup2.find('a')
        link = link.get('href')
    else:
        songpage_url = "http://www.azlyrics.com/lyrics/"
        end = ".html"
        nextartist = artist.replace(" ", "")
        nextsong_name = song_name.replace(" ", "")
        link = songpage_url + nextartist + "/" + nextsong_name + end

    url_parse = urllib2.urlopen(link)
    soup3 = BeautifulSoup(url_parse, "html.parser")

    listofdivs = soup3.find_all("div")
    newstrlist = []
    finallyrics = ""

    for item in listofdivs:
        newstrlist.append(str(item))

    for newitem in newstrlist:
        if("<!-- Usage of azlyrics.com content" in newitem):
            finallyrics = newitem

    finallyrics = finallyrics.replace("<br>", "")
    finallyrics = finallyrics.replace("</br>", "")
    finallyrics = finallyrics.replace("<div>", "")
    finallyrics = finallyrics.replace("</div>", "")
    finallyrics = finallyrics.replace("<i>", "")
    finallyrics = finallyrics.replace("</i>", "")
    finallyrics = finallyrics.replace("(", "")
    finallyrics = finallyrics.replace(")", "")
    finallyrics = finallyrics.replace("<!-- Usage of azlyrics.com content by any third-party lyrics provider is prohibited by our licensing agreement. Sorry about that. -->", "")
    finallyrics = finallyrics.replace("[Hook:]", "")
    finallyrics = finallyrics.replace("[Verse 1:]", "")
    finallyrics = finallyrics.replace("[Verse 2:]", "")
    finallyrics = finallyrics.replace("[x2]", "")
    finallyrics = finallyrics.replace("[x3]", "")
    finallyrics = finallyrics.replace("[x4]", "")
    finallyrics = finallyrics.replace("[x5]", "")
    finallyrics = finallyrics.strip()
    finallyrics = finallyrics.replace(",", "")

    return finallyrics


def get_gifs(song_lyrics):
    query_list = song_lyrics.split()
    link_list = []

    for lyric in query_list:

    	url = "http://api.giphy.com/v1/gifs/search?q="
    	api_key = "API KEY HERE"
    	final_url = url + lyric + api_key
    	parse_info = urllib2.urlopen(final_url)
    	data = json.load(parse_info)

    	for item in data['data']:
            url_loc = item['images']['downsized']['url']
            link_list.append(url_loc)

    return link_list

@app.route("/")
def beginvalues():
    return render_template("start.html")

@app.route("/done", methods=['GET', 'POST'])
def newvalues():
    artist_choice = request.form["artist"]
    song_selection = request.form["song"]
    all_lyrics = lyricscraper(artist_choice, song_selection)
    item_list = get_gifs(all_lyrics)
    return render_template("finish.html", all_lyrics = all_lyrics, item_list = item_list)

if __name__ == "__main__":
    app.run()
