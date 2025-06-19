import requests
import pandas as pd
import time
import os
import sqlite3
from datetime import datetime

# Your API configuration
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Your API configuration
API_KEY = os.getenv("FINNHUB_API_KEY")
if not API_KEY:
    raise ValueError("Please add FINNHUB_API_KEY to your .env file")
BASE_URL = "https://finnhub.io/api/v1"

# Define output directory
output_dir = r"C:\Users\Justin\Desktop\Python Projects\sec-financial-analytics-pipeline\exports\advanced_analytics"

# Create directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

def safe_round(value, decimals=2):
    """Safely round a value, handling None and non-numeric values"""
    try:
        if value is None or value == 0:
            return 0
        return round(float(value), decimals)
    except (TypeError, ValueError):
        return 0

def safe_get(data, key, default=0):
    """Safely get a value from a dictionary, handling None values"""
    if not data:
        return default
    value = data.get(key, default)
    return value if value is not None else default

def get_tickers_from_database():
    """Get tickers from the SQLite database (same companies as your investment recommendations)"""
    db_path = r'C:\Users\Justin\Desktop\Python Projects\sec-financial-analytics-pipeline\data\financial_data.db'
    
    try:
        conn = sqlite3.connect(db_path)
        
        # Get unique tickers from the companies table
        query = "SELECT DISTINCT ticker FROM companies ORDER BY ticker"
        df = pd.read_sql_query(query, conn)
        tickers = df['ticker'].tolist()
        
        conn.close()
        
        print(f"📊 Found {len(tickers)} companies in database: {tickers}")
        return tickers
        
    except Exception as e:
        print(f"❌ Error reading database: {e}")
        print("📝 Using fallback tickers...")
        # Updated fallback to your NYSE stocks
        return ['JPM', 'JNJ', 'XOM', 'BA', 'T', 'GE', 'F', 'MMM']

def get_analyst_recommendations(symbol):
    """Fetch analyst recommendations for a given symbol"""
    url = f"{BASE_URL}/stock/recommendation?symbol={symbol}&token={API_KEY}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        if data and len(data) > 0:
            # Get the most recent recommendation data
            latest = data[0]  # Finnhub returns data sorted by date
            
            return {
                'ticker': symbol,
                'buy_ratings': safe_get(latest, 'buy', 0),
                'hold_ratings': safe_get(latest, 'hold', 0),
                'sell_ratings': safe_get(latest, 'sell', 0),
                'strongBuy_ratings': safe_get(latest, 'strongBuy', 0),
                'strongSell_ratings': safe_get(latest, 'strongSell', 0),
                'period': safe_get(latest, 'period', 'N/A')
            }
    except Exception as e:
        print(f"❌ Error fetching recommendations for {symbol}: {e}")
        return None

def get_current_price(symbol):
    """Fetch current stock price and extended daily performance"""
    url = f"{BASE_URL}/quote?symbol={symbol}&token={API_KEY}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        # Get basic price data
        current_price = safe_get(data, 'c', 0)
        previous_close = safe_get(data, 'pc', 0)
        day_high = safe_get(data, 'h', 0)
        day_low = safe_get(data, 'l', 0)
        
        return {
            'current_price': current_price,
            'previous_close': previous_close,
            'day_change': safe_get(data, 'd', 0),
            'day_change_percent': safe_get(data, 'dp', 0),
            'day_high': day_high,
            'day_low': day_low,
            'day_open': safe_get(data, 'o', 0),
            'volume': safe_get(data, 'v', 0)
        }
    except Exception as e:
        print(f"❌ Error fetching price for {symbol}: {e}")
        return None

def get_basic_metrics(symbol):
    """Fetch basic financial metrics (beta, market cap, etc.)"""
    url = f"{BASE_URL}/stock/metric?symbol={symbol}&metric=all&token={API_KEY}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        # Extract key metrics from the response
        metric = data.get('metric', {}) if data else {}
        
        return {
            'beta': safe_get(metric, 'beta', 0),
            'market_cap': safe_get(metric, 'marketCapitalization', 0),
            'pe_ratio': safe_get(metric, 'peNormalizedAnnual', 0),
            'price_to_book': safe_get(metric, 'pbAnnual', 0),
            'dividend_yield': safe_get(metric, 'dividendYieldIndicatedAnnual', 0),
            'roe': safe_get(metric, 'roeTTM', 0),
            'debt_to_equity': safe_get(metric, 'totalDebt/totalEquityAnnual', 0),
            'week_52_high': safe_get(metric, '52WeekHigh', 0),
            'week_52_low': safe_get(metric, '52WeekLow', 0)
        }
    except Exception as e:
        print(f"❌ Error fetching metrics for {symbol}: {e}")
        return None

def main():
    print("🔍 Getting your company list from database...")
    
    # Get tickers from database (same as your investment recommendations)
    tickers = get_tickers_from_database()
    
    print(f"\n📈 Fetching comprehensive Wall Street data for {len(tickers)} companies...")
    print("🎯 Getting: Analyst Ratings + Current Prices + Financial Metrics")
    print("=" * 80)
    
    # Collect data for all tickers
    results = []
    current_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    for i, ticker in enumerate(tickers, 1):
        print(f"[{i}/{len(tickers)}] Fetching comprehensive data for {ticker}...")
        
        # Get all three data sources
        recommendations = get_analyst_recommendations(ticker)
        current_price_data = get_current_price(ticker)
        metrics_data = get_basic_metrics(ticker)
        
        if recommendations:
            # Calculate totals and percentages
            total_analysts = (recommendations['buy_ratings'] +
                            recommendations['hold_ratings'] +
                            recommendations['sell_ratings'] +
                            recommendations['strongBuy_ratings'] +
                            recommendations['strongSell_ratings'])
            
            total_buy = recommendations['buy_ratings'] + recommendations['strongBuy_ratings']
            total_sell = recommendations['sell_ratings'] + recommendations['strongSell_ratings']
            buy_percentage = (total_buy / total_analysts * 100) if total_analysts > 0 else 0
            
            # Determine consensus
            if buy_percentage >= 60:
                consensus = "BUY"
            elif buy_percentage >= 40:
                consensus = "HOLD"
            else:
                consensus = "SELL"
            
            # Extract data safely
            current_price = safe_get(current_price_data, 'current_price', 0)
            beta = safe_get(metrics_data, 'beta', 0)
            market_cap = safe_get(metrics_data, 'market_cap', 0)
            week_52_high = safe_get(metrics_data, 'week_52_high', 0)
            week_52_low = safe_get(metrics_data, 'week_52_low', 0)
            
            # Calculate 52-week positioning
            distance_from_high = ((current_price - week_52_high) / week_52_high * 100) if week_52_high > 0 and current_price > 0 else 0
            distance_from_low = ((current_price - week_52_low) / week_52_low * 100) if week_52_low > 0 and current_price > 0 else 0
            
            # 🎯 COMPREHENSIVE RESULT: Include ALL data for Power BI
            result = {
                'ticker': ticker,
                'company_name': ticker,
                'wall_street_consensus': consensus,
                
                # 📊 INDIVIDUAL ANALYST RATINGS (Perfect for Power BI charts!)
                'strong_buy_count': recommendations['strongBuy_ratings'],
                'buy_count': recommendations['buy_ratings'], 
                'hold_count': recommendations['hold_ratings'],
                'sell_count': recommendations['sell_ratings'],
                'strong_sell_count': recommendations['strongSell_ratings'],
                
                # 📈 AGGREGATED RATING TOTALS
                'total_buy_ratings': total_buy,
                'total_sell_ratings': total_sell,
                'total_analysts': total_analysts,
                'buy_percentage': safe_round(buy_percentage, 1),
                
                # 🚀 CURRENT PRICE DATA
                'current_price': safe_round(current_price, 2),
                'previous_close': safe_round(safe_get(current_price_data, 'previous_close', 0), 2),
                'day_change': safe_round(safe_get(current_price_data, 'day_change', 0), 2),
                'day_change_percent': safe_round(safe_get(current_price_data, 'day_change_percent', 0), 2),
                'day_high': safe_round(safe_get(current_price_data, 'day_high', 0), 2),
                'day_low': safe_round(safe_get(current_price_data, 'day_low', 0), 2),
                'day_open': safe_round(safe_get(current_price_data, 'day_open', 0), 2),
                'volume': safe_get(current_price_data, 'volume', 0),
                
                # 📊 52-WEEK RANGE DATA
                'week_52_high': safe_round(week_52_high, 2),
                'week_52_low': safe_round(week_52_low, 2),
                'distance_from_52w_high': safe_round(distance_from_high, 1),
                'distance_from_52w_low': safe_round(distance_from_low, 1),
                
                # 💼 FINANCIAL METRICS
                'beta': safe_round(beta, 2),
                'market_cap': safe_round(market_cap / 1000, 1) if market_cap > 0 else 0,  # Convert to billions
                'pe_ratio': safe_round(safe_get(metrics_data, 'pe_ratio', 0), 1),
                'price_to_book': safe_round(safe_get(metrics_data, 'price_to_book', 0), 2),
                'dividend_yield': safe_round(safe_get(metrics_data, 'dividend_yield', 0), 2),
                'roe': safe_round(safe_get(metrics_data, 'roe', 0), 1),
                'debt_to_equity': safe_round(safe_get(metrics_data, 'debt_to_equity', 0), 2),
                
                # 📅 METADATA
                'period': recommendations['period'],
                'timestamp': current_timestamp
            }
            
            results.append(result)
            
            # Enhanced status reporting
            price_str = f"${current_price:.2f}" if current_price > 0 else "N/A"
            change_str = f"{safe_get(current_price_data, 'day_change_percent', 0):+.1f}%" if current_price_data else "N/A"
            beta_str = f"β{beta:.2f}" if beta > 0 else "N/A"
            mcap_str = f"${market_cap/1000:.1f}B" if market_cap > 0 else "N/A"
            high_distance = distance_from_high
            
            print(f"✅ {ticker}: {consensus} | Price: {price_str} ({change_str}) | Beta: {beta_str} | MCap: {mcap_str}")
            print(f"   📊 Analysts: {total_analysts} total, {buy_percentage:.1f}% BUY | 52W High: {high_distance:+.1f}%")
            print(f"   📈 [{recommendations['strongBuy_ratings']}|{recommendations['buy_ratings']}|{recommendations['hold_ratings']}|{recommendations['sell_ratings']}|{recommendations['strongSell_ratings']}]")
        else:
            print(f"⚠️  {ticker}: No analyst data available")
        
        # Rate limiting - wait 2 seconds between tickers (3 API calls per ticker)
        time.sleep(2)
    
    # Convert to DataFrame
    df = pd.DataFrame(results)
    
    if not df.empty:
        print("\n" + "=" * 120)
        print("📊 COMPREHENSIVE WALL STREET DATA SUMMARY:")
        print("=" * 120)
        
        # Enhanced summary with key metrics
        summary_df = df[['ticker', 'wall_street_consensus', 'current_price', 'day_change_percent', 
                        'beta', 'market_cap', 'distance_from_52w_high', 'total_analysts', 'buy_percentage']]
        
        print(summary_df.to_string(index=False))
        
        # Market performance summary
        print("\n" + "=" * 120)
        print("🚀 MARKET PERFORMANCE & RISK SUMMARY:")
        print("=" * 120)
        
        # Calculate averages safely
        beta_values = df[df['beta'] > 0]['beta']
        day_change_values = df[df['day_change_percent'] != 0]['day_change_percent']
        high_distance_values = df[df['distance_from_52w_high'] != 0]['distance_from_52w_high']
        
        avg_beta = beta_values.mean() if len(beta_values) > 0 else 0
        avg_day_change = day_change_values.mean() if len(day_change_values) > 0 else 0
        avg_distance_high = high_distance_values.mean() if len(high_distance_values) > 0 else 0
        high_beta_count = len(df[df['beta'] > 1.5])
        
        print(f"Average Beta (Market Risk): {avg_beta:.2f}")
        print(f"Average Daily Performance: {avg_day_change:+.1f}%")
        print(f"Average Distance from 52W High: {avg_distance_high:+.1f}%")
        print(f"High Beta Stocks (>1.5): {high_beta_count}/{len(df)}")
        
        # Analyst sentiment summary
        print("\n" + "=" * 120)
        print("🌟 OVERALL ANALYST SENTIMENT ACROSS ALL COMPANIES:")
        print("=" * 120)
        total_strong_buy = df['strong_buy_count'].sum()
        total_buy = df['buy_count'].sum()
        total_hold = df['hold_count'].sum()
        total_sell = df['sell_count'].sum()
        total_strong_sell = df['strong_sell_count'].sum()
        grand_total = df['total_analysts'].sum()
        
        print(f"Strong Buy: {total_strong_buy:>3} | Buy: {total_buy:>3} | Hold: {total_hold:>3} | Sell: {total_sell:>3} | Strong Sell: {total_strong_sell:>3}")
        print(f"Total Analysts Coverage: {grand_total}")
        print(f"Overall Bullish Sentiment: {((total_strong_buy + total_buy) / grand_total * 100):.1f}%")
        
        # Save with timestamp in filename
        timestamp_for_filename = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = os.path.join(output_dir, f'analyst_ratings_finnhub_{timestamp_for_filename}.csv')
        df.to_csv(output_file, index=False)
        print(f"\n💾 Timestamped data saved to analyst_ratings_finnhub_{timestamp_for_filename}.csv")
        
        # Also save as the latest version (this will overwrite)
        latest_file = os.path.join(output_dir, 'analyst_ratings_finnhub_latest.csv')
        df.to_csv(latest_file, index=False)
        print(f"📄 Latest version saved to analyst_ratings_finnhub_latest.csv")
        
        print(f"\n🎯 Ready for Advanced Power BI Analysis! You now have:")
        print(f"   📈 Your Algorithm: investment_recommendations_*.csv")
        print(f"   📊 Wall Street Complete: analyst_ratings_finnhub_*.csv")
        print(f"   🥊 Perfect for comprehensive 'Algorithm vs Wall Street' analysis!")
        print(f"\n🎨 Enhanced Power BI Visualization Ideas:")
        print(f"   📊 Stacked bar chart: Buy/Hold/Sell counts by company")
        print(f"   🎯 Scatter plot: Beta vs Analyst Sentiment (risk vs confidence)")
        print(f"   📈 Gauge charts: Distance from 52-week highs")
        print(f"   🔥 Heat map: Daily performance vs market cap")
        print(f"   💰 Cards: Live stock prices with daily changes")
        print(f"   📋 Table: Current metrics with color-coded performance")
        print(f"   🎲 Risk analysis: Beta vs dividend yield vs analyst ratings")
        
    else:
        print("❌ No data retrieved. Check your API key and network connection.")

if __name__ == "__main__":
    main()