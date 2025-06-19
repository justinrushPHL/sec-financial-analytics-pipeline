# src/data_collector.py
import requests
import json
import time
import logging
from typing import List, Dict, Optional
from datetime import datetime
import sys
from pathlib import Path

# Add project root to path for imports
sys.path.append(str(Path(__file__).parent.parent))
from config.config import SEC_BASE_URL, SEC_HEADERS, REQUEST_DELAY

class SECDataCollector:
    """Collects financial data from SEC EDGAR API"""
    
    def __init__(self):
        self.base_url = SEC_BASE_URL
        self.headers = SEC_HEADERS
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        self.logger = logging.getLogger(__name__)
        
        # Cache for company lookups
        self._company_tickers_cache = None
        
        # Validate headers
        if "your.email@example.com" in self.headers["User-Agent"]:
            self.logger.warning("Please update your email in config/config.py SEC_HEADERS")
    
    def _make_request(self, url: str, max_retries: int = 3) -> Optional[Dict]:
        """Make HTTP request with retry logic and rate limiting"""
        for attempt in range(max_retries):
            try:
                self.logger.debug(f"Making request to: {url}")
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                
                # Rate limiting
                time.sleep(REQUEST_DELAY)
                
                return response.json()
                
            except requests.exceptions.RequestException as e:
                self.logger.warning(f"Request failed (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    self.logger.error(f"All request attempts failed for {url}")
                    return None
        
        return None
    
    def get_company_tickers(self) -> Dict[str, Dict]:
        """Get ALL company ticker mappings from SEC API (dynamic lookup)"""
        if self._company_tickers_cache is not None:
            return self._company_tickers_cache
        
        self.logger.info("Fetching complete company ticker mappings from SEC...")
        
        # Correct SEC company tickers endpoint (found in documentation)
        url = "https://www.sec.gov/files/company_tickers.json"
        
        try:
            # Make direct request (not using _make_request to avoid rate limiting delay)
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            company_data = response.json()
            self.logger.info(f"Successfully loaded {len(company_data)} companies from SEC")
            
            # Cache the result
            self._company_tickers_cache = company_data
            return company_data
            
        except Exception as e:
            self.logger.error(f"Failed to fetch company tickers from SEC: {e}")
            self.logger.info("Falling back to hardcoded list of major companies...")
            
            # Fallback to hardcoded list if SEC API fails
            fallback_companies = {
                '0': {'cik_str': 320193, 'ticker': 'AAPL', 'title': 'Apple Inc.'},
                '1': {'cik_str': 789019, 'ticker': 'MSFT', 'title': 'Microsoft Corp'},
                '2': {'cik_str': 1652044, 'ticker': 'GOOGL', 'title': 'Alphabet Inc.'},
                '3': {'cik_str': 1018724, 'ticker': 'AMZN', 'title': 'Amazon.com Inc'},
                '4': {'cik_str': 1318605, 'ticker': 'TSLA', 'title': 'Tesla Inc'},
                '5': {'cik_str': 1045810, 'ticker': 'NVDA', 'title': 'NVIDIA Corp'},
                '6': {'cik_str': 1326801, 'ticker': 'META', 'title': 'Meta Platforms Inc'},
                '7': {'cik_str': 1065280, 'ticker': 'NFLX', 'title': 'Netflix Inc'},
                '8': {'cik_str': 19617, 'ticker': 'JPM', 'title': 'JPMorgan Chase & Co'},
                '9': {'cik_str': 1403161, 'ticker': 'V', 'title': 'Visa Inc.'},
                '10': {'cik_str': 200406, 'ticker': 'JNJ', 'title': 'Johnson & Johnson'},
                '11': {'cik_str': 104169, 'ticker': 'WMT', 'title': 'Walmart Inc'},
                '12': {'cik_str': 80424, 'ticker': 'PG', 'title': 'Procter & Gamble Co'},
                '13': {'cik_str': 731766, 'ticker': 'UNH', 'title': 'UnitedHealth Group Inc'},
                '14': {'cik_str': 354950, 'ticker': 'HD', 'title': 'Home Depot Inc'},
                # Add WK and CMG to fallback list
                '15': {'cik_str': 1564590, 'ticker': 'WK', 'title': 'Workiva Inc'},
                '16': {'cik_str': 1058090, 'ticker': 'CMG', 'title': 'Chipotle Mexican Grill Inc'}
            }
            
            self._company_tickers_cache = fallback_companies
            return fallback_companies
    
    def find_companies_by_tickers(self, target_tickers: List[str]) -> List[Dict]:
        """Find company information for specific tickers using dynamic lookup"""
        all_companies = self.get_company_tickers()
        target_companies = []
        
        # Convert tickers to uppercase for comparison
        target_tickers_upper = [ticker.upper().strip() for ticker in target_tickers]
        
        self.logger.info(f"Searching for companies with tickers: {target_tickers_upper}")
        
        # Search through all companies
        found_tickers = set()
        for key, company in all_companies.items():
            company_ticker = company.get('ticker', '').upper().strip()
            
            if company_ticker in target_tickers_upper:
                target_companies.append({
                    'cik': str(company['cik_str']).zfill(10),  # Pad with zeros
                    'ticker': company_ticker,
                    'company_name': company.get('title', f'Company {company_ticker}'),
                    'raw_cik': company['cik_str']
                })
                found_tickers.add(company_ticker)
                self.logger.info(f"✅ Found: {company_ticker} - {company.get('title')}")
        
        # Report missing tickers
        missing_tickers = set(target_tickers_upper) - found_tickers
        if missing_tickers:
            self.logger.warning(f"[FAILED] Could not find companies for: {list(missing_tickers)}")
            self.logger.info("These tickers may:")
            self.logger.info("  - Not exist or be delisted")
            self.logger.info("  - Be foreign companies not required to file with SEC")
            self.logger.info("  - Be ETFs, funds, or other non-corporate entities")
        
        self.logger.info(f"Successfully found {len(target_companies)} out of {len(target_tickers)} requested companies")
        return target_companies
    
    def get_company_submissions(self, cik: str) -> Optional[Dict]:
        """Get company submission data including recent filings"""
        url = f"{self.base_url}/submissions/CIK{cik}.json"
        self.logger.info(f"Fetching submissions for CIK {cik}")
        
        return self._make_request(url)
    
    def get_recent_filings(self, cik: str, forms: List[str] = None, limit: int = 10) -> List[Dict]:
        """Get recent filings for a company"""
        if forms is None:
            forms = ['10-K', '10-Q']
        
        submissions = self.get_company_submissions(cik)
        if not submissions:
            return []
        
        filings = []
        recent_filings = submissions.get('filings', {}).get('recent', {})
        
        if not recent_filings:
            self.logger.warning(f"No recent filings found for CIK {cik}")
            return []
        
        # Get the filing data
        forms_list = recent_filings.get('form', [])
        accession_numbers = recent_filings.get('accessionNumber', [])
        filing_dates = recent_filings.get('filingDate', [])
        primary_documents = recent_filings.get('primaryDocument', [])
        
        # Process filings
        for i, form in enumerate(forms_list):
            if form in forms and len(filings) < limit:
                filing_info = {
                    'cik': cik,
                    'form': form,
                    'accessionNumber': accession_numbers[i],
                    'filingDate': filing_dates[i],
                    'primaryDocument': primary_documents[i] if i < len(primary_documents) else None
                }
                filings.append(filing_info)
        
        self.logger.info(f"Found {len(filings)} recent filings for CIK {cik}")
        return filings
    
    def get_company_concept_data(self, cik: str, taxonomy: str = "us-gaap", tag: str = "Revenues") -> Optional[Dict]:
        """Get company concept data (specific financial metric over time)"""
        url = f"{self.base_url}/api/xbrl/companyconcept/CIK{cik}/{taxonomy}/{tag}.json"
        self.logger.debug(f"Fetching concept data: {taxonomy}:{tag} for CIK {cik}")
        
        return self._make_request(url)
    
    def get_company_facts(self, cik: str) -> Optional[Dict]:
        """Get all reported facts for a company"""
        url = f"{self.base_url}/api/xbrl/companyfacts/CIK{cik}.json"
        self.logger.info(f"Fetching company facts for CIK {cik}")
        
        return self._make_request(url)
    
    def extract_financial_metrics(self, company_facts: Dict, cik: str) -> List[Dict]:
        """Extract key financial metrics from company facts"""
        if not company_facts:
            return []
        
        financial_data = []
        
        # Get facts data
        facts = company_facts.get('facts', {})
        us_gaap = facts.get('us-gaap', {})
        
        # Common financial metrics and their possible SEC names
        metric_mappings = {
            'revenue': ['Revenues', 'RevenueFromContractWithCustomerExcludingAssessedTax', 'SalesRevenueNet'],
            'net_income': ['NetIncomeLoss', 'ProfitLoss'],
            'total_assets': ['Assets'],
            'stockholders_equity': ['StockholdersEquity'],
            'operating_income': ['OperatingIncomeLoss'],
            'eps_basic': ['EarningsPerShareBasic'],
            'eps_diluted': ['EarningsPerShareDiluted'],
            'current_assets': ['AssetsCurrent'],
            'current_liabilities': ['LiabilitiesCurrent'],
            'total_liabilities': ['Liabilities'],
            'operating_cash_flow': ['NetCashProvidedByUsedInOperatingActivities']
        }
        
        # Collect all unique filing periods
        all_periods = set()
        for metric_name, sec_names in metric_mappings.items():
            for sec_name in sec_names:
                if sec_name in us_gaap:
                    for unit_type, unit_data in us_gaap[sec_name].get('units', {}).items():
                        if unit_type in ['USD', 'USD/shares']:  # Focus on USD values
                            for entry in unit_data:
                                if entry.get('form') in ['10-K', '10-Q']:
                                    period_key = (entry.get('end'), entry.get('form'), entry.get('fy'))
                                    all_periods.add(period_key)
        
        # For each period, collect all available metrics
        for period_end, form_type, fiscal_year in all_periods:
            if not all([period_end, form_type, fiscal_year]):
                continue
                
            financial_record = {
                'cik': cik,
                'period_end_date': period_end,
                'form_type': form_type,
                'fiscal_year': fiscal_year,
                'filing_date': None  # Will be filled from first available metric
            }
            
            # Extract each metric for this period
            for metric_name, sec_names in metric_mappings.items():
                value = None
                filing_date = None
                
                for sec_name in sec_names:
                    if sec_name in us_gaap:
                        units = us_gaap[sec_name].get('units', {})
                        
                        # Try USD first, then USD/shares
                        for unit_type in ['USD', 'USD/shares']:
                            if unit_type in units:
                                for entry in units[unit_type]:
                                    if (entry.get('end') == period_end and 
                                        entry.get('form') == form_type and 
                                        entry.get('fy') == fiscal_year):
                                        value = entry.get('val')
                                        filing_date = entry.get('filed')
                                        break
                            if value is not None:
                                break
                    if value is not None:
                        break
                
                financial_record[metric_name] = value
                if filing_date and not financial_record['filing_date']:
                    financial_record['filing_date'] = filing_date
            
            # Only add record if we have at least some financial data
            if any(financial_record.get(metric) for metric in metric_mappings.keys()):
                financial_data.append(financial_record)
        
        self.logger.info(f"Extracted {len(financial_data)} financial records for CIK {cik}")
        return financial_data
    
    def collect_company_data(self, tickers: List[str]) -> Dict[str, List[Dict]]:
        """Main method to collect all data for specified tickers"""
        self.logger.info(f"Starting data collection for tickers: {tickers}")
        
        # Find companies using dynamic lookup
        companies = self.find_companies_by_tickers(tickers)
        if not companies:
            self.logger.error("No companies found for specified tickers")
            return {'companies': [], 'financial_data': []}
        
        all_financial_data = []
        
        for company in companies:
            self.logger.info(f"Processing {company['ticker']} (CIK: {company['cik']})")
            
            try:
                # Get company facts (comprehensive financial data)
                company_facts = self.get_company_facts(company['cik'])
                
                if company_facts:
                    # Extract financial metrics
                    financial_data = self.extract_financial_metrics(company_facts, company['cik'])
                    all_financial_data.extend(financial_data)
                    
                    self.logger.info(f"Collected {len(financial_data)} records for {company['ticker']}")
                else:
                    self.logger.warning(f"No facts data available for {company['ticker']}")
                
            except Exception as e:
                self.logger.error(f"Error processing {company['ticker']}: {e}")
                continue
        
        self.logger.info(f"Data collection complete. Total records: {len(all_financial_data)}")
        
        return {
            'companies': companies,
            'financial_data': all_financial_data
        }