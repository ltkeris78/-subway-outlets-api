import sqlite3
import requests
import re
import json
from bs4 import BeautifulSoup

# Function to scrape a single page
def scrape_page(url):
    response = requests.get(url)
    html_text = response.text
    data = re.search(r'"markerData":(\[.*?\}\]),', html_text)
    
    if not data:
        print("No marker data found.")
        return []

    data = json.loads(data.group(1))
    outlets = []

    for d in data:
        soup = BeautifulSoup(d["infoBox"]["content"], "html.parser")
        name = soup.h4.text if soup.h4 else 'N/A'
        address = soup.find_all('p')[0].text if soup.find_all('p') else 'N/A'
        hours = soup.find_all('p')[1].text if len(soup.find_all('p')) > 1 else 'N/A'
        waze_link = soup.find_all('a')[1]['href'] if len(soup.find_all('a')) > 1 else 'N/A'

        # Extract latitude and longitude from the JSON data if available
        latitude = d["position"].get("lat")
        longitude = d["position"].get("lng")

        # Only include outlets in Kuala Lumpur
        if "Kuala Lumpur" in address:
            outlets.append((name, address, hours, waze_link, latitude, longitude))
    
    return outlets

# Function to get geographical coordinates using Nominatim
def get_coordinates(address):
    url = f'https://nominatim.openstreetmap.org/search?q={requests.utils.quote(address)}&format=json'
    response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
    data = response.json()
    
    if data:
        location = data[0]
        return location['lat'], location['lon']
    else:
        print(f"Geocoding error for address {address}: No results found")
        return None, None

# Function to create and initialize the SQLite database
def initialize_database():
    conn = sqlite3.connect('subway_outlets.db')
    c = conn.cursor()
    c.execute('DROP TABLE IF EXISTS outlets')
    c.execute('''CREATE TABLE outlets
                 (name TEXT, address TEXT, hours TEXT, waze_link TEXT, latitude REAL, longitude REAL, UNIQUE(name, address))''')
    return conn, c

# Function to insert outlet data into the database
def insert_outlets(c, outlets):
    for outlet in outlets:
        name, address, hours, waze_link, latitude, longitude = outlet
        if latitude is None or longitude is None:
            latitude, longitude = get_coordinates(address)
        try:
            c.execute('INSERT INTO outlets (name, address, hours, waze_link, latitude, longitude) VALUES (?, ?, ?, ?, ?, ?)', 
                      (name, address, hours, waze_link, latitude, longitude))
            print(f"Name: {name}, Address: {address}, Operating Hours: {hours}, Waze Link: {waze_link}, Latitude: {latitude}, Longitude: {longitude}")
        except sqlite3.IntegrityError:
            print(f"Duplicate entry for outlet: {name} at {address}")

# Function to scrape all pages and save data into the database
def scrape_and_save_data():
    base_url = 'https://subway.com.my/find-a-subway?page='
    conn, c = initialize_database()

    # Assuming there are 5 pages. Adjust the range if more pages are present.
    for page in range(1, 6):
        page_url = f'{base_url}{page}'
        print(f"Scraping page: {page_url}")
        outlets = scrape_page(page_url)
        insert_outlets(c, outlets)
    
    conn.commit()
    print("\nSubway Outlets in Kuala Lumpur with Coordinates:")
    for row in c.execute('SELECT * FROM outlets WHERE address LIKE "%Kuala Lumpur%"'):
        print(f"Name: {row[0]}, Address: {row[1]}, Operating Hours: {row[2]}, Waze Link: {row[3]}, Latitude: {row[4]}, Longitude: {row[5]}")
    conn.close()
    print("Data successfully scraped, geocoded, and saved to the database.")

# Run the scraping and saving process
scrape_and_save_data()
