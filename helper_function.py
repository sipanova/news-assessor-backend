import os
import re
import time
from newspaper import Article
import pandas as pd
import unicodedata
import ftfy
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage
# from vllm import LLM, SamplingParams


def print_line():
    print("----------------------------------------------------")

def calcuate_execution_time(start_time):
    end_time = time.time()
    processing_time = time.strftime('%H:%M:%S', time.gmtime(time.time() - start_time))
    print(f"Processing time: {processing_time}")
    
def is_valid_email(email: str) -> bool:
    """Validate email format using regex."""
    email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(email_pattern, email) is not None

def clean_text(text):
    if not text or not text.strip():  
        return text  
    
    text = ftfy.fix_text(text)
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

    data_v2 = data_v1[['url', 'title', 'content', 'lang', 'post_type']].copy()

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
            data_v2.at[index, "content_extracted"] = False
            data_v2.at[index, "error"] = f"{e}"

    print(f"Number of exceptions: {exception_counter}/{len(data_v2)}")
    print(f"% of exceptions: {exception_counter*100/len(data_v2)} %")
    data_v2.to_json(f"{folder_name}/processed_data.json", orient="records", lines=True, force_ascii=False)

def process_by_llama_mini():
    pass

def process_by_gpt_4o(folder_name, filename):
    llm = ChatOpenAI(model_name="gpt-4o", temperature=0.7)
    file_location = "uploads/processed_data.json"

    # Load the JSON data into a DataFrame
    data = pd.read_json(file_location, orient="records", lines=True)

    # Define question list
    questions = [
        "Regarding Switzerland, what is the overall sentiment among the following possible answers (Very negative, Negative, Neutral, Positive, or Very positive, No sentiment)? Please do not provide explanation.",
        
        "Regarding nature dimension in Switzerland, what is the article about among the following possible answers (Nature Dimension not addressed, Landscape/scenery, Geography, Weather/climate, Preserved nature, Nature activities, Other aspect of Nature dimension)? Please do not provide explanation.",
        "Regarding nature dimension in Switzerland, what is the sentiment among the following possible answers (Very negative, Negative, Neutral, Positive, Very positive, No sentiment)? Please do not provide explanation.",
        
        "Regarding functional dimension in Switzerland, what is the article about among the following possible answers (Functional Dimension not addressed, Education system, Science/innovation, Products, Economy, Infrastructure, Politics, Living/working conditions, Security, Other aspect of Functional dimension)? Please do not provide explanation.",
        "Regarding functional dimension in Switzerland, what is the sentiment among the following possible answers (Very negative, Negative, Neutral, Positive, Very positive, No sentiment)? Please do not provide explanation.",
        
        "Regarding normative dimension in Switzerland, what is the article about among the following possible answers (Normative Dimension not addressed, Environmental protection, Freedom/human rights, Civil rights, International engagement, Ethical issues/scandals, Conflict avoidance, Tolerance/openness, Other aspect of Normative dimension)? Please do not provide explanation.",
        "Regarding normative dimension in Switzerland, what is the sentiment among the following possible answers (Very negative, Negative, Neutral, Positive, Very positive, No sentiment)? Please do not provide explanation.",
        
        "Regarding cultural dimension in Switzerland, what is the article about among the following possible answers (Cultural Dimension not addressed, Sports, Food, Cultural offer, Personalities, Traditions, History, Cultural diversity, Other aspect of Culture dimension)? Please do not provide explanation.",
        "Regarding cultural dimension in Switzerland, what is the sentiment among the following possible answers (Very negative, Negative, Neutral, Positive, Very positive, No sentiment)? Please do not provide explanation.",

        "Among the following possible answers (No disinformation type, False connection, False context, Misleading content, Fabricated content, Manipulated content, Other disinformation type), is there disinformation in the article?",
        "Among the following possible answers (No disinformation technique, Ad hominem attack, Emotional language, False dichotomies, Incoherence, Scapegoating, Other disinformation technique), what is the disinformation technique that is used if any?",
        
        "What is it about in short?"
    ]

    data['article_source'] = ''

    # Define column names to store results
    columns = [
        'overall_sentiment', 'nature_dimension', 'nature_sentiment', 'functional_dimension', 'functional_sentiment',
        'normative_dimension', 'normative_sentiment', 'cultural_dimension', 'cultural_sentiment',
        'disinformation_type', 'disinformation_technique', 'summary'
    ]

    # Initialize empty columns
    for col in columns:
        data[col] = ''

    # Process each article
    for index, row in data.iterrows():
        if (not row['content_extracted']) or row['extracted_content'] == "" or len(row['content']) > len(row['extracted_content']):
            article = row['content']
            data.at[index, 'article_source'] = 'content'
        else:
            article = row['extracted_content']
            data.at[index, 'article_source'] = 'extracted_content'


        combined_prompt = f"Based on the following article, answer the questions:\n\nArticle: {article}\n\n"
        for i, question in enumerate(questions, 1):
            combined_prompt += f"{i}. {question}\n"
        
        # Get response from GPT-4o
        response = llm([HumanMessage(content=combined_prompt)]).content
        
        # Extract answers from the response
        answers = re.findall(r'\d+\.\s(.*)', response)
        
        # Store answers in dataframe
        if len(answers) == len(columns):
            data.loc[index, columns] = answers

    # data.to_json("final_file.json", orient="records", lines=True, force_ascii=False)
    data.to_csv("uploads/final_file.csv", index=False, encoding='utf-8')
