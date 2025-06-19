# SEC Financial Analytics Platform

**Enterprise-Grade Financial Data Platform with Advanced SQL Analytics & Executive Business Intelligence**

A comprehensive financial intelligence platform that delivers real-time SEC EDGAR data analysis, proprietary investment algorithms, and executive-level Power BI dashboards for any combination of publicly traded companies (up to 8 stocks) through advanced Python programming, sophisticated SQL analytics, and professional business intelligence development.

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![Power BI](https://img.shields.io/badge/Power%20BI-Dashboard-yellow.svg)](https://powerbi.microsoft.com)
[![SQL](https://img.shields.io/badge/SQL-Advanced-green.svg)](https://sqlite.org)
[![SEC API](https://img.shields.io/badge/SEC%20API-Live%20Data-red.svg)](https://data.sec.gov)

## 🚀 Project Overview

This enterprise-grade platform leverages advanced Python programming, complex SQL analytics, and professional business intelligence through:

- **Production Python Development** - Advanced API integration, data processing, and financial modeling
- **Live SEC EDGAR API Integration** - Real-time financial data collection with rate limiting and retry logic
- **Advanced SQL Analytics Portfolio** - 800+ lines of sophisticated financial analysis queries
- **Proprietary Investment Algorithm** - Multi-factor scoring system with Wall Street comparison
- **Executive Power BI Dashboards** - 6 comprehensive dashboards with advanced DAX measures
- **Production Database Design** - Optimized SQLite schema with proper indexing and relationships

## 📊 Business Intelligence Showcase

### 🎯 Executive Dashboard Suite (Power BI)

**Professional Financial Intelligence Platform featuring:**

**6-Dashboard Executive Suite:**
1. **Financial Health Scorecard** - *Key Performance Indicators Analysis*
2. **Financial Performance Analysis** - *Performance Trends & Financial Health Metrics*
3. **Investment Intelligence Dashboard** - *Data-Driven Algorithmic Recommendations*
4. **Wall Street Analyst Ratings** - *Consensus Ratings, Price Targets & Market Sentiment*
5. **Risk and Value Assessment** - *PE vs ROE and Price-to-Book vs Dividend Analysis*
6. **Investment Recommendation Analysis** - *Personal Investment Thesis vs. Wall Street Consensus*

[📸 View Dashboard Screenshots](docs/dashboard_screenshots/) | [📊 Download Power BI File](docs/SEC_Financial_Intelligence_Dashboard.pbix)

### 💡 Key Business Insights Delivered

**Investment Algorithm Performance:**
- **Top Recommendations**: Microsoft (8.2/10), Apple (6.4/10), Coca-Cola (6.3/10)
- **Growth Leaders**: General Electric and Microsoft (both 10/10 growth scores)
- **Efficiency Champions**: Walmart and Apple leading operational excellence
- **Risk Considerations**: Mixed liquidity profiles across traditional vs tech companies

**Market Intelligence:**
- Profitability leaders show consistent strong fundamentals (Microsoft, Apple, Coca-Cola)
- Growth patterns vary significantly across traditional vs technology sectors
- Operational efficiency correlates with sustainable competitive advantages
- Liquidity management varies by industry and business model

## 🏗️ Technical Architecture

```
SEC EDGAR API → Data Collection → Advanced Processing → SQLite Database → SQL Analytics → Power BI Intelligence
     ↓              ↓                    ↓                   ↓              ↓              ↓
Live Data      Rate Limited       Financial Metrics     Optimized        Investment     Executive
Collection     Python Pipeline    Calculation          Schema Design     Algorithm      Dashboards
```

### Core Components:
- **`interactive_init.py`** - User-friendly data collection with company selection
- **`run_analysis.py`** - Master pipeline orchestration and execution
- **`export_advanced_analytics.py`** - Proprietary investment algorithm
- **`get_analyst_ratings.py`** - Wall Street analyst data integration (Finnhub API)
- **Advanced SQL Portfolio** - Comprehensive analytics library (800+ lines)
- **Power BI Intelligence** - Executive dashboards with sophisticated DAX measures

## 📈 Dataset & Coverage

**Companies Analyzed**: 8 diversified major companies (configurable for any publicly traded companies)
- Apple (AAPL), Microsoft (MSFT), Procter & Gamble (PG), Coca-Cola (KO)
- Tesla (TSLA), General Electric (GE), Walmart (WMT), Walt Disney (DIS)

**Platform Flexibility**: Users can analyze any publicly traded companies (up to 8 companies) through an interactive console prompt when executing `run_analysis.py`.

**Data Scope**:
- **Time Range**: 2009-2025 (16+ years of historical data)
- **Records**: 850+ validated financial statement records
- **Filing Types**: 10-K (Annual), 10-Q (Quarterly) with form-specific analysis
- **Metrics**: 27 comprehensive financial metrics including calculated ratios

**Real-Time Integration**:
- SEC EDGAR API for historical financial data
- Finnhub API for current analyst ratings and market data
- Automated data validation and quality scoring

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Finnhub API key (free tier available)

### Installation & Setup

1. **Clone the repository**
```bash
git clone https://github.com/justinrushPHL/sec-financial-analytics-platform.git
cd sec-financial-analytics-platform
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure API access**
```bash
cp .env.example .env
# Edit .env and add your Finnhub API key
```

5. **Run the complete pipeline**
```bash
python run_analysis.py
```

### Alternative Execution Methods

```bash
# Interactive company selection
python interactive_init.py

# Legacy pipeline runner  
python main.py

# Individual components
python export_advanced_analytics.py    # Investment algorithm only
python get_analyst_ratings.py          # Wall Street data only
```

## 💼 Advanced SQL Analytics Portfolio

**Demonstrating sophisticated SQL programming across multiple complexity levels:**

### 📊 Basic SQL Demonstrations
- Revenue analysis and company comparisons
- Time-series filtering and fiscal year analysis
- Form type differentiation (10-K vs 10-Q context)

### 🔧 Intermediate SQL Expertise  
- Window functions for year-over-year growth analysis
- LAG/LEAD functions for trend identification
- Multi-table joins with complex fiscal period conditions
- Statistical analysis using PERCENTILE_CONT and STDDEV

### 🧠 Advanced SQL Programming
- Complex CTEs with recursive business logic
- Dynamic benchmarking algorithms against sector medians
- Proprietary financial health scoring using nested CASE statements
- Multi-dimensional composite scoring with weighted calculations

### 🎯 Executive-Level Analytics
- Automated investment recommendation engines
- Risk assessment calculations with threshold monitoring
- Competitive positioning analytics with market share evolution
- Filing data quality assessment and completeness scoring

[📜 View Complete SQL Portfolio](sql/sample_queries.sql)

## 🎯 Proprietary Investment Algorithm

**Multi-Factor Financial Health Scoring System:**

### Scoring Methodology (Weighted 10-point scale)
- **Profitability Score** (25%): Net margin + Operating efficiency analysis
- **Growth Trajectory** (25%): Revenue growth + Market expansion trends
- **Liquidity Score** (20%): Current ratio + Quick ratio assessment  
- **Operational Efficiency** (20%): Asset turnover + Inventory management
- **Base Score Component** (10%): Stability factor (fixed at 6.0)

### Algorithm vs Wall Street Comparison
```python
# Example: Current top recommendations
Algorithm Ratings:     Wall Street Consensus:
Microsoft: BUY         85% BUY/STRONG BUY
Apple: HOLD           70% BUY/HOLD  
Coca-Cola: HOLD       65% BUY/HOLD
```

**Investment Performance Validation:**
- Correlation analysis with professional analyst recommendations
- Risk-adjusted return calculations
- Sector benchmark comparisons with statistical significance testing

## 📁 Project Structure

```
sec-financial-analytics-platform/
├── 📁 config/
│   └── config.py                    # Environment & API configuration
├── 📁 src/  
│   ├── data_collector.py            # SEC API integration with retry logic
│   └── database_manager.py          # SQLite optimization & export management
├── 📁 sql/
│   └── sample_queries.sql           # 800+ lines advanced SQL analytics
├── 📁 docs/
│   ├── SEC_Financial_Intelligence_Dashboard.pbix  # Executive Power BI dashboards
│   ├── dax_measures.md              # Advanced DAX documentation
│   └── 📁 dashboard_screenshots/     # Visual portfolio showcase
├── 📁 data/
│   └── financial_data.db            # Optimized SQLite database
├── 📁 exports/
│   └── 📁 advanced_analytics/        # Investment algorithm outputs
├── 📊 run_analysis.py               # **MAIN EXECUTION FILE**
├── 📊 interactive_init.py           # User-friendly data collection
├── 📊 export_advanced_analytics.py  # Investment algorithm engine
├── 📊 get_analyst_ratings.py        # Wall Street comparison data
└── 📊 main.py                       # Alternative pipeline runner
```

## 🎨 Power BI Dashboard Deep Dive

### Advanced DAX Financial Engineering

**5-Factor Weighted Composite Scoring Algorithm:**
```dax
Financial Health Score = 
([Profitability Score] * 0.25) + 
([Liquidity Score] * 0.20) + 
([Growth Score Simple] * 0.25) + 
([Efficiency Score] * 0.20) + 
(6 * 0.10)
```

**Dynamic Executive Metrics:**
```dax
Top Performer = 
VAR TopCompany = TOPN(1, VALUES(Company[Name]), [Financial Health Score], DESC)
RETURN MAXX(TopCompany, Company[Name]) & " (" & FORMAT([Financial Health Score], "0.0") & ")"
```

**Strategic Value Classification:**
```dax
Value_Quadrant = 
IF([price_to_book] <= 1.5 && [dividend_yield] >= 3, "Value Sweet Spot",
   IF([price_to_book] <= 1.5, "Growth Value", 
      IF([dividend_yield] >= 3, "Income Premium", "Expensive Growth")))
```

### Dashboard Features
- **Interactive Filtering** - Fiscal year, company, and metric slicing
- **Real-Time Calculations** - Dynamic scoring with live data updates  
- **Executive KPI Cards** - Top/bottom performers with automatic identification
- **Risk Alert System** - Threshold monitoring with visual indicators
- **Competitive Intelligence** - Algorithm vs Wall Street validation

[📊 Complete DAX Documentation](docs/dax_measures.md)

## 💡 Key Technical Achievements

### Data Engineering Excellence
- **Production API Integration** - Rate limiting, retry logic, comprehensive error handling
- **Database Optimization** - Strategic indexing, normalized schema, query performance
- **Data Quality Management** - Validation, cleaning, completeness scoring
- **Automated Export Pipeline** - BI-ready CSV generation with timestamp management

### Financial Domain Expertise  
- **XBRL Processing** - Complex SEC filing parsing across multiple taxonomies
- **Financial Ratio Calculations** - Industry-standard metrics with proper handling
- **Investment Algorithm Development** - Multi-factor scoring with statistical validation
- **Risk Assessment Modeling** - Early warning systems with threshold management

### Business Intelligence Mastery
- **Advanced DAX Programming** - Complex calculations with proper context handling
- **Executive Dashboard Design** - C-suite ready visualization and insights
- **Interactive Analytics** - Real-time filtering with performance optimization
- **Strategic Business Logic** - Value classification and competitive positioning

## 🔮 Technical Roadmap

### Architecture Evolution
- [ ] **Real-Time Streaming** - Scheduled automatic data updates
- [ ] **Machine Learning Integration** - Predictive financial modeling
- [ ] **REST API Development** - External data access endpoints  
- [ ] **Cloud Deployment** - Azure/AWS scalable architecture
- [ ] **Additional Data Sources** - Market data, sentiment analysis
- [ ] **Mobile Dashboard** - Power BI mobile optimization

### Enterprise Scaling
- [ ] **PostgreSQL Migration** - Enterprise database upgrade
- [ ] **Docker Containerization** - Deployment standardization
- [ ] **CI/CD Pipeline** - Automated testing and deployment
- [ ] **Multi-Tenant Architecture** - Enterprise user management

## 📊 Portfolio Demonstration Value

### For Data Analyst Roles
- ✅ **Advanced Python Programming** - Production-grade API integration and financial modeling
- ✅ **Advanced SQL Programming** - Complex analytics beyond basic reporting
- ✅ **Financial Domain Knowledge** - CPA/MBA-level analysis and interpretation
- ✅ **Business Intelligence Tools** - Professional Power BI development
- ✅ **Data Pipeline Engineering** - End-to-end ETL process design

### For Business Intelligence Positions  
- ✅ **Executive Dashboard Development** - C-suite ready visualization
- ✅ **Advanced DAX Programming** - Complex financial calculations
- ✅ **Strategic Business Analysis** - Investment recommendations and insights
- ✅ **Data Architecture Design** - Scalable BI solution development

### For Data Engineering Roles
- ✅ **Python API Integration Expertise** - Production-grade data collection
- ✅ **Database Design & Optimization** - Performance-focused schema development
- ✅ **Data Quality Management** - Validation, cleaning, monitoring systems
- ✅ **Real-World Application** - Financial services industry experience

### For Data Science Positions
- ✅ **Advanced Python Programming** - Complex data processing and analysis
- ✅ **Financial Modeling & Algorithm Development** - Multi-factor scoring systems
- ✅ **Statistical Analysis** - Performance validation and benchmarking
- ✅ **Business Intelligence Integration** - Model deployment and visualization

## 📝 Data Sources & Compliance

**Primary Data Sources:**
- **SEC EDGAR API** - Official financial filings (data.sec.gov)
- **Finnhub API** - Real-time market data and analyst ratings

**Regulatory Compliance:**
- Full compliance with SEC.gov robots.txt and rate limiting guidelines
- Proper API authentication and usage tracking
- Data usage within public domain and fair use guidelines

**Data Quality Standards:**
- Comprehensive validation across 27 financial metrics
- Form-type specific processing (10-K vs 10-Q context)
- Historical data integrity with audit trail maintenance

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📧 Contact & Portfolio

**Justin Rush** - Senior Data Analytics Professional

[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/justinrush/)
[![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/justinrushPHL)

**Project Repository**: [github.com/justinrushPHL/sec-financial-analytics-platform](https://github.com/justinrushPHL/sec-financial-analytics-platform)

---

## 🏆 Portfolio Impact Statement

*This project delivers a complete financial intelligence platform combining enterprise-grade data engineering, advanced SQL programming, sophisticated financial analysis, and executive-level business intelligence. The integration of advanced Python development, proprietary investment algorithms, and production-ready deliverables represents the full spectrum of technical and analytical capabilities required for senior data science and analytics positions.*

**Core Competencies Delivered:**
- Advanced Python Programming & API Integration
- Enterprise Data Engineering & Database Design  
- Advanced SQL Analytics & Financial Modeling
- Proprietary Algorithm Development & Statistical Analysis
- Executive Business Intelligence & Dashboard Development
- Production Code Quality & Documentation Excellence

---

*Last Updated: June 19, 2025 | Built for Senior Data Analytics Portfolio Demonstration*
