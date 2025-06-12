# SEC Financial Analytics Pipeline

A comprehensive financial data pipeline that extracts, processes, and analyzes SEC EDGAR filings for major technology companies.

## 📊 Project Overview

This project demonstrates end-to-end data engineering and financial analysis capabilities by:
- Extracting real-time financial data from SEC EDGAR API
- Processing and cleaning financial statements (10-K, 10-Q, 8-K filings)
- Storing data in optimized SQLite database with proper indexing
- Providing analytical tools and dashboard capabilities

## 🏗️ Architecture

```
SEC EDGAR API → Data Collection → Data Processing → SQLite Database → Analytics & Visualization
```

### Key Components:
- **Data Collector**: SEC API integration with retry logic and rate limiting
- **Database Manager**: SQLite schema design with financial metrics optimization
- **Data Processor**: Financial statement parsing and ratio calculations
- **Analytics Tools**: SQL query engine and data export capabilities

## 📈 Dataset

**Coverage**: 8 major technology companies (AAPL, MSFT, GOOGL, AMZN, TSLA, NVDA, META, NFLX)
**Time Range**: 2009-2025 (17+ years of data)
**Records**: 850+ financial statements
**Data Types**: Annual (10-K) and Quarterly (10-Q) reports

### Financial Metrics Included:
- Revenue and profitability metrics
- Balance sheet items (assets, liabilities, equity)
- Cash flow statements
- Financial ratios (margins, liquidity, leverage)
- Earnings per share (basic and diluted)

## 🚀 Quick Start

### Prerequisites
```bash
Python 3.9+
pip install -r requirements.txt
```

### Setup
1. **Clone the repository**
```bash
git clone https://github.com/YOUR_USERNAME/sec-financial-analytics-pipeline.git
cd sec-financial-analytics-pipeline
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Run the pipeline**
```bash
python main.py
```

## 📋 Usage

### Data Collection
```bash
# Run full pipeline (collect, process, store)
python main.py

# View collected data
python view_data.py 1    # Latest revenue by company
python view_data.py 2    # Profitability comparison
python view_data.py 3    # Data summary
```

### Database Queries
```bash
# Connect to SQLite database
sqlite3 data/financial_data.db

# Run sample queries
.read sql/sample_queries.sql
```

### Data Export
The pipeline automatically exports data to CSV format for business intelligence tools:
```
exports/financial_data_export_YYYYMMDD_HHMMSS.csv
```

## 📊 Key Insights from the Data

**Revenue Leaders (2024)**:
- Amazon: $638B
- Apple: $391B  
- Google: $350B
- Microsoft: $245B

**Profitability Champions**:
- NVIDIA: 56% net margin (AI boom impact)
- Meta: 38% net margin (efficiency improvements)
- Microsoft: 36% net margin (cloud dominance)

## 🛠️ Technical Features

### Data Engineering
- **Robust API handling** with exponential backoff retry logic
- **Data validation** and cleaning for financial metrics
- **Efficient database design** with proper indexing
- **Automated data export** in BI-ready format

### Financial Analysis
- **Multi-year trend analysis** across major tech companies
- **Profitability benchmarking** with industry comparisons
- **Financial health metrics** (liquidity, leverage ratios)
- **Growth trajectory modeling**

## 📁 Project Structure

```
sec-financial-analytics-pipeline/
├── config/
│   └── config.py              # Configuration settings
├── src/
│   ├── data_collector.py      # SEC API integration
│   ├── database_manager.py    # Database operations
│   ├── data_processor.py      # Financial data processing
│   └── utils.py              # Utility functions
├── sql/
│   └── sample_queries.sql     # Pre-built analytical queries
├── data/
│   └── financial_data.db      # SQLite database
├── exports/
│   └── *.csv                  # Data exports for BI tools
├── logs/                      # Application logs
├── main.py                    # Pipeline orchestrator
├── view_data.py              # Data exploration tool
└── requirements.txt          # Dependencies
```

## 🎯 Business Intelligence Integration

The exported CSV data is optimized for:
- **Power BI** dashboards and reports
- **Tableau** financial analytics
- **Excel** pivot tables and analysis
- **Python/R** statistical modeling

### Dashboard Recommendations:
1. **Revenue Trend Analysis** - Multi-year company comparisons
2. **Profitability Dashboard** - Margin analysis and benchmarking  
3. **Financial Health Scorecard** - Liquidity and leverage metrics
4. **Market Share Evolution** - Competitive positioning over time

## 📊 Executive Financial Intelligence Dashboard

**Built with Power BI | Advanced DAX | Interactive Analytics**

Transform raw SEC financial data into executive-ready insights with our comprehensive Power BI dashboard featuring sophisticated financial health algorithms and strategic competitive analysis.

### 🎯 Dashboard Overview

**4-Page Executive Suite:**
1. **Financial Health Scorecard** - Heat map matrix with 5-factor scoring system
2. **Company Rankings & KPIs** - Dynamic leaderboards and performance metrics  
3. **Financial Trends Analysis** - Multi-year revenue and health trajectories
4. **Strategic Competitive Analysis** - Revenue vs health scatter plot with quadrant analysis

### 📈 Advanced DAX Financial Algorithms

**5-Factor Financial Health Scoring (2-10 scale):**

```dax
Financial Health Score = 
([Profitability Score] + [Liquidity Score] + [Growth Score Simple] + [Efficiency Score]) / 4
```

**Key Metrics:**
- **Profitability Score**: Net margin + ROE analysis
- **Liquidity Score**: Current ratio + Quick ratio assessment  
- **Efficiency Score**: Asset turnover + Inventory turnover
- **Growth Score**: Revenue growth trajectory analysis

### 🎯 Strategic Business Intelligence

**Competitive Quadrant Analysis:**
- 🟢 **Market Leaders**: High revenue + Strong financial health (Apple)
- 🔵 **Growth Gems**: Excellent efficiency, scaling opportunity (NVIDIA, Meta)
- 🔴 **Risky Giants**: High revenue but concerning metrics (Amazon)
- 🟡 **Strategic Opportunities**: Mixed positioning for analysis

### 📊 Key Executive Insights

**Top Financial Performers (2024):**
- **NVIDIA**: 8.40 score - AI boom driving exceptional efficiency
- **Meta**: 8.20 score - Operational excellence and profitability focus
- **Apple**: 7.60 score - Balanced revenue scale and financial health

**Strategic Findings:**
- Revenue scale ≠ Financial health (Amazon paradox)
- Companies with high efficiency ratios show sustainable growth patterns
- Investment strategies should balance growth potential with financial stability

### 📁 Dashboard Files

- **Power BI Dashboard**: [`exports/SEC_Financial_Intelligence_Dashboard_v1.pbix`](./exports/SEC_Financial_Intelligence_Dashboard_v1.pbix)
- **DAX Documentation**: [`exports/dax_measures.md`](./exports/dax_measures.md)
- **Screenshots**: [`exports/dashboard_screenshots/`](./exports/dashboard_screenshots/)

### 🔄 Data Integration

**Seamless Pipeline Integration:**
- Python SEC pipeline → CSV export → Power BI refresh
- Quarterly update capability aligned with SEC filing schedules
- Automated financial health recalculation with new data

### 💼 Business Value

**Executive Decision Support:**
- Reduce financial analysis time from hours to minutes
- Data-driven investment and strategic planning insights
- Professional board-ready presentations and reports
- Competitive intelligence for portfolio management

---

## 🔮 Future Enhancements

- [ ] Real-time data streaming with scheduled updates
- [ ] Additional financial ratios and metrics
- [ ] Integration with market data (stock prices, valuation multiples)
- [ ] Predictive modeling for financial forecasting
- [ ] RESTful API for data access
- [ ] Interactive web dashboard with Plotly Dash

## 📝 Data Sources

**Primary**: SEC EDGAR API (https://data.sec.gov)
**Forms Processed**: 10-K (Annual), 10-Q (Quarterly), 8-K (Current)
**Update Frequency**: Real-time (when pipeline is executed)

## ⚖️ Compliance

This project respects SEC.gov's robots.txt and rate limiting guidelines. All data is publicly available through official SEC channels.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📧 Contact

**Project Author**: Justin Rush
**LinkedIn**: [Your LinkedIn Profile]
**Portfolio**: [Your Portfolio Website]

---

*This project demonstrates proficiency in data engineering, financial analysis, database design, and business intelligence - core skills for data analyst and business intelligence roles.*