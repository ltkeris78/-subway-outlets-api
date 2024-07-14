import requests
import sqlite3
from time import sleep

def geocode_address(address):
    endpoint = f'https://nominatim.openstreetmap.org/search?q={address}&format=json'
    response = requests.get(endpoint)
    if response.status_code == 200 and response.json():
        result = response.json()[0]
        return result['lat'], result['lon']
    return None, None

# Open database connection
conn = sqlite3.connect('subway_outlets.db')
cursor = conn.cursor()

# Add new columns for latitude and longitude if not exist
try:
    cursor.execute('ALTER TABLE outlets ADD COLUMN latitude REAL')
    cursor.execute('ALTER TABLE outlets ADD COLUMN longitude REAL')
except sqlite3.OperationalError:
    pass  # Columns already exist

# Fetch addresses and geocode
cursor.execute('SELECT rowid, address FROM outlets')
rows = cursor.fetchall()
for row in rows:
    outlet_id, address = row
    lat, lng = geocode_address(address)
    if lat and lng:
        cursor.execute('UPDATE outlets SET latitude = ?, longitude = ? WHERE rowid = ?', (lat, lng, outlet_id))
    sleep(1)  # To avoid overwhelming the API

conn.commit()
conn.close()
