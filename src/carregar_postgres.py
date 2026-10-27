import os
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL
from dotenv import load_dotenv
from pathlib import Path

# Carrega as variáveis de ambiente do arquivo .env
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

def obter_conexao():
    """Cria a engine de conexão com o PostgreSQL usando SQLAlchemy."""
    usuario = os.getenv('DB_USER')
    senha = os.getenv('DB_PASSWORD')
    host = os.getenv('DB_HOST')
    porta = os.getenv('DB_PORT')
    banco = os.getenv('DB_NAME')
    
    # CORREÇÃO: Força o uso do driver psycopg2 explicitamente
    obrigatorias = {"DB_USER": usuario, "DB_PASSWORD": senha, "DB_HOST": host, "DB_PORT": porta, "DB_NAME": banco}
    ausentes = [chave for chave, valor in obrigatorias.items() if not valor]
    if ausentes:
        raise ValueError(f"Variáveis de conexão ausentes: {', '.join(ausentes)}")
    url = URL.create(
        "postgresql+psycopg2", username=usuario, password=senha,
        host=host, port=int(porta), database=banco,
    )
    return create_engine(url, pool_pre_ping=True)

def carregar_dados():
    """Lê o CSV validado e insere no banco PostgreSQL."""
    
    # 1. Caminho do arquivo
    caminho_csv = BASE_DIR / "data" / "processed" / "dados_validos.csv"
    
    # Verifica se o arquivo existe
    if not caminho_csv.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {caminho_csv}. Rode a Fase 2 primeiro!")
    
    print("Lendo CSV...")
    df = pd.read_csv(caminho_csv)
    
    # Converte a coluna 'data' para o tipo datetime do pandas (o banco espera DATE)
    df['data'] = pd.to_datetime(df['data']).dt.date
    
    print("Conectando ao banco...")
    engine = obter_conexao()
    
    print("Inserindo dados na tabela 'inspecoes'...")
    # Limpa e recarrega em uma única transação, sem dropar constraints nem índices.
    with engine.begin() as connection:
        connection.execute(text("DELETE FROM inspecoes"))
        df.to_sql(name="inspecoes", con=connection, if_exists="append", index=False)
    
    print(f"✅ Sucesso! {len(df)} registros inseridos na tabela 'inspecoes'.")

if __name__ == "__main__":
    carregar_dados()
