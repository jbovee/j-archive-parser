from bs4 import BeautifulSoup
import requests
import time
import lxml
import sys
import os
import re
import csv

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
FOLDER = os.path.join(CURRENT_DIR, 'podium-data')

def main():
	# allEpisodes = get_episode_range(1,35)
	# create_save_folder()
	listfile = os.path.join(FOLDER, 'episode-list.csv')
	# write_to_csv(listfile, allEpisodes)
	tournfile = os.path.join(CURRENT_DIR, 'tournament-episodes.csv')
	podiumData = get_podium_data(listfile,tournfile)
	datafile = os.path.join(FOLDER, 'podium-data.csv')
	write_to_csv(datafile,podiumData)

def get_podium_data(episodesFile,tournamentsFile):
	allEpisodes = read_from_csv(episodesFile)[::-1]
	tournEps = get_tourn_ep_list(tournamentsFile)
	results = []
	episode_i = 0
	while episode_i < len(allEpisodes)-1:
		sys_print("Episode {} out of {}, id no. {}, game no. {}".format(episode_i,len(allEpisodes),allEpisodes[ episode_i ]['gameId'],allEpisodes[ episode_i ]['epNum']))
		offset = 1
		currentEp = allEpisodes[ episode_i ]
		nextEp = allEpisodes[ episode_i+offset ]
		# Increase offset until next episode is non-tournament
		while (int(nextEp['epNum']) in tournEps):
			offset += 1
			nextEp = allEpisodes[ episode_i+offset ]
		currentContestants = re.split(r' vs\. ', currentEp['contestants'])
		winnerIndices = []
		# Check if episodes are immediately before/after each other
		# If they are, can use list of contestant names to determine winner(s)
		# If not, need to request game page and parse winner(s)
		if int(nextEp['epNum']) == int(currentEp['epNum'])+offset:
			nextContestants = re.split(r' vs\. ', nextEp['contestants'])
			champSet = set(currentContestants).intersection(nextContestants)
			winnerIndices = [i for i, contestant in enumerate(currentContestants) if contestant in champSet]
		else:
			winnerIndices = parse_winners(currentEp['gameId'])
			time.sleep(5)
		results.append({
			"gameId": int(currentEp['gameId']),
			"season": int(currentEp['season']),
			"epNum": int(currentEp['epNum']),
			"date": currentEp['date'],
			"left": currentContestants[0],
			"middle": currentContestants[1],
			"right": currentContestants[2],
			"winnerIndices": winnerIndices
		})
		episode_i += offset
	return results

def create_save_folder():
	if not os.path.isdir(FOLDER):
		print('Creating %s folder' % FOLDER)
		os.mkdir(FOLDER)

def parse_winners(episodeId):
	page = requests.get("http://www.j-archive.com/showgame.php?game_id={}".format(episodeId))
	pageSoup = BeautifulSoup(page.text, 'lxml')
	try:
		finalScores = [int(score.text.replace('$','').replace(',','')) for score in pageSoup.find('h3', string='Final scores:').findNext('table').find_all('tr')[1].find_all('td')]
	except:
		print("No final scores section for game with ID {}".format(episodeId))
		return []
	adjustedScores = [score if score >= 0 else 0 for score in finalScores]
	maxScore = max(adjustedScores)
	return [i for i, score in enumerate(adjustedScores) if score == maxScore and score != 0]

def get_episode_list(season):
	seasonPage = requests.get('http://j-archive.com/showseason.php?season={}'.format(season))
	seasonSoup = BeautifulSoup(seasonPage.text, 'lxml')
	epNumRe = re.compile(r'\#(\d{1,4})')
	epDateRe = re.compile(r'\d{4}-\d{2}-\d{2}')
	gameIdRe = re.compile(r'game_id=(\d+)')
	episodes = [row.find_all('td') for row in seasonSoup.find_all('tr')]
	return [{
				"season": season,
				"epNum": epNumRe.search(episode[0].text.strip()).group(1),
				"gameId": eIdRe.search(episode[0].a['href']).group(1),
				"date": epDateRe.search(episode[0].text.strip()).group(0),
				"contestants": episode[1].text.strip(),
				"info": episode[2].text.strip()
			}
			for episode in episodes]

def get_episode_range(start,end):
	episodes = []
	for season in range(start,end+1):
		sys_print("Season {}".format(season))
		episodes = get_episode_list(season) + episodes
		time.sleep(5)
	return episodes

def get_tourn_ep_list(filename):
	result = []
	with open(filename,'r',newline='',encoding='utf-8') as csvfile:
		reader = csv.reader(csvfile)
		next(reader, None)
		for row in reader:
			result = result + list(range(int(row[0]),int(row[1])+1))
	return result

def sys_print(string):
	sys.stdout.write("{}\n".format(string))
	sys.stdout.flush()

def write_to_csv(filename, data):
	with open(filename,'w',newline='',encoding='utf-8') as csvfile:
		writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
		keys = data[0].keys()
		writer.writerow(list(keys))
		for d in data:
			writer.writerow([d[key] for key in keys])

def read_from_csv(filename):
	result = []
	with open(filename,'r',newline='',encoding='utf-8') as csvfile:
		reader = csv.reader(csvfile)
		headers = next(reader, None)
		for row in reader:
			d = {}
			for h, v in zip(headers, row):
				d[h] = v
			result.append(d)
	return result

if __name__=="__main__":
	main()