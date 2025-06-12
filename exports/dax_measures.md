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
VAR NetMargin = DIVIDE(AVERAGE('financial_data_export_20250611_153833'[net_income_millions]), AVERAGE('financial_data_export_20250611_153833'[revenue_millions])) * 100
VAR ROE = DIVIDE(AVERAGE('financial_data_export_20250611_153833'[net_income_millions]), AVERAGE('financial_data_export_20250611_153833'[stockholders_equity_millions])) * 100
RETURN IF(NetMargin >= 20 && ROE >= 15, 10, IF(NetMargin >= 15 && ROE >= 10, 8, IF(NetMargin >= 10 && ROE >= 5, 6, IF(NetMargin >= 5 && ROE >= 0, 4, 2))))
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
VAR CurrentRatio = DIVIDE(AVERAGE('financial_data_export_20250611_153833'[current_assets_millions]), AVERAGE('financial_data_export_20250611_153833'[current_liabilities_millions]))
VAR QuickRatio = DIVIDE(AVERAGE('financial_data_export_20250611_153833'[current_assets_millions]) - AVERAGE('financial_data_export_20250611_153833'[inventory_millions]), AVERAGE('financial_data_export_20250611_153833'[current_liabilities_millions]))
RETURN IF(CurrentRatio >= 2.5 && QuickRatio >= 1.5, 10, IF(CurrentRatio >= 2.0 && QuickRatio >= 1.2, 8, IF(CurrentRatio >= 1.5 && QuickRatio >= 1.0, 6, IF(CurrentRatio >= 1.2 && QuickRatio >= 0.8, 4, 2))))
```

**Business Logic:**
- Evaluates both current ratio and quick ratio for comprehensive liquidity analysis
- Score 10: Current ratio ≥2.5 AND Quick ratio ≥1.5 (excellent liquidity buffer)
- Score 8: Current ratio ≥2.0 AND Quick ratio ≥1.2 (strong liquidity position)
- Score 6: Current ratio ≥1.5 AND Quick ratio ≥1.0 (adequate liquidity)
- Score 4: Current ratio ≥1.2 AND Quick ratio ≥0.8 (marginal liquidity)
- Score 2: Below minimum thresholds (liquidity concerns)

### 3. Efficiency Score
**Purpose:** Assesses how effectively company utilizes its assets  
**Scale:** 2-10 (2 = Poor efficiency, 10 = Excellent efficiency)

```dax
Efficiency Score = 
VAR AssetTurnover = DIVIDE(AVERAGE('financial_data_export_20250611_153833'[revenue_millions]), AVERAGE('financial_data_export_20250611_153833'[total_assets_millions]))
VAR InventoryTurnover = DIVIDE(AVERAGE('financial_data_export_20250611_153833'[cost_of_goods_sold_millions]), AVERAGE('financial_data_export_20250611_153833'[inventory_millions]))
RETURN IF(AssetTurnover >= 1.5 && InventoryTurnover >= 8, 10, IF(AssetTurnover >= 1.2 && InventoryTurnover >= 6, 8, IF(AssetTurnover >= 1.0 && InventoryTurnover >= 4, 6, IF(AssetTurnover >= 0.8 && InventoryTurnover >= 2, 4, 2))))
```

**Business Logic:**
- Combines asset turnover and inventory turnover for operational efficiency assessment
- Score 10: Asset turnover ≥1.5 AND Inventory turnover ≥8 (highly efficient operations)
- Score 8: Asset turnover ≥1.2 AND Inventory turnover ≥6 (strong efficiency)
- Score 6: Asset turnover ≥1.0 AND Inventory turnover ≥4 (adequate efficiency)
- Score 4: Asset turnover ≥0.8 AND Inventory turnover ≥2 (below average efficiency)
- Score 2: Below minimum thresholds (poor operational efficiency)

### 4. Growth Score Simple
**Purpose:** Evaluates company's revenue growth trajectory  
**Scale:** 2-10 (2 = Poor/negative growth, 10 = Excellent growth)

```dax
Growth Score Simple = 
VAR RevenueGrowth = DIVIDE(AVERAGE('financial_data_export_20250611_153833'[revenue_millions]) - AVERAGE('financial_data_export_20250611_153833'[revenue_millions]), AVERAGE('financial_data_export_20250611_153833'[revenue_millions])) * 100
RETURN IF(RevenueGrowth >= 25, 10, IF(RevenueGrowth >= 15, 8, IF(RevenueGrowth >= 10, 6, IF(RevenueGrowth >= 5, 4, 2))))
```

**Business Logic:**
- Measures year-over-year revenue growth percentage
- Score 10: Revenue growth ≥25% (exceptional growth)
- Score 8: Revenue growth ≥15% (strong growth)
- Score 6: Revenue growth ≥10% (solid growth)
- Score 4: Revenue growth ≥5% (modest growth)
- Score 2: Growth <5% (stagnant or declining)

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
    & " (" & FORMAT(TopScore, "0.00") & ")"
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
    & " (" & FORMAT(BottomScore, "0.00") & ")"
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
    "0.00"
)
```

### Total Companies
**Purpose:** Counts distinct companies in analysis

```dax
Total Companies = 
DISTINCTCOUNT('financial_data_export_20250611_153833'[Company Name])
```

---

## 📋 Technical Notes

### Data Source
- **Table:** `financial_data_export_20250611_153833`
- **Source:** SEC EDGAR financial filings
- **Time Period:** 2009-2025
- **Companies:** 8 major technology companies

### Calculation Context
- All measures use `AVERAGE()` function to handle multiple fiscal years per company
- Measures are designed to work with fiscal year slicers for period comparison
- Error handling built into ratio calculations using `DIVIDE()` function

### Performance Considerations
- Measures calculated at query time for real-time filtering
- Optimized for interactive dashboard performance
- Compatible with DirectQuery and Import modes

---

## 🔄 Maintenance & Updates

### Refreshing Data
1. Update source CSV file with latest SEC data
2. Refresh Power BI dataset
3. All measures automatically recalculate with new data

### Modifying Thresholds
Financial health scoring thresholds can be adjusted based on:
- Industry benchmarks
- Economic conditions
- Strategic objectives
- Stakeholder requirements

### Adding New Metrics
Framework supports additional measures such as:
- Debt-to-equity ratios
- Working capital analysis
- Market performance indicators
- ESG compliance scores

---

*Last Updated: June 11, 2025*  
*Created for SEC Financial Analytics Intelligence Platform*