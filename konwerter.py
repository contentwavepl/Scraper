import os
import requests
from bs4 import BeautifulSoup
import json

def convert_html_to_wordpress_posts(folder_path, wordpress_url, wordpress_username, wordpress_password):
    for root, directories, files in os.walk(folder_path):
        for file in files:
            if file.endswith('.html'):
                file_path = os.path.join(root, file)
                if "AfterMarket.pl" not in file_path:
                    convert_single_html_to_wordpress_post(file_path, wordpress_url, wordpress_username, wordpress_password)

def convert_single_html_to_wordpress_post(html_file, wordpress_url, wordpress_username, wordpress_password):
    with open(html_file, 'r') as file:
        html_content = file.read()

    soup = BeautifulSoup(html_content, 'html.parser')
    title_element = soup.find('title')

    if title_element is not None and title_element.text.strip():
        title = title_element.text.strip()
    else:
        title = "Domyślny tytuł"

    if "AfterMarket.pl" not in title:
        article_content = soup.find('div', class_='articleContent')

        if article_content is not None:
            content = str(article_content)
        else:
            content = ""

        category_element = soup.find(class_='category-name')
        if category_element is not None:
            category_name = category_element.find('a').text.strip()
            category_id = create_category(category_name, wordpress_url, wordpress_username, wordpress_password)
        else:
            category_id = None

        post_data = {
            'title': title,
            'content': content,
            'categories': [category_id] if category_id else []  # Dodawanie identyfikatora kategorii do słownika post_data
        }

        response = requests.post(
            f'{wordpress_url}/wp-json/wp/v2/posts',
            auth=(wordpress_username, wordpress_password),
            headers={'Content-Type': 'application/json'},
            data=json.dumps(post_data)
        )

        if response.status_code == 201:
            print(f"Przekonwertowano plik {html_file} na post WordPressa.")
        else:
            print(f"Błąd podczas przekształcania pliku {html_file}: {response.text}")
    else:
        print(f"Plik {html_file} zostaje pominięty ze względu na wyraz 'AfterMarket.pl' w tytule.")



def create_category(category_name, wordpress_url, wordpress_username, wordpress_password):
    category_data = {
        'name': category_name,
        'slug': category_name.lower(),  # Użyj nazwy kategorii jako slug
        'description': '',
        'parent': 0  # Identyfikator rodzica - 0 oznacza brak rodzica (główna kategoria)
    }

    response = requests.post(
        f'{wordpress_url}/wp-json/wp/v2/categories',
        auth=(wordpress_username, wordpress_password),
        headers={'Content-Type': 'application/json'},
        data=json.dumps(category_data)
    )

    if response.status_code == 201:
        category = response.json()
        category_id = category['id']
        print(f"Utworzono nową kategorię o nazwie '{category_name}' z identyfikatorem {category_id}.")
        return category_id
    else:
        print(f"Błąd podczas tworzenia kategorii '{category_name}': {response.text}")
        return None




# Przykładowe użycie
folder_path = 'wirtualnyhel.pl/'
wordpress_url = 'https://artur.host346314.xce.pl'  # Adres URL strony WordPress
wordpress_username = 'admin'
wordpress_password = 'PCBf Q2cg 2rSw 5eiU hawC W186'

convert_html_to_wordpress_posts(folder_path, wordpress_url, wordpress_username, wordpress_password)
