from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, when
from spark_stream_structure import message_schema

# Initialize SparkSession
spark = SparkSession.builder \
    .appName("SparkStreamManager") \
    .getOrCreate()

spark.sparkContext.setLogLevel("ERROR")

# Kafka configuration
kafka_broker = "kafka:9092"

# Function to read and parse Kafka topic into a DataFrame
def read_and_parse(topic):
    print("Reading and parsing topic: {}".format(topic))
    
    df = spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", kafka_broker) \
        .option("subscribe", topic) \
        .option("startingOffsets", "earliest") \
        .load()
    
    parsed_df = df.selectExpr("CAST(value AS STRING) as json_value") \
        .withColumn("data", from_json(col("json_value"), message_schema)) \
        .select("data.*")
    
    return parsed_df

# Function to process both topics and write them to HDFS
def process_combined_topics(output_path, checkpoint_path):
    print("Starting combined Spark Streaming for topics: 'message'")
    
    # Read and parse both topics
    message_df = read_and_parse("message")

    print("Preparing to write to HDFS...")

    # Write the combined DataFrame to HDFS as Parquet, partitioned by `timestamp`
    query = message_df.writeStream \
        .outputMode("append") \
        .format("parquet") \
        .option("path", output_path) \
        .option("checkpointLocation", checkpoint_path) \
        .partitionBy("chat_id") \
        .start()
    
    print("Streaming started. Checkpoint path: {}".format(checkpoint_path))
    return query
