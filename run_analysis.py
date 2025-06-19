#!/usr/bin/env python3
"""
Simple Master Financial Analytics Pipeline
Runs all components directly without subprocess issues
"""

import logging
import sys
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.append(str(Path(__file__).parent / 'src'))
sys.path.append(str(Path(__file__).parent))

def setup_logging():
    """Setup logging configuration"""
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=[
            logging.FileHandler('simple_master_pipeline.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )

def run_data_collection():
    """Run the interactive data collection"""
    print("🔍 STEP 1: DATA COLLECTION")
    print("=" * 50)
    
    try:
        # Import and run the interactive_init main function
        import interactive_init
        success = interactive_init.main()
        return success
    except Exception as e:
        print(f"❌ Data collection failed: {e}")
        return False

def run_investment_analysis():
    """Run the investment algorithm analysis"""
    print("\n🧠 STEP 2: INVESTMENT ALGORITHM ANALYSIS")
    print("=" * 50)
    
    try:
        # Import and run export_advanced_analytics
        import export_advanced_analytics
        # Assuming it has a main function, otherwise we'll run the whole module
        if hasattr(export_advanced_analytics, 'main'):
            success = export_advanced_analytics.main()
        else:
            # If no main function, just importing runs the script
            print("✅ Investment analysis completed!")
            success = True
        return success
    except Exception as e:
        print(f"❌ Investment analysis failed: {e}")
        return False

def run_analyst_ratings():
    """Run the Wall Street analyst ratings collection"""
    print("\n📈 STEP 3: WALL STREET ANALYST RATINGS")
    print("=" * 50)
    
    try:
        import get_analyst_ratings
        get_analyst_ratings.main()
        print("✅ Analyst ratings completed successfully!")
        return True  # Always return True since the function completed
    except Exception as e:
        print(f"❌ Analyst ratings failed: {e}")
        return False

def main():
    """Run the complete pipeline"""
    setup_logging()
    
    start_time = datetime.now()
    
    print("🏦 SIMPLE MASTER FINANCIAL ANALYTICS PIPELINE")
    print("=" * 80)
    print("This will run the complete pipeline:")
    print("  1️⃣  Data Collection (interactive_init.py)")
    print("  2️⃣  Investment Analysis (export_advanced_analytics.py)")
    print("  3️⃣  Wall Street Comparison (get_analyst_ratings.py)")
    print("=" * 80)
    
    # Step 1: Data Collection (Interactive)
    success_1 = run_data_collection()
    
    if not success_1:
        print("\n❌ Data collection failed - cannot continue")
        return False
    
    print("\n✅ Data collection successful! Moving to analysis...")
    
    # Step 2: Investment Analysis
    success_2 = run_investment_analysis()
    
    if success_2:
        print("✅ Investment analysis successful!")
    else:
        print("⚠️  Investment analysis had issues, continuing...")
    
    # Step 3: Analyst Ratings
    success_3 = run_analyst_ratings()
    
    if success_3:
        print("✅ Analyst ratings successful!")
    else:
        print("⚠️  Analyst ratings had issues")
    
    # Final Summary
    end_time = datetime.now()
    duration = end_time - start_time
    
    print("\n" + "=" * 80)
    print("🏁 PIPELINE COMPLETE!")
    print("=" * 80)
    print(f"⏰ Total runtime: {duration}")
    
    print("\n📊 RESULTS:")
    print(f"  Data Collection: {'✅ SUCCESS' if success_1 else '❌ FAILED'}")
    print(f"  Investment Analysis: {'✅ SUCCESS' if success_2 else '⚠️ ISSUES'}")
    print(f"  Analyst Ratings: {'✅ SUCCESS' if success_3 else '⚠️ ISSUES'}")
    
    print("\n📁 CHECK YOUR EXPORTS FOLDER:")
    print("  📄 exports/financial_data_*.csv")
    print("  📄 exports/advanced_analytics/investment_recommendations_*.csv")
    print("  📄 exports/advanced_analytics/analyst_ratings_*.csv")
    
    print("\n🎯 READY FOR POWER BI!")
    print("Your 'Algorithm vs Wall Street' comparison awaits! 📊")
    
    return success_1  # Success if at least data collection worked

if __name__ == "__main__":
    success = main()
    
    if success:
        print("\n🎉 Master pipeline completed successfully!")
    else:
        print("\n💥 Pipeline failed")
    
    input("\nPress Enter to exit...")
    sys.exit(0 if success else 1)