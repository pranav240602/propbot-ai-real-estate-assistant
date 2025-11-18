"""
Input Validation & Security for PropBot
Handles edge cases and malicious inputs
"""

import re
import logging
from typing import Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class InputValidator:
    """Validate and sanitize user inputs"""
    
    def __init__(self):
        self.max_query_length = 500
        self.sql_injection_patterns = [
            r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|EXECUTE)\b)",
            r"(--|;|\/\*|\*\/|xp_|sp_)",
            r"(\bOR\b.*=.*)",
            r"(\bUNION\b.*\bSELECT\b)"
        ]
        
        self.valid_neighborhoods = [
            'back bay', 'beacon hill', 'south end', 'north end', 'dorchester',
            'roxbury', 'jamaica plain', 'charlestown', 'east boston', 'allston',
            'brighton', 'fenway', 'south boston', 'seaport', 'west end'
        ]
    
    def validate_query(self, query: str) -> Dict[str, Any]:
        """Validate chat query"""
        
        # Check if None or empty
        if query is None:
            return {
                'valid': False,
                'error': 'Query cannot be empty',
                'sanitized': None
            }
        
        # Convert to string if not
        query = str(query).strip()
        
        # Check length
        if len(query) == 0:
            return {
                'valid': False,
                'error': 'Query cannot be empty. Try: "Show me properties in Back Bay"',
                'sanitized': None
            }
        
        if len(query) > self.max_query_length:
            return {
                'valid': False,
                'error': f'Query too long (max {self.max_query_length} characters)',
                'sanitized': None
            }
        
        # Check for SQL injection
        for pattern in self.sql_injection_patterns:
            if re.search(pattern, query, re.IGNORECASE):
                logger.warning(f"🚨 SQL injection attempt detected: {query}")
                return {
                    'valid': False,
                    'error': 'Invalid query. Please ask about properties naturally.',
                    'sanitized': None
                }
        
        # Check if only special characters
        if re.match(r'^[^a-zA-Z0-9\s]+$', query):
            return {
                'valid': False,
                'error': 'Please use words to describe what you\'re looking for!',
                'sanitized': None
            }
        
        # Sanitize: remove excessive spaces, special chars
        sanitized = re.sub(r'\s+', ' ', query)
        sanitized = re.sub(r'[<>{}]', '', sanitized)
        
        return {
            'valid': True,
            'sanitized': sanitized,
            'error': None
        }
    
    def validate_property_search(self, search_params: Dict) -> Dict[str, Any]:
        """Validate property search parameters"""
        
        errors = []
        
        # Validate bedrooms
        if search_params.get('bedrooms') is not None:
            bedrooms = search_params['bedrooms']
            if not isinstance(bedrooms, int):
                errors.append("Bedrooms must be a number")
            elif bedrooms < 0 or bedrooms > 10:
                errors.append("Bedrooms must be between 0 and 10")
        
        # Validate bathrooms
        if search_params.get('bathrooms') is not None:
            bathrooms = search_params['bathrooms']
            if not isinstance(bathrooms, int):
                errors.append("Bathrooms must be a number")
            elif bathrooms < 0 or bathrooms > 10:
                errors.append("Bathrooms must be between 0 and 10")
        
        # Validate prices
        if search_params.get('min_price') is not None:
            min_price = search_params['min_price']
            if not isinstance(min_price, (int, float)):
                errors.append("Minimum price must be a number")
            elif min_price < 0:
                errors.append("Minimum price cannot be negative")
            elif min_price > 50000000:
                errors.append("Minimum price seems unrealistic (max $50M)")
        
        if search_params.get('max_price') is not None:
            max_price = search_params['max_price']
            if not isinstance(max_price, (int, float)):
                errors.append("Maximum price must be a number")
            elif max_price < 0:
                errors.append("Maximum price cannot be negative")
            elif max_price > 50000000:
                errors.append("Maximum price seems unrealistic (max $50M)")
        
        # Check min < max
        if (search_params.get('min_price') and search_params.get('max_price') and 
            search_params['min_price'] > search_params['max_price']):
            errors.append("Minimum price cannot be greater than maximum price")
        
        # Validate neighborhood
        if search_params.get('neighborhood'):
            neighborhood = str(search_params['neighborhood']).lower()
            if neighborhood not in self.valid_neighborhoods:
                errors.append(f"Unknown neighborhood. Try: {', '.join(self.valid_neighborhoods[:5])}")
        
        if errors:
            return {
                'valid': False,
                'errors': errors
            }
        
        return {
            'valid': True,
            'errors': []
        }

# Test
if __name__ == "__main__":
    validator = InputValidator()
    
    # Test valid query
    result = validator.validate_query("Show me properties in Back Bay")
    print(f"Valid query: {result}")
    
    # Test SQL injection
    result = validator.validate_query("'; DROP TABLE properties; --")
    print(f"SQL injection: {result}")
    
    # Test empty
    result = validator.validate_query("")
    print(f"Empty query: {result}")
    
    # Test search params
    result = validator.validate_property_search({
        'bedrooms': 3,
        'min_price': 500000,
        'max_price': 1000000
    })
    print(f"Valid search: {result}")
    
    # Test invalid search
    result = validator.validate_property_search({
        'bedrooms': 99,
        'min_price': 2000000,
        'max_price': 1000000
    })
    print(f"Invalid search: {result}")
