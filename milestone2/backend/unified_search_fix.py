# Find this part in your main.py around the /unified_search endpoint
# and replace the response formatting section with this:

        # Format response with price information
        response = {
            "query": request.query,
            "properties": [],
            "rentals": [],
            "context": {
                "schools": results['context'].get('schools', [])[:5],
                "transit": results['context'].get('transit', [])[:5],
                "crime": results['context'].get('boston_crime', [])[:3],
                "demographics": results['context'].get('demographics', [])[:2],
                "businesses": results['context'].get('yelp_businesses_20251024_185237', [])[:5]
            },
            "total_results": {
                "properties": len(results['properties']),
                "rentals": len(results['rentals'])
            }
        }
        
        # Add properties with metadata (including price)
        for i, prop in enumerate(results['properties'][:10]):
            if 'metadatas' in results['results'].get('boston_properties', {}):
                metadata = results['results']['boston_properties']['metadatas'][i] if i < len(results['results']['boston_properties']['metadatas']) else {}
                property_info = {
                    "description": prop,
                    "price": metadata.get('TOTAL_VALUE', 'N/A'),
                    "bedrooms": metadata.get('BED_RMS', 'N/A'),
                    "bathrooms": metadata.get('FULL_BTH', 'N/A'),
                    "sqft": metadata.get('living_square_feet', 'N/A'),
                    "year_built": metadata.get('year_built', 'N/A')
                }
                response['properties'].append(property_info)
            else:
                response['properties'].append({"description": prop})
        
        return response
