@app.route('/categories', methods=['GET'])
def get_categories_info():
    """Endpoint to get information about categories and their object counts."""
    xml_url = request.args.get('url', DEFAULT_XML_URL)
    try:
        response = requests.get(xml_url)
        response.raise_for_status()

        # Decode content and sanitize it
        xml_content = response.content.decode('utf-8', errors='ignore')
        xml_content = re.sub(r'[^\x09\x0A\x0D\x20-\x7F]+', '', xml_content)

        # Parse the XML content
        root = ET.fromstring(xml_content)

        # Dictionary to hold category counts
        category_counts = {}

        # Iterate through each 'item' in the XML
        for item in root.findall('.//item'):
            # Attempt to find the 'Type' of the item
            category = item.find('Type')
            if category is not None and category.text:
                category_name = category.text.strip()
            else:
                # If 'Type' is missing, assign a default category
                category_name = 'Uncategorized'

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
