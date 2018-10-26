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
	print(get_episode_list(1))
	pass

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