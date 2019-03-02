from bs4 import BeautifulSoup
import re
import os
import sys
import time
import requests
import concurrent.futures as futures

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
SITE_FOLDER = os.path.join(CURRENT_DIR, 'j-archive archive')
NUM_THREADS = 2
try:
	import multiprocessing
	NUM_THREADS = multiprocessing.cpu_count() * 2
	print('Using {} threads'.format(NUM_THREADS))
except (ImportError, NotImplementedError):
	pass

def main():
	create_save_folder()
	seasons = list(range(1,36))
	with futures.ThreadPoolExecutor(max_workers=NUM_THREADS) as executor:
		for season in seasons:
			f = executor.submit(download_season, season)

def create_save_folder():
	if not os.path.isdir(SITE_FOLDER):
		sys_print("Creating {} folder".format(SITE_FOLDER))
		os.mkdir(SITE_FOLDER)

def download_season(season):
	sys_print('Downloading Season {}'.format(season))
	season_folder = os.path.join(SITE_FOLDER, "season {}".format(season))
	if not os.path.isdir(season_folder):
		sys_print("Creating season {} folder".format(season))
		os.mkdir(season_folder)
	seasonPage = requests.get('http://j-archive.com/showseason.php?season={}'.format(season))
	seasonSoup = BeautifulSoup(seasonPage.text, 'lxml')
	epIdRe = re.compile(r'game_id=(\d+)')
	epNumRe = re.compile(r'\#(\d{1,4})')
	episodeRe = re.compile(r'http:\/\/www\.j-archive\.com\/showgame\.php\?game_id=[0-9]+')
	episodeLinks = [link for link in seasonSoup.find_all('a') if episodeRe.match(link.get('href'))][::-1]
	for link in episodeLinks:
		episodeNumber = epNumRe.search(link.text.strip()).group(1)
		gameFile = os.path.join(season_folder,'{}.html'.format(episodeNumber))
		if not os.path.isfile(gameFile):
			episodeId = epIdRe.search(link['href']).group(1)
			gamePage = requests.get('http://j-archive.com/showgame.php?game_id={}'.format(episodeId))
			open(gameFile, 'wb').write(gamePage.content)
			time.sleep(5)
	sys_print('Season {} finished'.format(season))

def sys_print(string):
	sys.stdout.write("{}\n".format(string))
	sys.stdout.flush()

if __name__=="__main__":
	main()