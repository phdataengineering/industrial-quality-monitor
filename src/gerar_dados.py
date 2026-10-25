"""
Industrial Quality Monitor - Fase 1
Gera dados sintéticos de inspeções de qualidade industrial.

Regras de calibração (documentadas):
- Volume: 1000 registros
- Taxa global de defeito: ~10%
- Taxa por turno: diurno 6% | tarde 10% | noturno 16%
- Seed fixa: 42 (reprodutibilidade obrigatória)
"""

import csv
import random
from datetime import datetime, timedelta
from pathlib import Path

# ==================== CONFIGURAÇÃO ====================
SEED = 42
TOTAL_REGISTROS = 1000
OUTPUT_PATH = Path(__file__).parent.parent / "data" / "raw" / "inspecoes.csv"

PRODUTOS = ["A", "B", "C", "D"]
TURNOS = ["diurno", "tarde", "noturno"]
OPERADORES = [f"OP{str(i).zfill(2)}" for i in range(1, 9)]  # OP01 a OP08

# Probabilidade de defeito por turno (sinal intencional para ML)
TAXA_DEFEITO_TURNO = {
    "diurno": 0.06,
    "tarde": 0.10,
    "noturno": 0.16,
}

TIPOS_DEFEITO = [
    ("trinca", 0.30),
    ("dimensional", 0.25),
    ("superficie", 0.20),
    ("montagem", 0.15),
    ("eletrico", 0.10),
]

DATA_INICIO = datetime(2026, 1, 1)
DATA_FIM = datetime(2026, 3, 31)


def escolher_tipo_defeito() -> str:
    """Seleciona tipo de defeito de acordo com a distribuição definida."""
    tipos, pesos = zip(*TIPOS_DEFEITO)
    return random.choices(tipos, weights=pesos, k=1)[0]


def gerar_data_aleatoria() -> str:
    """Gera data ISO entre DATA_INICIO e DATA_FIM."""
    delta = DATA_FIM - DATA_INICIO
    dias = random.randint(0, delta.days)
    return (DATA_INICIO + timedelta(days=dias)).strftime("%Y-%m-%d")


def gerar_registro(id_ordem: int) -> dict:
    """Gera um único registro de inspeção."""
    turno = random.choice(TURNOS)
    tem_defeito = random.random() < TAXA_DEFEITO_TURNO[turno]

    quantidade_inspecionada = random.randint(20, 200)

    if tem_defeito:
        tipo_defeito = escolher_tipo_defeito()
        # Quantidade de defeito: 1 até 10% do lote
        max_defeito = max(1, int(quantidade_inspecionada * 0.10))
        quantidade_defeito = random.randint(1, max_defeito)
        defeito = "sim"
    else:
        tipo_defeito = ""
        quantidade_defeito = 0
        defeito = "nao"

    return {
        "id_ordem": f"OP{str(id_ordem).zfill(5)}",
        "data": gerar_data_aleatoria(),
        "produto": random.choice(PRODUTOS),
        "turno": turno,
        "operador": random.choice(OPERADORES),
        "quantidade_inspecionada": quantidade_inspecionada,
        "defeito": defeito,
        "tipo_defeito": tipo_defeito,
        "quantidade_defeito": quantidade_defeito,
    }


def gerar_dataset() -> list[dict]:
    """Gera a lista completa de registros com seed fixa."""
    random.seed(SEED)
    return [gerar_registro(i) for i in range(1, TOTAL_REGISTROS + 1)]


def salvar_csv(registros: list[dict], caminho: Path) -> None:
    """Salva os registros em CSV."""
    caminho.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "id_ordem",
        "data",
        "produto",
        "turno",
        "operador",
        "quantidade_inspecionada",
        "defeito",
        "tipo_defeito",
        "quantidade_defeito",
    ]

    with open(caminho, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(registros)


def imprimir_resumo(registros: list[dict]) -> None:
    """Imprime estatísticas básicas para validação rápida."""
    total = len(registros)
    com_defeito = sum(1 for r in registros if r["defeito"] == "sim")
    taxa_global = com_defeito / total * 100

    print(f"\n{'='*50}")
    print(f"Dataset gerado com sucesso")
    print(f"{'='*50}")
    print(f"Total de registros     : {total}")
    print(f"Registros com defeito  : {com_defeito} ({taxa_global:.1f}%)")
    print(f"Seed utilizada         : {SEED}")
    print(f"Arquivo salvo em       : {OUTPUT_PATH}")
    print(f"\nTaxa de defeito por turno:")

    for turno in TURNOS:
        total_turno = sum(1 for r in registros if r["turno"] == turno)
        defeitos_turno = sum(
            1 for r in registros if r["turno"] == turno and r["defeito"] == "sim"
        )
        taxa = defeitos_turno / total_turno * 100 if total_turno > 0 else 0
        print(f"  - {turno:<8}: {taxa:.1f}%  ({defeitos_turno}/{total_turno})")

    print(f"{'='*50}\n")


def main() -> None:
    print("Gerando dados sintéticos de inspeções de qualidade...")
    registros = gerar_dataset()
    salvar_csv(registros, OUTPUT_PATH)
    imprimir_resumo(registros)


if __name__ == "__main__":
    main()
