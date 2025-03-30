import os
import re
from newspaper import Article
import pandas as pd
import unicodedata
import ftfy


def is_valid_email(email: str) -> bool:
    """Validate email format using regex."""
    email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(email_pattern, email) is not None

def clean_text(text):
    if not text or not text.strip():  # Check for None, empty, or whitespace-only input
        return text  # Return as is (or return an empty string if preferred)
    
    # Fix text encoding issues
    text = ftfy.fix_text(text)
    
    # Normalize unicode characters (e.g., fix apostrophes, ellipses, etc.)
    text = unicodedata.normalize("NFC", text)
    
    return text

def extract_article(url):
    article = Article(url)
    article.download()
    article.parse()
    return article.title, article.text


def data_pre_processing(folder_name, filename):
    file_location = os.path.join(folder_name, filename)
    data_v1 = pd.read_csv(file_location)
    data_v2 = data_v1[['url', 'title', 'content', 'lang']]

    exception_counter = 0
    for index, entity in data_v2.iterrows():
        try:
            title, content = extract_article(entity['url'])
            data_v2.at[index, "extracted_title"] = clean_text(title)
            data_v2.at[index, "extracted_content"] = clean_text(content)
            data_v2.at[index, "title"] = clean_text(data_v2.at[index, "title"])
            data_v2.at[index, "content"] = clean_text(data_v2.at[index, "content"])
            data_v2.at[index, "content_extracted"] = True
            data_v2.at[index, "error"] = ""
        except Exception as e:
            exception_counter += 1
            # print(f"Error processing row {index}: {e}")
            # print(f"URL: {entity['url']}")
            data_v2.at[index, "content_extracted"] = False
            data_v2.at[index, "error"] = f"{e}"
            # print(f'----------------------------------------------------------------')

    print(f"Number of exceptions: {exception_counter}/{len(data_v2)}")
    print(f"% of exceptions: {exception_counter*100/len(data_v2)} %")

    data_v2.to_json(f"{folder_name}/processed_data.json", orient="records", lines=True, force_ascii=False)