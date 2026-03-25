from flask import Flask, jsonify
from flask_cors import CORS
import psycopg2

app = Flask(__name__)
CORS(app)

conn = psycopg2.connect(
    host="database.datalake.kmm.app.br",
    port="5430",
    database="datalake",
    user="dl2661",
    password="&mD2I7@DM6tH!@n@"
)

@app.route('/manutencoes')
def manutencoes():
    cur = conn.cursor()
    
    cur.execute("""
    SELECT 
        e."PLACA",
        CASE 
            WHEN UPPER(vtc."DESCRICAO") LIKE 'SR%' THEN 'CARRETA'
            ELSE 'CAVALO'
        END AS "CATEGORIA",
        tm."NOME" AS "SERVICO_REALIZADO",
        TO_CHAR(os."DATA_FECHAMENTO", 'DD/MM/YYYY') AS "DATA_CONCLUSAO",
        os."NUM_ORDEM_SERVICO" AS "OS_FINALIZADA",
        p2."RAZAO_SOCIAL" AS "OFICINA_EXECUTORA",
        TO_CHAR((os."DATA_FECHAMENTO" + INTERVAL '1 year'), 'DD/MM/YYYY') AS "PROXIMO_VENCIMENTO_2027"
    FROM almoxarifado.equipamento e 
    INNER JOIN manutencao.ordem_servico os ON e."EQUIPAMENTO_ID" = os."EQUIPAMENTO_ID" 
    INNER JOIN manutencao.os_tabela_manutencao otm ON os."ORDEM_SERVICO_ID" = otm."ORDEM_SERVICO_ID" 
    INNER JOIN manutencao.tabela_manutencao tm ON tm."TABELA_ID" = otm."TABELA_ID" 
    LEFT JOIN kss.pessoa p2 ON p2."COD_PESSOA" = os."COD_PESSOA_OFICINA"
    INNER JOIN veiculo.veiculo v ON e."PLACA" = v."PLACA" 
    LEFT JOIN veiculo.veiculo_modalidade vm ON vm."PLACA"  = v."PLACA" 
    LEFT JOIN veiculo.veiculo_tipo_carroceria vtc ON vtc."TIPO_CARROCERIA_ID" = v."TIPO_CARROCERIA_ID" 
    WHERE os."DATA_FECHAMENTO" IS NOT NULL
      AND EXTRACT(YEAR FROM os."DATA_FECHAMENTO") = 2026
      AND UPPER(TRIM(vm."MODALIDADE")) = 'FROTA'
      AND (
        UPPER(vtc."DESCRICAO") IN ('CAVALO MECANICO 4X2', 'CAVALO MECANICO 6X2') 
        OR UPPER(vtc."DESCRICAO") LIKE 'SR%'
      )
    ORDER BY os."DATA_FECHAMENTO" DESC, e."PLACA"
    LIMIT 50
    """)

    colunas = [desc[0] for desc in cur.description]
    dados = cur.fetchall()

    resultado = []
    for linha in dados:
        resultado.append(dict(zip(colunas, linha)))

    return jsonify(resultado)

if __name__ == "__main__":
    app.run()