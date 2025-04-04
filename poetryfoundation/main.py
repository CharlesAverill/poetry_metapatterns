import pandas as pd
import requests
from bs4 import BeautifulSoup
import wikipedia
import re
import time
from tqdm import tqdm
import os
from urllib.parse import quote
import sys
import argparse

# Configure requests and Wikipedia
requests.packages.urllib3.disable_warnings()
user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
headers = {'User-Agent': user_agent}
session = requests.Session()
wikipedia.set_rate_limiting(True)

# Create caches to avoid redundant searches
poet_location_cache = {}
poet_birth_year_cache = {}

def clean_text(text):
    if not text:
        return ""
    text = re.sub(r'\s+', ' ', text).strip()
    text = re.sub(r'<[^>]*>', '', text)
    return text

def extract_year(text):
    if not text:
        return None
    
    # Look for birth year patterns
    # Pattern like "born YYYY"
    born_year = re.search(r'born\s+in\s+(\d{4})', text, re.IGNORECASE)
    if born_year:
        return born_year.group(1)
    
    # Pattern like "born Month Day, YYYY"
    born_date = re.search(r'born\s+[a-zA-Z]+\s+\d{1,2}(st|nd|rd|th)?\s*,\s*(\d{4})', text, re.IGNORECASE)
    if born_date:
        return born_date.group(2)
    
    # Pattern like "YYYY-YYYY" (birth-death years)
    years_range = re.search(r'\((\d{4})\s*[-–—]\s*\d{4}\)', text)
    if years_range:
        return years_range.group(1)
    
    # Pattern like "(YYYY-)" (birth year only)
    birth_only = re.search(r'\((\d{4})\s*[-–—]\s*\)', text)
    if birth_only:
        return birth_only.group(1)
    
    # Simple 4 digit year as fallback
    year = re.search(r'\b(1[7-9]\d{2}|20[0-2]\d)\b', text)
    if year:
        y = int(year.group(1))
        # Only accept years between 1700 and current year that are likely birth years
        if 1700 <= y <= 2023:
            return year.group(1)
    
    return None

def clean_location(raw_location):
    if not raw_location:
        return ""
        
    if "modern day bangladesh" in raw_location.lower() or "what is now" in raw_location.lower():
        match = re.search(r'(modern\s*day|what\s*is\s*now)\s+(\w+)', raw_location, re.IGNORECASE)
        if match:
            return match.group(2).capitalize()
    
    if "wilton, new hampshire" in raw_location.lower() and "july" in raw_location.lower():
        return "Wilton, New Hampshire"
    
    location = re.sub(r'\(.*?\)', '', raw_location).strip()
    
    location = re.sub(r'\d{1,2}(st|nd|rd|th)?\s+(of\s+)?(january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{2,4}', '', location, flags=re.IGNORECASE).strip()
    location = re.sub(r'\b\d{1,2}\s+(january|february|march|april|may|june|july|august|september|october|november|december)(\s+\d{2,4})?\b', '', location, flags=re.IGNORECASE).strip()
    location = re.sub(r'(january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{1,2}(st|nd|rd|th)?(\s*,\s*\d{2,4})?', '', location, flags=re.IGNORECASE).strip()
    
    location = re.sub(r'\b\d{4}\b', '', location).strip()
    location = re.sub(r'\b\d{1,2}/\d{1,2}(/\d{2,4})?\b', '', location).strip()
    
    location = re.sub(r'^(what is|what was|now|currently|modern day|modern|present day|present)\s+', '', location, flags=re.IGNORECASE).strip()
    
    location = re.sub(r'\s*,\s*was\s+.*$', '', location).strip()
    location = re.sub(r'\s+and\s+was\s+.*$', '', location).strip()
    location = re.sub(r'\s+where\s+.*$', '', location).strip()
    location = re.sub(r'\s+was\s+officially\s+appointed\s+.*$', '', location).strip()
    
    comma_parts = location.split(',')
    if len(comma_parts) > 1:
        if len(comma_parts) == 2 and len(comma_parts[1].strip().split()) <= 3:
            location = f"{comma_parts[0].strip()}, {comma_parts[1].strip()}"
        elif len(comma_parts) >= 3:
            filtered_parts = []
            for part in comma_parts:
                part = part.strip()
                if re.search(r'\b(january|february|march|april|may|june|july|august|september|october|november|december)\b', part, re.IGNORECASE) or \
                   re.search(r'\b\d{1,2}(st|nd|rd|th)?\b', part) or \
                   re.search(r'was\s+officially', part, re.IGNORECASE) or \
                   len(part.strip()) < 2:
                    continue
                filtered_parts.append(part)
            if filtered_parts:
                location = ', '.join(filtered_parts)
    
    location = re.sub(r'^(in|at|on|near|from|of|the)\s+', '', location, flags=re.IGNORECASE).strip()
    location = re.sub(r'\s+(in|at|on|near|from|of)$', '', location, flags=re.IGNORECASE).strip()
    
    location = re.sub(r'\s+in\s+\w+$', '', location).strip()
    
    countries_regions = [
        'Afghanistan', 'Albania', 'Algeria', 'Andorra', 'Angola', 'Argentina', 'Armenia', 'Australia',
        'Austria', 'Azerbaijan', 'Bahamas', 'Bahrain', 'Bangladesh', 'Barbados', 'Belarus', 'Belgium',
        'Belize', 'Benin', 'Bhutan', 'Bolivia', 'Bosnia', 'Botswana', 'Brazil', 'Brunei', 'Bulgaria',
        'Burkina Faso', 'Burundi', 'Cambodia', 'Cameroon', 'Canada', 'Chad', 'Chile', 'China', 'Colombia',
        'Congo', 'Costa Rica', 'Croatia', 'Cuba', 'Cyprus', 'Denmark', 'Djibouti', 'Dominican Republic',
        'Ecuador', 'Egypt', 'El Salvador', 'England', 'Eritrea', 'Estonia', 'Eswatini', 'Ethiopia',
        'Fiji', 'Finland', 'France', 'Gabon', 'Gambia', 'Georgia', 'Germany', 'Ghana', 'Greece', 'Grenada',
        'Guatemala', 'Guinea', 'Guyana', 'Haiti', 'Honduras', 'Hungary', 'Iceland', 'India', 'Indonesia',
        'Iran', 'Iraq', 'Ireland', 'Israel', 'Italy', 'Jamaica', 'Japan', 'Jordan', 'Kazakhstan', 'Kenya',
        'Kuwait', 'Kyrgyzstan', 'Laos', 'Latvia', 'Lebanon', 'Lesotho', 'Liberia', 'Libya', 'Liechtenstein',
        'Lithuania', 'Luxembourg', 'Madagascar', 'Malawi', 'Malaysia', 'Maldives', 'Mali', 'Malta', 'Mauritania',
        'Mauritius', 'Mexico', 'Moldova', 'Monaco', 'Mongolia', 'Montenegro', 'Morocco', 'Mozambique', 'Myanmar',
        'Namibia', 'Nepal', 'Netherlands', 'New Zealand', 'Nicaragua', 'Niger', 'Nigeria', 'North Korea',
        'Norway', 'Oman', 'Pakistan', 'Palestine', 'Panama', 'Papua New Guinea', 'Paraguay', 'Peru', 'Philippines',
        'Poland', 'Portugal', 'Qatar', 'Romania', 'Russia', 'Rwanda', 'Saudi Arabia', 'Scotland', 'Senegal',
        'Serbia', 'Seychelles', 'Sierra Leone', 'Singapore', 'Slovakia', 'Slovenia', 'Somalia', 'South Africa',
        'South Korea', 'South Sudan', 'Spain', 'Sri Lanka', 'Sudan', 'Suriname', 'Sweden', 'Switzerland', 'Syria',
        'Taiwan', 'Tajikistan', 'Tanzania', 'Thailand', 'Togo', 'Trinidad and Tobago', 'Tunisia', 'Turkey',
        'Turkmenistan', 'Uganda', 'Ukraine', 'United Arab Emirates', 'United Kingdom', 'Uruguay', 'USA', 'United States',
        'Uzbekistan', 'Vatican City', 'Venezuela', 'Vietnam', 'Wales', 'Yemen', 'Zambia', 'Zimbabwe'
    ]
    
    for country in countries_regions:
        if re.search(r'\b' + re.escape(country) + r'\b', location, re.IGNORECASE):
            return country
    
    if not location or len(location) < 2:
        return ""
    
    return location

def get_poet_birth_year_from_poetry_foundation(poet_name):
    try:
        # Search for the poet on Poetry Foundation website
        encoded_name = quote(poet_name)
        search_url = f"https://www.poetryfoundation.org/search?query={encoded_name}"
        print(f"    Searching for '{poet_name}' on Poetry Foundation...")
        response = session.get(search_url, headers=headers, timeout=10, verify=False)
        
        if response.status_code != 200:
            print(f"    Failed to access Poetry Foundation search. Status code: {response.status_code}")
            return None
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find the first search result and get the poet's page URL
        result = soup.find('div', class_='c-feature-hd') or soup.find('div', class_='c-txt-feature-title')
        if result and result.find('a'):
            poet_url = "https://www.poetryfoundation.org" + result.find('a')['href']
            print(f"    Found poet page: {poet_url.split('/')[-1]}")
            
            # Access the poet's page
            poet_response = session.get(poet_url, headers=headers, timeout=10, verify=False)
            if poet_response.status_code != 200:
                print(f"    Failed to access poet page. Status code: {poet_response.status_code}")
                return None
                
            poet_soup = BeautifulSoup(poet_response.text, 'html.parser')
            
            # Look for biography or bio-brief sections which often contain birth year
            bio_section = poet_soup.find('div', class_='c-biography') or poet_soup.find('div', class_='c-feature-sub')
            if bio_section:
                bio_text = clean_text(bio_section.get_text())
                
                # Look for birth year in the biography
                year = extract_year(bio_text)
                if year:
                    print(f"    Found birth year for {poet_name} from Poetry Foundation bio: {year}")
                    return year
                    
        print(f"    Could not extract birth year from Poetry Foundation for {poet_name}")
        return None
        
    except Exception as e:
        print(f"    Error with Poetry Foundation search for {poet_name}: {e}")
        return None

def get_poet_birth_year_from_wikipedia(poet_name):
    try:
        # Search Wikipedia for the poet
        print(f"    Searching Wikipedia for '{poet_name}'...")
        search_results = wikipedia.search(poet_name, results=5)
        
        for result in search_results:
            try:
                # Try to get the page for each result
                print(f"    Checking Wikipedia page: '{result}'")
                
                # Get the page content
                page = wikipedia.page(result, auto_suggest=False)
                wiki_content = page.content
                
                # First check if this page seems to be about a poet
                if not any(term in wiki_content.lower() for term in ['poet', 'poetry', 'poem', 'literary', 'writer', 'author']):
                    print(f"    Wikipedia page for '{result}' doesn't seem to be about a poet. Skipping...")
                    continue
                
                # Check if the summary or content contains the poet's name
                if poet_name.lower() not in page.summary.lower() and poet_name.lower() not in wiki_content.lower():
                    print(f"    Wikipedia page for '{result}' doesn't contain the poet's name. Skipping...")
                    continue
                
                # Look for birth year in the summary (which is more reliable)
                print(f"    Checking summary for birth year...")
                year = extract_year(page.summary)
                if year:
                    print(f"    Found birth year for {poet_name} from Wikipedia summary: {year}")
                    return year
                
                # If not found in summary, look in the content with specific patterns
                print(f"    Checking content for birth year...")
                birth_patterns = [
                    r'\b(born\s+[^,\n]+(,\s+|\s+in\s+)(\d{4}))',
                    r'\(born\s+(\d{4})\)',
                    r'\((\d{4})[-–—]\d{4}\)',
                    r'\((\d{4})[-–—]\)',
                    r'born\s+in\s+(\d{4})'
                ]
                
                for pattern in birth_patterns:
                    match = re.search(pattern, wiki_content, re.IGNORECASE)
                    if match:
                        year = match.group(1)
                        print(f"    Found birth year for {poet_name} from Wikipedia content: {year}")
                        return year
                
                print(f"    Could not extract birth year from Wikipedia for {poet_name}")
                return None
                
            except Exception as e:
                print(f"    Error extracting birth year from Wikipedia: {e}")
                continue
        
        print(f"    No suitable Wikipedia page found for {poet_name}")
        return None
                
    except Exception as e:
        print(f"    Error searching Wikipedia: {e}")
        return None

def get_poet_birth_year(poet_name):
    # Skip empty poet names
    if not poet_name or pd.isna(poet_name) or poet_name.strip() == "":
        print(f"Skipping empty poet name")
        return "Unknown"
    
    # Check cache first
    if poet_name in poet_birth_year_cache:
        print(f"Using cached birth year for '{poet_name}': {poet_birth_year_cache[poet_name]}")
        return poet_birth_year_cache[poet_name]
    
    print(f"\nFinding birth year for: {poet_name}")
    
    # First try Poetry Foundation
    year = get_poet_birth_year_from_poetry_foundation(poet_name)
    if year:
        poet_birth_year_cache[poet_name] = year
        return year
    
    # If not found, try Wikipedia
    year = get_poet_birth_year_from_wikipedia(poet_name)
    if year:
        poet_birth_year_cache[poet_name] = year
        return year
    
    # If still not found, return Unknown
    print(f"Could not find birth year for {poet_name}")
    poet_birth_year_cache[poet_name] = "Unknown"
    return "Unknown"

def get_poet_location_from_poetry_foundation(poet_name):
    try:
        encoded_name = quote(poet_name)
        search_url = f"https://www.poetryfoundation.org/search?query={encoded_name}"
        print(f"Searching for '{poet_name}' on Poetry Foundation...")
        response = session.get(search_url, headers=headers, timeout=10, verify=False)
        
        if response.status_code != 200:
            print(f"Failed to access Poetry Foundation search. Status code: {response.status_code}")
            return None
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        result = soup.find('div', class_='c-feature-hd') or soup.find('div', class_='c-txt-feature-title')
        if result and result.find('a'):
            poet_url = "https://www.poetryfoundation.org" + result.find('a')['href']
            print(f"Found poet page: {poet_url.split('/')[-1]}")
            
            print(f"Waiting 1 second before accessing poet page...")
            time.sleep(1)
            
            print(f"Accessing poet's detailed page...")
            poet_response = session.get(poet_url, headers=headers, timeout=10, verify=False)
            
            if poet_response.status_code != 200:
                print(f"Failed to access poet page. Status code: {poet_response.status_code}")
                return None
                
            poet_soup = BeautifulSoup(poet_response.text, 'html.parser')
            print(f"Analyzing poet's biography for location information...")
            
            bio_elements = [
                poet_soup.find('div', class_='c-feature-sub'),
                poet_soup.find('div', class_='c-txt-bio'), 
                poet_soup.find('div', class_='c-basic-text'),
                poet_soup.find('section', class_='c-profile-section--bio')
            ]
            
            bio_found = False
            for i, bio in enumerate(bio_elements):
                if bio:
                    bio_found = True
                    bio_text = clean_text(bio.get_text().lower())
                    bio_preview = bio_text[:50] + '...' if len(bio_text) > 50 else bio_text
                    print(f"Found biography text ({len(bio_text)} chars): '{bio_preview}'")
                    
                    location_patterns = [
                        r'born in ([^.]+)',
                        r'was born in ([^.]+)',
                        r'born .*? in ([^.]+)',
                        r'from ([^.]+)',
                        r'lives in ([^.]+)',
                        r'lived in ([^.]+)',
                        r'residing in ([^.]+)'
                    ]
                    
                    for pattern in location_patterns:
                        match = re.search(pattern, bio_text)
                        if match:
                            raw_location = match.group(1).strip()
                            print(f"Found location pattern match: '{raw_location}'")
                            
                            location = clean_location(raw_location)
                            
                            if location and len(location) > 1:
                                print(f"Extracted clean location: '{location}'")
                                return location
                            else:
                                print(f"Extracted location was too short or empty after cleaning")
            
            if not bio_found:
                print(f"No biography text found on poet's page")
        else:
            print(f"No poet page found in search results")
                                
    except Exception as e:
        print(f"Error accessing Poetry Foundation: {str(e)[:100]}")
    
    print(f"No location found on Poetry Foundation")
    return None

def get_poet_location_from_wikipedia(poet_name):
    try:
        search_queries = [
            f"{poet_name} poet",
            f"{poet_name} poetry",
            f"{poet_name} writer"
        ]
        
        all_search_results = []
        for query in search_queries:
            results = wikipedia.search(query, results=3)
            all_search_results.extend(results)
        
        seen = set()
        search_results = []
        for result in all_search_results:
            if result not in seen:
                seen.add(result)
                search_results.append(result)
        
        for result in search_results:
            try:
                wiki_page = wikipedia.page(result, auto_suggest=False)
                wiki_content = wiki_page.content.lower()
                wiki_title = wiki_page.title.lower()
                
                poet_indicators = ['poet', 'poetry', 'poem', 'poems', 'verse', 'literary', 'writer', 'author']
                is_poet = False
                
                summary = wiki_page.summary.lower()
                for indicator in poet_indicators:
                    if indicator in summary[:500]:
                        is_poet = True
                        break
                
                if not is_poet:
                    for indicator in poet_indicators:
                        if indicator in wiki_title:
                            is_poet = True
                            break
                
                if not is_poet and ('poet' in wiki_content or 'poetry' in wiki_content):
                    poetry_mentions = wiki_content.count('poet') + wiki_content.count('poetry') + wiki_content.count('poems')
                    if poetry_mentions > 5:
                        is_poet = True
                
                if not is_poet:
                    print(f"Skipping {result} for {poet_name} - not identified as a poet")
                    continue
                
                location_patterns = [
                    r'born[^.,;]*?(?:in|at)\s+([^.,;(\[\]\n]+(?:[.,]\s*[^.,;(\[\]\n]+){0,2})',
                    r'was born[^.,;]*?(?:in|at)\s+([^.,;(\[\]\n]+(?:[.,]\s*[^.,;(\[\]\n]+){0,2})',
                    r'\(born[^)]*?(?:in|at)\s+([^.,;)(\[\]\n]+)'
                ]
                
                for pattern in location_patterns:
                    match = re.search(pattern, wiki_content)
                    if match:
                        location = match.group(1).strip()
                        location = clean_location(location)
                        
                        if location and len(location) > 1 and not location.isdigit():
                            print(f"Found location for {poet_name} from Wikipedia: {location}")
                            return location
                
                for pattern in location_patterns:
                    match = re.search(pattern, summary)
                    if match:
                        location = match.group(1).strip()
                        location = clean_location(location)
                        
                        if location and len(location) > 1 and not location.isdigit():
                            print(f"Found location for {poet_name} from Wikipedia summary: {location}")
                            return location
                
            except Exception as e:
                print(f"Error with Wikipedia page {result} for {poet_name}: {e}")
                continue
    
    except Exception as e:
        print(f"Error with Wikipedia search for {poet_name}: {e}")
    
    return None

def get_poet_location(poet_name):
    if not poet_name or pd.isna(poet_name) or poet_name.strip() == "":
        print(f"Skipping empty poet name")
        return "Unknown"
        
    poet_name = poet_name.strip()
    
    if poet_name in poet_location_cache:
        print(f"Using cached location for '{poet_name}': {poet_location_cache[poet_name]}")
        return poet_location_cache[poet_name]
    
    print(f"\nProcessing poet: '{poet_name}'")
    
    print(f"  Searching Poetry Foundation for '{poet_name}'...")
    location = get_poet_location_from_poetry_foundation(poet_name)
    
    if location:
        print(f"  Found location from Poetry Foundation: '{location}'")
    else:
        print(f"  No location found on Poetry Foundation, trying Wikipedia...")
        location = get_poet_location_from_wikipedia(poet_name)
    
    if not location:
        print(f"  No location found for '{poet_name}'. Marking as 'Unknown'")
        location = "Unknown"
    
    poet_location_cache[poet_name] = location
    return location

def extract_locations(input_file='PoetryFoundationData.csv', output_file='PoetryFoundationData_with_locations.csv', limit=200):
    print("\n" + "="*80)
    print("POETRY LOCATION EXTRACTOR")
    print("="*80)
    
    start_time = time.time()
    
    print("\nLoading Poetry Foundation data...")
    try:
        full_df = pd.read_csv(input_file)
        print(f"Successfully loaded data with {len(full_df)} poems.")
    except Exception as e:
        print(f"Error loading CSV file: {e}")
        return None
    
    limited_rows = min(limit, len(full_df))
    df = full_df.head(limited_rows).copy()
    print(f"\nSCOPE: Processing first {limited_rows} poems out of {len(full_df)} total poems.")
    
    unique_poets = df['Poet'].dropna().unique()
    print(f"Found {len(unique_poets)} unique poets in the limited dataset.")
    
    poet_locations = {}
    
    print("\nPHASE 1: Extracting location data for each poet...")
    print("="*50)
    
    progress_counter = 0
    poets_count = len(unique_poets)
    
    for poet in unique_poets:
        progress_counter += 1
        print(f"\n[{progress_counter}/{poets_count}] Processing: {poet}")
        
        poet_locations[poet] = get_poet_location(poet)
        
        if progress_counter < poets_count:
            print(f"Waiting 0.5 seconds before next poet...")
            time.sleep(0.5)
    
    print("\n" + "="*50)
    print("\nPHASE 2: Mapping poet locations to poems...")
    
    df['location'] = df['Poet'].map(poet_locations).fillna("Unknown")
    
    print("Successfully mapped locations to poems.")
    print("\nPHASE 3: Preparing final dataset...")
    
    result_df = full_df.copy()
    result_df.loc[df.index, 'location'] = df['location']
    
    try:
        result_df.to_csv(output_file, index=False)
        print(f"Successfully saved updated dataset to {output_file}")
    except Exception as e:
        print(f"Error saving CSV file: {e}")
        return None
    
    location_stats = df['location'].value_counts()
    known_locations = limited_rows - location_stats.get("Unknown", 0)
    success_rate = (known_locations/limited_rows*100) if limited_rows > 0 else 0
    
    elapsed_time = time.time() - start_time
    minutes, seconds = divmod(elapsed_time, 60)
    
    print("\n" + "="*80)
    print("RESULTS SUMMARY")
    print("="*80)
    print(f"\nSuccessfully found locations for {known_locations} out of {limited_rows} processed poems ({success_rate:.2f}%)")
    print(f"Total processing time: {int(minutes)} minutes and {int(seconds)} seconds")
    print(f"The remaining {len(full_df) - limited_rows} poems were preserved but not processed.")
    
    print("\nTOP 5 LOCATIONS:")
    for location, count in location_stats.head(5).items():
        print(f"  - {location}: {count} poems")
        
    print("\n" + "="*80)
    print("PROCESS COMPLETED SUCCESSFULLY")
    print("="*80)
    
    return result_df

def extract_birth_years(input_file='PoetryFoundationData_with_locations.csv', output_file='PoetryFoundationData_with_locations_and_years.csv'):
    print("\n" + "="*80)
    print("POETRY BIRTH YEAR EXTRACTOR")
    print("="*80)
    
    start_time = time.time()
    
    # Load the Poetry Foundation data
    print("\nLoading Poetry Foundation data...")
    try:
        poetry_data = pd.read_csv(input_file)
        print(f"Successfully loaded data with {len(poetry_data)} poems.")
    except Exception as e:
        print(f"Error loading CSV file: {e}")
        return None
    
    # Create a backup of the original file
    backup_file = input_file.replace('.csv', '_backup_year.csv')
    poetry_data.to_csv(backup_file, index=False)
    print(f"Created backup at: {backup_file}")
    
    # Add year column if it doesn't exist
    if 'year' not in poetry_data.columns:
        poetry_data['year'] = ""
    
    # Count how many unique poets we need to process
    unique_poets = poetry_data['Poet'].unique()
    print(f"Found {len(unique_poets)} unique poets to process")
    
    # Process all poets to get their birth years
    print("\nStarting birth year extraction...\n")
    for i, poet in enumerate(tqdm(unique_poets, desc="Processing poets")):
        if i % 10 == 0:
            print(f"\n--- Progress: {i}/{len(unique_poets)} poets processed ---\n")
        
        # Get the birth year for this poet
        year = get_poet_birth_year(poet)
        
        # Update all poems by this poet with the found year
        poetry_data.loc[poetry_data['Poet'] == poet, 'year'] = year
        
        # Add a small delay to prevent overwhelming the servers
        time.sleep(0.5)
    
    # Save the updated data
    try:
        poetry_data.to_csv(output_file, index=False)
        print(f"\nSaved updated data with birth years to: {output_file}")
    except Exception as e:
        print(f"Error saving CSV file: {e}")
        return None
    
    # Report on findings
    total_poems = len(poetry_data)
    poems_with_years = len(poetry_data[poetry_data['year'] != "Unknown"])
    year_success_percentage = (poems_with_years / total_poems) * 100 if total_poems > 0 else 0
    
    elapsed_time = time.time() - start_time
    minutes, seconds = divmod(elapsed_time, 60)
    
    print("\n" + "="*80)
    print("RESULTS SUMMARY")
    print("="*80)
    print(f"\nTotal poems processed: {total_poems}")
    print(f"Poems with birth years found: {poems_with_years} ({year_success_percentage:.1f}%)")
    print(f"Poems without birth years: {total_poems - poems_with_years} ({100 - year_success_percentage:.1f}%)")
    print(f"Total processing time: {int(minutes)} minutes and {int(seconds)} seconds")
    
    print("\n" + "="*80)
    print("PROCESS COMPLETED SUCCESSFULLY")
    print("="*80)
    
    return poetry_data

def filter_no_year_poems(input_file='PoetryFoundationData_with_locations_and_years.csv', 
                        output_file='PoetryFoundationData_with_locations_and_years_filtered.csv'):
    print("\n" + "="*80)
    print("FILTER POEMS WITHOUT YEARS")
    print("="*80)
    
    # Load the CSV file with locations and years
    print("\nLoading CSV file with locations and years...")
    try:
        data = pd.read_csv(input_file)
        print(f"Successfully loaded data with {len(data)} poems.")
    except Exception as e:
        print(f"Error loading CSV file: {e}")
        return None

    # Get total number of poems before filtering
    total_before = len(data)
    print(f"Total number of poems before filtering: {total_before}")

    # Identify poems without years
    no_year_poems = data[(data['year'].isna()) | (data['year'] == '') | (data['year'] == 'Unknown')]
    no_year_count = len(no_year_poems)
    print(f"Number of poems without years: {no_year_count}")

    # Remove poems without years
    filtered_data = data[(~data['year'].isna()) & (data['year'] != '') & (data['year'] != 'Unknown')]

    # Get total number of poems after filtering
    total_after = len(filtered_data)
    print(f"Total number of poems after filtering: {total_after}")

    # Create a backup of the original file
    backup_file = input_file.replace('.csv', '_backup.csv')
    data.to_csv(backup_file, index=False)
    print(f"Created backup at: {backup_file}")

    # Save the filtered data to a new file
    try:
        filtered_data.to_csv(output_file, index=False)
        print(f"Saved filtered data to: {output_file}")
    except Exception as e:
        print(f"Error saving CSV file: {e}")
        return None

    # Display year distribution in the filtered data
    year_counts = filtered_data['year'].value_counts().sort_index()
    print("\nYear distribution in filtered data (top 10):")
    for year, count in year_counts.head(10).items():
        print(f"{year}: {count} poems")

    # Display percentage of poems retained
    retention_percentage = (total_after / total_before) * 100 if total_before > 0 else 0
    print(f"\n{total_after} poems remain with years ({retention_percentage:.1f}% of the original dataset)")

    # Show poet statistics
    poets_before = data['Poet'].nunique()
    poets_after = filtered_data['Poet'].nunique()
    print(f"\nPoets with at least one poem before filtering: {poets_before}")
    print(f"Poets with at least one poem after filtering: {poets_after}")
    print(f"Lost {poets_before - poets_after} poets after filtering")

    print("\n" + "="*80)
    print("PROCESS COMPLETED SUCCESSFULLY")
    print("="*80)
    
    return filtered_data

def add_twenty_years(input_file='PoetryFoundationData_with_locations_and_years_filtered.csv', 
                    output_file=None):
    print("\n" + "="*80)
    print("ADD 20 YEARS TO BIRTH YEARS")
    print("="*80)
    
    # Load the CSV file
    print("\nLoading CSV file...")
    try:
        data = pd.read_csv(input_file)
        print(f"Successfully loaded data with {len(data)} poems.")
    except Exception as e:
        print(f"Error loading CSV file: {e}")
        return None

    # Create a backup of the original file
    backup_file = input_file.replace('.csv', '_backup.csv')
    data.to_csv(backup_file, index=False)
    print(f"Created backup at: {backup_file}")

    # Display some statistics before modification
    print("\nBefore adding 20 years:")
    print(f"Earliest year: {data['year'].min()}")
    print(f"Latest year: {data['year'].max()}")
    print(f"Average year: {data['year'].mean():.1f}")

    # Convert the 'year' column to integers, add 20, and convert back to strings
    data['year'] = data['year'].astype(int) + 20

    # Display statistics after modification
    print("\nAfter adding 20 years:")
    print(f"Earliest year: {data['year'].min()}")
    print(f"Latest year: {data['year'].max()}")
    print(f"Average year: {data['year'].mean():.1f}")

    # Save the modified data back to the file
    if output_file is None:
        output_file = input_file
        
    try:
        data.to_csv(output_file, index=False)
        print(f"\nSaved updated data with +20 years to: {output_file}")
    except Exception as e:
        print(f"Error saving CSV file: {e}")
        return None

    # Display a sample of the modified data
    print("\nSample of updated data:")
    sample = data[['Poet', 'location', 'year']].sample(5)
    print(sample)

    # Display year distribution after modification
    year_counts = data['year'].value_counts().sort_index()
    print("\nYear distribution after adding 20 years (top 10):")
    for year, count in year_counts.head(10).items():
        print(f"{year}: {count} poems")
    
    print("\n" + "="*80)
    print("PROCESS COMPLETED SUCCESSFULLY")
    print("="*80)
    
    return data

def main():
    parser = argparse.ArgumentParser(description='Poetry Data Processing Tool')
    parser.add_argument('--action', type=str, choices=['extract_locations', 'extract_years', 'filter_no_years', 'add_20_years', 'all'], 
                        help='Action to perform', required=True)
    parser.add_argument('--input', type=str, help='Input file path')
    parser.add_argument('--output', type=str, help='Output file path')
    parser.add_argument('--limit', type=int, default=200, help='Number of poems to process (for extract_locations)')
    
    # If no arguments were passed, show the help message and exit
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
        
    args = parser.parse_args()
    
    if args.action == 'extract_locations':
        input_file = args.input if args.input else 'PoetryFoundationData.csv'
        output_file = args.output if args.output else 'PoetryFoundationData_with_locations.csv'
        extract_locations(input_file, output_file, args.limit)
        
    elif args.action == 'extract_years':
        input_file = args.input if args.input else 'PoetryFoundationData_with_locations.csv'
        output_file = args.output if args.output else 'PoetryFoundationData_with_locations_and_years.csv'
        extract_birth_years(input_file, output_file)
        
    elif args.action == 'filter_no_years':
        input_file = args.input if args.input else 'PoetryFoundationData_with_locations_and_years.csv'
        output_file = args.output if args.output else 'PoetryFoundationData_with_locations_and_years_filtered.csv'
        filter_no_year_poems(input_file, output_file)
        
    elif args.action == 'add_20_years':
        input_file = args.input if args.input else 'PoetryFoundationData_with_locations_and_years_filtered.csv'
        output_file = args.output if args.output is not None else input_file
        add_twenty_years(input_file, output_file)
        
    elif args.action == 'all':
        print("\n" + "="*80)
        print("RUNNING COMPLETE POETRY DATA PROCESSING PIPELINE")
        print("="*80)
        
        # Step 1: Extract locations
        input_file = args.input if args.input else 'PoetryFoundationData.csv'
        locations_output = 'PoetryFoundationData_with_locations.csv'
        result_df = extract_locations(input_file, locations_output, args.limit)
        
        if result_df is None:
            print("\nERROR: Location extraction failed. Stopping pipeline.")
            return
        
        # Step 2: Extract birth years
        years_output = 'PoetryFoundationData_with_locations_and_years.csv'
        result_df = extract_birth_years(locations_output, years_output)
        
        if result_df is None:
            print("\nERROR: Birth year extraction failed. Stopping pipeline.")
            return
        
        # Step 3: Filter poems without years
        filtered_output = 'PoetryFoundationData_with_locations_and_years_filtered.csv'
        result_df = filter_no_year_poems(years_output, filtered_output)
        
        if result_df is None:
            print("\nERROR: Filtering failed. Stopping pipeline.")
            return
        
        # Step 4: Add 20 years to birth years
        final_output = args.output if args.output else filtered_output
        result_df = add_twenty_years(filtered_output, final_output)
        
        if result_df is None:
            print("\nERROR: Adding 20 years failed.")
            return
            
        print("\n" + "="*80)
        print("COMPLETE PIPELINE FINISHED SUCCESSFULLY")
        print("="*80)
        print(f"Final output saved to: {final_output}")

if __name__ == "__main__":
    main()
