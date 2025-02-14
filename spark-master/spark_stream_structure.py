from pyspark.sql.types import StructType, StructField, StringType, LongType, DoubleType

# Define schema for full message JSON data
message_schema = StructType([
    StructField("id", StringType(), True),
    StructField("message", StringType(), True),
    StructField("created_At", StringType(), True),
    StructField("user_id", StringType(), True),
    StructField("type", StringType(), True),
    StructField("chat_id", StringType(), True)
])

# Define schema for chatid and user topic data
chat_user_schema = StructType([
    StructField("chat_id", StringType(), True),
    StructField("user_id", StringType(), True)
])
