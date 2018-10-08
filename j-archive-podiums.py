from bs4 import BeautifulSoup
import requests
import time
import lxml
import sys
import os
import re
import csv

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
FOLDER = os.path.join(CURRENT_DIR, 'j-archive-podium-data')

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
	epNumRe = re.compile(r'\#\d{1,4}')
	epDateRe = re.compile(r'\d{4}-\d{2}-\d{2}')
	episodes = [row.find_all('td') for row in seasonSoup.find_all('tr')]
	return [{"epNum": epNumRe.search(episode[0].text.strip()).group(0), "date": epDateRe.search(episode[0].text.strip()).group(0), "contestants": episode[1].text.strip(), "info": episode[2].text.strip()} for episode in episodes]

if __name__=="__main__":
	main()