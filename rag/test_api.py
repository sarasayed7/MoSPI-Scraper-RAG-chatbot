import requests
import json

# The URL of your local FastAPI endpoint
url = "http://127.0.0.1:8000/query"

# The query you want to send to the RAG chatbot
query_data = {
    "query": "What is the unemployment rate for males in urban areas?"
}

# Set the headers to specify that we are sending JSON data
headers = {
    "Content-Type": "application/json"
}

print(f"Sending POST request to {url} with query: '{query_data['query']}'")

try:
    # Send the POST request with the JSON payload
    response = requests.post(url, data=json.dumps(query_data), headers=headers)
    
    # Check if the request was successful
    response.raise_for_status()

    # Parse the JSON response
    response_json = response.json()
    
    # Print the result
    print("\n--- API Response ---")
    print(json.dumps(response_json, indent=4))
    
except requests.exceptions.RequestException as e:
    print(f"Error: An HTTP request error occurred. Please ensure your API is running.")
    print(f"Details: {e}")
except json.JSONDecodeError:
    print("Error: Failed to decode the JSON response.")
    print(f"Response content: {response.text}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")