import requests
from pprint import pprint
from lxml import html
from selenium import webdriver
import warnings
warnings.filterwarnings('ignore')
from webdriver_manager.chrome import ChromeDriverManager


user_agent = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2)'
                            ' AppleWebKit/537.36 (KHTML, like Gecko) '
                            'Chrome/79.0.3945.88 Safari/537.36'}


