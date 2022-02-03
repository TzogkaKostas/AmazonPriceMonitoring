#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import re
import json
import time
import requests
import argparse
import datetime, random
import UserAgent
from bs4 import BeautifulSoup
from termcolor import colored

ua = UserAgent.UserAgent()

# read config json from path
def get_config(config):
	with open(config, 'r') as f:
		# handle '// ' to json string
		input_str = re.sub(r'// .*\n', '\n', f.read())
		return json.loads(input_str)

def parse_args():
	parser = argparse.ArgumentParser()
	parser.add_argument('-c', '--config',
						default='%s/config.json' % os.path.dirname(os.path.realpath(__file__)),
						help='Add your config.json path')
	parser.add_argument('-t', '--poll-interval', type=int, default=780,
						help='Time(second) between checking, default is 780 s.')

	return parser.parse_args()

def get_config_parameter(key):
	return config[key]

def get_datetime():
	return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def parse_product(product):
	return product[0]

def get_product_price(response):

	webpage = BeautifulSoup(response.content, "html.parser")

	price_container = webpage.find(id="corePrice_desktop").find("span", class_="a-offscreen")

	if price_container == None:
		price_container = "   "
	else:
		price_container = price_container.text

	price = re.findall('\d+.\d+', price_container)
	if price:
		price = float(price[0])
	else:
		price = None

	return price

def get_product_name(response):

	webpage = BeautifulSoup(response.content, "html.parser")

	name_container = webpage.find(id="productTitle")

	return name_container.text.strip()[:30] + "..."

def get_product_info(product_url):

	# set random user agent prevent banning
	response = requests.get(product_url, headers={
		'User-Agent': ua.random(),
		'Accept-Language':    'zh-tw',
		'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
		'Connection':'keep-alive',
		'Accept-Encoding':'gzip, deflate'
	})
	response.raise_for_status()

	return get_product_name(response), get_product_price(response)

def scan_products(products):
	for product in products:
		product_url = parse_product(product)
		name, price = get_product_info(product_url)
		if price == None:
			price = colored('OUT OF STOCK', 'red')
		else:
			price = colored(price, 'green')

		print("[", get_datetime(), "]", name, "-", product_url, "-", price)

def sleep_at_least(sleep_time):
	_time = sleep_time + random.randint(0, 150)
	print("Sleeping for", round(_time/60, 1), "minutes..." )
	time.sleep(_time)

def main():

	global config
	args = parse_args()
	config = get_config(args.config)
	sleep_time = config['sleep-time']
	products = config['products']

	print("Start scanning of products...")
	while True:
		scan_products(products)

		sleep_at_least(sleep_time)	


if __name__ == '__main__':
	main()
