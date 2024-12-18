from flask import Flask, jsonify, Response, request
import requests
import json

app = Flask(__name__)

# API URLs
CATEGORIES = {
    "decouverte": "https://api-v3.tourinsoft.com/api/syndications/reunion.tourinsoft.com/39BAB676-97BB-4C78-9D7D-28DD43753314?format=json",
    "hebergement": "https://api-v3.tourinsoft.com/api/syndications/reunion.tourinsoft.com/B2BC0524-ADC3-45D5-8A77-A0D70D2425B3?format=json",
    "info_service": "https://api-v3.tourinsoft.com/api/syndications/reunion.tourinsoft.com/5A285C91-D35F-4873-8F3C-A032ABB418D3?format=json",
    "loisir": "https://api-v3.tourinsoft.com/api/syndications/reunion.tourinsoft.com/C32A0407-A66F-48D5-8DB0-618FDF03F49F?format=json",
    "restauration": "https://api-v3.tourinsoft.com/api/syndications/reunion.tourinsoft.com/CC575EE1-AA90-49BD-B23F-1935C4B151CD?format=json",
    "transport": "https://api-v3.tourinsoft.com/api/syndications/reunion.tourinsoft.com/15DD031A-CAAC-4E1B-AA75-5F65D7A437E8?format=json"
}

def fetch_and_structure_data(api_url):
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        data = response.json()

        structured_data = []
        if isinstance(data, dict) and "value" in data:
            items = data["value"]
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
                            "name": item.get("Structure", {}).get("Name", "Unknown") if item.get("Structure") else "Unknown",
                            "email": item.get("Structure", {}).get("Email", "Unknown") if item.get("Structure") else "Unknown"
                        },
                        "classification": {
                            "type": item.get("ClassificationType", {}).get("ThesLibelle", "Unknown") if item.get("ClassificationType") else "Unknown",
                            "category": item.get("Classificationcategorie", {}).get("ThesLibelle", "Unknown") if item.get("Classificationcategorie") else "Unknown"
                        },
                        "equipments": [
                            equip.get("ThesLibelle", "Unknown") for equip in item.get("PrestationsEquipementss", []) if equip
                        ],
                        "proximity": [
                            prox.get("ThesLibelle", "Unknown") for prox in item.get("PrestationProximites", []) if prox
                        ],
                        "photos": [
                            photo.get("Photo", {}).get("Url", "Unknown") for photo in item.get("Photos", []) if photo
                        ],
                        "languages": [
                            lang.get("ThesLibelle", "Unknown") for lang in item.get("LanguesParleess", []) if lang
                        ],
                        "opening_periods": [
                            period.get("Periode", "Unknown") for period in item.get("PeriodeOuvertures", []) if period
                        ]
                    })
        return structured_data
    except Exception as e:
        return {"error": str(e)}

@app.route('/')
def home():
    return jsonify({
        "message": "Bienvenue dans l'analyseur de données Tourinsoft ! Utilisez /analyze pour obtenir l'analyse des données ou appelez une catégorie individuelle."
    })

@app.route('/analyze')
def analyze():
    categories = request.args.getlist('category')
    aggregated_data = {}
    total_count = 0

    if categories:
        selected_categories = {cat: CATEGORIES[cat] for cat in categories if cat in CATEGORIES}
    else:
        selected_categories = CATEGORIES

    for category, api_url in selected_categories.items():
        data = fetch_and_structure_data(api_url)
        if isinstance(data, list):
            count = len(data)
            total_count += count
        else:
            count = 0
        aggregated_data[category] = {"count": count, "data": data}

    response_json = json.dumps({"total_count": total_count, "categories": aggregated_data}, ensure_ascii=False, indent=4)
    return Response(response_json, content_type="application/json")

@app.route('/analyze/<category>')
def analyze_category(category):
    if category not in CATEGORIES:
        return jsonify({"error": "Invalid category"}), 400

    api_url = CATEGORIES[category]
    data = fetch_and_structure_data(api_url)
    count = len(data) if isinstance(data, list) else 0

    response_json = json.dumps({"category": category, "count": count, "data": data}, ensure_ascii=False, indent=4)
    return Response(response_json, content_type="application/json")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
