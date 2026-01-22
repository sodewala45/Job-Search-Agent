import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re

# 1. PAGE SETUP
st.set_page_config(page_title="AI Auto-Hunter", page_icon="🤖", layout="wide")

# 2. THE "SECRET DOOR" SCRAPER
def scrape_linkedin_jobs(keywords, location="Remote"):
    # Using LinkedIn's guest search API (No login required)
    url = f"https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords={keywords}&location={location}&start=0"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    }
    
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    job_cards = soup.find_all("li")
    
    job_list = []
    for card in job_cards:
        try:
            title = card.find("h3", class_="base-search-card__title").get_text(strip=True)
            company = card.find("h4", class_="base-search-card__subtitle").get_text(strip=True)
            link = card.find("a", class_="base-card__full-link")["href"]
            job_list.append({"Title": title, "Company": company, "Link": link})
        except:
            continue
    return job_list

# 3. INTERFACE
st.title("🤖 AI Auto-Hunter: Autonomous Job Discovery")
st.markdown("##### The agent will find jobs, you just click 'Approve'.")

# 4. DISCOVERY SIDEBAR
with st.sidebar:
    st.header("Search Parameters")
    role = st.text_input("Target Role", "Python AI Automation")
    loc = st.text_input("Location", "Remote")
    
    if st.button("🚀 Find New Jobs Now"):
        with st.spinner("Agent is scouting LinkedIn..."):
            st.session_state.found_jobs = scrape_linkedin_jobs(role, loc)
            st.success(f"Found {len(st.session_state.found_jobs)} opportunities!")

# 5. APPROVAL QUEUE
if 'found_jobs' in st.session_state and st.session_state.found_jobs:
    st.subheader("📋 Pending Approval Queue")
    
    for idx, job in enumerate(st.session_state.found_jobs):
        with st.container():
            c1, c2, c3 = st.columns([3, 2, 1])
            with c1:
                st.write(f"**{job['Title']}**")
                st.caption(f"Company: {job['Company']}")
            with c2:
                st.link_button("View Original Post", job['Link'])
            with c3:
                # Once approved, this will generate the custom DM
                if st.button("Approve & Draft", key=f"app_{idx}"):
                    st.session_state.selected_job = job
                    st.toast("Job Approved! Preparing Outreach...")

# 6. AUTO-DRAFT SECTION
if 'selected_job' in st.session_state:
    st.divider()
    st.subheader(f"✨ Custom Outreach for {st.session_state.selected_job['Title']}")
    
    # Logic: Mentions your specific agents (Logistics/TikTok)
    custom_dm = f"""
Hi Hiring Manager at {st.session_state.selected_job['Company']},

I noticed your opening for the {st.session_state.selected_job['Title']} role. I've built and deployed a suite of autonomous agents, including a Logistics Optimizer and a TikTok Lead Generator, using Python and CI/CD.

I’d love to show you how I can automate workflows for your team. Here is my live portfolio: [YOUR PORTFOLIO LINK]
    """
    st.text_area("Copy this to LinkedIn Message:", custom_dm, height=200)
    st.info("💡 Next Step: Open the 'View Original Post' link and paste this message to the recruiter.")
