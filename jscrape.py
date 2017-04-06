from bs4 import BeautifulSoup
import requests
import re

### Maybe look into breaking up into functions ###

seasons = requests.get('http://j-archive.com/listseasons.php')

soupseasons = BeautifulSoup(seasons.text, 'html.parser')

r = re.compile(r'showseason\.php\?season=')

seasonlinks = []

for link in soupseasons.find_all('a'):
	reg = r.match(link.get('href'))
	if reg:
		seasonlinks.append("http://j-archive.com/"+link.get('href'))

r = re.compile(r'http:\/\/www\.j-archive\.com\/showgame\.php\?game_id=')

for season in seasonlinks[::-1][-1:]:
	episodes = requests.get(season)
	soupepisodes = BeautifulSoup(episodes.text, 'html.parser')

	episodelinks = []

	for link in soupepisodes.find_all('a'):
		reg = r.match(link.get('href'))
		if reg:
			episodelinks.append(link.get('href'))

	for episodelink in episodelinks:
		episode = requests.get(episodelink)
		soupepisode = BeautifulSoup(episode.text, 'html.parser')

		#print(soupepisode.find(id='game_title'))

		isBlank = True if soupepisode.find(id='jeopardy_round') is None else False