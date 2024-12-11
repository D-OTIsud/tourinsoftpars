from flask import Flask, jsonify, Response
import requests
import json

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
        structured_data = []
        if isinstance(data, dict) and "value" in data:
            items = data["value"]  # Access the 'value' list
            for item in items:
                if isinstance(item, dict):
                    structured_data.append({
                        "name": item.get("SyndicObjectName", "Unknown"),
                        "type": item.get("ObjectTypeName", "Unknown"),
                        "commune": item.get("Commune", "Unknown"),
                        "address": {
                            "line": item.get("Adresse1", "Unknown"),
                            "postal_code": item.get("CodePostal", "Unknown")
                        },
                        "location": {
                            "latitude": item.get("GmapLatitude", "Unknown"),
                            "longitude": item.get("GmapLongitude", "Unknown")
                        },
                        "tarif": item.get("Tarif", "Non spécifié"),
                        "structure": {
                            "name": item.get("Structure", {}).get("Name", "Unknown"),
                            "email": item.get("Structure", {}).get("Email", "Unknown")
                        },
                        "classification": {
                            "type": item.get("ClassificationType", {}).get("ThesLibelle", "Unknown"),
                            "category": item.get("Classificationcategorie", {}).get("ThesLibelle", "Unknown")
                        },
                        "equipments": [
                            equip.get("ThesLibelle", "Unknown") for equip in item.get("PrestationsEquipementss", [])
                        ],
                        "proximity": [
                            prox.get("ThesLibelle", "Unknown") for prox in item.get("PrestationProximites", [])
                        ],
                        "photos": [
                            photo.get("Photo", {}).get("Url", "Unknown") for photo in item.get("Photos", [])
                        ],
                        "languages": [
                            lang.get("ThesLibelle", "Unknown") for lang in item.get("LanguesParleess", [])
                        ],
                        "opening_periods": [
                            period.get("Periode", "Unknown") for period in item.get("PeriodeOuvertures", [])
                        ]
                    })

        # Return the structured data
        response_json = json.dumps({"count": len(structured_data), "data": structured_data}, ensure_ascii=False)
        return Response(response_json, content_type="application/json")
    except Exception as e:
        # Handle any errors that occur
        error_response = {"error": str(e)}
        return Response(json.dumps(error_response, ensure_ascii=False), content_type="application/json")

if __name__ == '__main__':
    # Run the Flask app, accessible on all network interfaces
    app.run(debug=True, host='0.0.0.0', port=5000)
