from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, to_json, struct, collect_list
from spark_stream_structure import chat_user_schema

# Initialize SparkSession
spark = SparkSession.builder \
    .appName("StreamGetAllMessages") \
    .getOrCreate()

spark.sparkContext.setLogLevel("ERROR")

kafka_broker = "kafka:9092"

def process_get_all_messages(read_topic, output_topic, path, checkpoint_path):

    print(f"Initializing Spark Stream for topic: {read_topic}")

    # Read the filter conditions from the topic `post_messages`
    df = spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", kafka_broker) \
        .option("subscribe", read_topic) \
        .option("startingOffsets", "earliest") \
        .load()

    print(f"Stream initialized for topic: {read_topic}. Parsing JSON messages...")

    # Parse JSON from Kafka to extract `chat_id`
    filter_conditions = df.selectExpr("CAST(value AS STRING) as json_value") \
        .withColumn("data", from_json(col("json_value"), chat_user_schema)) \
        .select("data.chat_id").filter(col("chat_id").isNotNull())

    print("Parsed filter conditions. Listening for chat_id...")

    def process_batch(batch_df, batch_id):
        print(f"Processing batch {batch_id}...")
        
        # Collect chat_ids from the incoming batch
        chat_ids = [row.chat_id for row in batch_df.collect()]
        print(f"Received chat_ids: {chat_ids}")
        
        if chat_ids:
            # Read messages from HDFS and filter by chat_id
            hdfs_df = spark.read.parquet(path).filter(col("chat_id").isin(chat_ids))
            
            # Group messages by chat_id and collect them into a list
            grouped_df = hdfs_df.groupBy("chat_id").agg(
                collect_list(struct("id", "message", "created_At", "type")).alias("messages")
            )

            # Convert the grouped DataFrame to JSON format for Kafka output
            result_df = grouped_df.selectExpr(
                "CAST(chat_id AS STRING) as key",  # Use `chat_id` as the Kafka message key
                "to_json(struct(chat_id, messages)) as value"  # Convert the whole group to JSON
            )

            # Write the result back to Kafka
            result_df.write \
                .format("kafka") \
                .option("kafka.bootstrap.servers", kafka_broker) \
                .option("topic", output_topic) \
                .save()

            print(f"Sent grouped messages for chat_ids: {chat_ids} to topic: {output_topic}")

    # Start the stream with foreachBatch for custom processing
    query = filter_conditions.writeStream \
        .outputMode("update") \
        .option("checkpointLocation", checkpoint_path) \
        .foreachBatch(process_batch) \
        .start()

    print(f"Streaming started for topic: {read_topic}. Checkpoint path: {checkpoint_path}")

    return query
