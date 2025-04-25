# IS3107 Group Project – Airflow Data Pipeline

This project contains a collection of Airflow DAGs and custom Python scripts to automate the retrieval and processing of real-world datasets such as HDB resale data, MRT station data, school locations, rental prices, stock prices, and unemployment rates.

---

## 🛠️ Setup Instructions

To get started, install the required Python packages using the `requirements.txt` file:

```bash
pip install -r requirements/requirements.txt
```

### What does this do?

The `requirements.txt` file contains all the necessary dependencies used in this project, such as:

- `pandas` – for data manipulation  
- `requests` – for calling APIs  
- `yfinance` – for retrieving stock market data  
- `beautifulsoup4` – for scraping HTML content  
- `apache-airflow` – for running scheduled DAGs  

Installing these ensures that your environment has everything needed to run the Airflow DAGs and associated data processing functions without errors.

---

##  Project Structure

```
project-root/
├── airflow/
│   └── dags/
│       ├── daily_dag.py
│       └── apis/
│           ├── HDB_API.py
│           ├── MRT_API.py
│           └── ...
├── requirements/
│   └── requirements.txt  
└── README.md
```

---
