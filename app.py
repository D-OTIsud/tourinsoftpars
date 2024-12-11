from flask import Flask, jsonify
import requests

app = Flask(__name__)

# API URL
API_URL = "https://api-v3.tourinsoft.com/api/syndications/reunion.tourinsoft.com/B2BC0524-ADC3-45D5-8A77-A0D70D2425B3?format=json"

@app.route('/')
def home():
    return jsonify({
        "message": "Bienvenue dans l'analyseur SyndicObjectName ! Utilisez /analyze pour obtenir l'analyse des données."
    })

@app.route('/analyze')
def analyze():
    try:
        # Fetch the JSON data from the API
        response = requests.get(API_URL)
        response.raise_for_status()
        data = response.json()

        # Ensure the data contains the 'value' key and it is a list
        if isinstance(data, dict) and "value" in data:
            items = data["value"]  # Access the 'value' list
            # Extract SyndicObjectName from each item in the list
            syndic_names = [
                item.get("SyndicObjectName", "Unknown") for item in items if isinstance(item, dict)
            ]
            syndic_count = len(syndic_names)
        else:
            # Handle unexpected structure
            syndic_names = []
            syndic_count = 0

        # Return the analysis with ensure_ascii=False
        return jsonify({
            "count": syndic_count,
            "names": syndic_names
        }, ensure_ascii=False)
    except Exception as e:
        # Handle any errors that occur
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Run the Flask app, accessible on all network interfaces
    app.run(debug=True, host='0.0.0.0', port=5000)
