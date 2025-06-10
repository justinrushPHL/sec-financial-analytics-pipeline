#!/usr/bin/env python3
"""
Debug tool for SEC API connections
"""

import requests
import sys
from pathlib import Path

# Add to path
sys.path.append('.')
from config.config import SEC_BASE_URL, SEC_HEADERS

def test_sec_connection():
    """Test basic connection to SEC"""
    print("Testing SEC API Connection...")
    print(f"Base URL: {SEC_BASE_URL}")
    print(f"Headers: {SEC_HEADERS}")
    print()
    
    # Test a simple API endpoint - Apple's company facts
    apple_cik = "0000320193"
    test_url = f"{SEC_BASE_URL}/api/xbrl/companyfacts/CIK{apple_cik}.json"
    
    try:
        print(f"Testing URL: {test_url}")
        response = requests.get(test_url, headers=SEC_HEADERS, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✓ Successfully connected to SEC API")
            print(f"Company: {data.get('entityName', 'Unknown')}")
            print(f"CIK: {data.get('cik', 'Unknown')}")
            
            # Check if facts are available
            facts = data.get('facts', {})
            us_gaap = facts.get('us-gaap', {})
            print(f"Available US-GAAP metrics: {len(us_gaap)}")
            
            # Show some sample metrics
            print("\nSample available metrics:")
            for i, metric in enumerate(list(us_gaap.keys())[:5]):
                print(f"  - {metric}")
            
            return True
        else:
            print(f"✗ Failed with status code: {response.status_code}")
            print(f"Response: {response.text[:200]}...")
            return False
            
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        return False

def test_company_submissions():
    """Test company submissions endpoint"""
    print("\n" + "="*50)
    print("Testing Company Submissions API...")
    
    # Test Apple submissions
    apple_cik = "0000320193"
    test_url = f"{SEC_BASE_URL}/submissions/CIK{apple_cik}.json"
    
    try:
        print(f"Testing URL: {test_url}")
        response = requests.get(test_url, headers=SEC_HEADERS, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✓ Successfully fetched submissions")
            print(f"Company: {data.get('name', 'Unknown')}")
            print(f"Tickers: {data.get('tickers', [])}")
            
            # Check recent filings
            recent_filings = data.get('filings', {}).get('recent', {})
            if recent_filings:
                forms = recent_filings.get('form', [])
                filing_dates = recent_filings.get('filingDate', [])
                
                print(f"Recent filings count: {len(forms)}")
                print("Recent filings:")
                for i in range(min(5, len(forms))):
                    print(f"  - {forms[i]} filed on {filing_dates[i]}")
            
            return True
        else:
            print(f"✗ Failed with status code: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        return False

def main():
    print("SEC API Debug Tool")
    print("="*50)
    
    # Test basic connection
    connection_ok = test_sec_connection()
    
    # Test submissions
    submissions_ok = test_company_submissions()
    
    print("\n" + "="*50)
    if connection_ok and submissions_ok:
        print("🎉 All SEC API tests passed!")
        print("Your pipeline should work correctly.")
    else:
        print("❌ Some tests failed.")
        print("This might indicate network issues or SEC API changes.")
        print("Try running the tests again in a few minutes.")

if __name__ == "__main__":
    main()