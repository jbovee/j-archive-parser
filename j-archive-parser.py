from bs4 import BeautifulSoup
import requests
import os
import re
import csv

# Break up CSVs into seasons

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
FOLDER = os.path.join(current_working_directory, "j-archive-csv")
SECONDS_BETWEEN_REQUESTS = 5

def main():
	create_save_folder()
	get_all_seasons()

def create_save_folder():
    if not os.path.isdir(FOLDER):
        print "Creating %s folder" % FOLDER
        os.mkdir(FOLDER)

def get_all_seasons():
	seasonsPage = requests.get('http://j-archive.com/listseasons.php')
	soupSeasons = BeautifulSoup(seasonsPage.text, 'html.parser')
	r = re.compile(r'season=[0-9a-zA-Z]+')
	r2 = re.compile(r'showseason\.php\?season=')

	seasons = [r.search(link).group(0).split('=')[1] for link in soupSeasons.find_all('a') if r2.match(link.get('href'))]

	for season in seasons[::-1][-1:]:
		parse_season(season)

def parse_season(season):
	episodesPage = requests.get(season)
	soupEpisodes = BeautifulSoup(episodesPage.text, 'html.parser')
	r = re.compile(r'game_id=[0-9]+')
	r2 = re.compile(r'http:\/\/www\.j-archive\.com\/showgame\.php\?game_id=[0-9]+')

	episodeIds = [r.search(link.get('href')).group(0).split('=')[1] for link in soupEpisodes.find_all('a') if r2.match(link.get('href'))]

	#write csv titles
	seasonFile = "j-archive-season-%s" % season
	saveFile = os.path.join(FOLDER, seasonFile)
	with open(saveFile,'wa') as csvfile:
		for id in episodeIds:
			ep = parse_episode(id)
			write_episode(ep,csvfile)

def parse_episode(episodeLink):
	episode = requests.get(episodeLink)
	soupEpisode = BeautifulSoup(episode.text, 'html.parser')

	#print(soupEpisode.find(id='game_title'))

	hasRounds = True if soupEpisode.find(id='jeopardy_round') else False

	return parsedEpisode

def parse_round():
	if round:
		#Jeopardy and double jeopardy rounds
	else:
		#Final jeopardy

def write_episode(episode, outfile):
	#episode will be input as list of array, each one being a question and its info

if __name__ == "__main__":
	main()