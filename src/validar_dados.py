"""
Industrial Quality Monitor - Fase 2
Validação de dados de inspeções de qualidade.
"""

from pathlib import Path
import pandas as pd

# ==================== CAMINHOS ====================
BASE_DIR = Path(__file__).parent.parent
ARQUIVO_ENTRADA = BASE_DIR / "data" / "raw" / "inspecoes.csv"
ARQUIVO_VALIDOS = BASE_DIR / "data" / "processed" / "dados_validos.csv"
ARQUIVO_INCONSISTENCIAS = BASE_DIR / "data" / "processed" / "inconsistencias.csv"

DATA_MIN = "2026-01-01"
DATA_MAX = "2026-03-31"


def carregar_dados(caminho: Path) -> pd.DataFrame:
    if not caminho.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {caminho}")
    df = pd.read_csv(caminho)
    print(f"Dados carregados: {len(df)} registros")
    return df


def validar_quantidade_inspecionada(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    mask = df["quantidade_inspecionada"] > 0
    invalidos = df[~mask].copy()
    if not invalidos.empty:
        invalidos["motivo"] = "quantidade_inspecionada deve ser maior que 0"
    return df[mask].copy(), invalidos


def validar_tipo_defeito_obrigatorio(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    tipo_vazio = df["tipo_defeito"].isna() | (df["tipo_defeito"].astype(str).str.strip() == "")
    mask_invalido = (df["defeito"] == "sim") & tipo_vazio
    invalidos = df[mask_invalido].copy()
    if not invalidos.empty:
        invalidos["motivo"] = "defeito='sim' mas tipo_defeito está vazio"
    return df[~mask_invalido].copy(), invalidos


def validar_tipo_defeito_vazio(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    tipo_preenchido = df["tipo_defeito"].notna() & (df["tipo_defeito"].astype(str).str.strip() != "")
    mask_invalido = (df["defeito"] == "nao") & tipo_preenchido
    invalidos = df[mask_invalido].copy()
    if not invalidos.empty:
        invalidos["motivo"] = "defeito='nao' mas tipo_defeito está preenchido"
    return df[~mask_invalido].copy(), invalidos


def validar_quantidade_defeito(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    mask_invalido = df["quantidade_defeito"] > df["quantidade_inspecionada"]
    invalidos = df[mask_invalido].copy()
    if not invalidos.empty:
        invalidos["motivo"] = "quantidade_defeito maior que quantidade_inspecionada"
    return df[~mask_invalido].copy(), invalidos


def validar_data(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    datas = pd.to_datetime(df["data"], errors="coerce")
    mask_valido = (datas >= DATA_MIN) & (datas <= DATA_MAX)
    invalidos = df[~mask_valido].copy()
    if not invalidos.empty:
        invalidos["motivo"] = f"data fora do intervalo {DATA_MIN} a {DATA_MAX}"
    return df[mask_valido].copy(), invalidos


def validar_valor_defeito(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    mask_valido = df["defeito"].isin(["sim", "nao"])
    invalidos = df[~mask_valido].copy()
    if not invalidos.empty:
        invalidos["motivo"] = "defeito deve ser 'sim' ou 'nao'"
    return df[mask_valido].copy(), invalidos


def salvar_resultados(df_validos: pd.DataFrame, df_inconsistencias: pd.DataFrame) -> None:
    """Salva os dois arquivos de saída."""
    ARQUIVO_VALIDOS.parent.mkdir(parents=True, exist_ok=True)

    df_validos.to_csv(ARQUIVO_VALIDOS, index=False, encoding="utf-8")
    print(f"Arquivo salvo: {ARQUIVO_VALIDOS} ({len(df_validos)} registros)")

    df_inconsistencias.to_csv(ARQUIVO_INCONSISTENCIAS, index=False, encoding="utf-8")
    print(f"Arquivo salvo: {ARQUIVO_INCONSISTENCIAS} ({len(df_inconsistencias)} registros)")


def main():
    print("Iniciando validação de dados...\n")

    df = carregar_dados(ARQUIVO_ENTRADA)
    todas_inconsistencias = []

    df, inc = validar_quantidade_inspecionada(df)
    print(f"Regra 1 - Inconsistentes: {len(inc)}")
    todas_inconsistencias.append(inc)

    df, inc = validar_tipo_defeito_obrigatorio(df)
    print(f"Regra 2 - Inconsistentes: {len(inc)}")
    todas_inconsistencias.append(inc)

    df, inc = validar_tipo_defeito_vazio(df)
    print(f"Regra 3 - Inconsistentes: {len(inc)}")
    todas_inconsistencias.append(inc)

    df, inc = validar_quantidade_defeito(df)
    print(f"Regra 4 - Inconsistentes: {len(inc)}")
    todas_inconsistencias.append(inc)

    df, inc = validar_data(df)
    print(f"Regra 5 - Inconsistentes: {len(inc)}")
    todas_inconsistencias.append(inc)

    df, inc = validar_valor_defeito(df)
    print(f"Regra 6 - Inconsistentes: {len(inc)}")
    todas_inconsistencias.append(inc)

    df_inconsistencias = pd.concat(todas_inconsistencias, ignore_index=True)

    print(f"\n===== RESUMO FINAL =====")
    print(f"Registros válidos:        {len(df)}")
    print(f"Registros inconsistentes: {len(df_inconsistencias)}")

    # Salvar os arquivos
    print()
    salvar_resultados(df, df_inconsistencias)


if __name__ == "__main__":
    main()