#!/usr/bin/env python3
"""
Quick database viewer and query runner
Usage: python view_data.py [query_number]
"""

import sqlite3
import pandas as pd
import sys
from pathlib import Path

# Add to path for imports
sys.path.append('.')
from config.config import DATABASE_PATH

def run_query(query_num=None):
    """Run a predefined query or show options"""
    
    queries = {
        1: {
            "name": "Latest Revenue by Company",
            "sql": """
                SELECT 
                    c.ticker,
                    c.company_name,
                    fs.fiscal_year,
                    ROUND(fs.revenue / 1000000000.0, 2) as revenue_billions,
                    fs.filing_date
                FROM financial_statements fs
                JOIN companies c ON fs.cik = c.cik
                WHERE fs.form_type = '10-K' 
                    AND fs.revenue IS NOT NULL
                    AND fs.fiscal_year = (
                        SELECT MAX(fiscal_year) 
                        FROM financial_statements fs2 
                        WHERE fs2.cik = fs.cik AND fs2.form_type = '10-K'
                    )
                ORDER BY fs.revenue DESC;
            """
        },
        2: {
            "name": "Profitability Comparison",
            "sql": """
                SELECT 
                    c.ticker,
                    fs.fiscal_year,
                    ROUND(fs.revenue / 1000000.0, 2) as revenue_millions,
                    ROUND(fs.net_income / 1000000.0, 2) as net_income_millions,
                    CASE 
                        WHEN fs.revenue > 0 THEN ROUND((fs.net_income * 100.0 / fs.revenue), 2)
                        ELSE NULL 
                    END as net_margin_percent
                FROM financial_statements fs
                JOIN companies c ON fs.cik = c.cik
                WHERE fs.form_type = '10-K' 
                    AND fs.revenue > 0 
                    AND fs.net_income IS NOT NULL
                    AND fs.fiscal_year >= 2022
                ORDER BY net_margin_percent DESC;
            """
        },
        3: {
            "name": "Data Summary",
            "sql": """
                SELECT 
                    c.ticker,
                    COUNT(*) as total_records,
                    COUNT(CASE WHEN fs.form_type = '10-K' THEN 1 END) as annual_reports,
                    MIN(fs.fiscal_year) as earliest_year,
                    MAX(fs.fiscal_year) as latest_year
                FROM companies c
                LEFT JOIN financial_statements fs ON c.cik = fs.cik
                GROUP BY c.ticker
                ORDER BY c.ticker;
            """
        }
    }
    
    if not DATABASE_PATH.exists():
        print("❌ Database not found. Please run 'python main.py' first.")
        return
    
    if query_num is None:
        print("Available queries:")
        for num, query in queries.items():
            print(f"{num}. {query['name']}")
        print("\nUsage: python view_data.py [query_number]")
        print("Example: python view_data.py 1")
        return
    
    if query_num not in queries:
        print(f"❌ Query {query_num} not found. Available: {list(queries.keys())}")
        return
    
    print(f"Running: {queries[query_num]['name']}")
    print("="*50)
    
    try:
        with sqlite3.connect(DATABASE_PATH) as conn:
            df = pd.read_sql_query(queries[query_num]['sql'], conn)
            
            if df.empty:
                print("No data found. The database might be empty.")
            else:
                print(df.to_string(index=False))
                print(f"\nTotal rows: {len(df)}")
    
    except Exception as e:
        print(f"❌ Error running query: {e}")

def show_database_info():
    """Show basic database information"""
    if not DATABASE_PATH.exists():
        print("❌ Database not found.")
        return
    
    try:
        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.cursor()
            
            # Get table info
            cursor.execute("SELECT COUNT(*) FROM companies")
            company_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM financial_statements")
            statement_count = cursor.fetchone()[0]
            
            print(f"📊 Database Info:")
            print(f"   Companies: {company_count}")
            print(f"   Financial Statements: {statement_count}")
            
            if statement_count > 0:
                cursor.execute("SELECT MIN(fiscal_year), MAX(fiscal_year) FROM financial_statements")
                year_range = cursor.fetchone()
                print(f"   Year Range: {year_range[0]} - {year_range[1]}")
    
    except Exception as e:
        print(f"❌ Error reading database: {e}")

def main():
    print("SEC Financial Analytics - Database Viewer")
    print("="*50)
    
    show_database_info()
    print()
    
    if len(sys.argv) > 1:
        try:
            query_num = int(sys.argv[1])
            run_query(query_num)
        except ValueError:
            print("❌ Please provide a valid query number")
    else:
        run_query()

if __name__ == "__main__":
    main()
