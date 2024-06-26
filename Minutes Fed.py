import requests
from bs4 import BeautifulSoup
import os
import dateutil.parser as dparser

import re
import nltk
from nltk.tokenize import  word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.stem import porter
year_start = 1936
year_end = 2018
##Download html files from the Fed page. For every year since 1936.
for year in range(year_start,year_end):
    url = f'https://www.federalreserve.gov/monetarypolicy/fomchistorical{year}.htm'
    response = requests.get(url)
    html_content = response.text

    soup = BeautifulSoup(html_content, 'html.parser')

    # Finds HTML element where minutes are included.
    minutes_section = soup.find('div', class_='col-xs-12 col-sm-8 col-md-9')

    # Finds all labels <a> inside this section
    links = minutes_section.find_all('a')

    # Iterate over the links and download the HTML files
    directory = f'C:/Users/LUIS/Documents/Fed Minutes'
    if not os.path.exists(directory):
        os.makedirs(directory)

    base_url = 'https://www.federalreserve.gov/'#This is the base URL. You add the href to access the page.

    # Iterate over the links and download only the HTML files
    for link in links:
        href = link['href'] #Encuentra el hipervinculo desde donde se llega a la pagina con la informacion de las minutas.
        if ('minutes' in href or 'MINUTES' in href or 'histmin' in href or 'moa' in href) and (href.endswith('.htm')):  # Filtra usando palabras que indican que son direcciones con las minutas.
            file_url = base_url + href  # Construct the complete URL
            file_response = requests.get(file_url)

            filename = href.split('/')[-1]
            filename = filename.split('.htm')[0] + '.htm'# Extract the filename from the URL

            date = dparser.parse(filename, fuzzy=True,dayfirst=False)
            month = date.month
            year = date.year
            filepath = os.path.join(directory, f'minutes_{year}{month:02d}.html')
            with open(filepath, 'wb') as file:
                file.write(file_response.content)
        elif ('minutes' in href or 'MINUTES' in href or 'histmin' in href or 'moa' in href) and (href.endswith('.pdf')):
            file_url = base_url + href  # Construct the complete URL
            file_response = requests.get(file_url)
            filename = href.split('/')[-1]
            filename = filename.split('.pdf')[0] + '.pdf'# Extract the filename from the URL
            date = dparser.parse(filename, fuzzy=True, dayfirst=False)
            month = date.month
            year = date.year
            filepath = os.path.join(directory, f'minutes_{year}{month:02d}.pdf')
            with open(filepath, 'wb') as file:
                file.write(file_response.content)





