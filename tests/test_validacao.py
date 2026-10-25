"""
Testes da Fase 2 - Validação de dados
Industrial Quality Monitor
"""

import pandas as pd
import pytest
from pathlib import Path
import sys

# Adiciona a pasta src ao path para conseguir importar o módulo
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from validar_dados import (
    validar_quantidade_inspecionada,
    validar_tipo_defeito_obrigatorio,
    validar_tipo_defeito_vazio,
    validar_quantidade_defeito,
    validar_data,
    validar_valor_defeito,
)


def criar_registro_base(**overrides):
    """Cria um registro válido padrão. Pode sobrescrever campos."""
    registro = {
        "id_ordem": "OP99999",
        "data": "2026-02-15",
        "produto": "A",
        "turno": "diurno",
        "operador": "OP01",
        "quantidade_inspecionada": 100,
        "defeito": "nao",
        "tipo_defeito": "",
        "quantidade_defeito": 0,
    }
    registro.update(overrides)
    return pd.DataFrame([registro])


# ==================== TESTES ====================

def test_quantidade_inspecionada_invalida():
    """Regra 1: quantidade_inspecionada <= 0 deve ser inconsistente"""
    df = criar_registro_base(quantidade_inspecionada=0)
    validos, invalidos = validar_quantidade_inspecionada(df)

    assert len(validos) == 0
    assert len(invalidos) == 1
    assert "quantidade_inspecionada" in invalidos.iloc[0]["motivo"]


def test_defeito_sim_sem_tipo():
    """Regra 2: defeito=sim sem tipo_defeito deve ser inconsistente"""
    df = criar_registro_base(defeito="sim", tipo_defeito="")
    validos, invalidos = validar_tipo_defeito_obrigatorio(df)

    assert len(validos) == 0
    assert len(invalidos) == 1
    assert "tipo_defeito está vazio" in invalidos.iloc[0]["motivo"]


def test_defeito_nao_com_tipo():
    """Regra 3: defeito=nao com tipo_defeito preenchido deve ser inconsistente"""
    df = criar_registro_base(defeito="nao", tipo_defeito="trinca")
    validos, invalidos = validar_tipo_defeito_vazio(df)

    assert len(validos) == 0
    assert len(invalidos) == 1
    assert "tipo_defeito está preenchido" in invalidos.iloc[0]["motivo"]


def test_quantidade_defeito_maior():
    """Regra 4: quantidade_defeito > quantidade_inspecionada"""
    df = criar_registro_base(quantidade_inspecionada=50, quantidade_defeito=80)
    validos, invalidos = validar_quantidade_defeito(df)

    assert len(validos) == 0
    assert len(invalidos) == 1


def test_data_fora_do_intervalo():
    """Regra 5: data fora de 2026-01-01 a 2026-03-31"""
    df = criar_registro_base(data="2025-12-31")
    validos, invalidos = validar_data(df)

    assert len(validos) == 0
    assert len(invalidos) == 1


def test_defeito_valor_invalido():
    """Regra 6: defeito com valor diferente de sim/nao"""
    df = criar_registro_base(defeito="talvez")
    validos, invalidos = validar_valor_defeito(df)

    assert len(validos) == 0
    assert len(invalidos) == 1


def test_registro_totalmente_valido():
    """Um registro correto deve passar em todas as regras"""
    df = criar_registro_base()

    df, _ = validar_quantidade_inspecionada(df)
    df, _ = validar_tipo_defeito_obrigatorio(df)
    df, _ = validar_tipo_defeito_vazio(df)
    df, _ = validar_quantidade_defeito(df)
    df, _ = validar_data(df)
    df, _ = validar_valor_defeito(df)

    assert len(df) == 1