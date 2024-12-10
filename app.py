from flask import Flask, jsonify, request
import requests
import xml.etree.ElementTree as ET

app = Flask(__name__)

DEFAULT_XML_URL = "https://api-v3.tourinsoft.com/api/syndications/reunion.tourinsoft.com/B2BC0524-ADC3-45D5-8A77-A0D70D2425B3"

def xml_to_dict(element):
    """Recursive function to convert XML elements to a dictionary."""
    result = {}
    for child in element:
        if len(child):
            result[child.tag] = xml_to_dict(child)  # Recursive call for nested elements
        else:
            result[child.tag] = child.text or ""  # Handle empty text
    return result

@app.route('/convert', methods=['GET'])
def convert_to_json():
    # Use default XML URL or override with query parameter
    xml_url = request.args.get('url', DEFAULT_XML_URL)
    
    # Fetch the XML data
    try:
        response = requests.get(xml_url)
        response.raise_for_status()
        xml_content = response.text
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500

    # Parse the XML content
    try:
        root = ET.fromstring(xml_content)
        json_data = xml_to_dict(root)
    except ET.ParseError as e:
        return jsonify({"error": f"XML Parsing Error: {e}"}), 500

    # Return the JSON response
    return jsonify(json_data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
