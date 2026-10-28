"""Tests for the opt-in Spark ETL (skipped when the Spark extra is absent)."""
from datetime import date

import pytest

pyspark = pytest.importorskip("pyspark")
from pyspark.sql import SparkSession

from src.etl_spark import INSPECTION_SCHEMA, validar_inspecoes


@pytest.fixture(scope="module")
def spark():
    session = (
        SparkSession.builder.master("local[2]")
        .appName("industrial-quality-monitor-tests")
        .config("spark.ui.enabled", "false")
        .config("spark.sql.shuffle.partitions", "2")
        .getOrCreate()
    )
    session.sparkContext.setLogLevel("ERROR")
    yield session
    session.stop()


def inspection(
    order_id: str,
    *,
    inspected: int = 20,
    defect: str = "nao",
    defect_type: str | None = None,
    defect_count: int = 0,
    inspected_date: date = date(2026, 2, 1),
):
    return (
        order_id,
        inspected_date,
        "A",
        "diurno",
        "OP01",
        inspected,
        defect,
        defect_type,
        defect_count,
    )


def test_etl_spark_preserves_schema_and_rejects_invalid_rows(spark):
    source = spark.createDataFrame(
        [
            inspection("ok"),
            inspection("qty", inspected=0),
            inspection("missing-type", defect="sim", defect_type=None, defect_count=1),
            inspection("unexpected-type", defect_type="trinca"),
            inspection("too-many", defect_count=21),
            inspection("out-of-range", inspected_date=date(2025, 12, 31)),
            inspection("bad-label", defect="maybe"),
        ],
        schema=INSPECTION_SCHEMA,
    )

    valid, invalid = validar_inspecoes(source)

    assert valid.count() == 1
    assert valid.schema == INSPECTION_SCHEMA
    assert invalid.count() == 6
    assert "motivo" in invalid.columns
    assert {row.motivo for row in invalid.select("motivo").distinct().collect()} == {
        "quantidade_inspecionada deve ser maior que 0",
        "defeito='sim' mas tipo_defeito está vazio",
        "defeito='nao' mas tipo_defeito está preenchido",
        "quantidade_defeito maior que quantidade_inspecionada",
        "data fora do intervalo 2026-01-01 a 2026-03-31",
        "defeito deve ser 'sim' ou 'nao'",
    }
