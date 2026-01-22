import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
import urllib.parse

# 1. PAGE SETUP
st.set_page_config(page_title="AI Elite Hunter", page_icon="🎯", layout="wide")

# 2. MATCHING LOGIC
def calculate_match_score(resume_text, job_title, keywords):
    def extract_keywords(text):
        words = re.findall(r'\w+', text.lower())
        stop_words = {'the', 'and', 'with', 'from', 'this', 'that', 'your', 'will', 'is', 'are', 'for', 'requirements', 'skills'}
        return set([w for w in words if len(w) > 3 and w not in stop_words])
    
    res_k = extract_keywords(resume_text)
    job_k = extract_keywords(f"{job_title} {keywords}")
    
    if not job_k: return 0
    matched = res_k.intersection(job_k)
    return int((len(matched) / len(job_k)) * 100)

# 3. SCRAPER ENGINE
def get_high_match_jobs(keywords, resume_text, min_score=50):
    # LinkedIn Guest API
    url = f"https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords={urllib.parse.quote(keywords)}&location=Remote"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        job_cards = soup.find_all("li")
        
        high_match_list = []
        for card in job_cards:
            try:
                title = card.find("h3", class_="base-search-card__title").get_text(strip=True)
                company = card.find("h4", class_="base-search-card__subtitle").get_text(strip=True)
                link = card.find("a", class_="base-card__full-link")["href"].split('?')[0] # Clean URL
                
                score = calculate_match_score(resume_text, title, keywords)
                
                if score >= min_score:
                    high_match_list.append({"Title": title, "Company": company, "Link": link, "Score": score})
            except: continue
        return high_match_list
    except Exception as e:
        st.error(f"Scraper Error: {e}")
        return []

# 4. INTERFACE
st.title("🚀 AI Elite Auto-Hunter")
st.markdown("##### Agent Strategy: Scrape → Match >50% → One-Click Apply")

# Profile Input (Your "DNA")
if 'resume_profile' not in st.session_state:
    st.session_state.resume_profile = "AI Automation, Python, Streamlit, CI/CD, Logistics, Web Scraping, Autonomous Agents"

resume_input = st.text_area("Your Skills DNA:", st.session_state.resume_profile, height=100)

# Search Controls
col_a, col_b = st.columns([3, 1])
with col_a:
    role_input = st.text_input("Job Keywords", "AI Automation Engineer")
with col_b:
    min_match = st.slider("Min Match %", 0, 100, 50)

if st.button("🔍 Run Autonomous Scout"):
    with st.spinner("Agent is scanning LinkedIn for >50% matches..."):
        st.session_state.results = get_high_match_jobs(role_input, resume_input, min_match)

# 5. RESULTS & SEMI-AUTO APPLY
if 'results' in st.session_state and st.session_state.results:
    st.success(f"Found {len(st.session_state.results)} High-Match Opportunities!")
    
    for idx, job in enumerate(st.session_state.results):
        with st.expander(f"⭐ {job['Score']}% Match | {job['Title']} at {job['Company']}"):
            
            # The custom message
            msg = f"Hi, I noticed the {job['Title']} role. My profile is a {job['Score']}% match. I've built 3 AI agents (Logistics, TikTok, and this ATS Hunter). Check my live portfolio here: [YOUR_PORTFOLIO_LINK]"
            
            st.write("📋 **Step 1: Copy this message** (Click the icon on the top right of the box below)")
            st.code(msg, language="text") 
            
            st.write("🚀 **Step 2: Apply**")
            st.link_button("Open LinkedIn Job Page", job['Link'])
            
            st.caption("Once LinkedIn opens, just press Ctrl+V to paste your message.")
