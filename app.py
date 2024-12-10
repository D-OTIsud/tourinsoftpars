from flask import Flask, request, Response
import requests
import xml.etree.ElementTree as ET
import json

app = Flask(__name__)

# Default XML URL
DEFAULT_XML_URL = "https://api-v3.tourinsoft.com/api/syndications/reunion.tourinsoft.com/B2BC0524-ADC3-45D5-8A77-A0D70D2425B3"

@app.route('/categories', methods=['GET'])
def get_categories_info():
    """Endpoint to get information about categories and their object counts."""
    xml_url = request.args.get('url', DEFAULT_XML_URL)
    try:
        # Fetch the XML data
        response = requests.get(xml_url)
        response.raise_for_status()

        # Parse the XML content
        root = ET.fromstring(response.content)

        # Dictionary to hold category counts
        category_counts = {}

        # Iterate through each 'item' in the XML
        for item in root.findall('.//item'):
            # Find the category of the item
            category = item.find('Type')
            if category is not None and category.text:
                category_name = category.text.strip()
                if category_name in category_counts:
                    category_counts[category_name] += 1
                else:
                    category_counts[category_name] = 1

        # Convert the category counts to a list of dictionaries
        categories_info = [
            {"category": name, "object_count": count}
            for name, count in category_counts.items()
        ]

        return Response(json.dumps(categories_info, indent=4), content_type="application/json")

    except requests.exceptions.RequestException as e:
        error_message = {"error": str(e)}
        return Response(json.dumps(error_message, indent=4), content_type="application/json", status=500)

    except ET.ParseError as e:
        error_message = {
            "error": f"XML Parsing Error: {e}",
            "content": response.text
        }
        return Response(json.dumps(error_message, indent=4), content_type="application/json", status=500)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
