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

def sys_print(string):
	sys.stdout.write("{}\n".format(string))
	sys.stdout.flush()

if __name__=="__main__":
	main()