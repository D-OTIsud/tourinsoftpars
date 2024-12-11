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
        # Fetch the JSON data
        response = requests.get(API_URL)
        response.raise_for_status()
        data = response.json()

        # Extract SyndicObjectName
        syndic_names = [item.get("SyndicObjectName", "Unknown") for item in data]
        syndic_count = len(syndic_names)

        # Return analysis in JSON format
        return jsonify({
            "count": syndic_count,
            "names": syndic_names
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
