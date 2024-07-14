import requests

# Define the base URL
base_url = "http://127.0.0.1:8000"

# Function to send query and print results
def send_query(query):
    response = requests.post(f"{base_url}/search", json={"query": query})
    return response.json()

# Query to find the outlets that close the latest
query_latest = "Which are the outlets that close the latest?"
result_latest = send_query(query_latest)
print("Outlets that close the latest:")
print(result_latest)

# Query to find the outlets that close the earliest
query_earliest = "Which are the outlets that close the earliest?"
result_earliest = send_query(query_earliest)
print("Outlets that close the earliest:")
print(result_earliest)

# Query to find the number of outlets located in Bangsar
query_bangsar = "How many outlets are located in Bangsar?"
result_bangsar = send_query(query_bangsar)
print("Number of outlets in Bangsar:")
print(result_bangsar)

# General query to test LLM integration
query_general = "What are the operating hours for Subway outlets?"
result_general = send_query(query_general)
print("General query result:")
print(result_general)
