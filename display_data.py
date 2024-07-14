import sqlite3

# Connect to SQLite database
conn = sqlite3.connect('subway_outlets.db')
c = conn.cursor()

# Query all rows in the outlets table
c.execute('SELECT * FROM outlets')
rows = c.fetchall()

# Print all rows
print("Subway Outlets Data:")
for row in rows:
    print(f"Name: {row[0]}, Address: {row[1]}, Operating Hours: {row[2]}, Waze Link: {row[3]}")

# Close the connection
conn.close()


import sqlite3

# Connect to SQLite database
conn = sqlite3.connect('subway_outlets.db')
c = conn.cursor()

# Query all rows in the outlets table
c.execute('SELECT * FROM outlets')
rows = c.fetchall()

# Print all rows
print("Subway Outlets Data:")
for row in rows:
    print(f"Name: {row[0]}, Address: {row[1]}, Operating Hours: {row[2]}, Waze Link: {row[3]}, Latitude: {row[4]}, Longitude: {row[5]}")

# Calculate the number of outlets
number_of_outlets = len(rows)
print(f"\nTotal number of Subway outlets: {number_of_outlets}")

# Close the connection
conn.close()
