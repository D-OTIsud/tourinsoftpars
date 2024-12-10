from flask import Flask, jsonify, request
import requests
import xml.etree.ElementTree as ET

app = Flask(__name__)

# Default XML URL
DEFAULT_XML_URL = "https://tp.deep-process.com"

def xml_to_dict(element):
    """Recursive function to convert XML elements to a dictionary."""
    result = {}
    for child in element:
        # Handle duplicate tags by storing them in a list
        if child.tag in result:
            if not isinstance(result[child.tag], list):
                result[child.tag] = [result[child.tag]]
            result[child.tag].append(xml_to_dict(child) if len(child) else child.text or "")
        else:
            result[child.tag] = xml_to_dict(child) if len(child) else child.text or ""
    return result

@app.route('/')
def index():
    """Default route providing usage information."""
    return jsonify({"message": "Welcome to the XML to JSON API!", "usage": "Use /convert endpoint to convert XML to JSON."})

@app.route('/convert', methods=['GET'])
def convert_to_json():
    """Endpoint to convert XML to JSON."""
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
