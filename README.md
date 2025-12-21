Markdown# 🛒 Azure Databricks Retail Lakehouse

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

```mermaid
graph LR
    A[Raw JSON Events] -->|Auto Loader| B[(Bronze Layer)]
    B -->|DLT Expectation| C[(Silver Layer)]
    C -->|Aggregation| D[(Gold Layer)]
    style B fill:#cd7f32,stroke:#333,stroke-width:2px
    style C fill:#c0c0c0,stroke:#333,stroke-width:2px
    style D fill:#ffd700,stroke:#333,stroke-width:2px
🛠 Tech StackCloud Provider: Microsoft AzurePlatform: Databricks (Premium Tier)Orchestration: Delta Live Tables (DLT) WorkflowsStorage Format: Delta LakeLanguage: PySpark (Python)Data Source: Databricks public sample datasets🚀 Getting StartedPrerequisitesAzure Databricks Workspace (Premium tier required for DLT)Unity Catalog Access (or legacy Hive Metastore)Compute Resources (Ability to create a DLT Pipeline)📋 Step-by-Step SetupStep 1: Clone the RepositoryLog into your Azure Databricks workspace.Navigate to Workspace → Users → [Your Username].Click Create → Git Folder (or Import).Enter repository URL:[https://github.com/Tithir-Mahmud-Bakshi/azure-databricks-retail-lakehouse.git](https://github.com/Tithir-Mahmud-Bakshi/azure-databricks-retail-lakehouse.git)
(Or manually upload the elt_pipeline.py file if Git integration is not configured)Step 2: Create a Delta Live Tables Pipeline⚠️ Important: This code uses the dlt module which only works in DLT pipelines, not regular notebooks!Navigate to Workflows:In the left sidebar, click Workflows → Delta Live TablesClick Create PipelineConfigure Pipeline Settings:SettingValueDescriptionPipeline NameRetail_Lakehouse_DemoChoose any nameProduct EditionAdvancedRequired for Data Quality ExpectationsPipeline ModeTriggeredRuns once as a batch (saves cost)Source Code/Workspace/.../elt_pipeline.pySelect the file you importedDestinationUnity CatalogRecommended for governanceCatalogdb_ws_exam_prep(Or your main catalog)Target Schemaretail_lakehouseThe database to createClick "Create"Step 3: Run the PipelineClick Start.The pipeline will provision a cluster (approx. 3-5 minutes).Watch the graph turn Green for Bronze, Silver, and Gold.Step 4: Verify ResultsOnce the pipeline completes, use the SQL Editor to query the results.Note: Replace <catalog> with your Unity Catalog name (e.g., db_ws_exam_prep or azure_databricks_personal).SQL-- View Bronze raw events
SELECT * FROM <catalog>.retail_lakehouse.bronze_events LIMIT 10;

-- View Silver cleaned events (No NULL actions)
SELECT * FROM <catalog>.retail_lakehouse.silver_events LIMIT 10;

-- View Gold aggregated metrics
SELECT * FROM <catalog>.retail_lakehouse.gold_daily_action_counts 
ORDER BY event_date DESC;
💻 Code Highlights1. Auto Loader (Bronze Layer)Efficiently ingests new files without expensive directory listings:Python@dlt.table(comment="Raw streaming data ingested via Auto Loader")
def bronze_events():
    return (
        spark.readStream.format("cloudFiles")
        .option("cloudFiles.format", "json")
        .option("cloudFiles.inferColumnTypes", "true")
        .load(SOURCE_PATH)
    )
2. Data Quality Expectations (Silver Layer)Enforce data integrity with declarative quality rules (expect_or_drop):Python@dlt.expect_or_drop("valid_action", "action IS NOT NULL")
def silver_events():
    return (
        dlt.read("bronze_events")
        .select(...)
        # ... transformation logic
    )
3. Business Aggregations (Gold Layer)Create analytics-ready datasets for BI tools:Python@dlt.table(comment="Daily summary of user actions")
def gold_daily_action_counts():
    return (
        dlt.read("silver_events")
        .groupBy("event_date", "action")
        .agg(count("*").alias("action_count"))
        .orderBy(desc("event_date"))
    )
🔧 TroubleshootingError: "UC_HIVE_METASTORE_DISABLED_EXCEPTION"Cause: You are querying without specifying the Catalog.Solution: Use the 3-level namespace in your query: SELECT * FROM <catalog>.<schema>.<table> (e.g., db_ws_exam_prep.retail_lakehouse.gold_daily_action_counts).Error: "ModuleNotFoundError: No module named 'dlt'"Cause: You are trying to run elt_pipeline.py as a standard notebook.Solution: This file must be run as a DLT Pipeline (Workflows -> Delta Live Tables).📊 Sample OutputAfter successful execution, your Gold table will contain aggregated daily metrics:event_dateactionaction_count2016-07-28Close58202016-07-28Open48222016-07-27Open590🔄 Next Steps (Optimization)To prepare this pipeline for high-scale production, the next step is implementing Optimization strategies:Partitioning: Partitioning the Silver table by event_date to speed up date-based filtering.Z-Ordering: Applying OPTIMIZE ... ZORDER BY (action) on the Gold table to speed up specific action queries.🤝 ContributingContributions are welcome! Please feel free to submit a Pull Request.Happy Data Engineering! 🚀
