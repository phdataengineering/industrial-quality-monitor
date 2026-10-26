-- 1. Taxa de defeito por turno
SELECT 
    turno,
    COUNT(*) AS total_inspecoes,
    SUM(CASE WHEN defeito = 'sim' THEN 1 ELSE 0 END) AS total_defeitos,
    ROUND((SUM(CASE WHEN defeito = 'sim' THEN 1.0 ELSE 0.0 END) / COUNT(*)) * 100, 2) AS taxa_defeito_percentual
FROM inspecoes
GROUP BY turno
ORDER BY taxa_defeito_percentual DESC;

-- 2. Taxa de defeito por produto
SELECT 
    produto,
    COUNT(*) AS total_inspecoes,
    SUM(CASE WHEN defeito = 'sim' THEN 1 ELSE 0 END) AS total_defeitos,
    ROUND((SUM(CASE WHEN defeito = 'sim' THEN 1.0 ELSE 0.0 END) / COUNT(*)) * 100, 2) AS taxa_defeito_percentual
FROM inspecoes
GROUP BY produto
ORDER BY taxa_defeito_percentual DESC;

-- 3. Evolução temporal (defeitos por mês)
SELECT 
    TO_CHAR(data, 'YYYY-MM') AS mes,
    COUNT(*) AS total_inspecoes,
    SUM(CASE WHEN defeito = 'sim' THEN 1 ELSE 0 END) AS total_defeitos,
    ROUND((SUM(CASE WHEN defeito = 'sim' THEN 1.0 ELSE 0.0 END) / COUNT(*)) * 100, 2) AS taxa_defeito_percentual
FROM inspecoes
GROUP BY mes
ORDER BY mes;
