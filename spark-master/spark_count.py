# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
from pyspark.sql import SparkSession

# Initialiser SparkSession
spark = SparkSession.builder \
    .appName("CountRowsInParquet") \
    .getOrCreate()

# Chemin du fichier Parquet
parquet_path = "hdfs://namenode:9000/data/send_message_parquet"

# Lire les fichiers Parquet
df = spark.read.parquet(parquet_path)
df.show()

# Compter le nombre de lignes
row_count = df.count()

# Afficher le résultat (sans caractère spécial)
print("Nombre total de lignes dans le fichier Parquet : {}".format(row_count))

# Arrêter la session Spark
spark.stop()
