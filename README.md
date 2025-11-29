# 🛒 Azure Databricks Retail Lakehouse

![Azure](https://img.shields.io/badge/azure-%230072C6.svg?style=for-the-badge&logo=microsoftazure&logoColor=white)
![Databricks](https://img.shields.io/badge/Databricks-FF3621?style=for-the-badge&logo=databricks&logoColor=white)
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)

## 📖 Project Overview
This project demonstrates a production-grade **Medallion Architecture** pipeline built on **Azure Databricks**. It ingests real-time streaming data, enforces data quality using **Delta Live Tables (DLT)**, and aggregates business metrics for downstream BI reporting.

**Goal:** Process raw user-action events into a Gold-level "Daily Action Count" table using the Lakehouse paradigm.

## 🏗 Architecture
* **Bronze Layer (Ingestion):** Uses **Auto Loader (`cloudFiles`)** to incrementally ingest raw JSON data from cloud storage. Handles schema evolution automatically.
* **Silver Layer (Quality):** Cleans data and enforces schema validation using **DLT Expectations**. Rows with missing actions are dropped to ensure data integrity.
* **Gold Layer (Aggregates):** Aggregates daily user actions for executive reporting.

## 🛠 Tech Stack
* **Cloud Provider:** Microsoft Azure
* **Platform:** Databricks (Premium Tier)
* **Orchestration:** Databricks Workflows (Triggered Mode)
* **Governance:** Unity Catalog (3-Level Namespace)
* **Language:** PySpark (Python)

## 💻 Code Highlights

### 1. Auto Loader (Ingestion)
I utilized Databricks Auto Loader to efficiently detect new files without listing the entire directory, a critical optimization for cloud storage cost reduction.
```python
spark.readStream.format("cloudFiles")
    .option("cloudFiles.format", "json")
    .option("cloudFiles.schemaEvolutionMode", "rescue")
    .load(SOURCE_PATH)
