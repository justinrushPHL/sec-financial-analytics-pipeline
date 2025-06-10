# src/database_manager.py
import sqlite3
import pandas as pd
from pathlib import Path
import logging
from typing import List, Dict, Optional
from datetime import datetime

class DatabaseManager:
    """Manages SQLite database operations for financial data"""
    
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        self.init_database()
    
    def init_database(self):
        """Initialize database with required tables"""
        self.logger.info(f"Initializing database at {self.db_path}")
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Companies table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS companies (
                    cik TEXT PRIMARY KEY,
                    ticker TEXT NOT NULL UNIQUE,
                    company_name TEXT NOT NULL,
                    sic_code TEXT,
                    industry TEXT,
                    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Financial statements table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS financial_statements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cik TEXT NOT NULL,
                    filing_date DATE NOT NULL,
                    period_end_date DATE NOT NULL,
                    form_type TEXT NOT NULL,
                    fiscal_year INTEGER NOT NULL,
                    fiscal_quarter INTEGER,
                    
                    -- Income Statement (in actual dollars, not thousands)
                    revenue BIGINT,
                    cost_of_revenue BIGINT,
                    gross_profit BIGINT,
                    operating_expenses BIGINT,
                    operating_income BIGINT,
                    net_income BIGINT,
                    eps_basic DECIMAL(10,4),
                    eps_diluted DECIMAL(10,4),
                    shares_outstanding BIGINT,
                    
                    -- Balance Sheet
                    total_assets BIGINT,
                    current_assets BIGINT,
                    total_liabilities BIGINT,
                    current_liabilities BIGINT,
                    stockholders_equity BIGINT,
                    
                    -- Cash Flow
                    operating_cash_flow BIGINT,
                    investing_cash_flow BIGINT,
                    financing_cash_flow BIGINT,
                    free_cash_flow BIGINT,
                    
                    -- Metadata
                    accession_number TEXT,
                    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    
                    FOREIGN KEY (cik) REFERENCES companies(cik),
                    UNIQUE(cik, period_end_date, form_type)
                )
            ''')
            
            # Create indexes for performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_fs_cik_year ON financial_statements(cik, fiscal_year)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_fs_form_type ON financial_statements(form_type)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_fs_filing_date ON financial_statements(filing_date)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_companies_ticker ON companies(ticker)')
            
            conn.commit()
            self.logger.info("Database initialized successfully")
    
    def insert_company(self, company_data: Dict) -> bool:
        """Insert or update company data"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO companies 
                    (cik, ticker, company_name, sic_code, industry, updated_date)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    company_data['cik'],
                    company_data['ticker'],
                    company_data['company_name'],
                    company_data.get('sic_code'),
                    company_data.get('industry'),
                    datetime.now()
                ))
                conn.commit()
                self.logger.info(f"Inserted/updated company: {company_data['ticker']}")
                return True
        except Exception as e:
            self.logger.error(f"Error inserting company {company_data.get('ticker', 'Unknown')}: {e}")
            return False
    
    def insert_financial_statement(self, financial_data: Dict) -> bool:
        """Insert financial statement data"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO financial_statements 
                    (cik, filing_date, period_end_date, form_type, fiscal_year, fiscal_quarter,
                     revenue, cost_of_revenue, gross_profit, operating_income, net_income,
                     eps_basic, eps_diluted, total_assets, current_assets, total_liabilities,
                     current_liabilities, stockholders_equity, operating_cash_flow,
                     investing_cash_flow, financing_cash_flow, accession_number)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    financial_data['cik'],
                    financial_data['filing_date'],
                    financial_data['period_end_date'],
                    financial_data['form_type'],
                    financial_data['fiscal_year'],
                    financial_data.get('fiscal_quarter'),
                    financial_data.get('revenue'),
                    financial_data.get('cost_of_revenue'),
                    financial_data.get('gross_profit'),
                    financial_data.get('operating_income'),
                    financial_data.get('net_income'),
                    financial_data.get('eps_basic'),
                    financial_data.get('eps_diluted'),
                    financial_data.get('total_assets'),
                    financial_data.get('current_assets'),
                    financial_data.get('total_liabilities'),
                    financial_data.get('current_liabilities'),
                    financial_data.get('stockholders_equity'),
                    financial_data.get('operating_cash_flow'),
                    financial_data.get('investing_cash_flow'),
                    financial_data.get('financing_cash_flow'),
                    financial_data.get('accession_number')
                ))
                conn.commit()
                self.logger.info(f"Inserted financial data for CIK {financial_data['cik']}, "
                               f"period {financial_data['period_end_date']}")
                return True
        except Exception as e:
            self.logger.error(f"Error inserting financial data: {e}")
            return False
    
    def get_companies(self) -> pd.DataFrame:
        """Get all companies from database"""
        with sqlite3.connect(self.db_path) as conn:
            return pd.read_sql_query("SELECT * FROM companies ORDER BY ticker", conn)
    
    def get_financial_data(self, ticker: Optional[str] = None) -> pd.DataFrame:
        """Get financial data, optionally filtered by ticker"""
        query = '''
            SELECT c.ticker, c.company_name, fs.*
            FROM financial_statements fs
            JOIN companies c ON fs.cik = c.cik
        '''
        params = []
        
        if ticker:
            query += " WHERE c.ticker = ?"
            params.append(ticker)
        
        query += " ORDER BY c.ticker, fs.fiscal_year DESC, fs.filing_date DESC"
        
        with sqlite3.connect(self.db_path) as conn:
            return pd.read_sql_query(query, conn, params=params)
    
    def export_for_powerbi(self, output_path: Path) -> pd.DataFrame:
        """Export comprehensive dataset for Power BI"""
        query = '''
            SELECT 
                c.ticker,
                c.company_name,
                c.industry,
                fs.fiscal_year,
                fs.fiscal_quarter,
                fs.form_type,
                fs.filing_date,
                fs.period_end_date,
                
                -- Revenue metrics (convert to millions for readability)
                ROUND(fs.revenue / 1000000.0, 2) as revenue_millions,
                ROUND(fs.cost_of_revenue / 1000000.0, 2) as cost_of_revenue_millions,
                ROUND(fs.gross_profit / 1000000.0, 2) as gross_profit_millions,
                ROUND(fs.operating_income / 1000000.0, 2) as operating_income_millions,
                ROUND(fs.net_income / 1000000.0, 2) as net_income_millions,
                
                -- Per share metrics
                fs.eps_basic,
                fs.eps_diluted,
                
                -- Balance sheet (in millions)
                ROUND(fs.total_assets / 1000000.0, 2) as total_assets_millions,
                ROUND(fs.current_assets / 1000000.0, 2) as current_assets_millions,
                ROUND(fs.total_liabilities / 1000000.0, 2) as total_liabilities_millions,
                ROUND(fs.current_liabilities / 1000000.0, 2) as current_liabilities_millions,
                ROUND(fs.stockholders_equity / 1000000.0, 2) as stockholders_equity_millions,
                
                -- Cash flow (in millions)
                ROUND(fs.operating_cash_flow / 1000000.0, 2) as operating_cash_flow_millions,
                ROUND(fs.investing_cash_flow / 1000000.0, 2) as investing_cash_flow_millions,
                ROUND(fs.financing_cash_flow / 1000000.0, 2) as financing_cash_flow_millions,
                
                -- Calculated ratios
                CASE 
                    WHEN fs.revenue > 0 THEN ROUND((fs.net_income * 100.0 / fs.revenue), 2)
                    ELSE NULL 
                END as net_margin_percent,
                
                CASE 
                    WHEN fs.revenue > 0 THEN ROUND((fs.operating_income * 100.0 / fs.revenue), 2)
                    ELSE NULL 
                END as operating_margin_percent,
                
                CASE 
                    WHEN fs.current_liabilities > 0 THEN ROUND((fs.current_assets * 1.0 / fs.current_liabilities), 2)
                    ELSE NULL 
                END as current_ratio,
                
                CASE 
                    WHEN fs.total_assets > 0 THEN ROUND((fs.total_liabilities * 100.0 / fs.total_assets), 2)
                    ELSE NULL 
                END as debt_to_assets_percent
                
            FROM financial_statements fs
            JOIN companies c ON fs.cik = c.cik
            WHERE fs.revenue IS NOT NULL
            ORDER BY c.ticker, fs.fiscal_year DESC, fs.form_type
        '''
        
        with sqlite3.connect(self.db_path) as conn:
            df = pd.read_sql_query(query, conn)
        
        # Export to CSV
        df.to_csv(output_path, index=False)
        self.logger.info(f"Exported {len(df)} records to {output_path}")
        
        return df
    
    def get_database_stats(self) -> Dict:
        """Get database statistics"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Count companies
            cursor.execute("SELECT COUNT(*) FROM companies")
            company_count = cursor.fetchone()[0]
            
            # Count financial statements
            cursor.execute("SELECT COUNT(*) FROM financial_statements")
            statement_count = cursor.fetchone()[0]
            
            # Get date range
            cursor.execute("SELECT MIN(filing_date), MAX(filing_date) FROM financial_statements")
            date_range = cursor.fetchone()
            
            return {
                "companies": company_count,
                "financial_statements": statement_count,
                "date_range": date_range
            }