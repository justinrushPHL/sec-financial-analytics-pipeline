#!/usr/bin/env python3
"""
SEC Financial Analytics Pipeline
Main script to run the complete data collection and processing pipeline
"""

import logging
import sys
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.append(str(Path(__file__).parent / 'src'))
sys.path.append(str(Path(__file__).parent))

from src.data_collector import SECDataCollector
from src.database_manager import DatabaseManager
from config.config import (
    DATABASE_PATH, 
    EXPORTS_DIR, 
    INITIAL_TICKERS,
    PROJECT_ROOT
)

def setup_logging():
    """Setup logging configuration"""
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=[
            logging.FileHandler(PROJECT_ROOT / 'pipeline.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )

def main():
    """Main pipeline execution"""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    logger.info("="*60)
    logger.info("SEC Financial Analytics Pipeline Starting")
    logger.info("="*60)
    
    try:
        # Initialize components
        collector = SECDataCollector()
        db_manager = DatabaseManager(DATABASE_PATH)
        
        # Step 1: Collect data from SEC
        logger.info("Step 1: Collecting data from SEC EDGAR API...")
        data = collector.collect_company_data(INITIAL_TICKERS)
        
        companies = data['companies']
        financial_data = data['financial_data']
        
        if not companies:
            logger.error("No companies found! Check your tickers and try again.")
            return
        
        logger.info(f"Found {len(companies)} companies:")
        for company in companies:
            logger.info(f"  - {company['ticker']}: {company['company_name']}")
        
        # Step 2: Save companies to database
        logger.info("Step 2: Saving companies to database...")
        for company in companies:
            success = db_manager.insert_company(company)
            if not success:
                logger.warning(f"Failed to save company: {company['ticker']}")
        
        # Step 3: Save financial data to database  
        logger.info("Step 3: Saving financial data to database...")
        saved_count = 0
        for record in financial_data:
            success = db_manager.insert_financial_statement(record)
            if success:
                saved_count += 1
        
        logger.info(f"Saved {saved_count}/{len(financial_data)} financial records")
        
        # Step 4: Generate database statistics
        logger.info("Step 4: Database statistics...")
        stats = db_manager.get_database_stats()
        logger.info(f"Database contains:")
        logger.info(f"  - {stats['companies']} companies")
        logger.info(f"  - {stats['financial_statements']} financial statements")
        if stats['date_range'][0] and stats['date_range'][1]:
            logger.info(f"  - Date range: {stats['date_range'][0]} to {stats['date_range'][1]}")
        
        # Step 5: Export data for Power BI
        logger.info("Step 5: Exporting data for Power BI...")
        export_file = EXPORTS_DIR / f"financial_data_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        df = db_manager.export_for_powerbi(export_file)
        
        logger.info(f"Exported {len(df)} records to {export_file}")
        
        # Step 6: Show sample data
        logger.info("Step 6: Sample of exported data:")
        if not df.empty:
            print("\nSample records:")
            print(df.head(3).to_string(index=False))
            
            print(f"\nAvailable columns: {list(df.columns)}")
            print(f"Companies in dataset: {df['ticker'].unique()}")
            print(f"Date range: {df['filing_date'].min()} to {df['filing_date'].max()}")
        
        logger.info("="*60)
        logger.info("Pipeline completed successfully!")
        logger.info("="*60)
        logger.info("Next steps:")
        logger.info("1. Review the exported CSV file in the exports/ directory")
        logger.info("2. Import the CSV into Power BI")
        logger.info("3. Create your dashboard visualizations")
        logger.info("4. Run SQL queries against the SQLite database for analysis")
        
    except KeyboardInterrupt:
        logger.info("Pipeline interrupted by user")
    except Exception as e:
        logger.error(f"Pipeline failed with error: {e}")
        logger.exception("Full error details:")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)