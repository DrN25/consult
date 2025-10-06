"""
Test script for PMC to DOI API
"""

import requests
import json

BASE_URL = "http://localhost:8001"

def test_endpoint(method: str, url: str, data=None, description=""):
    print("=" * 80)
    print(f"TEST: {description}")
    print("=" * 80)
    print(f"Method: {method}")
    print(f"URL: {url}")
    if data:
        print(f"Body: {json.dumps(data, indent=2)}")
    print()
    
    try:
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)
        
        print(f"Status: {response.status_code}")
        print(f"Response:")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        print()
        
        if response.status_code == 200:
            result = response.json()
            if isinstance(result, dict) and "found" in result:
                if result["found"]:
                    print(f"✅ DOI Found: {result.get('doi')}")
                else:
                    print(f"❌ PMC Not Found: {result.get('message')}")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    print()

def main():
    print("=" * 80)
    print("PMC TO DOI API - TEST SUITE")
    print("=" * 80)
    print()
    
    # Test 1: Root endpoint
    test_endpoint(
        "GET",
        f"{BASE_URL}/",
        description="Root endpoint - API information"
    )
    
    # Test 2: Health check
    test_endpoint(
        "GET",
        f"{BASE_URL}/health",
        description="Health check"
    )
    
    # Test 3: GET with PMC prefix
    test_endpoint(
        "GET",
        f"{BASE_URL}/doi/PMC2910419",
        description="GET request with PMC prefix"
    )
    
    # Test 4: GET without PMC prefix
    test_endpoint(
        "GET",
        f"{BASE_URL}/doi/2910419",
        description="GET request without PMC prefix"
    )
    
    # Test 5: POST request
    test_endpoint(
        "POST",
        f"{BASE_URL}/doi",
        data={"pmc_id": "PMC2910419"},
        description="POST request with JSON body"
    )
    
    # Test 6: Different PMC ID
    test_endpoint(
        "GET",
        f"{BASE_URL}/doi/PMC3639165",
        description="Different PMC ID (biofilm article)"
    )
    
    # Test 7: Non-existent PMC
    test_endpoint(
        "GET",
        f"{BASE_URL}/doi/PMC999999999",
        description="Non-existent PMC ID (should return not found)"
    )
    
    # Test 8: POST with non-existent PMC
    test_endpoint(
        "POST",
        f"{BASE_URL}/doi",
        data={"pmc_id": "PMC999999999"},
        description="POST with non-existent PMC ID"
    )
    
    print("=" * 80)
    print("TEST SUITE COMPLETE")
    print("=" * 80)
    print("\nVerify:")
    print("1. All valid PMC IDs return correct DOI")
    print("2. Invalid PMC IDs return found=false")
    print("3. Both GET and POST methods work")
    print("4. PMC prefix is optional")

if __name__ == "__main__":
    main()
