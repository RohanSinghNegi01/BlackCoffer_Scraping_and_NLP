import pandas as pd
import requests
from bs4 import BeautifulSoup
import os

# Load the Excel file
df = pd.read_excel("Input.xlsx")

output_dir = r'C:\Users\ROHAN\Desktop\NLP\URL_ID'
os.makedirs(output_dir, exist_ok=True)
# Function to extract article title and text from a given URL
def extract_article_text(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract the article title and body text
            title = soup.find('h1') or soup.find('title')
            title_text = title.get_text(strip=True) if title else 'No Title'

            article_body = soup.find('article')
            if article_body:
                paragraphs = article_body.find_all('p')
            else:
                # Fallback: try to find all paragraphs (not inside an 'article' tag)
                paragraphs = soup.find_all('p')

            article_text = '\n'.join(paragraph.get_text(strip=True) for paragraph in paragraphs)

            return f"{title_text}\n\n{article_text}"
        else:
            return None
    except Exception as e:
        print(f"Failed to extract {url}: {e}")
        return None

# Iterate through the DataFrame rows
for index, row in df.iterrows():
    url_id = row['URL_ID']
    url = row['URL']

    # Extract the article text
    article_text = extract_article_text(url)

    if article_text:
        file_path = os.path.join(output_dir, f"{url_id}.txt")
        # Save the extracted text to a .txt file named after the URL_ID
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(article_text)
        print(f"Extracted and saved article {url_id}")
    else:
        print(f"Failed to extract or save article {url_id}")
