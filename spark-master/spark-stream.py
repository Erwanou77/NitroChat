from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, when
from pyspark.sql.types import StructType, StructField, StringType, LongType, DoubleType

# Initialize SparkSession
spark = SparkSession.builder \
    .appName("KafkaToHDFSPartitioned") \
    .getOrCreate()

spark.sparkContext.setLogLevel("ERROR")

# Kafka configuration
kafka_broker = "kafka:9092"

# Define schema for JSON data
schema = StructType([
    StructField("id", StringType(), True),
    StructField("messages", LongType(), True),
    StructField("timestamp", LongType(), True),
    StructField("user", DoubleType(), True),
    StructField("type", StringType(), True)
])

# Function to read, process, and write each topic to HDFS
def process_topic(topic, output_path, checkpoint_path, apply_transformation=False):
    df = spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", kafka_broker) \
        .option("subscribe", topic) \
        .option("startingOffsets", "earliest") \
        .load()

    # Parse JSON from the Kafka message value
    parsed_df = df.selectExpr("CAST(value AS STRING) as json_value") \
        .withColumn("data", from_json(col("json_value"), schema)) \
        .select("data.*")

    # Apply transformation if required (only for ia_output_data)
    if apply_transformation:
        transformed_df = parsed_df.withColumn(
            "messages",
            when(col("id") == "specific_id", col("messages") + 100).otherwise(col("messages"))
        )
    else:
        transformed_df = parsed_df

    # Write the processed data to HDFS as Parquet, partitioned by `timestamp`
    query = transformed_df.writeStream \
        .outputMode("append") \
        .format("parquet") \
        .option("path", output_path) \
        .option("checkpointLocation", checkpoint_path) \
        .partitionBy("timestamp") \
        .trigger(processingTime="30 seconds") \
        .start()

    return query

# Process `send_message` topic (no transformation)
send_message_query = process_topic(
    topic="message",
    output_path="hdfs://namenode:9000/data/send_message_parquet",
    checkpoint_path="hdfs://namenode:9000/checkpoints/send_message_checkpoint",
    apply_transformation=False  # No transformation for this topic
)

# Process `ia_output_data` topic (with transformation)
ia_output_data_query = process_topic(
    topic="ia",
    output_path="hdfs://namenode:9000/data/ia_output_data_parquet",
    checkpoint_path="hdfs://namenode:9000/checkpoints/ia_output_data_checkpoint",
    apply_transformation=True  # Apply transformation for this topic
)

# Await termination of both streams
send_message_query.awaitTermination()
ia_output_data_query.awaitTermination()