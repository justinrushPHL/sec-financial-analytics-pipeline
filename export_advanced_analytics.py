import sqlite3
import pandas as pd
from datetime import datetime
import os

# Connect to database
db_path = 'data/financial_data.db'
conn = sqlite3.connect(db_path)

# Create exports directory if it doesn't exist
export_dir = 'exports/advanced_analytics'
os.makedirs(export_dir, exist_ok=True)

timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

# Export 1: Investment Recommendations
investment_query = """
SELECT 
    c.ticker,
    c.company_name,
    ROUND(AVG(CASE WHEN fs.fiscal_year >= 2023 AND fs.revenue > 0 THEN (fs.net_income * 100.0 / fs.revenue) END), 2) as current_margin,
    ROUND(AVG(CASE WHEN fs.fiscal_year BETWEEN 2020 AND 2022 AND fs.revenue > 0 THEN (fs.net_income * 100.0 / fs.revenue) END), 2) as historical_margin,
    COUNT(CASE WHEN fs.fiscal_year >= 2023 AND fs.form_type = '10-K' THEN 1 END) as recent_annual_filings,
    COUNT(CASE WHEN fs.fiscal_year >= 2023 AND fs.form_type = '10-Q' THEN 1 END) as recent_quarterly_filings,
    MAX(fs.filing_date) as latest_filing_date,
    MAX(CASE WHEN fs.filing_date = (SELECT MAX(filing_date) FROM financial_statements fs2 WHERE fs2.cik = fs.cik) 
        THEN fs.form_type END) as latest_form_type,
    CASE 
        WHEN AVG(CASE WHEN fs.fiscal_year >= 2023 AND fs.revenue > 0 THEN (fs.net_income * 100.0 / fs.revenue) END) > 25 THEN 'STRONG BUY'
        WHEN AVG(CASE WHEN fs.fiscal_year >= 2023 AND fs.revenue > 0 THEN (fs.net_income * 100.0 / fs.revenue) END) > 15 THEN 'BUY'
        ELSE 'HOLD'
    END as recommendation
FROM financial_statements fs
JOIN companies c ON fs.cik = c.cik
WHERE fs.form_type IN ('10-K', '10-Q')
    AND fs.revenue IS NOT NULL
    AND fs.net_income IS NOT NULL
GROUP BY c.ticker, c.company_name
ORDER BY current_margin DESC
"""

df_investment = pd.read_sql_query(investment_query, conn)

# Save timestamped version
timestamped_file = f'{export_dir}/investment_recommendations_{timestamp}.csv'
df_investment.to_csv(timestamped_file, index=False)
print(f"📊 Exported timestamped: investment_recommendations_{timestamp}.csv")

# Save latest version (overwrites each time)
latest_file = f'{export_dir}/investment_recommendations_latest.csv'
df_investment.to_csv(latest_file, index=False)
print(f"📄 Exported latest: investment_recommendations_latest.csv")

conn.close()

print(f"\n🎯 Ready for Power BI! Use these files:")
print(f"   📈 Your Algorithm: investment_recommendations_latest.csv")
print(f"   📊 Wall Street: analyst_ratings_finnhub_latest.csv")
print(f"   🔄 Both auto-update when you refresh Power BI data!")