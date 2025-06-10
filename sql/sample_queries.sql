-- Sample SQL Queries for Financial Analysis
-- Save this file as sql/sample_queries.sql

-- Query 1: Latest Annual Revenue by Company (10-K filings only)
-- Shows the most recent annual revenue for each company
SELECT 
    c.ticker,
    c.company_name,
    fs.fiscal_year,
    ROUND(fs.revenue / 1000000000.0, 2) as revenue_billions,
    fs.filing_date,
    fs.period_end_date
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
ORDER BY fs.revenue DESC;

-- Query 2: Revenue Growth Analysis (Year-over-Year)
-- Calculate revenue growth rates for each company
WITH revenue_by_year AS (
    SELECT 
        c.ticker,
        c.company_name,
        fs.fiscal_year,
        fs.revenue,
        LAG(fs.revenue) OVER (PARTITION BY fs.cik ORDER BY fs.fiscal_year) as prior_year_revenue
    FROM financial_statements fs
    JOIN companies c ON fs.cik = c.cik
    WHERE fs.form_type = '10-K' 
        AND fs.revenue IS NOT NULL
)
SELECT 
    ticker,
    company_name,
    fiscal_year,
    ROUND(revenue / 1000000.0, 2) as revenue_millions,
    ROUND(prior_year_revenue / 1000000.0, 2) as prior_year_revenue_millions,
    CASE 
        WHEN prior_year_revenue > 0 THEN 
            ROUND(((revenue - prior_year_revenue) * 100.0 / prior_year_revenue), 2)
        ELSE NULL 
    END as revenue_growth_percent
FROM revenue_by_year
WHERE prior_year_revenue IS NOT NULL
    AND fiscal_year >= 2022
ORDER BY revenue_growth_percent DESC;

-- Query 3: Profitability Comparison
-- Compare profit margins across companies
SELECT 
    c.ticker,
    c.company_name,
    fs.fiscal_year,
    ROUND(fs.revenue / 1000000.0, 2) as revenue_millions,
    ROUND(fs.net_income / 1000000.0, 2) as net_income_millions,
    ROUND(fs.operating_income / 1000000.0, 2) as operating_income_millions,
    CASE 
        WHEN fs.revenue > 0 THEN ROUND((fs.net_income * 100.0 / fs.revenue), 2)
        ELSE NULL 
    END as net_margin_percent,
    CASE 
        WHEN fs.revenue > 0 THEN ROUND((fs.operating_income * 100.0 / fs.revenue), 2)
        ELSE NULL 
    END as operating_margin_percent
FROM financial_statements fs
JOIN companies c ON fs.cik = c.cik
WHERE fs.form_type = '10-K' 
    AND fs.revenue > 0 
    AND fs.net_income IS NOT NULL
    AND fs.fiscal_year >= 2022
ORDER BY net_margin_percent DESC;

-- Query 4: Balance Sheet Strength
-- Analyze financial position and liquidity
SELECT 
    c.ticker,
    c.company_name,
    fs.fiscal_year,
    ROUND(fs.total_assets / 1000000.0, 2) as total_assets_millions,
    ROUND(fs.current_assets / 1000000.0, 2) as current_assets_millions,
    ROUND(fs.total_liabilities / 1000000.0, 2) as total_liabilities_millions,
    ROUND(fs.current_liabilities / 1000000.0, 2) as current_liabilities_millions,
    ROUND(fs.stockholders_equity / 1000000.0, 2) as equity_millions,
    CASE 
        WHEN fs.current_liabilities > 0 THEN 
            ROUND((fs.current_assets * 1.0 / fs.current_liabilities), 2)
        ELSE NULL 
    END as current_ratio,
    CASE 
        WHEN fs.total_assets > 0 THEN 
            ROUND((fs.total_liabilities * 100.0 / fs.total_assets), 2)
        ELSE NULL 
    END as debt_to_assets_percent
FROM financial_statements fs
JOIN companies c ON fs.cik = c.cik
WHERE fs.form_type = '10-K'
    AND fs.total_assets IS NOT NULL
    AND fs.fiscal_year >= 2022
ORDER BY current_ratio DESC;

-- Query 5: Top Performers by Revenue (Latest Year)
-- Rank companies by most recent annual revenue
SELECT 
    ROW_NUMBER() OVER (ORDER BY fs.revenue DESC) as rank,
    c.ticker,
    c.company_name,
    fs.fiscal_year,
    ROUND(fs.revenue / 1000000000.0, 2) as revenue_billions,
    ROUND(fs.net_income / 1000000000.0, 2) as net_income_billions,
    CASE 
        WHEN fs.revenue > 0 THEN ROUND((fs.net_income * 100.0 / fs.revenue), 2)
        ELSE NULL 
    END as profit_margin_percent
FROM financial_statements fs
JOIN companies c ON fs.cik = c.cik
WHERE fs.form_type = '10-K' 
    AND fs.revenue IS NOT NULL
    AND fs.fiscal_year = (
        SELECT MAX(fiscal_year) 
        FROM financial_statements 
        WHERE form_type = '10-K' AND revenue IS NOT NULL
    )
ORDER BY fs.revenue DESC;

-- Query 6: EPS Trends
-- Track earnings per share over time
SELECT 
    c.ticker,
    c.company_name,
    fs.fiscal_year,
    fs.eps_basic,
    fs.eps_diluted,
    LAG(fs.eps_diluted) OVER (PARTITION BY fs.cik ORDER BY fs.fiscal_year) as prior_year_eps,
    CASE 
        WHEN LAG(fs.eps_diluted) OVER (PARTITION BY fs.cik ORDER BY fs.fiscal_year) != 0 
        THEN ROUND(((fs.eps_diluted - LAG(fs.eps_diluted) OVER (PARTITION BY fs.cik ORDER BY fs.fiscal_year)) * 100.0 / 
                   LAG(fs.eps_diluted) OVER (PARTITION BY fs.cik ORDER BY fs.fiscal_year)), 2)
        ELSE NULL 
    END as eps_growth_percent
FROM financial_statements fs
JOIN companies c ON fs.cik = c.cik
WHERE fs.form_type = '10-K' 
    AND fs.eps_diluted IS NOT NULL
    AND fs.fiscal_year >= 2021
ORDER BY c.ticker, fs.fiscal_year;

-- Query 7: Data Completeness Check
-- See what data we have for each company
SELECT 
    c.ticker,
    c.company_name,
    COUNT(*) as total_filings,
    COUNT(CASE WHEN fs.form_type = '10-K' THEN 1 END) as annual_reports,
    COUNT(CASE WHEN fs.form_type = '10-Q' THEN 1 END) as quarterly_reports,
    MIN(fs.fiscal_year) as earliest_year,
    MAX(fs.fiscal_year) as latest_year,
    COUNT(CASE WHEN fs.revenue IS NOT NULL THEN 1 END) as records_with_revenue,
    COUNT(CASE WHEN fs.net_income IS NOT NULL THEN 1 END) as records_with_net_income
FROM companies c
LEFT JOIN financial_statements fs ON c.cik = fs.cik
GROUP BY c.cik, c.ticker, c.company_name
ORDER BY c.ticker;

-- Query 8: Cash Flow Analysis (if data is available)
-- Analyze operating cash flow vs net income
SELECT 
    c.ticker,
    c.company_name,
    fs.fiscal_year,
    ROUND(fs.operating_cash_flow / 1000000.0, 2) as operating_cf_millions,
    ROUND(fs.net_income / 1000000.0, 2) as net_income_millions,
    CASE 
        WHEN fs.net_income != 0 THEN 
            ROUND((fs.operating_cash_flow * 1.0 / fs.net_income), 2)
        ELSE NULL 
    END as cf_to_income_ratio
FROM financial_statements fs
JOIN companies c ON fs.cik = c.cik
WHERE fs.form_type = '10-K'
    AND fs.operating_cash_flow IS NOT NULL
    AND fs.net_income IS NOT NULL
    AND fs.net_income != 0
    AND fs.fiscal_year >= 2022
ORDER BY cf_to_income_ratio DESC;