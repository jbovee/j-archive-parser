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

	for episode in episodelinks:
		#Get episode page html
		#Search for jeopardy_round/double_jeopardy_round/final_jeopardy_round divs to check if page has no questions
		#Jeopardy round
		#For each category collect info about each question (question, answer, value, category, round, order picked, airdate, episode number, more?) and write out to file
		#Same style for double jeopardy round
		#Get final jeopardy round
		## Maybe identify between regular questions and daily doubles and mark how much was wagered
		print(episode)