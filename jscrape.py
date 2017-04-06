from bs4 import BeautifulSoup
import requests
import re

### Maybe look into breaking up into functions ###

seasons = requests.get('http://j-archive.com/listseasons.php')

soupSeasons = BeautifulSoup(seasons.text, 'html.parser')

r = re.compile(r'showseason\.php\?season=')

seasonLinks = []

for link in soupSeasons.find_all('a'):
	reg = r.match(link.get('href'))
	if reg:
		seasonLinks.append("http://j-archive.com/"+link.get('href'))

r = re.compile(r'http:\/\/www\.j-archive\.com\/showgame\.php\?game_id=')

for season in seasonLinks[::-1][-1:]:
	episodes = requests.get(season)
	soupEpisodes = BeautifulSoup(episodes.text, 'html.parser')

	episodeLinks = []

	for link in soupEpisodes.find_all('a'):
		reg = r.match(link.get('href'))
		if reg:
			episodeLinks.append(link.get('href'))

	for episodeLink in episodeLinks:
		episode = requests.get(episodeLink)
		soupEpisode = BeautifulSoup(episode.text, 'html.parser')

		#print(soupEpisode.find(id='game_title'))

		isBlank = True if soupEpisode.find(id='jeopardy_round') is None else False