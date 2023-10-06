import requests
from bs4 import BeautifulSoup
import pandas as pd
import math


def scrape_description(job_url):
    """
    This function scrapes the job desciption and requirements.
    Args: url of the job web page
    Returns: job description
    """
    job_response = requests.get(job_url)
    # Check if the web page exists
    if job_response.status_code == 200:
        job_src = job_response.text
        job_soup = BeautifulSoup(job_src, 'lxml')
        
        # Find job description
        desc_div = job_soup.find('h2', string='Job Description').find_next('div', class_='t-break')
        job_desc = ''
        if desc_div:
            desc = [item.text.strip() for item in desc_div]
            job_desc = ' '.join(desc)
        
        # Find skills
        skills_divs = job_soup.find_all('div', class_='card-content')
        skills_desc = ''
        for card in skills_divs:
            if card.find_next('h2', string='Skills'):
                skills_items = card.find_all(['p', 'li'])
                if skills_items:
                    skills = [item.text.strip() for item in skills_items]
                    skills_desc = ' '.join(skills)
        
        # Add skills to job_desc if job_desc already has content
        if job_desc:
            job_desc += ' ' + skills_desc
        else:
            job_desc = skills_desc
        
        # Parse job description and skills
        desc_soup = BeautifulSoup(job_desc, 'lxml')
        return desc_soup
    
    else:
        print('HTTP request failed.')


def scrape_job(search):
    """
    This function iterates over every page of a job search and extracts info from each job posting.
    Args: job search
    Returns: a nested list with each sublist containing info about a job posting
    """
    rows = []
    pages_num = num_of_pages(search)
    search = search.replace(' ', '-')
    base_url = f'https://www.bayt.com/en/egypt/jobs/{search}-jobs'
    base_response = requests.get(base_url)
    if base_response.status_code == 200:
        base_src = base_response.text
        base_soup = BeautifulSoup(base_src, 'lxml')
        # Get the total number of jobs and divide it by the maximum number of jobs listed in each page and round up
        jobs_num = base_soup.find('div', class_='col p0').text[1:-12]
        pages_num = math.ceil(int(jobs_num) / 20)
    else:
        print('HTTP request failed.')
    
    for page_num in range(1, pages_num+1):
        page_url = f'https://www.bayt.com/en/egypt/jobs/{search}-jobs/?page={page_num}'
        page_response = requests.get(page_url)
        if page_response.status_code == 200:
            page_src = page_response.text
            page_soup = BeautifulSoup(page_src, 'lxml')
            cards = page_soup.find_all('li', class_='has-pointer-d')
            for card in cards:
                row = []
                job_path = card.find('a', href=True)['href']
                job_url = f'https://www.bayt.com{job_path}'
                job_title = card.find('a').text[1:-1]
                company = card.find('b', class_='jb-company').text
                location = card.find('span', class_='jb-loc').text
                desc_soup = scrape_description(job_url)
                if desc_soup.find('p'):  # Get the text of each paragraph in  the soup
                    for paragraph in desc_soup.find('p'):
                        job_desc = paragraph.text
                # Add the extracted info to row (each job)
                row.append(job_url)
                row.append(job_title)
                row.append(company)
                row.append(location)
                row.append(job_desc)
                # Then add row to rows (all jobs)
                rows.append(row)
        else:
            print('HTTP request failed.')
    return rows


columns = ['job_url', 'job_title', 'company', 'location', 'job_desc']


da_search = 'data analysis'
da_rows = scrape_job(da_search)
da_df = pd.DataFrame(da_rows, columns=columns)


ds_search = 'data science'
ds_rows = scrape_job(ds_search)
ds_df = pd.DataFrame(ds_rows, columns=columns)


de_search = 'data engineer'
de_rows = scrape_job(de_search)
de_df = pd.DataFrame(de_rows, columns=columns)


ml_search = 'machine learning'
ml_rows = scrape_job(ml_search)
ml_df = pd.DataFrame(ml_rows, columns=columns)


data = [de_df, ds_df, da_df, ml_df]
jobs_df = pd.concat(data, axis=0)
jobs_df.to_csv('jobs_df.csv', index=False)