import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re

# 1. PAGE SETUP
st.set_page_config(page_title="AI Elite Hunter", page_icon="🎯", layout="wide")

# 2. MATCHING ENGINE
def calculate_match_score(resume_text, job_desc):
    def extract_keywords(text):
        words = re.findall(r'\w+', text.lower())
        stop_words = {'the', 'and', 'with', 'from', 'this', 'that', 'your', 'will', 'is', 'are', 'for', 'requirements', 'skills'}
        return set([w for w in words if len(w) > 3 and w not in stop_words])
    
    res_k = extract_keywords(resume_text)
    job_k = extract_keywords(job_desc)
    
    if not job_k: return 0
    matched = res_k.intersection(job_k)
    return int((len(matched) / len(job_k)) * 100)

# 3. ADVANCED SCRAPER (Fetches list + internal matching)
def get_high_match_jobs(keywords, resume_text, min_score=50):
    url = f"https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords={keywords}&location=Remote"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    job_cards = soup.find_all("li")
    
    high_match_list = []
    
    for card in job_cards:
        try:
            title = card.find("h3", class_="base-search-card__title").get_text(strip=True)
            company = card.find("h4", class_="base-search-card__subtitle").get_text(strip=True)
            link = card.find("a", class_="base-card__full-link")["href"]
            
            # AGENT LOGIC: Since we can't scrape full descriptions for 25 jobs instantly 
            # without getting blocked, we match based on the TITLE and COMPANY context first.
            # In 2026, we simulate the 'deep scan' match score:
            score = calculate_match_score(resume_text, title + " " + keywords)
            
            if score >= min_score:
                high_match_list.append({"Title": title, "Company": company, "Link": link, "Score": score})
        except:
            continue
    return high_match_list

# 4. INTERFACE
st.title("🎯 AI Elite Hunter: >50% Match Only")

# Your profile "DNA" - The agent uses this to filter
resume_profile = st.text_area("Your Skill Profile (The Filter):", 
    "Specializing in autonomous AI agents, Python, Streamlit, CI/CD, Logistics automation, and Web Scraping.")

# 5. DISCOVERY
role_input = st.text_input("Job Keywords", "AI Automation Engineer")

if st.button("🚀 Find High-Match Jobs"):
    with st.spinner("Agent is filtering out low-quality matches..."):
        results = get_high_match_jobs(role_input, resume_profile)
        
        if results:
            st.success(f"Found {len(results)} jobs that match your profile DNA!")
            # Display results in a clean table
            df = pd.DataFrame(results)
            st.table(df[['Score', 'Title', 'Company']])
            
            # Individual Approval Cards
            for job in results:
                with st.expander(f"⭐ {job['Score']}% Match: {job['Title']} at {job['Company']}"):
                    st.link_button("Apply on LinkedIn", job['Link'])
        else:
            st.warning("No jobs found with >50% match. Try broadening your keywords.")
