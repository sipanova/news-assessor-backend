from datetime import datetime
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
      "What is the overall sentiment regarding Switzerland? (Very negative, Negative, Neutral, Positive, Very positive)",
      "Which aspect of the natural dimension is discussed? (Nature Dimension not addressed, Landscape/scenery, Geography, Weather/climate, Preserved nature, Nature activities, Other aspect of Nature dimension)",
      "What is the sentiment toward the natural dimension? (Very negative, Negative, Neutral, Positive, Very positive, No Sentiment)",
      "Which aspect of the functional dimension is discussed? (Functional Dimension not addressed, Education system, Science/innovation, Products, Economy, Infrastructure, Politics, Living/working conditions, Security, Other aspect of Functional dimension)",
      "What is the sentiment toward the functional dimension? (Very negative, Negative, Neutral, Positive, Very positive, No Sentiment)",
      "Which aspect of the normative dimension is discussed? (Normative Dimension not addressed, Environmental protection, Freedom/human rights, Civil rights, International engagement, Ethical issues/scandals, Conflict avoidance, Tolerance/openness, Other aspect of Normative dimension)",
      "What is the sentiment toward the normative dimension? (Very negative, Negative, Neutral, Positive, Very positive, No Sentiment)",
      "Which aspect of the cultural dimension is discussed? (Cultural Dimension not addressed, Sports, Food, Cultural offer, Personalities, Traditions, History, Cultural diversity, Other aspect of Culture dimension)",
      "What is the sentiment toward the cultural dimension? (Very negative, Negative, Neutral, Positive, Very positive, No Sentiment)",
      "Does the article contain disinformation? (No disinformation type, False connection, False context, Misleading content, Fabricated content, Manipulated content, Other disinformation type)",
      "What disinformation technique is used, if any? (No disinformation technique, Ad hominem attack, Emotional language, False dichotomies, Incoherence, Scapegoating, Other disinformation technique)",
      "What is the article about in short?"
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


        combined_prompt = f"""
        You are given an article about Switzerland. Read it carefully.

        ARTICLE:
        {article}

        TASK:
        Answer the following multiple-choice questions based only on the information in the article.

        Instructions:
        - Choose **only one** of the options provided for each question.
        - Write only the selected option (e.g., "A", "B", "C", or "D").
        - **Do not** explain your answer.

        QUESTIONS:
        """
        for i, question in enumerate(questions, 1):
            combined_prompt += f"{i}. {question}\n"
        
        # Get response from GPT-4o
        response = llm([HumanMessage(content=combined_prompt)]).content
        
        # Extract answers from the response
        answers = re.findall(r'\d+\.\s(.*)', response)
        
        # Store answers in dataframe
        if len(answers) == len(columns):
            data.loc[index, columns] = answers
    print(f"test_1")
    data_count = len(data)
    print(f"data_count: {data_count}")
    now = datetime.now()
    print(f"now: {now}")
    timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")
    print(f"timestamp: {timestamp}")
    # data.to_json("final_file.json", orient="records", lines=True, force_ascii=False)
    data.to_csv(f"uploads/final_file_GPT-4o_{data_count}_{timestamp}.csv", index=False, encoding='utf-8')
