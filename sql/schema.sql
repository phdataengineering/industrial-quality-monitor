-- Cria a tabela de inspeções
CREATE TABLE IF NOT EXISTS inspecoes (
    id_ordem VARCHAR(10) PRIMARY KEY,
    data DATE NOT NULL,
    produto VARCHAR(1) NOT NULL,
    turno VARCHAR(10) NOT NULL,
    operador VARCHAR(5) NOT NULL,
    quantidade_inspecionada INTEGER NOT NULL,
    defeito VARCHAR(3) NOT NULL CHECK (defeito IN ('sim', 'nao')),
    tipo_defeito VARCHAR(50),
    quantidade_defeito INTEGER NOT NULL
);

-- Cria os índices para otimizar as consultas analíticas
CREATE INDEX IF NOT EXISTS idx_inspecoes_turno ON inspecoes(turno);
CREATE INDEX IF NOT EXISTS idx_inspecoes_produto ON inspecoes(produto);
CREATE INDEX IF NOT EXISTS idx_inspecoes_data ON inspecoes(data);
