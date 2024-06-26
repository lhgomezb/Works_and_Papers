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
import re
import PyPDF2
import spacy
import os
from PyPDF2 import PdfReader

##REMOVE FUNCTIONS FOR HTML FILES
def remove_headers(section):
    headers = section.find_all(['a','h1', 'h2', 'h3', 'h4', 'h5', 'h6','img'])
    for header in headers:
        header.decompose()
    # Get the modified HTML without headers
    html_without_headers = section
    return html_without_headers

def remove_class_elements(section):
    # Find and remove all header elements
    class_elements = section.find_all(class_=['attendees','committee','footnotes'])
    for element in class_elements:
        element.decompose()
    # Get the modified HTML without headers
    html_without_class_elements = section
    return html_without_class_elements

def remove_footer(section):
    # Find and remove all header elements
    footers = section.find_all('div',id='footer')
    for footer in footers:
        footer.decompose()
    # Get the modified HTML without headers
    html_without_footer = section
    return html_without_footer

def remove_irrelevant_info(section):
    # Parse the HTML content
    section_without_headers = remove_headers(section)
    section_without_class_elements = remove_class_elements(section_without_headers)
    section_relevant = remove_footer(section_without_class_elements)
    return section_relevant

def extract_minutes_body_section(filepath):
    html_file = open(filepath)
    contents = html_file.read()
    soup = BeautifulSoup(contents, 'html.parser')
    corpus_section = soup.find('div', id='article')
    if corpus_section == None:
        corpus_section = soup.find('div', id='content')
        if corpus_section == None:
            corpus_section = soup.find('table', celpadding='5')
            if corpus_section == None:
                corpus_section = soup.find('table', cellpadding='5')

    return corpus_section

##REMOVE FUNCTIONS FOR PDF FILES

def remove_headers(page_text):
    # Filter Headings
    # Remove quotes and periods
    page_text = re.sub(r'[\'"]', '', page_text)
    header_pattern = r'^\s*(?:[A-Z\d\s]*[A-Z][A-Z\d\s]*\s?\.\s?\d*[A-Z\d\s]*)\s*$'
    page_text = re.sub(header_pattern, '', page_text, flags=re.MULTILINE)

    # Remove standalone dates
    date_pattern = r'^\d{1,2}/\d{1,2}/\d{2,4}$'
    page_text = re.sub(date_pattern, '', page_text, flags=re.MULTILINE)

    return page_text


def remove_person_names(text):
    # Load the model in english from spaCy
    nlp = spacy.load('en_core_web_sm')

    # Analyze the text with spaCy
    doc = nlp(text)

    # Create a filtered text without persons' names.
    filtered_text = ''
    for token in doc:
        if token.ent_type_ != 'PERSON':  # Filtrar solo los tokens que no son nombres de personas
            filtered_text += token.text_with_ws

    return filtered_text


def remove_lines_starting_with_mr(text):
    lines = text.split('\n')
    filtered_lines = [line for line in lines if (not line.startswith('Mr.')) and (not line.startswith('PRESENT'))]
    filtered_text = '\n'.join(filtered_lines)
    return filtered_text


def remove_overindented_lines_after_subtitle(text):
    filtered_text = re.sub(r'(PRESENT.*?\n)([ \t]+.*?\n)+', r'\1', text)
    return filtered_text


def extract_text_from_pdf(file_path):
    with open(file_path, 'rb') as file:
        pdf = PdfReader(file)

        # Extraer el texto de todas las páginas del PDF
        text = ''
        for page in pdf.pages:
            text += page.extract_text()
    text = remove_lines_starting_with_mr(text)
    text = remove_headers(text)
    text = remove_person_names(text)
    return text


def save_text_to_file(text, output_file):
    with open(output_file, 'w', encoding='utf-8') as file:
        file.write(text)


for year in range(1936, 2018):

    for month in range(1, 13):
        directory = f'C:/Users/LUIS/Documents/Fed Minutes'
        text_filepath = f'C:/Users/LUIS/Documents/Fed Minutes Corpus/minutes_{year}{month:02d}.txt'
        try:
            filepath = os.path.join(directory, f'minutes_{year}{month:02d}.html')
            section = extract_minutes_body_section(filepath)
            section_clean = remove_irrelevant_info(section)
            corpus_section_text = section_clean.text
            with open(text_filepath, 'w') as file:
                file.write(corpus_section_text)
        except:
            try:
                filepath = os.path.join(directory, f'minutes_{year}{month:02d}.pdf')
                corpus_section_text = extract_text_from_pdf(filepath)
                save_text_to_file(corpus_section_text, text_filepath)
            except:
                continue

2 + 2