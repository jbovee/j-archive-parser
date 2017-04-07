from bs4 import BeautifulSoup
import requests
import re

### Maybe look into breaking up into functions ###
# Break up CSVs into seasons

SECONDS_BETWEEN_REQUESTS = 5

def main():
	#Open/create file to be written to
	seasons = get_all_seasons()

def get_all_seasons():
	seasonPage = requests.get('http://j-archive.com/listseasons.php')
	soupSeasons = BeautifulSoup(seasonPage.text, 'html.parser')
	r = re.compile(r'season=[0-9a-zA-Z]+')
	r2 = re.compile(r'showseason\.php\?season=')

	seasons = [r.search(link).group(0).split('=')[1] for link in soupSeasons.find_all('a') if r2.match(link.get('href'))]

	for season in seasons[::-1][-1:]:
		get_episodes(season)

def parse_season(season):
	episodes = requests.get(season)
	soupEpisodes = BeautifulSoup(episodes.text, 'html.parser')
	r = re.compile(r'game_id=[0-9]+')
	r2 = re.compile(r'http:\/\/www\.j-archive\.com\/showgame\.php\?game_id=[0-9]+')

	episodeIds = [r.search(link.get('href')).group(0).split('=')[1] for link in soupEpisodes.find_all('a') if r2.match(link.get('href'))]

	#write csv titles
	for id in episodeIds:
		ep = parse_episode(id)
		write_episode(ep,outfile)

def parse_episode(episodeLink):
	episode = requests.get(episodeLink)
	soupEpisode = BeautifulSoup(episode.text, 'html.parser')

	#print(soupEpisode.find(id='game_title'))

	isBlank = True if soupEpisode.find(id='jeopardy_round') is None else False

def parse_round():
	if round:
		#Jeopardy and double jeopardy rounds
	else:
		#Final jeopardy

def write_episode(episode, outfile):

if __name__ == "__main__":
	main()