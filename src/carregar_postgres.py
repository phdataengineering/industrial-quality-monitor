import os
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
from pathlib import Path

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

def obter_conexao():
    """Cria a engine de conexão com o PostgreSQL usando SQLAlchemy."""
    usuario = os.getenv('DB_USER')
    senha = os.getenv('DB_PASSWORD')
    host = os.getenv('DB_HOST')
    porta = os.getenv('DB_PORT')
    banco = os.getenv('DB_NAME')
    
    # CORREÇÃO: Força o uso do driver psycopg2 explicitamente
    connection_string = f"postgresql+psycopg2://{usuario}:{senha}@{host}:{porta}/{banco}"
    
    # Cria a engine com pool_pre_ping para evitar conexões mortas
    return create_engine(connection_string, pool_pre_ping=True)

def carregar_dados():
    """Lê o CSV validado e insere no banco PostgreSQL."""
    
    # 1. Caminho do arquivo
    caminho_csv = Path("data/processed/dados_validos.csv")
    
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
    # O if_exists='replace' recria a tabela se ela já existir, limpando os dados antigos
    df.to_sql(name='inspecoes', con=engine, if_exists='replace', index=False)
    
    print(f"✅ Sucesso! {len(df)} registros inseridos na tabela 'inspecoes'.")

if __name__ == "__main__":
    carregar_dados()