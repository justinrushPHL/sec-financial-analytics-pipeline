# config/config.py
import os
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
EXPORTS_DIR = PROJECT_ROOT / "exports"
SQL_DIR = PROJECT_ROOT / "sql"

# Database
DATABASE_PATH = DATA_DIR / "financial_data.db"

# SEC API Configuration
SEC_BASE_URL = "https://data.sec.gov"
SEC_HEADERS = {
    "User-Agent": "Financial Analytics Pipeline justin.rush8612@gmail.com",  # CHANGE THIS!
    "Accept-Encoding": "gzip, deflate",
    "Host": "data.sec.gov"
}

# Rate limiting (SEC allows 10 requests per second)
REQUEST_DELAY = 0.1  # seconds between requests

# Target companies for initial testing
INITIAL_TICKERS = [
    "AAPL",  # Apple
    "MSFT",  # Microsoft  
    "GOOGL", # Alphabet
    "AMZN",  # Amazon
    "TSLA",  # Tesla
    "NVDA",  # Nvidia
    "META",  # Meta
    "NFLX",  # Netflix
]

# Financial metrics to extract
FINANCIAL_METRICS = {
    # Income Statement
    "revenue": ["Revenues", "Revenue", "TotalRevenues", "SalesRevenueNet"],
    "cost_of_revenue": ["CostOfRevenue", "CostOfGoodsAndServicesSold"],
    "gross_profit": ["GrossProfit"],
    "operating_income": ["OperatingIncomeLoss", "IncomeLossFromContinuingOperations"],
    "net_income": ["NetIncomeLoss", "ProfitLoss"],
    "eps_basic": ["EarningsPerShareBasic"],
    "eps_diluted": ["EarningsPerShareDiluted"],
    
    # Balance Sheet
    "total_assets": ["Assets"],
    "current_assets": ["AssetsCurrent"],
    "total_liabilities": ["Liabilities"],
    "current_liabilities": ["LiabilitiesCurrent"],
    "stockholders_equity": ["StockholdersEquity"],
    
    # Cash Flow
    "operating_cash_flow": ["NetCashProvidedByUsedInOperatingActivities"],
    "investing_cash_flow": ["NetCashProvidedByUsedInInvestingActivities"],
    "financing_cash_flow": ["NetCashProvidedByUsedInFinancingActivities"],
}

# Ensure directories exist
for directory in [DATA_DIR, RAW_DATA_DIR, EXPORTS_DIR, SQL_DIR]:
    directory.mkdir(parents=True, exist_ok=True)