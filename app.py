from flask import Flask, jsonify
import requests

app = Flask(__name__)

# API URL
API_URL = "https://api-v3.tourinsoft.com/api/syndications/reunion.tourinsoft.com/B2BC0524-ADC3-45D5-8A77-A0D70D2425B3?format=json"

@app.route('/')
def home():
    return jsonify({
        "message": "Welcome to the SyndicObjectName Analyzer! Use /analyze to get the data analysis."
    })

@app.route('/analyze')
def analyze():
    try:
        # Fetch the JSON data from the API
        response = requests.get(API_URL)
        response.raise_for_status()
        data = response.json()

        # Analyze the structure of the returned data
        if isinstance(data, list):
            # If data is a list, process each item
            syndic_names = [
                item.get("SyndicObjectName", "Unknown") if isinstance(item, dict) else str(item)
                for item in data
            ]
            syndic_count = len(syndic_names)
        elif isinstance(data, dict):
            # If data is a dictionary, assume it contains a list under a key (e.g., "items")
            syndic_names = [
                item.get("SyndicObjectName", "Unknown") for item in data.get("items", [])
            ]
            syndic_count = len(syndic_names)
        else:
            # Handle unexpected data structures
            syndic_names = ["Unexpected data structure"]
            syndic_count = 0

        # Return the analysis as JSON
        return jsonify({
            "count": syndic_count,
            "names": syndic_names
        })
    except Exception as e:
        # Return error message if something goes wrong
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Run the Flask app, accessible on all network interfaces
    app.run(debug=True, host='0.0.0.0', port=5000)
