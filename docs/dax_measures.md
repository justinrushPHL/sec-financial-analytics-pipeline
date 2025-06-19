# DAX Measures Documentation

## Overview
This document contains all custom DAX measures created for the SEC Financial Intelligence Dashboard. These measures transform raw SEC EDGAR financial data into actionable business intelligence metrics using advanced financial analysis algorithms.

---

## 📊 Core Financial Health Measures

### 1. Profitability Score
**Purpose:** Evaluates company profitability using net margin and return on equity  
**Scale:** 2-10 (2 = Poor, 10 = Excellent)

```dax
Profitability Score = 
VAR NetMargin = DIVIDE(
    AVERAGE('financial_data_export_20250611_153833'[net_income_millions]), 
    AVERAGE('financial_data_export_20250611_153833'[Revenue ($ Millions)])
) * 100
VAR ROE = DIVIDE(
    AVERAGE('financial_data_export_20250611_153833'[net_income_millions]), 
    AVERAGE('financial_data_export_20250611_153833'[stockholders_equity_millions])
) * 100
RETURN 
IF(NetMargin >= 20 && ROE >= 15, 10,
   IF(NetMargin >= 15 && ROE >= 10, 8,
      IF(NetMargin >= 10 && ROE >= 5, 6,
         IF(NetMargin >= 5 && ROE >= 0, 4, 2))))
```

**Business Logic:**
- Combines net profit margin and return on equity for comprehensive profitability assessment
- Score 10: Net margin ≥20% AND ROE ≥15% (exceptional profitability)
- Score 8: Net margin ≥15% AND ROE ≥10% (strong profitability)
- Score 6: Net margin ≥10% AND ROE ≥5% (adequate profitability)
- Score 4: Net margin ≥5% AND ROE ≥0% (marginal profitability)
- Score 2: Below minimum thresholds (poor profitability)

### 2. Liquidity Score
**Purpose:** Measures company's ability to meet short-term obligations  
**Scale:** 2-10 (2 = Poor liquidity, 10 = Excellent liquidity)

```dax
Liquidity Score = 
VAR CurrentRatio = DIVIDE(
    AVERAGE('financial_data_export_20250611_153833'[current_assets_millions]), 
    AVERAGE('financial_data_export_20250611_153833'[current_liabilities_millions])
)
RETURN 
IF(CurrentRatio >= 3.0, 10,
   IF(CurrentRatio >= 2.5, 9,
      IF(CurrentRatio >= 2.0, 8,
         IF(CurrentRatio >= 1.5, 6,
            IF(CurrentRatio >= 1.2, 4, 2)))))
```

**Business Logic:**
- Evaluates current ratio (current assets / current liabilities) for liquidity analysis
- Score 10: Current ratio ≥3.0 (excellent liquidity buffer)
- Score 9: Current ratio ≥2.5 (very strong liquidity)
- Score 8: Current ratio ≥2.0 (strong liquidity position)
- Score 6: Current ratio ≥1.5 (adequate liquidity)
- Score 4: Current ratio ≥1.2 (marginal liquidity)
- Score 2: Below 1.2 (liquidity concerns)

### 3. Efficiency Score
**Purpose:** Assesses how effectively company utilizes its assets  
**Scale:** 2-10 (2 = Poor efficiency, 10 = Excellent efficiency)

```dax
Efficiency Score = 
VAR AssetTurnover = DIVIDE(
    AVERAGE('financial_data_export_20250611_153833'[Revenue ($ Millions)]), 
    AVERAGE('financial_data_export_20250611_153833'[total_assets_millions])
)
RETURN 
IF(AssetTurnover >= 1.5, 10,
   IF(AssetTurnover >= 1.2, 8,
      IF(AssetTurnover >= 1.0, 6,
         IF(AssetTurnover >= 0.8, 4, 2))))
```

**Business Logic:**
- Measures asset turnover (revenue / total assets) for operational efficiency
- Score 10: Asset turnover ≥1.5 (highly efficient operations)
- Score 8: Asset turnover ≥1.2 (strong efficiency)
- Score 6: Asset turnover ≥1.0 (adequate efficiency)
- Score 4: Asset turnover ≥0.8 (below average efficiency)
- Score 2: Below 0.8 (poor operational efficiency)

### 4. Growth Score Simple
**Purpose:** Evaluates company's revenue growth trajectory  
**Scale:** 2-10 (2 = Poor/negative growth, 10 = Excellent growth)

```dax
Growth Score Simple = 
VAR Revenue2024 = CALCULATE(
    MAX('financial_data_export_20250611_153833'[Revenue ($ Millions)]), 
    'financial_data_export_20250611_153833'[Fiscal Year] = 2024 && 
    'financial_data_export_20250611_153833'[form_type] = "10-K"
)
VAR Revenue2023 = CALCULATE(
    MAX('financial_data_export_20250611_153833'[Revenue ($ Millions)]), 
    'financial_data_export_20250611_153833'[Fiscal Year] = 2023 && 
    'financial_data_export_20250611_153833'[form_type] = "10-K"
)
VAR GrowthRate = DIVIDE(Revenue2024 - Revenue2023, Revenue2023) * 100
RETURN 
IF(GrowthRate >= 12, 10,
   IF(GrowthRate >= 8, 8,
      IF(GrowthRate >= 5, 6,
         IF(GrowthRate >= 2, 4,
            IF(GrowthRate >= 0, 3, 2)))))
```

**Business Logic:**
- Measures year-over-year revenue growth (2024 vs 2023) using annual filings only
- Score 10: Revenue growth ≥12% (exceptional growth)
- Score 8: Revenue growth ≥8% (strong growth)
- Score 6: Revenue growth ≥5% (solid growth)
- Score 4: Revenue growth ≥2% (modest growth)
- Score 3: Revenue growth ≥0% (flat/minimal growth)
- Score 2: Negative growth (declining revenue)

### 5. Financial Health Score
**Purpose:** Composite score combining all financial health dimensions  
**Scale:** 2-10 (2 = Poor overall health, 10 = Excellent overall health)

```dax
Financial Health Score = 
([Profitability Score] + [Liquidity Score] + [Growth Score Simple] + [Efficiency Score]) / 4
```

**Business Logic:**
- Equally weighted average of all four core financial health metrics
- Provides comprehensive assessment of company's overall financial position
- Used as primary ranking metric for executive dashboards

---

## 🎯 Executive Summary Measures

### Top Performer
**Purpose:** Dynamically identifies the highest-scoring company with score

```dax
Top Performer = 
VAR TopCompany = 
    TOPN(
        1,
        VALUES('financial_data_export_20250611_153833'[Company Name]),
        [Financial Health Score],
        DESC
    )
VAR TopScore = 
    MAXX(TopCompany, [Financial Health Score])
RETURN 
    MAXX(TopCompany, 'financial_data_export_20250611_153833'[Company Name]) 
    & " (" & FORMAT(TopScore, "0.0") & ")"
```

### Bottom Performer
**Purpose:** Dynamically identifies the lowest-scoring company with score

```dax
Bottom Performer = 
VAR BottomCompany = 
    TOPN(
        1,
        VALUES('financial_data_export_20250611_153833'[Company Name]),
        [Financial Health Score],
        ASC
    )
VAR BottomScore = 
    MINX(BottomCompany, [Financial Health Score])
RETURN 
    MAXX(BottomCompany, 'financial_data_export_20250611_153833'[Company Name]) 
    & " (" & FORMAT(BottomScore, "0.0") & ")"
```

### Average Financial Health
**Purpose:** Shows average financial health score across all companies

```dax
Average Financial Health = 
FORMAT(
    AVERAGEX(
        VALUES('financial_data_export_20250611_153833'[Company Name]),
        [Financial Health Score]
    ), 
    "0.0"
)
```

### Total Companies
**Purpose:** Counts distinct companies in analysis

```dax
Total Companies = 
DISTINCTCOUNT('financial_data_export_20250611_153833'[Company Name])
```

---

## 📊 Wall Street Analyst Measures

### Bullish Percentage
**Purpose:** Calculates percentage of analyst ratings that are bullish (Strong Buy + Buy)

```dax
Bullish Percentage = 
DIVIDE(
    SUM(analyst_ratings_finnhub_latest[strong_buy_count]) + 
    SUM(analyst_ratings_finnhub_latest[buy_count]),
    SUM(analyst_ratings_finnhub_latest[strong_buy_count]) + 
    SUM(analyst_ratings_finnhub_latest[buy_count]) + 
    SUM(analyst_ratings_finnhub_latest[hold_count]) + 
    SUM(analyst_ratings_finnhub_latest[sell_count]) + 
    SUM(analyst_ratings_finnhub_latest[strong_sell_count]),
    0
) * 100
```

### Value Quadrant Classification
**Purpose:** Categorizes companies based on valuation metrics

```dax
Value_Quadrant = 
IF([price_to_book] <= 1.5 && [dividend_yield] >= 3, "Value Sweet Spot",
   IF([price_to_book] <= 1.5 && [dividend_yield] < 3, "Growth Value", 
      IF([price_to_book] > 1.5 && [dividend_yield] >= 3, "Income Premium",
         "Expensive Growth")))
```

**Business Logic:**
- **Value Sweet Spot**: P/B ≤1.5 AND Dividend yield ≥3% (undervalued with income)
- **Growth Value**: P/B ≤1.5 AND Dividend yield <3% (undervalued growth play)
- **Income Premium**: P/B >1.5 AND Dividend yield ≥3% (premium for income)
- **Expensive Growth**: P/B >1.5 AND Dividend yield <3% (growth at premium valuation)

---

## 📋 Technical Notes

### Data Sources
- **Primary Table:** `financial_data_export_20250611_153833` (SEC EDGAR data)
- **Analyst Data:** `analyst_ratings_finnhub_latest` (Finnhub API data)
- **Time Period:** 2009-2025 (SEC data), Current (analyst data)
- **Companies:** 8 major companies (AAPL, MSFT, GE, PG, WMT, DIS, KO, TSLA)

### Key Column Names
- **Revenue:** `Revenue ($ Millions)`
- **Company:** `Company Name`
- **Fiscal Year:** `Fiscal Year`
- **Form Type:** `form_type` (10-K for annual, 10-Q for quarterly)

### Calculation Context
- Growth measures use `MAX()` with form_type filter to get annual data only
- Other measures use `AVERAGE()` to handle multiple fiscal years per company
- All measures designed for real-time filtering and slicing
- Error handling built into ratio calculations using `DIVIDE()` function

### Performance Considerations
- Measures calculated at query time for real-time filtering
- Optimized for interactive dashboard performance
- Compatible with DirectQuery and Import modes
- Growth calculations filtered to annual filings only for accuracy

---

## 🔄 Maintenance & Updates

### Data Refresh Process
1. Update source CSV files with latest SEC and analyst data
2. Refresh Power BI dataset
3. All measures automatically recalculate with new data
4. Verify growth calculations are picking up latest fiscal year

### Threshold Adjustments
Financial health scoring thresholds are calibrated for 2025 market conditions:
- **Growth thresholds** reflect post-COVID economic normalization
- **Profitability thresholds** account for current interest rate environment
- **Liquidity thresholds** consider current market volatility

### Known Data Quality Issues
- **Apple 2024**: Shows -0.83% growth (accurate reflection of business reality)
- **Quarterly vs Annual**: Growth measure specifically uses 10-K filings only
- **Missing columns**: Some legacy measures reference columns not in current dataset

---

## 🎯 Dashboard Integration

### Primary Scorecard
Uses all five core measures to create comprehensive company rankings:
1. Financial Health Score (composite)
2. Individual dimension scores (Profitability, Liquidity, Growth, Efficiency)
3. Value quadrant classification
4. Wall Street consensus comparison

### Interactive Features
- **Fiscal year slicing**: Compare performance across different years
- **Company filtering**: Focus analysis on specific companies
- **Metric drilling**: Click through from composite scores to individual components
- **Benchmark comparison**: Algorithm vs Wall Street recommendations

---

*Last Updated: June 19, 2025*  
*Updated for current data structure and 2025 market conditions*  
*Created for SEC Financial Analytics Intelligence Platform*