import dlt
from pyspark.sql.functions import col, to_date, count, desc

# -------------------------------------------------------------------------
# PROJECT: Retail Lakehouse Pipeline
# EXAM TOPIC: Ingestion (Auto Loader) -> Quality (Expectations) -> Aggregation
# -------------------------------------------------------------------------

# Path to Databricks Public Sample Data
SOURCE_PATH = "/databricks-datasets/structured-streaming/events/"

# --- BRONZE LAYER ---
# Goal: Ingest raw JSON files efficiently using Auto Loader
@dlt.table(
    comment="Raw streaming data ingested via Auto Loader",
    table_properties={"quality": "bronze"}
)
def bronze_events():
    return (
        spark.readStream.format("cloudFiles") 
        .option("cloudFiles.format", "json") 
        .option("cloudFiles.inferColumnTypes", "true") 
        .load(SOURCE_PATH) 
    )

# --- SILVER LAYER ---
# Goal: Clean data and enforce Data Quality
@dlt.table(
    comment="Cleaned events with parsed dates",
    partition_cols=["event_date"], 
    table_properties={"quality": "silver"}
)
@dlt.expect_or_drop("valid_action", "action IS NOT NULL")
def silver_events():
    return (
        dlt.read("bronze_events")
        .select(
            col("time").cast("timestamp").alias("event_time"),
            col("action"),
            to_date(col("time").cast("timestamp")).alias("event_date"),
            col("_rescued_data") 
        )
    )

# --- GOLD LAYER ---
# Goal: Aggregate for Business Reporting
@dlt.table(
    comment="Daily summary of user actions",
    table_properties={"quality": "gold"}
)
def gold_daily_action_counts():
    return (
        dlt.read("silver_events")
        .groupBy("event_date", "action")
        .agg(count("*").alias("action_count"))
        .orderBy(desc("event_date"))
    )