# 🛒 Azure Databricks Retail Lakehouse

[![Azure](https://img.shields.io/badge/azure-%230072C6.svg?style=for-the-badge&logo=microsoftazure&logoColor=white)](https://azure.microsoft.com/)
[![Databricks](https://img.shields.io/badge/Databricks-FF3621?style=for-the-badge&logo=databricks&logoColor=white)](https://databricks.com/)
[![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)](https://www.python.org/)

## 📖 Project Overview

This project demonstrates a production-grade **Medallion Architecture** pipeline built on **Azure Databricks**. It ingests real-time streaming data, enforces data quality using **Delta Live Tables (DLT)**, and aggregates business metrics for downstream BI reporting.

**Goal:** Process raw user-action events into a Gold-level "Daily Action Count" table using the Lakehouse paradigm.

---

## 🏗 Architecture

### Medallion Architecture Layers

* **Bronze Layer (Ingestion):** Uses **Auto Loader (`cloudFiles`)** to incrementally ingest raw JSON data from cloud storage. Handles schema evolution automatically.
* **Silver Layer (Quality):** Cleans data and enforces schema validation using **DLT Expectations**. Rows with missing actions are dropped to ensure data integrity.
* **Gold Layer (Aggregates):** Aggregates daily user actions for executive reporting.

```
📁 Data Flow
│
├─ Bronze (Raw) ──────────┐
│   • JSON Events          │
│   • Auto Loader          │
│   • Schema Evolution     │
│                          ▼
├─ Silver (Cleaned) ──────┐
│   • Data Quality Checks  │
│   • Date Parsing         │
│   • NULL Filtering       │
│                          ▼
└─ Gold (Aggregated) ─────┐
    • Daily Counts         │
    • Business Metrics     │
```

---

## 🛠 Tech Stack

* **Cloud Provider:** Microsoft Azure
* **Platform:** Databricks (Community/Premium Edition)
* **Orchestration:** Delta Live Tables (DLT) Pipelines
* **Storage Format:** Delta Lake
* **Language:** PySpark (Python)
* **Data Source:** Databricks sample dataset

---

## 🚀 Getting Started

### Prerequisites

1. **Azure Databricks Workspace**
   - Sign up for a free [Azure account](https://azure.microsoft.com/free/) (if you don't have one)
   - Create an [Azure Databricks workspace](https://learn.microsoft.com/en-us/azure/databricks/getting-started/)
   - OR use [Databricks Community Edition](https://community.cloud.databricks.com/) (free tier)

2. **Required Access**
   - Workspace User permissions
   - Ability to create Delta Live Tables pipelines
   - Access to compute resources

---

## 📋 Step-by-Step Setup

### Step 1: Clone the Repository

1. Log into your Azure Databricks workspace
2. Navigate to **Workspace** → **Users** → *[Your Username]*
3. Click **Create** → **Git Folder** (or use Repos)
4. Enter repository URL:
   ```
   https://github.com/Tithir-Mahmud-Bakshi/azure-databricks-retail-lakehouse.git
   ```
5. Click **Create**

**Alternative:** Manually create a notebook and copy the code from `elt_pipeline.py`

---

### Step 2: Create a Delta Live Tables Pipeline

> ⚠️ **Important:** This code uses the `dlt` module which **only works in DLT pipelines**, not regular notebooks!

1. **Navigate to Workflows:**
   - In the left sidebar, click **Workflows** → **Delta Live Tables**
   - Click **Create Pipeline**

2. **Configure Pipeline Settings:**

   | Setting | Value | Description |
   |---------|-------|-------------|
   | **Pipeline Name** | `retail-lakehouse-pipeline` | Choose any name you like |
   | **Product Edition** | Core/Pro/Advanced | Choose based on your workspace |
   | **Pipeline Mode** | Triggered | Runs on-demand (recommended for learning) |
   | **Notebook Libraries** | `/Workspace/path/to/elt_pipeline` | Path to your notebook |
   | **Target** | `retail_lakehouse` | Database where tables will be created |
   | **Storage Location** | `/tmp/dlt/retail_lakehouse` | Where Delta files are stored |
   | **Cluster Mode** | Fixed Size | Or use Enhanced Autoscaling |

3. **Cluster Configuration:**
   - **Node Type:** Standard_DS3_v2 (or smallest available)
   - **Workers:** 1-2 workers (minimum for testing)
   - **Autoscaling:** Enable if available

4. **Advanced Settings (Optional):**
   - **Channel:** Current (latest runtime)
   - **Enable Expectations:** Check this box
   - **Development Mode:** Enable for faster iterations during testing

5. **Click "Create"**

---

### Step 3: Run the Pipeline

1. Once the pipeline is created, click **Start**
2. The pipeline will:
   - Create compute cluster (2-5 minutes)
   - Execute Bronze → Silver → Gold transformations
   - Display real-time lineage graph

3. **Monitor Progress:**
   - View the **Data Flow Graph** to see layer dependencies
   - Check **Event Logs** for detailed execution info
   - Review **Data Quality Metrics** for expectation results

4. **Expected Runtime:** 5-10 minutes for first run

---

### Step 4: Verify Results

#### Option A: Query Tables Directly

```python
# In a new notebook, run:
%sql
-- View Bronze raw events
SELECT * FROM retail_lakehouse.bronze_events LIMIT 10;

-- View Silver cleaned events
SELECT * FROM retail_lakehouse.silver_events LIMIT 10;

-- View Gold aggregated metrics
SELECT * FROM retail_lakehouse.gold_daily_action_counts ORDER BY event_date DESC;
```

#### Option B: Use Data Explorer

1. Go to **Data** → **Databases** in the left sidebar
2. Find `retail_lakehouse` database
3. Browse tables: `bronze_events`, `silver_events`, `gold_daily_action_counts`
4. Click on any table to preview data

---

## 💻 Code Highlights

### 1. Auto Loader (Bronze Layer)

Efficiently ingests new files without expensive directory listings:

```python
@dlt.table(comment="Raw streaming data ingested via Auto Loader")
def bronze_events():
    return (
        spark.readStream.format("cloudFiles")
        .option("cloudFiles.format", "json")
        .option("cloudFiles.inferColumnTypes", "true")
        .load(SOURCE_PATH)
    )
```

**Benefits:**
- Automatic schema inference
- Incremental processing (only new files)
- Built-in checkpoint management

---

### 2. Data Quality Expectations (Silver Layer)

Enforce data integrity with declarative quality rules:

```python
@dlt.expect_or_drop("valid_action", "action IS NOT NULL")
def silver_events():
    return (
        dlt.read("bronze_events")
        .select(
            col("time").cast("timestamp").alias("event_time"),
            col("action"),
            to_date(col("time").cast("timestamp")).alias("event_date")
        )
    )
```

**Quality Metrics Available:**
- Records passing expectations
- Records dropped for violations
- Expectation success rate

---

### 3. Business Aggregations (Gold Layer)

Create analytics-ready datasets:

```python
@dlt.table(comment="Daily summary of user actions")
def gold_daily_action_counts():
    return (
        dlt.read("silver_events")
        .groupBy("event_date", "action")
        .agg(count("*").alias("action_count"))
        .orderBy(desc("event_date"))
    )
```

---

## 🔧 Troubleshooting

### Error: "ModuleNotFoundError: No module named 'dlt'"

**Cause:** You're trying to run the code in a standard notebook instead of a DLT pipeline.

**Solution:** Follow Step 2 above to create a proper DLT pipeline.

---

### Error: "Path does not exist: /databricks-datasets/..."

**Cause:** Sample dataset not available in your workspace.

**Solution:** The path `/databricks-datasets/structured-streaming/events/` should exist in all Databricks workspaces. If not:
1. Contact your workspace admin
2. Or replace `SOURCE_PATH` with your own data location

---

### Pipeline Stuck on "Starting Cluster"

**Cause:** Cluster provisioning can take 3-5 minutes.

**Solution:** Wait patiently. Check the **Cluster Events** tab for progress.

---

### Error: "PERMISSION_DENIED: Cannot create table"

**Cause:** Insufficient permissions on the target catalog/schema.

**Solution:**
1. Ensure you have `CREATE TABLE` permissions
2. Try changing `Target` to a schema you own
3. Or use: `hive_metastore.default` as target

---

## 📊 Sample Output

After successful execution, your Gold table will contain data like:

| event_date | action | action_count |
|------------|--------|--------------|
| 2016-07-26 | Open   | 1,245        |
| 2016-07-26 | Close  | 892          |
| 2016-07-25 | Open   | 1,189        |
| 2016-07-25 | Close  | 856          |

---

## 🎯 Learning Outcomes

By completing this project, you'll learn:

- ✅ How to implement Medallion Architecture in Databricks
- ✅ Using Auto Loader for efficient incremental ingestion
- ✅ Applying data quality checks with DLT Expectations
- ✅ Creating streaming and batch transformations
- ✅ Building production-ready data pipelines
- ✅ Working with Delta Lake format

---

## 🔄 Next Steps

1. **Extend the Pipeline:**
   - Add more data quality rules
   - Create additional Gold tables (e.g., weekly aggregates)
   - Implement SCD Type 2 logic in Silver

2. **Connect BI Tools:**
   - Connect Power BI or Tableau to Gold tables
   - Build dashboards on aggregated data

3. **Add CI/CD:**
   - Use Databricks Asset Bundles for deployment
   - Implement automated testing

4. **Explore Advanced Features:**
   - Change Data Capture (CDC)
   - Slowly Changing Dimensions (SCD)
   - Real-time materialized views

---

## 📚 Additional Resources

- [Delta Live Tables Documentation](https://docs.databricks.com/delta-live-tables/index.html)
- [Medallion Architecture Guide](https://www.databricks.com/glossary/medallion-architecture)
- [Auto Loader Best Practices](https://docs.databricks.com/ingestion/auto-loader/index.html)
- [Data Quality with Expectations](https://docs.databricks.com/delta-live-tables/expectations.html)

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

## 📧 Questions?

If you encounter issues:
1. Check the **Troubleshooting** section above
2. Review Databricks logs in the pipeline UI
3. Open an issue in this repository

---

## 📄 License

This project is open source and available under the MIT License.

---

**Happy Data Engineering! 🚀**
