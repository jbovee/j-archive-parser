from __future__ import print_function
from bs4 import BeautifulSoup
import requests
import time
import lxml
import sys
import os
import re
import csv
import progressbar
import concurrent.futures as futures

# Break up CSVs into seasons

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
FOLDER = os.path.join(CURRENT_DIR, "j-archive-csv")
SECONDS_BETWEEN_REQUESTS = 5
NUM_THREADS = 2
try:
	import multiprocessing
	NUM_THREADS = multiprocessing.cpu_count() * 2
	print('Using {} threads'.format(NUM_THREADS))
except (ImportError, NotImplementedError):
	pass

def main():
	create_save_folder()
	get_all_seasons()

def create_save_folder():
    if not os.path.isdir(FOLDER):
        print("Creating %s folder" % FOLDER)
        os.mkdir(FOLDER)

def get_all_seasons():
	seasonsPage = requests.get('http://j-archive.com/listseasons.php')
	soupSeasons = BeautifulSoup(seasonsPage.text, 'lxml')
	r = re.compile(r'season=[0-9a-zA-Z]+')
	r2 = re.compile(r'showseason\.php\?season=')

	seasons = [r.search(link.get('href')).group(0).split('=')[1] for link in soupSeasons.find_all('a') if r2.match(link.get('href'))][::-1]

	with futures.ThreadPoolExecutor(max_workers=NUM_THREADS) as executor:
		for season in seasons:
			f = executor.submit(parse_season, season)

def parse_season(season):
	print('Starting season {}'.format(season))
	episodesPage = requests.get('http://j-archive.com/showseason.php?season='+season)
	soupEpisodes = BeautifulSoup(episodesPage.text, 'lxml')
	r = re.compile(r'game_id=[0-9]+')
	r2 = re.compile(r'http:\/\/www\.j-archive\.com\/showgame\.php\?game_id=[0-9]+')

	episodeIds = [r.search(link.get('href')).group(0).split('=')[1] for link in soupEpisodes.find_all('a') if r2.match(link.get('href'))][::-1]
	# extra_info
	extraInfo = [info.get_text() for info in soupEpisodes.find_all('td', class_='left_padded')][::-1]

	#write csv titles
	seasonFile = "j-archive-season-%s.csv" % season
	saveFile = os.path.join(FOLDER, seasonFile)

	time.sleep(SECONDS_BETWEEN_REQUESTS)
	with open(saveFile,'w',newline='',encoding='utf-8') as csvfile:
		episodeWriter = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
		episodeWriter.writerow(['epNum', 'airDate', 'extra_info', 'round_name', 'coord', 'category', 'order', 'value', 'daily_double', 'question', 'answer', 'correctAttempts', 'wrongAttempts'])
		for i in range(len(episodeIds)):
			#sys.stdout.write('\rSeason {}: Parsing episode {}/{}'.format(season, i, len(episodeIds)))
			#sys.stdout.flush()
			ep = parse_episode(episodeIds[i])
			if ep:
				ep = [[[clueElement for clueElement in clue] for clue in round] for round in ep]
				for round in ep:
					for question in round:
						question.insert(2, extraInfo[i].replace('\n','').strip()) if extraInfo[i] else question.insert(2, '')
						#print(question)
						episodeWriter.writerow(question)
	print('Season {} complete'.format(season))
	time.sleep(SECONDS_BETWEEN_REQUESTS)

def parse_episode(episodeLink):
	episode = requests.get('http://j-archive.com/showgame.php?game_id='+episodeLink)
	soupEpisode = BeautifulSoup(episode.text, 'lxml')

	epNum = re.search(r'#[0-9]+', soupEpisode.title.text).group(0)[1:]
	sj = re.compile(r'Super Jeopardy! show #[0-9]+')
	if sj.search(soupEpisode.title.text):
		epNum = sj.search(soupEpisode.title.text).group(0).replace('show #', '')
	trbk = re.compile(r'Trebek pilot #[0-9]+')
	if trbk.search(soupEpisode.title.text):
		epNum = trbk.search(soupEpisode.title.text).group(0).replace('#', '')
	# air_date
	airDate = re.search(r'([0-9]{4})[-]([0-9]{2})[-]([0-9]{2})', soupEpisode.title.text).group(0)

	hasRoundJ = True if soupEpisode.find(id='jeopardy_round') else False
	hasRoundDJ = True if soupEpisode.find(id='double_jeopardy_round') else False
	hasRoundFJ = True if soupEpisode.find(id='final_jeopardy_round') else False

	parsedRounds = []

	if hasRoundJ:
		j_table = soupEpisode.find(id='jeopardy_round')
		parsedRounds.append(parse_round(0, j_table, epNum, airDate))

	if hasRoundDJ:
		dj_table = soupEpisode.find(id='double_jeopardy_round')
		parsedRounds.append(parse_round(1, dj_table, epNum, airDate))

	if hasRoundFJ:
		fj_table = soupEpisode.find(id='final_jeopardy_round')
		parsedRounds.append(parse_round(2, fj_table, epNum, airDate))

	time.sleep(SECONDS_BETWEEN_REQUESTS)
	if parsedRounds:
		return parsedRounds
	else:
		return None

def parse_round(round, table, epNum, airDate):
	roundClues = []
	if round == 0 or round == 1:
		categories = [cat.text for cat in table.find_all('td', class_='category_name')]
		x = 0
		for clue in table.find_all('td', class_='clue'):
			exists = True if clue.text.strip() else False
			if exists:
				coord = tuple([int(x) for x in (re.search(r'[0-9]_[0-9]', clue.find('td', class_='clue_text').get('id')).group(0).split('_'))])
				valueRaw = clue.find('td', class_=re.compile('clue_value')).text
				value = valueRaw.lstrip('D: $').replace(',','')
				question = clue.find('td', class_='clue_text').text
				answer = BeautifulSoup(clue.find('div', onmouseover=True).get('onmouseover'), 'lxml').find('em', class_='correct_response').text
				daily_double = True if re.match(r'DD:', valueRaw) else False
				wrong = BeautifulSoup(clue.find('div', onmouseover=True).get('onmouseover'), 'lxml').find_all('td', class_='wrong')
				n = len(wrong)
				for w in wrong:
					if re.match(r'Triple Stumper', w.text):
						n = 3
				wrongAttempts = n
				correctAttempts = len(BeautifulSoup(clue.find('div', onmouseover=True).get('onmouseover'), 'lxml').find_all('td', class_='right'))
				totalAttemps = wrongAttempts + correctAttempts
				order = clue.find('td', class_='clue_order_number').text
				category = categories[x]
				round_name = 'Jeopardy' if round == 0 else 'Double Jeopardy'
				roundClues.append([epNum, airDate, round_name, coord, category, order, value, daily_double, question, answer, correctAttempts, wrongAttempts])
			x = 0 if x == 5 else x + 1
		#Jeopardy and double jeopardy rounds
		#Get categories
		#Go through all clues, keeping track of which column and using that to attribute category
	else:
		#Final Jeopardy
		coord = (1,1)
		value = False
		question = table.find('td', id='clue_FJ').text
		answer = BeautifulSoup(table.find('div', onmouseover=True).get('onmouseover'), 'lxml').find('em').text
		daily_double = False
		wrongAttempts = len(BeautifulSoup(table.find('div', onmouseover=True).get('onmouseover'), 'lxml').find_all('td', class_='wrong'))
		correctAttempts = len(BeautifulSoup(table.find('div', onmouseover=True).get('onmouseover'), 'lxml').find_all('td', class_='right'))
		totalAttemps = wrongAttempts + correctAttempts
		order = 0
		category = table.find('td', class_='category_name').text
		round_name = 'Final Jeopardy'
		roundClues.append([epNum, airDate, round_name, coord, category, order, value, daily_double, question, answer, correctAttempts, wrongAttempts])
	return roundClues

if __name__ == "__main__":
	main()