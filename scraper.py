import requests
import serpapi
from datetime import datetime, timedelta
import pandas as pd
import logging
from bs4 import BeautifulSoup
import json

logging.basicConfig(level=logging.INFO)
positions_list = [
    "AI engineer",
    "Gen AI engineer", 
    "AI developer",
    "gen AI developer",
    "ML engineer",
    "Machine learning engineer",
    "Computer Vision engineer",
    "Computer Vision developer",
    "NLP developer",
    "NLP engineer",
    "Junior AI developer",
    # Related positions
    "Data Scientist",
    "Research Scientist",
    "Machine Learning Researcher",
    "Deep Learning Engineer",
    "AI Research Engineer",
    "Prompt Engineer",
    "MLOps Engineer",
    "AI Product Manager",
    "LLM Engineer",
    "Generative AI Engineer",
    "Computer Vision Researcher",
    "NLP Engineer",
    "Senior AI Engineer",
    "AI/ML Engineer"
]

# Calculate date range: from 2 weeks ago to today
today = datetime.now()
two_weeks_ago = today - timedelta(weeks=2)
date_min = two_weeks_ago.strftime("%m/%d/%Y")
date_max = today.strftime("%m/%d/%Y")

client = serpapi.Client(api_key="75a24421f1ae00dcf65416d10fc9e7177e6b1a1166a3184e39f6dec717d981ed")

positions = pd.DataFrame(columns=['title', 'link', 'about_this_result'])

for position in positions_list:

    logging.info(f"Searching for: {position}")

    try:
          
      results = client.search({
        "engine": "google",
        "google_domain": "google.com",
        "q": f"site:ashbyhq.com \\\"{position}\\\" location:\"United States\"",
        "gl": "us",
        "hl": "en",
        "tbs": f"cdr:1,cd_min:{date_min},cd_max:{date_max}"
      })
      
      positions = pd.concat([positions, pd.DataFrame(results['organic_results'])[['title', 'link', 'about_this_result']]], ignore_index=True)

    except Exception as e:
      logging.error(f"Unexpected error for {position}: {e}")

logging.info(f"Total positions found: {len(positions)}")

def extract_job_description(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        data = json.loads(soup.find("script").string)
        location = data.get('jobLocation', {}).get('address', {})
        country = location.get('addressCountry')
        job_description = soup.find_all('meta', attrs={'name': 'description'})[0]['content']
        return country, job_description
    except Exception as e:
        logging.error(f"Error extracting job description from {url}: {e}")
        return "", ""
    
positions['country'] = positions['link'].apply(lambda url: extract_job_description(url)[0])
positions['job_description'] = positions['link'].apply(lambda url: extract_job_description(url)[1])
positions.dropna(inplace=True)
positions.to_csv("positions_with_descriptions.csv", index=False)