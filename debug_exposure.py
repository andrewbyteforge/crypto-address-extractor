#!/usr/bin/env python3
"""
Debug script to check exposure data extraction
"""

import json
import logging

logging.basicConfig(level=logging.DEBUG)

def test_exposure_parsing():
    """Test parsing of exposure API response."""
    
    # Sample response structure from Chainalysis API
    sample_response = {
        "directExposure": {
            "services": [
                {
                    "name": "Binance",
                    "category": "exchange",
                    "percentage": 45.2,
                    "value": 1000000
                },
                {
                    "name": "Hydra Market",
                    "category": "darknet market",
                    "percentage": 5.3,
                    "value": 120000
                }
            ]
        },
        "indirectExposure": {
            "services": [
                {
                    "name": "Coinbase",
                    "category": "exchange",
                    "percentage": 12.1,
                    "value": 250000
                }
            ]
        }
    }
    
    print("Sample Exposure Response:")
    print(json.dumps(sample_response, indent=2))
    
    # Test extraction
    direct_services = sample_response.get('directExposure', {}).get('services', [])
    indirect_services = sample_response.get('indirectExposure', {}).get('services', [])
    
    print(f"\nFound {len(direct_services)} direct services")
    print(f"Found {len(indirect_services)} indirect services")
    
    # Test filtering
    exchanges = []
    darknet_markets = []
    
    for service in direct_services + indirect_services:
        category = service.get('category', '').lower()
        if 'exchange' in category:
            exchanges.append(service)
        elif 'darknet' in category:
            darknet_markets.append(service)
    
    print(f"\nFiltered to {len(exchanges)} exchanges and {len(darknet_markets)} darknet markets")
    
    for ex in exchanges:
        print(f"  Exchange: {ex['name']} - {ex['percentage']}%")
    
    for dm in darknet_markets:
        print(f"  Darknet: {dm['name']} - {dm['percentage']}%")


if __name__ == "__main__":
    test_exposure_parsing()
