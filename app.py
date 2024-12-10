from flask import Flask, request, Response
import requests
import xml.etree.ElementTree as ET
import json
import re

app = Flask(__name__)

# Correct default XML URL
DEFAULT_XML_URL = "https://api-v3.tourinsoft.com/api/syndications/reunion.tourinsoft.com/B2BC0524-ADC3-45D5-8A77-A0D70D2425B3"

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
    message = {
        "message": "Welcome to the XML to JSON API!",
        "usage": "Use /convert endpoint to convert XML to JSON.",
        "example": "/convert?url=https://your-xml-url.com"
    }
    return Response(json.dumps(message, indent=4), content_type="application/json")

@app.route('/convert', methods=['GET'])
def convert_to_json():
    """Endpoint to convert XML to JSON."""
    # Use default XML URL or override with query parameter
    xml_url = request.args.get('url', DEFAULT_XML_URL)
    
    try:
        # Fetch the XML data
        response = requests.get(xml_url)
        response.raise_for_status()

        # Validate Content-Type header
        if not response.headers.get('Content-Type', '').startswith('application/xml'):
            error_message = {
                "error": "The response is not valid XML.",
                "content": response.text
            }
            return Response(json.dumps(error_message, indent=4), content_type="application/json", status=400)

        # Decode content and sanitize it
        xml_content = response.content.decode('utf-8', errors='ignore')
        xml_content = re.sub(r'[^\x09\x0A\x0D\x20-\x7F]+', '', xml_content)  # Remove invalid characters

        # Debug: Return raw content for debugging purposes
        if request.args.get('debug') == 'true':
            debug_message = {"raw_content": xml_content}
            return Response(json.dumps(debug_message, indent=4), content_type="application/json")

        # Parse the XML content
        root = ET.fromstring(xml_content)
        json_data = xml_to_dict(root)

        # Return the parsed JSON data
        return Response(json.dumps(json_data, indent=4), content_type="application/json")

    except requests.exceptions.RequestException as e:
        # Handle request errors (e.g., connection issues)
        error_message = {"error": str(e)}
        return Response(json.dumps(error_message, indent=4), content_type="application/json", status=500)

    except ET.ParseError as e:
        # Handle XML parsing errors
        error_message = {
            "error": f"XML Parsing Error: {e}",
            "content": xml_content
        }
        return Response(json.dumps(error_message, indent=4), content_type="application/json", status=500)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
