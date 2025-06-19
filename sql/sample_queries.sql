-- =====================================================================================
-- SEC FINANCIAL ANALYTICS - COMPLETE SQL PORTFOLIO WITH FORM TYPE INTEGRATION
-- Enhanced to show 10-K (Annual) vs 10-Q (Quarterly) filing context throughout
-- Matches your actual database schema: companies + financial_statements tables
-- =====================================================================================

-- =====================================================================================
-- SECTION 1: ENHANCED FOUNDATIONAL ANALYTICS WITH FORM TYPE CONTEXT
-- =====================================================================================

-- Query 1: Latest Annual Revenue with Market Share and Filing Context
WITH latest_revenue AS (
    SELECT 
        c.ticker,
        c.company_name,
        fs.fiscal_year,
        fs.fiscal_quarter,
        fs.form_type,
        fs.revenue,
        fs.filing_date,
        fs.period_end_date,
        CASE 
            WHEN fs.form_type = '10-K' THEN fs.fiscal_year || ' Annual Report'
            WHEN fs.form_type = '10-Q' THEN 'Q' || fs.fiscal_quarter || ' ' || fs.fiscal_year
            ELSE fs.form_type
        END as filing_description
    FROM financial_statements fs
    JOIN companies c ON fs.cik = c.cik
    WHERE fs.form_type = '10-K' 
        AND fs.revenue IS NOT NULL
        AND fs.fiscal_year = (
            SELECT MAX(fiscal_year) 
            FROM financial_statements fs2 
            WHERE fs2.cik = fs.cik 
            AND fs2.form_type = '10-K'
            AND fs2.revenue IS NOT NULL
        )
),
market_totals AS (
    SELECT SUM(revenue) as total_market_revenue
    FROM latest_revenue
)
SELECT 
    lr.ticker,
    lr.company_name,
    lr.filing_description,
    lr.fiscal_year,
    lr.form_type,
    ROUND(fs.operating_cash_flow / 1000000.0, 2) as operating_cf_millions,
    ROUND(fs.net_income / 1000000.0, 2) as net_income_millions,
    ROUND(fs.investing_cash_flow / 1000000.0, 2) as investing_cf_millions,
    ROUND(fs.financing_cash_flow / 1000000.0, 2) as financing_cf_millions,
    CASE 
        WHEN fs.net_income != 0 THEN 
            ROUND((fs.operating_cash_flow * 1.0 / fs.net_income), 2)
        ELSE NULL 
    END as cf_to_income_ratio,
    -- Cash flow quality assessment
    CASE 
        WHEN (fs.operating_cash_flow * 1.0 / fs.net_income) > 1.2 
        THEN '🟢 High Quality Earnings'
        WHEN (fs.operating_cash_flow * 1.0 / fs.net_income) > 0.8 
        THEN '🟡 Good Quality Earnings'
        WHEN (fs.operating_cash_flow * 1.0 / fs.net_income) > 0.5 
        THEN '🟠 Moderate Quality'
        ELSE '🔴 Low Quality Earnings'
    END as earnings_quality,
    -- Free cash flow
    ROUND(fs.free_cash_flow / 1000000.0, 2) as free_cf_millions,
    -- Filing timing context
    JULIANDAY('now') - JULIANDAY(fs.filing_date) as days_since_filing,
    -- Cash flow trend by filing type
    LAG(fs.operating_cash_flow) OVER (
        PARTITION BY fs.cik, fs.form_type 
        ORDER BY fs.fiscal_year, fs.fiscal_quarter
    ) as prev_period_operating_cf,
    CASE 
        WHEN LAG(fs.operating_cash_flow) OVER (
            PARTITION BY fs.cik, fs.form_type 
            ORDER BY fs.fiscal_year, fs.fiscal_quarter
        ) != 0 
        THEN ROUND(((fs.operating_cash_flow - LAG(fs.operating_cash_flow) OVER (
            PARTITION BY fs.cik, fs.form_type 
            ORDER BY fs.fiscal_year, fs.fiscal_quarter
        )) * 100.0 / ABS(LAG(fs.operating_cash_flow) OVER (
            PARTITION BY fs.cik, fs.form_type 
            ORDER BY fs.fiscal_year, fs.fiscal_quarter
        ))), 2)
        ELSE NULL
    END as cf_growth_percent
FROM financial_statements fs
JOIN companies c ON fs.cik = c.cik
WHERE fs.form_type IN ('10-K', '10-Q')
    AND fs.operating_cash_flow IS NOT NULL
    AND fs.net_income IS NOT NULL
    AND fs.net_income != 0
    AND fs.fiscal_year >= 2022
ORDER BY cf_to_income_ratio DESC, fs.fiscal_year DESC;

-- =====================================================================================
-- SECTION 7: BUSINESS INTELLIGENCE VIEWS WITH FORM TYPE INTEGRATION
-- =====================================================================================

-- Executive Summary View with Filing Breakdown
CREATE VIEW IF NOT EXISTS executive_summary_enhanced AS
SELECT 
    'Portfolio Overview' as category,
    'Total Portfolio Revenue (Latest Annual)' as metric,
    ROUND(SUM(fs.revenue) / 1000000000.0, 1) || 'B' as value,
    'From ' || COUNT(DISTINCT c.ticker) || ' companies' as context
FROM financial_statements fs
JOIN companies c ON fs.cik = c.cik
WHERE fs.form_type = '10-K' 
    AND fs.fiscal_year = (SELECT MAX(fiscal_year) FROM financial_statements WHERE form_type = '10-K')
UNION ALL
SELECT 
    'Portfolio Overview',
    'Average Net Margin (Latest Annual)',
    ROUND(AVG(CASE WHEN fs.revenue > 0 THEN fs.net_income * 100.0 / fs.revenue END), 1) || '%',
    'Based on ' || COUNT(*) || ' annual reports'
FROM financial_statements fs
WHERE fs.form_type = '10-K' 
    AND fs.fiscal_year = (SELECT MAX(fiscal_year) FROM financial_statements WHERE form_type = '10-K')
    AND fs.revenue > 0
UNION ALL
SELECT 
    'Data Coverage',
    'Total Filings Available',
    COUNT(*) || ' filings',
    COUNT(CASE WHEN form_type = '10-K' THEN 1 END) || ' annual + ' || 
    COUNT(CASE WHEN form_type = '10-Q' THEN 1 END) || ' quarterly'
FROM financial_statements
WHERE fiscal_year >= 2020
UNION ALL
SELECT 
    'Data Freshness',
    'Most Recent Filing',
    MAX(filing_date) || ' (' || 
    CASE 
        WHEN form_type = '10-K' THEN 'Annual'
        WHEN form_type = '10-Q' THEN 'Q' || fiscal_quarter
        ELSE 'Other'
    END || ')',
    ROUND(JULIANDAY('now') - JULIANDAY(MAX(filing_date))) || ' days ago'
FROM financial_statements;

-- Risk Alert System with Filing Context
CREATE VIEW IF NOT EXISTS risk_alerts_enhanced AS
SELECT 
    c.ticker,
    'Liquidity Risk' as alert_type,
    'Current ratio below 1.5' as description,
    'HIGH' as severity,
    fs.form_type || ' filing from ' || fs.filing_date as data_source,
    CASE 
        WHEN fs.form_type = '10-K' THEN 'Annual Report'
        WHEN fs.form_type = '10-Q' THEN 'Q' || fs.fiscal_quarter || ' Report'
        ELSE 'Other'
    END as filing_context,
    JULIANDAY('now') - JULIANDAY(fs.filing_date) as days_since_filing
FROM financial_statements fs
JOIN companies c ON fs.cik = c.cik
WHERE fs.form_type IN ('10-K', '10-Q')
    AND fs.fiscal_year >= 2023
    AND fs.current_liabilities > 0
    AND (fs.current_assets * 1.0 / fs.current_liabilities) < 1.5
UNION ALL
SELECT 
    c.ticker,
    'Profitability Risk',
    'Net margin below 10%',
    'MEDIUM',
    fs.form_type || ' filing from ' || fs.filing_date,
    CASE 
        WHEN fs.form_type = '10-K' THEN 'Annual Report'
        WHEN fs.form_type = '10-Q' THEN 'Q' || fs.fiscal_quarter || ' Report'
        ELSE 'Other'
    END,
    JULIANDAY('now') - JULIANDAY(fs.filing_date)
FROM financial_statements fs
JOIN companies c ON fs.cik = c.cik
WHERE fs.form_type IN ('10-K', '10-Q')
    AND fs.fiscal_year >= 2023
    AND fs.revenue > 0
    AND (fs.net_income * 100.0 / fs.revenue) < 10
UNION ALL
SELECT 
    c.ticker,
    'Leverage Risk',
    'Debt-to-Assets above 60%',
    'MEDIUM',
    fs.form_type || ' filing from ' || fs.filing_date,
    CASE 
        WHEN fs.form_type = '10-K' THEN 'Annual Report'
        WHEN fs.form_type = '10-Q' THEN 'Q' || fs.fiscal_quarter || ' Report'
        ELSE 'Other'
    END,
    JULIANDAY('now') - JULIANDAY(fs.filing_date)
FROM financial_statements fs
JOIN companies c ON fs.cik = c.cik
WHERE fs.form_type IN ('10-K', '10-Q')
    AND fs.fiscal_year >= 2023
    AND fs.total_assets > 0
    AND (fs.total_liabilities * 100.0 / fs.total_assets) > 60;

-- =====================================================================================
-- SECTION 8: FILING DATA QUALITY AND COMPLETENESS ANALYSIS
-- =====================================================================================

-- Query 9: Comprehensive Data Quality Assessment by Filing Type
SELECT 
    c.ticker,
    c.company_name,
    
    -- Annual filings summary
    COUNT(CASE WHEN fs.form_type = '10-K' AND fs.fiscal_year >= 2020 THEN 1 END) as annual_filings_count,
    MIN(CASE WHEN fs.form_type = '10-K' THEN fs.fiscal_year END) as earliest_annual_year,
    MAX(CASE WHEN fs.form_type = '10-K' THEN fs.fiscal_year END) as latest_annual_year,
    MAX(CASE WHEN fs.form_type = '10-K' THEN fs.filing_date END) as latest_annual_filing,
    
    -- Quarterly filings summary
    COUNT(CASE WHEN fs.form_type = '10-Q' AND fs.fiscal_year >= 2020 THEN 1 END) as quarterly_filings_count,
    MIN(CASE WHEN fs.form_type = '10-Q' THEN fs.fiscal_year END) as earliest_quarterly_year,
    MAX(CASE WHEN fs.form_type = '10-Q' THEN fs.fiscal_year END) as latest_quarterly_year,
    MAX(CASE WHEN fs.form_type = '10-Q' THEN fs.filing_date END) as latest_quarterly_filing,
    
    -- Data completeness by key metrics
    COUNT(CASE WHEN fs.revenue IS NOT NULL AND fs.form_type = '10-K' THEN 1 END) as annual_revenue_records,
    COUNT(CASE WHEN fs.net_income IS NOT NULL AND fs.form_type = '10-K' THEN 1 END) as annual_income_records,
    COUNT(CASE WHEN fs.operating_cash_flow IS NOT NULL AND fs.form_type = '10-K' THEN 1 END) as annual_cashflow_records,
    
    COUNT(CASE WHEN fs.revenue IS NOT NULL AND fs.form_type = '10-Q' THEN 1 END) as quarterly_revenue_records,
    COUNT(CASE WHEN fs.net_income IS NOT NULL AND fs.form_type = '10-Q' THEN 1 END) as quarterly_income_records,
    COUNT(CASE WHEN fs.operating_cash_flow IS NOT NULL AND fs.form_type = '10-Q' THEN 1 END) as quarterly_cashflow_records,
    
    -- Most recent filings
    MAX(fs.filing_date) as most_recent_filing,
    MAX(CASE WHEN fs.filing_date = (SELECT MAX(filing_date) FROM financial_statements fs2 WHERE fs2.cik = fs.cik) 
        THEN fs.form_type END) as most_recent_form_type,
    MAX(CASE WHEN fs.filing_date = (SELECT MAX(filing_date) FROM financial_statements fs2 WHERE fs2.cik = fs.cik) 
        THEN fs.fiscal_year END) as most_recent_fiscal_year,
    MAX(CASE WHEN fs.filing_date = (SELECT MAX(filing_date) FROM financial_statements fs2 WHERE fs2.cik = fs.cik) 
        THEN fs.fiscal_quarter END) as most_recent_fiscal_quarter,
    
    -- Data quality scoring
    CASE 
        WHEN COUNT(CASE WHEN fs.form_type = '10-K' AND fs.fiscal_year >= 2020 THEN 1 END) >= 4 
        AND COUNT(CASE WHEN fs.form_type = '10-Q' AND fs.fiscal_year >= 2022 THEN 1 END) >= 6 
        THEN '🟢 Excellent Coverage'
        WHEN COUNT(CASE WHEN fs.form_type = '10-K' AND fs.fiscal_year >= 2020 THEN 1 END) >= 3 
        AND COUNT(CASE WHEN fs.form_type = '10-Q' AND fs.fiscal_year >= 2022 THEN 1 END) >= 3 
        THEN '🟡 Good Coverage'
        WHEN COUNT(CASE WHEN fs.form_type = '10-K' AND fs.fiscal_year >= 2020 THEN 1 END) >= 2 
        THEN '🟠 Limited Coverage'
        ELSE '🔴 Poor Coverage'
    END as data_coverage_quality,
    
    -- Filing recency
    JULIANDAY('now') - JULIANDAY(MAX(fs.filing_date)) as days_since_latest_filing,
    CASE 
        WHEN JULIANDAY('now') - JULIANDAY(MAX(fs.filing_date)) <= 90 THEN '🟢 Current'
        WHEN JULIANDAY('now') - JULIANDAY(MAX(fs.filing_date)) <= 180 THEN '🟡 Recent'
        WHEN JULIANDAY('now') - JULIANDAY(MAX(fs.filing_date)) <= 365 THEN '🟠 Stale'
        ELSE '🔴 Very Stale'
    END as data_recency_quality

FROM companies c
LEFT JOIN financial_statements fs ON c.cik = fs.cik
GROUP BY c.cik, c.ticker, c.company_name
ORDER BY data_coverage_quality, annual_filings_count DESC, quarterly_filings_count DESC;

-- =====================================================================================
-- SECTION 9: MOST RECENT FILING ANALYSIS
-- =====================================================================================

-- Query 10: Latest Filing Analysis with Full Context
SELECT 
    c.ticker,
    c.company_name,
    fs.fiscal_year,
    fs.fiscal_quarter,
    fs.form_type,
    
    -- Filing description and context
    CASE 
        WHEN fs.form_type = '10-K' THEN 'Annual Report for ' || fs.fiscal_year
        WHEN fs.form_type = '10-Q' THEN 'Q' || fs.fiscal_quarter || ' ' || fs.fiscal_year || ' Quarterly Report'
        ELSE fs.form_type
    END as filing_description,
    
    fs.filing_date,
    fs.period_end_date,
    JULIANDAY('now') - JULIANDAY(fs.filing_date) as days_since_filing,
    
    -- Financial performance
    ROUND(fs.revenue / 1000000000.0, 2) as revenue_billions,
    ROUND(fs.net_income / 1000000000.0, 2) as net_income_billions,
    ROUND((fs.net_income * 100.0 / fs.revenue), 2) as net_margin_percent,
    ROUND(fs.operating_cash_flow / 1000000000.0, 2) as operating_cf_billions,
    
    -- Balance sheet snapshot
    ROUND(fs.total_assets / 1000000000.0, 2) as total_assets_billions,
    ROUND(fs.current_assets / 1000000000.0, 2) as current_assets_billions,
    ROUND(fs.current_liabilities / 1000000000.0, 2) as current_liabilities_billions,
    CASE 
        WHEN fs.current_liabilities > 0 THEN 
            ROUND((fs.current_assets * 1.0 / fs.current_liabilities), 2)
        ELSE NULL 
    END as current_ratio,
    
    -- Performance indicators
    CASE 
        WHEN (fs.net_income * 100.0 / fs.revenue) > 25 THEN '🟢 High Profitability'
        WHEN (fs.net_income * 100.0 / fs.revenue) > 15 THEN '🟡 Good Profitability'
        WHEN (fs.net_income * 100.0 / fs.revenue) > 5 THEN '🟠 Moderate Profitability'
        ELSE '🔴 Low Profitability'
    END as profitability_rating,
    
    CASE 
        WHEN fs.current_liabilities > 0 AND (fs.current_assets * 1.0 / fs.current_liabilities) > 2.0 THEN '🟢 Strong Liquidity'
        WHEN fs.current_liabilities > 0 AND (fs.current_assets * 1.0 / fs.current_liabilities) > 1.5 THEN '🟡 Good Liquidity'
        WHEN fs.current_liabilities > 0 AND (fs.current_assets * 1.0 / fs.current_liabilities) > 1.0 THEN '🟠 Adequate Liquidity'
        ELSE '🔴 Poor Liquidity'
    END as liquidity_rating,
    
    -- Data freshness assessment
    CASE 
        WHEN JULIANDAY('now') - JULIANDAY(fs.filing_date) <= 30 THEN '🟢 Very Fresh'
        WHEN JULIANDAY('now') - JULIANDAY(fs.filing_date) <= 90 THEN '🟡 Fresh'
        WHEN JULIANDAY('now') - JULIANDAY(fs.filing_date) <= 180 THEN '🟠 Moderate'
        ELSE '🔴 Stale'
    END as data_freshness,
    
    -- Expected next filing
    CASE 
        WHEN fs.form_type = '10-K' THEN 'Next 10-Q expected ~' || 
            DATE(fs.period_end_date, '+3 months', '+45 days')
        WHEN fs.form_type = '10-Q' AND fs.fiscal_quarter = 3 THEN 'Next 10-K expected ~' || 
            DATE(fs.period_end_date, '+3 months', '+90 days')
        WHEN fs.form_type = '10-Q' THEN 'Next 10-Q expected ~' || 
            DATE(fs.period_end_date, '+3 months', '+45 days')
        ELSE 'Unknown'
    END as next_filing_expected

FROM financial_statements fs
JOIN companies c ON fs.cik = c.cik
WHERE fs.revenue IS NOT NULL
    AND fs.net_income IS NOT NULL
    AND fs.filing_date = (
        SELECT MAX(filing_date) 
        FROM financial_statements fs2 
        WHERE fs2.cik = fs.cik 
        AND fs2.revenue IS NOT NULL
    )
ORDER BY fs.filing_date DESC, fs.revenue DESC;

-- =====================================================================================
-- SECTION 10: QUICK TEST QUERIES WITH FORM TYPE CONTEXT
-- =====================================================================================

-- Test Query 1: Basic Revenue Ranking with Filing Context
SELECT 
    c.ticker,
    c.company_name,
    fs.fiscal_year,
    fs.form_type,
    CASE 
        WHEN fs.form_type = '10-K' THEN 'Annual'
        WHEN fs.form_type = '10-Q' THEN 'Q' || fs.fiscal_quarter
        ELSE 'Other'
    END as period_type,
    fs.filing_date,
    ROUND(fs.revenue / 1000000000.0, 2) as revenue_billions,
    JULIANDAY('now') - JULIANDAY(fs.filing_date) as days_since_filing
FROM financial_statements fs
JOIN companies c ON fs.cik = c.cik
WHERE fs.form_type = '10-K' 
    AND fs.fiscal_year = 2024
    AND fs.revenue IS NOT NULL
ORDER BY fs.revenue DESC;

-- Test Query 2: Profitability Check with Form Type Breakdown
SELECT 
    c.ticker,
    c.company_name,
    fs.fiscal_year,
    fs.form_type,
    CASE 
        WHEN fs.form_type = '10-K' THEN 'Annual Performance'
        WHEN fs.form_type = '10-Q' THEN 'Q' || fs.fiscal_quarter || ' Performance'
        ELSE 'Other'
    END as performance_context,
    fs.filing_date,
    ROUND(fs.revenue / 1000000.0, 2) as revenue_millions,
    ROUND(fs.net_income / 1000000.0, 2) as net_income_millions,
    ROUND((fs.net_income * 100.0 / fs.revenue), 2) as net_margin_percent,
    CASE 
        WHEN (fs.net_income * 100.0 / fs.revenue) > 25 THEN '🏆 Excellent'
        WHEN (fs.net_income * 100.0 / fs.revenue) > 15 THEN '⭐ Good'
        WHEN (fs.net_income * 100.0 / fs.revenue) > 5 THEN '📊 Fair'
        ELSE '⚠️ Poor'
    END as margin_rating
FROM financial_statements fs
JOIN companies c ON fs.cik = c.cik
WHERE fs.form_type IN ('10-K', '10-Q')
    AND fs.fiscal_year >= 2023
    AND fs.revenue > 0
ORDER BY fs.fiscal_year DESC, 
    CASE fs.form_type WHEN '10-K' THEN 0 ELSE 1 END,
    (fs.net_income * 100.0 / fs.revenue) DESC;

-- =====================================================================================
-- END OF COMPLETE SQL ANALYTICS PORTFOLIO WITH FORM TYPE INTEGRATION
-- 
-- This comprehensive portfolio now includes:
-- ✅ Form type context (10-K vs 10-Q) throughout all queries
-- ✅ Fiscal quarter information and seasonal analysis
-- ✅ Filing date tracking and data freshness indicators
-- ✅ Annual vs quarterly performance comparisons
-- ✅ Data quality assessment by filing type
-- ✅ Sequential and year-over-year growth analysis
-- ✅ Investment recommendations with data source transparency
-- ✅ Business intelligence views with filing context
-- ✅ Risk monitoring with filing source attribution
-- ✅ Comprehensive test queries for validation
-- 
-- Total: 800+ lines of advanced SQL analytics ready for interviews!
-- =====================================================================================(lr.revenue / 1000000000.0, 2) as revenue_billions,
    ROUND((lr.revenue * 100.0 / mt.total_market_revenue), 2) as market_share_pct,
    RANK() OVER (ORDER BY lr.revenue DESC) as revenue_rank,
    lr.filing_date,
    lr.period_end_date,
    JULIANDAY('now') - JULIANDAY(lr.filing_date) as days_since_filing,
    CASE 
        WHEN JULIANDAY('now') - JULIANDAY(lr.filing_date) <= 90 THEN '🟢 Recent'
        WHEN JULIANDAY('now') - JULIANDAY(lr.filing_date) <= 180 THEN '🟡 Moderate'
        ELSE '🔴 Stale'
    END as data_freshness
FROM latest_revenue lr
CROSS JOIN market_totals mt
ORDER BY lr.revenue DESC;

-- Query 2: Enhanced Revenue Growth Analysis with Quarterly Context
WITH revenue_by_period AS (
    SELECT 
        c.ticker,
        c.company_name,
        fs.fiscal_year,
        fs.fiscal_quarter,
        fs.form_type,
        fs.revenue,
        CASE 
            WHEN fs.form_type = '10-K' THEN 'Annual'
            WHEN fs.form_type = '10-Q' THEN 'Q' || fs.fiscal_quarter
            ELSE 'Other'
        END as period_type,
        LAG(fs.revenue) OVER (PARTITION BY fs.cik, fs.form_type ORDER BY fs.fiscal_year, fs.fiscal_quarter) as prev_period_revenue,
        LAG(fs.revenue, 2) OVER (PARTITION BY fs.cik, fs.form_type ORDER BY fs.fiscal_year, fs.fiscal_quarter) as two_periods_prior_revenue
    FROM financial_statements fs
    JOIN companies c ON fs.cik = c.cik
    WHERE fs.form_type IN ('10-K', '10-Q')
        AND fs.revenue IS NOT NULL
)
SELECT 
    ticker,
    company_name,
    fiscal_year,
    period_type,
    form_type,
    ROUND(revenue / 1000000.0, 2) as revenue_millions,
    ROUND(prev_period_revenue / 1000000.0, 2) as prior_period_revenue_millions,
    CASE 
        WHEN prev_period_revenue > 0 THEN 
            ROUND(((revenue - prev_period_revenue) * 100.0 / prev_period_revenue), 2)
        ELSE NULL 
    END as period_over_period_growth_percent,
    CASE 
        WHEN ((revenue - prev_period_revenue) * 100.0 / prev_period_revenue) > 20 THEN '🚀 High Growth'
        WHEN ((revenue - prev_period_revenue) * 100.0 / prev_period_revenue) > 10 THEN '📈 Steady Growth'
        WHEN ((revenue - prev_period_revenue) * 100.0 / prev_period_revenue) > 0 THEN '📊 Modest Growth'
        ELSE '📉 Declining'
    END as growth_category,
    CASE 
        WHEN two_periods_prior_revenue > 0 THEN 
            ROUND((POWER((revenue * 1.0 / two_periods_prior_revenue), 0.5) - 1) * 100, 2)
        ELSE NULL
    END as two_period_cagr,
    -- Growth context by filing type
    CASE 
        WHEN form_type = '10-K' THEN 'Year-over-Year'
        WHEN form_type = '10-Q' THEN 'Quarter-over-Quarter'
        ELSE 'Period-over-Period'
    END as growth_context
FROM revenue_by_period
WHERE prev_period_revenue IS NOT NULL
    AND fiscal_year >= 2022
ORDER BY fiscal_year DESC, form_type, period_over_period_growth_percent DESC;

-- Query 3: Profitability Analysis with Filing Type Breakdown
WITH profitability_data AS (
    SELECT 
        c.ticker,
        c.company_name,
        fs.fiscal_year,
        fs.fiscal_quarter,
        fs.form_type,
        fs.revenue,
        fs.net_income,
        fs.operating_income,
        fs.filing_date,
        CASE 
            WHEN fs.form_type = '10-K' THEN 'Annual Report'
            WHEN fs.form_type = '10-Q' THEN 'Q' || fs.fiscal_quarter || ' Report'
            ELSE fs.form_type
        END as report_type,
        CASE 
            WHEN fs.revenue > 0 THEN (fs.net_income * 100.0 / fs.revenue)
            ELSE NULL 
        END as net_margin_percent,
        CASE 
            WHEN fs.revenue > 0 THEN (fs.operating_income * 100.0 / fs.revenue)
            ELSE NULL 
        END as operating_margin_percent
    FROM financial_statements fs
    JOIN companies c ON fs.cik = c.cik
    WHERE fs.form_type IN ('10-K', '10-Q')
        AND fs.revenue > 0 
        AND fs.net_income IS NOT NULL
        AND fs.fiscal_year >= 2022
),
industry_benchmarks AS (
    SELECT 
        fiscal_year,
        form_type,
        AVG(net_margin_percent) as avg_net_margin,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY net_margin_percent) as median_net_margin,
        PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY net_margin_percent) as top_quartile_margin,
        COUNT(*) as filing_count
    FROM profitability_data
    GROUP BY fiscal_year, form_type
)
SELECT 
    pd.ticker,
    pd.company_name,
    pd.fiscal_year,
    pd.report_type,
    pd.form_type,
    pd.filing_date,
    ROUND(pd.revenue / 1000000.0, 2) as revenue_millions,
    ROUND(pd.net_income / 1000000.0, 2) as net_income_millions,
    ROUND(pd.operating_income / 1000000.0, 2) as operating_income_millions,
    ROUND(pd.net_margin_percent, 2) as net_margin_percent,
    ROUND(pd.operating_margin_percent, 2) as operating_margin_percent,
    ROUND(ib.avg_net_margin, 2) as industry_avg_margin,
    ROUND((pd.net_margin_percent - ib.avg_net_margin), 2) as margin_vs_industry,
    ib.filing_count as peer_filings_count,
    CASE 
        WHEN pd.net_margin_percent > ib.top_quartile_margin THEN '🏆 Top Quartile'
        WHEN pd.net_margin_percent > ib.median_net_margin THEN '⭐ Above Median'
        WHEN pd.net_margin_percent > ib.avg_net_margin THEN '📊 Above Average'
        ELSE '⚠️ Below Average'
    END as performance_tier
FROM profitability_data pd
JOIN industry_benchmarks ib ON pd.fiscal_year = ib.fiscal_year AND pd.form_type = ib.form_type
ORDER BY pd.fiscal_year DESC, pd.form_type, pd.net_margin_percent DESC;

-- =====================================================================================
-- SECTION 2: ADVANCED FINANCIAL HEALTH SCORING WITH FORM TYPE ANALYSIS
-- =====================================================================================

-- Query 4: Multi-Dimensional Financial Health Score with Filing Context
WITH financial_health AS (
    SELECT 
        c.ticker,
        c.company_name,
        fs.fiscal_year,
        fs.fiscal_quarter,
        fs.form_type,
        fs.filing_date,
        fs.current_assets,
        fs.current_liabilities,
        fs.total_assets,
        fs.total_liabilities,
        fs.stockholders_equity,
        fs.revenue,
        fs.net_income,
        CASE 
            WHEN fs.form_type = '10-K' THEN 'Annual Snapshot'
            WHEN fs.form_type = '10-Q' THEN 'Q' || fs.fiscal_quarter || ' Snapshot'
            ELSE 'Other'
        END as balance_sheet_context,
        -- Calculate financial ratios
        CASE 
            WHEN fs.current_liabilities > 0 THEN (fs.current_assets * 1.0 / fs.current_liabilities)
            ELSE NULL 
        END as current_ratio,
        CASE 
            WHEN fs.total_assets > 0 THEN (fs.total_liabilities * 100.0 / fs.total_assets)
            ELSE NULL 
        END as debt_to_assets_percent,
        CASE 
            WHEN fs.revenue > 0 THEN (fs.net_income * 100.0 / fs.revenue)
            ELSE NULL 
        END as profit_margin
    FROM financial_statements fs
    JOIN companies c ON fs.cik = c.cik
    WHERE fs.form_type IN ('10-K', '10-Q')
        AND fs.total_assets IS NOT NULL
        AND fs.fiscal_year >= 2020
),
health_scores AS (
    SELECT 
        *,
        -- Liquidity Score (0-100)
        CASE 
            WHEN current_ratio > 3.0 THEN 100
            WHEN current_ratio > 2.0 THEN 80
            WHEN current_ratio > 1.5 THEN 60
            WHEN current_ratio > 1.0 THEN 40
            ELSE 20
        END as liquidity_score,
        
        -- Leverage Score (0-100, lower debt = higher score)
        CASE 
            WHEN debt_to_assets_percent < 20 THEN 100
            WHEN debt_to_assets_percent < 40 THEN 80
            WHEN debt_to_assets_percent < 60 THEN 60
            WHEN debt_to_assets_percent < 80 THEN 40
            ELSE 20
        END as leverage_score,
        
        -- Profitability Score (0-100)
        CASE 
            WHEN profit_margin > 30 THEN 100
            WHEN profit_margin > 20 THEN 80
            WHEN profit_margin > 10 THEN 60
            WHEN profit_margin > 5 THEN 40
            WHEN profit_margin > 0 THEN 20
            ELSE 0
        END as profitability_score
    FROM financial_health
),
composite_scores AS (
    SELECT 
        *,
        ROUND((profitability_score * 0.4 + liquidity_score * 0.3 + leverage_score * 0.3), 1) as composite_health_score
    FROM health_scores
    WHERE current_ratio IS NOT NULL AND debt_to_assets_percent IS NOT NULL AND profit_margin IS NOT NULL
)
SELECT 
    ticker,
    company_name,
    fiscal_year,
    balance_sheet_context,
    form_type,
    filing_date,
    ROUND(current_ratio, 2) as current_ratio,
    ROUND(debt_to_assets_percent, 2) as debt_to_assets_percent,
    ROUND(profit_margin, 2) as profit_margin,
    profitability_score,
    liquidity_score,
    leverage_score,
    composite_health_score,
    ROUND(AVG(composite_health_score) OVER (
        PARTITION BY ticker, form_type 
        ORDER BY fiscal_year, fiscal_quarter 
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    ), 1) as rolling_avg_health,
    RANK() OVER (PARTITION BY fiscal_year, form_type ORDER BY composite_health_score DESC) as health_rank,
    CASE 
        WHEN composite_health_score >= 85 THEN '🟢 Excellent'
        WHEN composite_health_score >= 70 THEN '🟡 Good'
        WHEN composite_health_score >= 55 THEN '🟠 Fair'
        ELSE '🔴 Poor'
    END as health_rating,
    -- Filing timing context
    JULIANDAY('now') - JULIANDAY(filing_date) as days_since_filing
FROM composite_scores
ORDER BY fiscal_year DESC, form_type, composite_health_score DESC;

-- =====================================================================================
-- SECTION 3: INVESTMENT DECISION FRAMEWORK WITH DATA SOURCE TRANSPARENCY
-- =====================================================================================

-- Query 5: Automated Investment Recommendation Engine with Filing Analysis
WITH performance_analysis AS (
    SELECT 
        c.ticker,
        c.company_name,
        
        -- Recent performance (2023-2024) with source tracking
        AVG(CASE WHEN fs.fiscal_year >= 2023 AND fs.revenue > 0 THEN (fs.net_income * 100.0 / fs.revenue) END) as current_margin,
        COUNT(CASE WHEN fs.fiscal_year >= 2023 AND fs.form_type = '10-K' THEN 1 END) as recent_annual_filings,
        COUNT(CASE WHEN fs.fiscal_year >= 2023 AND fs.form_type = '10-Q' THEN 1 END) as recent_quarterly_filings,
        
        -- Historical performance
        AVG(CASE WHEN fs.fiscal_year BETWEEN 2020 AND 2022 AND fs.revenue > 0 THEN (fs.net_income * 100.0 / fs.revenue) END) as historical_margin,
        COUNT(CASE WHEN fs.fiscal_year BETWEEN 2020 AND 2022 AND fs.form_type = '10-K' THEN 1 END) as historical_annual_filings,
        
        -- Growth metrics
        AVG(CASE WHEN fs.fiscal_year >= 2023 THEN fs.revenue END) as recent_avg_revenue,
        AVG(CASE WHEN fs.fiscal_year BETWEEN 2020 AND 2022 THEN fs.revenue END) as historical_avg_revenue,
        
        -- Volatility measures
        STDDEV(CASE WHEN fs.fiscal_year >= 2020 AND fs.revenue > 0 THEN (fs.net_income * 100.0 / fs.revenue) END) as margin_volatility,
        COUNT(CASE WHEN fs.fiscal_year >= 2020 THEN 1 END) as years_of_data,
        
        -- Latest filing information
        MAX(fs.filing_date) as latest_filing_date,
        MAX(CASE WHEN fs.filing_date = (SELECT MAX(filing_date) FROM financial_statements fs2 WHERE fs2.cik = fs.cik) 
            THEN fs.form_type END) as latest_form_type,
        MAX(CASE WHEN fs.filing_date = (SELECT MAX(filing_date) FROM financial_statements fs2 WHERE fs2.cik = fs.cik) 
            THEN fs.fiscal_year END) as latest_fiscal_year,
        MAX(CASE WHEN fs.filing_date = (SELECT MAX(filing_date) FROM financial_statements fs2 WHERE fs2.cik = fs.cik) 
            THEN fs.fiscal_quarter END) as latest_fiscal_quarter

    FROM financial_statements fs
    JOIN companies c ON fs.cik = c.cik
    WHERE fs.form_type IN ('10-K', '10-Q')
        AND fs.revenue IS NOT NULL
        AND fs.net_income IS NOT NULL
    GROUP BY c.ticker, c.company_name
    HAVING COUNT(CASE WHEN fs.fiscal_year >= 2020 THEN 1 END) >= 3
),
investment_scores AS (
    SELECT 
        *,
        -- Revenue growth calculation
        CASE 
            WHEN historical_avg_revenue > 0 THEN 
                ((recent_avg_revenue - historical_avg_revenue) * 100.0 / historical_avg_revenue)
            ELSE NULL
        END as revenue_growth_trend,
        -- Margin improvement
        (current_margin - historical_margin) as margin_improvement,
        -- Investment scoring
        CASE 
            WHEN current_margin > 25 AND 
                 ((recent_avg_revenue - historical_avg_revenue) * 100.0 / historical_avg_revenue) > 15 AND 
                 margin_volatility < 5 
            THEN 'STRONG BUY'
            WHEN current_margin > 20 AND 
                 ((recent_avg_revenue - historical_avg_revenue) * 100.0 / historical_avg_revenue) > 10 
            THEN 'BUY'
            WHEN current_margin > 15 AND 
                 ((recent_avg_revenue - historical_avg_revenue) * 100.0 / historical_avg_revenue) > 5 
            THEN 'HOLD'
            WHEN current_margin > 10 OR 
                 ((recent_avg_revenue - historical_avg_revenue) * 100.0 / historical_avg_revenue) > 0 
            THEN 'WEAK HOLD'
            ELSE 'SELL'
        END as investment_recommendation
    FROM performance_analysis
)
SELECT 
    ticker,
    company_name,
    ROUND(current_margin, 2) as current_profitability,
    ROUND(historical_margin, 2) as historical_profitability,
    ROUND(margin_improvement, 2) as margin_trend,
    ROUND(revenue_growth_trend, 1) as revenue_growth_pct,
    ROUND(margin_volatility, 2) as earnings_volatility,
    
    -- Data source summary
    recent_annual_filings || ' annual + ' || recent_quarterly_filings || ' quarterly' as recent_data_sources,
    historical_annual_filings || ' annual reports' as historical_data_sources,
    
    -- Latest filing context
    CASE 
        WHEN latest_form_type = '10-K' THEN latest_fiscal_year || ' Annual Report'
        WHEN latest_form_type = '10-Q' THEN 'Q' || latest_fiscal_quarter || ' ' || latest_fiscal_year
        ELSE latest_form_type
    END as latest_filing_context,
    
    latest_filing_date,
    JULIANDAY('now') - JULIANDAY(latest_filing_date) as days_since_latest_filing,
    
    -- Investment recommendation with data quality indicator
    investment_recommendation,
    CASE 
        WHEN margin_volatility > 10 THEN 'High Risk'
        WHEN margin_volatility > 5 THEN 'Medium Risk'
        ELSE 'Low Risk'
    END as risk_profile,
    CASE 
        WHEN investment_recommendation = 'STRONG BUY' THEN '🟢'
        WHEN investment_recommendation = 'BUY' THEN '🟡'
        WHEN investment_recommendation LIKE '%HOLD%' THEN '🟠'
        ELSE '🔴'
    END as signal,
    
    -- Data quality score
    CASE 
        WHEN recent_annual_filings >= 2 AND recent_quarterly_filings >= 4 THEN '🟢 High Quality'
        WHEN recent_annual_filings >= 1 AND recent_quarterly_filings >= 2 THEN '🟡 Good Quality'
        WHEN recent_annual_filings >= 1 THEN '🟠 Limited Data'
        ELSE '🔴 Insufficient Data'
    END as data_quality

FROM investment_scores
WHERE current_margin IS NOT NULL AND historical_margin IS NOT NULL
ORDER BY 
    CASE investment_recommendation 
        WHEN 'STRONG BUY' THEN 1
        WHEN 'BUY' THEN 2
        WHEN 'HOLD' THEN 3
        WHEN 'WEAK HOLD' THEN 4
        ELSE 5
    END,
    current_profitability DESC;

-- =====================================================================================
-- SECTION 4: QUARTERLY VS ANNUAL PERFORMANCE COMPARISON
-- =====================================================================================

-- Query 6: Annual vs Quarterly Performance Analysis
WITH annual_data AS (
    SELECT 
        c.ticker,
        c.company_name,
        fs.fiscal_year,
        fs.revenue as annual_revenue,
        fs.net_income as annual_net_income,
        (fs.net_income * 100.0 / fs.revenue) as annual_margin,
        fs.filing_date as annual_filing_date
    FROM financial_statements fs
    JOIN companies c ON fs.cik = c.cik
    WHERE fs.form_type = '10-K'
        AND fs.revenue IS NOT NULL
        AND fs.net_income IS NOT NULL
        AND fs.fiscal_year >= 2022
),
quarterly_summary AS (
    SELECT 
        c.ticker,
        fs.fiscal_year,
        COUNT(*) as quarters_reported,
        SUM(fs.revenue) as total_quarterly_revenue,
        SUM(fs.net_income) as total_quarterly_net_income,
        AVG(fs.net_income * 100.0 / fs.revenue) as avg_quarterly_margin,
        MAX(fs.filing_date) as latest_quarterly_filing,
        GROUP_CONCAT('Q' || fs.fiscal_quarter) as quarters_available
    FROM financial_statements fs
    JOIN companies c ON fs.cik = c.cik
    WHERE fs.form_type = '10-Q'
        AND fs.revenue IS NOT NULL
        AND fs.net_income IS NOT NULL
        AND fs.fiscal_year >= 2022
    GROUP BY c.ticker, fs.fiscal_year
)
SELECT 
    a.ticker,
    a.company_name,
    a.fiscal_year,
    
    -- Annual data
    ROUND(a.annual_revenue / 1000000000.0, 2) as annual_revenue_billions,
    ROUND(a.annual_margin, 2) as annual_margin_percent,
    a.annual_filing_date,
    
    -- Quarterly data summary
    q.quarters_reported,
    q.quarters_available,
    ROUND(q.total_quarterly_revenue / 1000000000.0, 2) as quarterly_revenue_total_billions,
    ROUND(q.avg_quarterly_margin, 2) as avg_quarterly_margin_percent,
    q.latest_quarterly_filing,
    
    -- Variance analysis
    ROUND((a.annual_revenue - q.total_quarterly_revenue) / 1000000000.0, 2) as revenue_variance_billions,
    ROUND((a.annual_margin - q.avg_quarterly_margin), 2) as margin_variance_percent,
    
    -- Filing timing comparison
    JULIANDAY(a.annual_filing_date) - JULIANDAY(q.latest_quarterly_filing) as days_between_filings,
    
    -- Data completeness and consistency indicator
    CASE 
        WHEN q.quarters_reported = 3 AND ABS(a.annual_revenue - q.total_quarterly_revenue) / a.annual_revenue < 0.05 
        THEN '✅ Complete & Consistent'
        WHEN q.quarters_reported = 3 THEN '⚠️ Complete but Inconsistent'
        WHEN q.quarters_reported >= 2 THEN '🔍 Partial Quarterly Data'
        WHEN q.quarters_reported IS NULL THEN '❌ No Quarterly Data'
        ELSE '🔍 Irregular Reporting'
    END as data_quality_assessment

FROM annual_data a
LEFT JOIN quarterly_summary q ON a.ticker = q.ticker AND a.fiscal_year = q.fiscal_year
ORDER BY a.fiscal_year DESC, a.annual_revenue DESC;

-- =====================================================================================
-- SECTION 5: DETAILED QUARTERLY PERFORMANCE BREAKDOWN
-- =====================================================================================

-- Query 7: Comprehensive Quarterly Performance Analysis
SELECT 
    c.ticker,
    c.company_name,
    fs.fiscal_year,
    fs.fiscal_quarter,
    fs.form_type,
    
    -- Clear description of the filing
    CASE 
        WHEN fs.form_type = '10-K' THEN 'Annual Report (' || fs.fiscal_year || ')'
        WHEN fs.form_type = '10-Q' THEN 'Q' || fs.fiscal_quarter || ' ' || fs.fiscal_year || ' Quarterly Report'
        ELSE fs.form_type
    END as filing_description,
    
    fs.filing_date,
    fs.period_end_date,
    
    -- Financial metrics
    ROUND(fs.revenue / 1000000000.0, 2) as revenue_billions,
    ROUND(fs.net_income / 1000000000.0, 2) as net_income_billions,
    ROUND((fs.net_income * 100.0 / fs.revenue), 2) as net_margin_percent,
    
    -- Sequential quarter comparison (for 10-Q only)
    LAG(fs.revenue) OVER (
        PARTITION BY fs.cik, fs.form_type 
        ORDER BY fs.fiscal_year, fs.fiscal_quarter
    ) as prev_period_revenue,
    
    CASE 
        WHEN fs.form_type = '10-Q' AND LAG(fs.revenue) OVER (
            PARTITION BY fs.cik, fs.form_type 
            ORDER BY fs.fiscal_year, fs.fiscal_quarter
        ) > 0 
        THEN ROUND(((fs.revenue - LAG(fs.revenue) OVER (
            PARTITION BY fs.cik, fs.form_type 
            ORDER BY fs.fiscal_year, fs.fiscal_quarter
        )) * 100.0 / LAG(fs.revenue) OVER (
            PARTITION BY fs.cik, fs.form_type 
            ORDER BY fs.fiscal_year, fs.fiscal_quarter
        )), 2)
        ELSE NULL
    END as sequential_growth_percent,
    
    -- Year-over-year comparison
    LAG(fs.revenue, 4) OVER (
        PARTITION BY fs.cik, fs.form_type 
        ORDER BY fs.fiscal_year, fs.fiscal_quarter
    ) as yoy_revenue,
    
    CASE 
        WHEN LAG(fs.revenue, 4) OVER (
            PARTITION BY fs.cik, fs.form_type 
            ORDER BY fs.fiscal_year, fs.fiscal_quarter
        ) > 0 
        THEN ROUND(((fs.revenue - LAG(fs.revenue, 4) OVER (
            PARTITION BY fs.cik, fs.form_type 
            ORDER BY fs.fiscal_year, fs.fiscal_quarter
        )) * 100.0 / LAG(fs.revenue, 4) OVER (
            PARTITION BY fs.cik, fs.form_type 
            ORDER BY fs.fiscal_year, fs.fiscal_quarter
        )), 2)
        ELSE NULL
    END as yoy_growth_percent,
    
    -- Filing recency indicator
    JULIANDAY('now') - JULIANDAY(fs.filing_date) as days_since_filing,
    CASE 
        WHEN JULIANDAY('now') - JULIANDAY(fs.filing_date) <= 30 THEN '🟢 Very Recent'
        WHEN JULIANDAY('now') - JULIANDAY(fs.filing_date) <= 90 THEN '🟡 Recent'
        WHEN JULIANDAY('now') - JULIANDAY(fs.filing_date) <= 180 THEN '🟠 Somewhat Stale'
        ELSE '🔴 Stale Data'
    END as data_freshness,
    
    -- Performance context
    CASE 
        WHEN fs.form_type = '10-Q' AND fs.fiscal_quarter = 1 THEN 'Q1 - Fresh Start'
        WHEN fs.form_type = '10-Q' AND fs.fiscal_quarter = 2 THEN 'Q2 - Mid-Year'
        WHEN fs.form_type = '10-Q' AND fs.fiscal_quarter = 3 THEN 'Q3 - Pre-Holiday'
        WHEN fs.form_type = '10-K' THEN 'Full Year Results'
        ELSE 'Other Period'
    END as business_context

FROM financial_statements fs
JOIN companies c ON fs.cik = c.cik
WHERE fs.form_type IN ('10-K', '10-Q')
    AND fs.revenue IS NOT NULL
    AND fs.net_income IS NOT NULL
    AND fs.fiscal_year >= 2023
ORDER BY c.ticker, fs.fiscal_year DESC, 
    CASE fs.form_type WHEN '10-K' THEN 0 ELSE 1 END,
    fs.fiscal_quarter DESC;

-- =====================================================================================
-- SECTION 6: CASH FLOW QUALITY ANALYSIS WITH FORM TYPE CONTEXT
-- =====================================================================================

-- Query 8: Enhanced Cash Flow Analysis by Filing Type
SELECT 
    c.ticker,
    c.company_name,
    fs.fiscal_year,
    fs.fiscal_quarter,
    fs.form_type,
    CASE 
        WHEN fs.form_type = '10-K' THEN 'Annual Cash Flow'
        WHEN fs.form_type = '10-Q' THEN 'Q' || fs.fiscal_quarter || ' Cash Flow'
        ELSE 'Other'
    END as cash_flow_context,
    fs.filing_date,
    ROUND