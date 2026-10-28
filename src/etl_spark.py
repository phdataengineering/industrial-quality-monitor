"""Optional Apache Spark ETL for the synthetic inspection dataset.

The curated output keeps the original inspection columns and types so it can
be compared with the Pandas pipeline without changing the SQL contract.
"""
from __future__ import annotations

import os
from pathlib import Path

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import (
    DateType,
    IntegerType,
    StringType,
    StructField,
    StructType,
)

BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_PATH = Path(os.getenv("SPARK_INPUT_PATH", BASE_DIR / "data/raw/inspecoes.csv"))
OUTPUT_DIR = Path(os.getenv("SPARK_OUTPUT_DIR", BASE_DIR / "data/processed/spark"))
DATA_MIN = "2026-01-01"
DATA_MAX = "2026-03-31"

INSPECTION_SCHEMA = StructType([
    StructField("id_ordem", StringType(), nullable=False),
    StructField("data", DateType(), nullable=False),
    StructField("produto", StringType(), nullable=False),
    StructField("turno", StringType(), nullable=False),
    StructField("operador", StringType(), nullable=False),
    StructField("quantidade_inspecionada", IntegerType(), nullable=False),
    StructField("defeito", StringType(), nullable=False),
    StructField("tipo_defeito", StringType(), nullable=True),
    StructField("quantidade_defeito", IntegerType(), nullable=False),
])
INSPECTION_COLUMNS = [field.name for field in INSPECTION_SCHEMA.fields]


def validar_inspecoes(df: DataFrame) -> tuple[DataFrame, DataFrame]:
    """Apply deterministic checks in sequence, preserving first-failure reason."""
    validos = df
    rejeitados: list[DataFrame] = []

    tipo_preenchido = F.length(F.trim(F.coalesce(F.col("tipo_defeito"), F.lit("")))) > 0
    rules = [
        (
            F.col("quantidade_inspecionada") > 0,
            "quantidade_inspecionada deve ser maior que 0",
        ),
        (
            ~((F.col("defeito") == "sim") & ~tipo_preenchido),
            "defeito='sim' mas tipo_defeito está vazio",
        ),
        (
            ~((F.col("defeito") == "nao") & tipo_preenchido),
            "defeito='nao' mas tipo_defeito está preenchido",
        ),
        (
            F.col("quantidade_defeito") <= F.col("quantidade_inspecionada"),
            "quantidade_defeito maior que quantidade_inspecionada",
        ),
        (
            F.col("data").between(F.to_date(F.lit(DATA_MIN)), F.to_date(F.lit(DATA_MAX))),
            f"data fora do intervalo {DATA_MIN} a {DATA_MAX}",
        ),
        (
            F.col("defeito").isin("sim", "nao"),
            "defeito deve ser 'sim' ou 'nao'",
        ),
    ]

    for condition, reason in rules:
        condition = F.coalesce(condition, F.lit(False))
        rejected = validos.filter(~condition).withColumn("motivo", F.lit(reason))
        rejeitados.append(rejected)
        validos = validos.filter(condition)

    invalidos = rejeitados[0]
    for rejected in rejeitados[1:]:
        invalidos = invalidos.unionByName(rejected)
    return validos.select(*INSPECTION_COLUMNS), invalidos


def executar_etl(input_path: Path = INPUT_PATH, output_dir: Path = OUTPUT_DIR) -> dict[str, int]:
    if not input_path.is_file():
        raise FileNotFoundError(f"Arquivo de entrada não encontrado: {input_path}")

    spark = (
        SparkSession.builder
        .appName("industrial-quality-monitor-etl")
        .master("local[2]")
        .config("spark.ui.enabled", "false")
        .config("spark.sql.shuffle.partitions", "2")
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("WARN")
    try:
        source = (
            spark.read.option("header", True)
            .option("mode", "PERMISSIVE")
            .schema(INSPECTION_SCHEMA)
            .csv(str(input_path))
        )
        validos, invalidos = validar_inspecoes(source)
        total = source.count()
        valid_count = validos.count()
        invalid_count = invalidos.count()

        output_dir.mkdir(parents=True, exist_ok=True)
        validos.write.mode("overwrite").parquet(str(output_dir / "dados_validos"))
        invalidos.write.mode("overwrite").parquet(str(output_dir / "inconsistencias"))
        validos.groupBy("turno", "produto").agg(
            F.count("*").alias("total_inspecoes"),
            F.sum(F.when(F.col("defeito") == "sim", 1).otherwise(0)).alias("inspecoes_com_defeito"),
            F.avg(F.when(F.col("defeito") == "sim", 1.0).otherwise(0.0)).alias("taxa_defeito"),
        ).write.mode("overwrite").parquet(str(output_dir / "indicadores_turno_produto"))

        return {"total": total, "validos": valid_count, "inconsistencias": invalid_count}
    finally:
        spark.stop()


if __name__ == "__main__":
    resumo = executar_etl()
    print(
        "ETL Spark concluído: "
        f"{resumo['total']} registros, {resumo['validos']} válidos, "
        f"{resumo['inconsistencias']} inconsistências."
    )
