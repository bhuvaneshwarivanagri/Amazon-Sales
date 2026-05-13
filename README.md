# 🛒 Amazon India Sales Dashboard (2015–2025)

An interactive Streamlit dashboard for exploring 10 years of Amazon India e-commerce transaction data — covering revenue trends, geography, customer behaviour, product performance, and payment analytics.
Data is served directly from a PostgreSQL database, ensuring scalability and avoiding large CSV files in the repo.
---

## 📊 Dataset Overview
Property	Detail
Source	PostgreSQL database (amazon_2015_to_2025 table)
Rows	~1,031,394 transactions
Period	January 2015 – December 2025
Columns	33 features

### Key Columns

| Column | Description |
|---|---|
| `transaction_id` | Unique order identifier |
| `order_date` | Date of purchase |
| `customer_id / product_id` | Customer & product keys |
| `category / subcategory / brand` | Product hierarchy |
| `original_price_inr` | MRP before discount |
| `discount_percent` | Discount applied (%) |
| `final_amount_inr` | Amount paid (₹) |
| `customer_state / customer_city` | Geographic info |
| `customer_tier / customer_spending_tier` | Customer segmentation |
| `customer_age_group` | Age bracket |
| `payment_method` | COD, UPI, Card, etc. |
| `delivery_days / delivery_type` | Fulfilment metrics |
| `is_prime_member / is_prime_eligible` | Prime status flags |
| `is_festival_sale / festival_name` | Sale event tags |
| `customer_rating / product_rating` | Rating scores |
| `return_status` | Order return outcome |

---

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/<your-username>/amazon-sales-dashboard.git
cd amazon-sales-dashboard
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Add the dataset
Configure PostgreSQL connection
Update the connection string in  amazon.py with your database credentials:

python
engine = create_engine("postgresql+psycopg2://username:password@localhost:5432/Amazon_Sales

### 4. Run the app

```bash
streamlit run amazon.py
```

The dashboard opens at **http://localhost:8501** in your browser.

---

## 🖥️ Dashboard Features

### Sidebar Filters (Global)
- **Year range** slider (2015 – 2025)
- **Category** multi-select
- **State** multi-select
- **Payment method** multi-select
- **Prime members only** toggle

### Tab 1 · 📈 Revenue Trends
- Yearly revenue (bar) + order volume (line) dual-axis chart
- Monthly revenue heatmap (year × month)
- Festival Sale vs Regular Sale revenue comparison

### Tab 2 · 🗺️ Geography
- Revenue by state (horizontal bar)
- Customer tier distribution by state (stacked bar)

### Tab 3 · 👤 Customers
- Orders by age group (donut chart)
- Spending tier breakdown (bar)
- Prime vs Non-Prime avg order value over years (line)
- Return status distribution (donut)

### Tab 4 · 🏷️ Products
- Top 10 sub-categories by revenue
- Avg discount % by sub-category
- Product rating distribution (histogram)
- Top 15 brands by revenue

### Tab 5 · 💳 Payments & Delivery
- Payment method share (donut)
- Delivery type distribution (bar)
- Avg delivery days by state (bar)
- Payment method trend over years (multi-line)

### Raw Data Explorer
- Expandable table showing up to 500 filtered rows

---

## 📦 Tech Stack

| Library | Purpose |
|---|---|
| `streamlit` | Web app framework |
| `pandas` | Data wrangling |
| `plotly` | Interactive charts |

---

## 🗂️ Project Structure

```
amazon-sales-dashboard/
│
├── app.py                            # Main Streamlit application
├─── requirements.txt                  # Python dependencies
└── README.md                         # This file
```

---

## 📋 requirements.txt

```
streamlit>=1.35.0
pandas>=2.0.0
plotly>=5.20.0
PostgresSQL
```

---

## 📸 Screenshots

> Add screenshots of your dashboard here after running it locally.

```
screenshots/
├── revenue_trends.png
├── geography.png
├── customers.png
└── products.png
```

---

## 🤝 Contributing

Pull requests are welcome! For major changes, open an issue first to discuss what you'd like to change.

---

## 📄 License

This project is licensed under the **MIT License**.

---

## 🙏 Acknowledgements

- Dataset sourced from Kaggle / public domain
- Built with [Streamlit](https://streamlit.io) and [Plotly](https://plotly.com)
