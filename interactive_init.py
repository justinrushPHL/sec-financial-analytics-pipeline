#!/usr/bin/env python3
"""
Interactive SEC Financial Analytics Pipeline
Prompts user for company selection, then runs the complete pipeline
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

def prompt_for_tickers():
    """Interactive prompt for ticker selection"""
    print("="*80)
    print("SEC FINANCIAL ANALYTICS PIPELINE - INTERACTIVE SETUP")
    print("="*80)
    
    print("\nExample Companies:")
    print("-" * 50)
    print("  AAPL   - Apple Inc.")
    print("  MSFT   - Microsoft Corp")
    print("  GOOGL  - Alphabet Inc.")
    print("  AMZN   - Amazon.com Inc")
    print("  TSLA   - Tesla Inc")
    
    print("\nEnter any valid stock ticker symbols (e.g., AAPL MSFT WK GOOGL)")
    print("The system will validate against SEC database automatically.")
    print("You can select up to 8 companies for analysis.")
    print("Or type 'default' to use popular tech stocks")
    
    while True:
        user_input = input("\nEnter tickers: ").strip().upper()
        
        if not user_input:
            print("❌ Please enter some ticker symbols")
            continue
        
        if user_input == 'DEFAULT':
            selected_tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA', 'META', 'NFLX']
            print(f"✅ Using default tickers: {selected_tickers}")
            break
        
        # Parse tickers
        tickers = user_input.split()
        
        # Limit to 8
        if len(tickers) > 8:
            print(f"❌ Too many tickers ({len(tickers)}). Maximum is 8.")
            tickers = tickers[:8]
            print(f"🔧 Using first 8: {tickers}")
        
        selected_tickers = tickers
        print(f"✅ Selected {len(selected_tickers)} companies: {selected_tickers}")
        print("📡 Note: SEC API will validate these tickers automatically")
        
        confirm = input(f"\nProceed with these {len(selected_tickers)} companies? (y/n): ").lower()
        if confirm == 'y':
            break
        # If 'n', loop continues for new input
    
    return selected_tickers

def run_pipeline(selected_tickers):
    """Run the complete pipeline with selected tickers"""
    logger = logging.getLogger(__name__)
    
    logger.info("="*60)
    logger.info("SEC Financial Analytics Pipeline Starting")
    logger.info(f"Selected Tickers: {selected_tickers}")
    logger.info("="*60)
    
    try:
        # Step 0: Clear existing database BEFORE initializing anything
        logger.info("Step 0: Clearing existing database for fresh analysis...")
        try:
            # Delete the entire database file for guaranteed fresh start
            if DATABASE_PATH.exists():
                DATABASE_PATH.unlink()  # Delete the file
                logger.info("[SUCCESS] Old database deleted successfully")
            else:
                logger.info("ℹ️  No existing database found - creating fresh")
        except Exception as e:
            logger.warning(f"Database deletion failed: {e}")
            logger.info("Continuing anyway...")
        
        # Initialize components AFTER database deletion
        collector = SECDataCollector()
        db_manager = DatabaseManager(DATABASE_PATH)
        
        # Step 1: Collect data from SEC
        logger.info("Step 1: Collecting data from SEC EDGAR API...")
        data = collector.collect_company_data(selected_tickers)
        
        companies = data['companies']
        financial_data = data['financial_data']
        
        if not companies:
            logger.error("No companies found! Check your tickers and try again.")
            logger.error("The tickers you entered may not exist or have no SEC filings.")
            return False
        
        logger.info(f"Found {len(companies)} companies:")
        for company in companies:
            logger.info(f"  - {company['ticker']}: {company['company_name']}")
        
        # Show which tickers (if any) had no data
        found_tickers = [company['ticker'] for company in companies]
        missing_tickers = [ticker for ticker in selected_tickers if ticker not in found_tickers]
        if missing_tickers:
            logger.warning(f"No SEC data found for: {missing_tickers}")
            logger.warning("These companies may not exist or have no recent SEC filings")
        
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
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        tickers_str = "_".join(found_tickers)  # Use only found tickers for filename
        
        # Save timestamped version
        export_file = EXPORTS_DIR / f"financial_data_{tickers_str}_{timestamp}.csv"
        df = db_manager.export_for_powerbi(export_file)
        logger.info(f"📊 Exported timestamped: financial_data_{tickers_str}_{timestamp}.csv")
        
        # Save latest version (overwrites each time)
        latest_file = EXPORTS_DIR / f"financial_data_latest.csv"
        df.to_csv(latest_file, index=False)
        logger.info(f"📄 Exported latest: financial_data_latest.csv")
        
        logger.info(f"Exported {len(df)} records total")
        
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
        logger.info("1. Review the exported CSV files in the exports/ directory")
        logger.info("2. Run: python export_advanced_analytics.py")
        logger.info("3. Run: python get_analyst_ratings.py")
        logger.info("4. Import CSV files into Power BI for 'Algorithm vs Wall Street' analysis")
        
        return True
        
    except KeyboardInterrupt:
        logger.info("Pipeline interrupted by user")
        return False
    except Exception as e:
        logger.error(f"Pipeline failed with error: {e}")
        logger.exception("Full error details:")
        return False

def main():
    """Main execution function"""
    setup_logging()
    
    # Get user's ticker selection
    selected_tickers = prompt_for_tickers()
    
    # Run the pipeline
    success = run_pipeline(selected_tickers)
    
    if success:
        print("\n🎯 SUCCESS! Your financial database is ready.")
        print("\n📊 Database contains ONLY your selected companies")
        print("📊 Database Location: data/financial_data.db")
        print("📁 CSV Exports:")
        print("   • Timestamped: exports/financial_data_[tickers]_[timestamp].csv")
        print("   • Latest: exports/financial_data_latest.csv")
        print("\n🚀 Ready to run:")
        print("   python export_advanced_analytics.py")
        print("   python get_analyst_ratings.py")
        print("\n🎯 Power BI Ready Files (auto-updating):")
        print("   📈 financial_data_latest.csv")
        print("   📊 investment_recommendations_latest.csv")
        print("   📋 analyst_ratings_finnhub_latest.csv")
        print("\n💡 Note: If some tickers had no data, only companies with SEC filings were processed")
    else:
        print("\n❌ Pipeline failed. Check the logs for details.")
        print("💡 Common issues:")
        print("   - Invalid ticker symbols")
        print("   - Companies with no recent SEC filings")
        print("   - Network connectivity issues")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)