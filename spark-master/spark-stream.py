import time
from spark_stream_message import process_combined_topics
from spark_stream_get_all_message import process_get_all_messages

# Process both topics (`message` and `ia`) and write to the same HDFS path
combined_query = process_combined_topics(
    # topic="message",
    output_path="hdfs://namenode:9000/data/send_message_parquet",
    checkpoint_path="hdfs://namenode:9000/checkpoints/combined_checkpoint"
)

# Wait for 30 seconds before starting `get_all_messages_query`
print("Waiting 10 seconds before starting the second query...")
time.sleep(10)

# Process `post_messages` topic using the new schema
get_all_messages_query = process_get_all_messages(
    read_topic="post_messages",
    output_topic="get_messages",
    path="hdfs://namenode:9000/data/send_message_parquet",
    checkpoint_path="hdfs://namenode:9000/checkpoints/get_data_checkpoint"
)

# Await termination of all streams
combined_query.awaitTermination()
get_all_messages_query.awaitTermination()