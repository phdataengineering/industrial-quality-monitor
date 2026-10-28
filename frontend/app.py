"""Interface Streamlit para a API do Industrial Quality Monitor."""
from __future__ import annotations

import os
from urllib.parse import urlsplit

import requests
import streamlit as st

st.set_page_config(
    page_title="Industrial Quality Monitor",
    page_icon="🏭",
    layout="centered",
)

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8001").rstrip("/")
parsed_api_url = urlsplit(API_BASE_URL)
if (
    parsed_api_url.scheme not in {"http", "https"}
    or not parsed_api_url.hostname
    or parsed_api_url.username
    or parsed_api_url.password
    or parsed_api_url.path not in {"", "/"}
):
    st.error("A configuração da API está inválida.")
    st.stop()


def chamar_api(path: str, payload: dict) -> dict:
    """Envia dados somente ao host configurado e limita o tempo de espera."""
    response = requests.post(
        f"{API_BASE_URL}{path}",
        json=payload,
        timeout=(3, 180),
    )
    if response.status_code != 200:
        raise requests.HTTPError(f"A API respondeu com status {response.status_code}.")
    result = response.json()
    if not isinstance(result, dict):
        raise ValueError("A API retornou uma resposta inválida.")
    return result


@st.cache_data(ttl=15, show_spinner=False)
def api_ready() -> bool:
    try:
        response = requests.get(f"{API_BASE_URL}/ready", timeout=(2, 3))
        return response.status_code == 200
    except requests.RequestException:
        return False


st.title("🏭 Industrial Quality Monitor")
st.caption("Demonstração educacional com dados sintéticos. Não use a previsão para decisões industriais reais.")
if api_ready():
    st.success("API pronta para receber consultas.")
else:
    st.warning("API indisponível ou modelo ainda não carregado. Verifique o serviço e tente novamente.")

tab_prediction, tab_rag = st.tabs(["Simulador de defeitos", "Consulta aos procedimentos"])

with tab_prediction:
    st.subheader("Simulador de inspeção")
    st.write("Informe os dados do lote. As opções correspondem às categorias usadas no treinamento do modelo.")
    with st.form("prediction_form"):
        turno = st.selectbox("Turno", ["diurno", "tarde", "noturno"])
        produto = st.selectbox("Produto", ["A", "B", "C", "D"])
        operador = st.selectbox("Operador", [f"OP{i:02d}" for i in range(1, 9)])
        quantidade = st.number_input(
            "Quantidade inspecionada",
            min_value=1,
            max_value=1_000_000,
            value=100,
            step=1,
        )
        predict_clicked = st.form_submit_button("Prever defeito", type="primary")

    if predict_clicked:
        st.session_state.pop("prediction_result", None)
        try:
            with st.spinner("Consultando o modelo..."):
                result = chamar_api("/predict", {
                    "turno": turno,
                    "produto": produto,
                    "operador": operador,
                    "quantidade_inspecionada": int(quantidade),
                })
            st.session_state["prediction_result"] = result
        except requests.Timeout:
            st.error("A API demorou mais que o limite para responder. Tente novamente.")
        except requests.RequestException as error:
            st.error(str(error) if isinstance(error, requests.HTTPError) else "Não foi possível conectar à API.")
        except ValueError:
            st.error("A API retornou uma resposta inválida.")

    prediction_result = st.session_state.get("prediction_result")
    if prediction_result:
        probability = float(prediction_result["probabilidade_defeito"])
        if prediction_result["previsao_defeito"]:
            st.error("Defeito previsto para esta inspeção.")
        else:
            st.success("Nenhum defeito previsto para esta inspeção.")
        st.metric("Probabilidade estimada de defeito", f"{probability:.1%}")
        st.progress(max(0.0, min(1.0, probability)))
        st.caption("Resultado do modelo demonstrativo; não representa uma avaliação de qualidade real.")

with tab_rag:
    st.subheader("Assistente de procedimentos")
    st.write("Faça uma pergunta sobre os procedimentos técnicos disponíveis no projeto.")
    with st.form("rag_form"):
        question = st.text_area(
            "Pergunta",
            placeholder="Ex.: O que fazer se a trinca for maior que 2 mm?",
            max_chars=500,
            height=100,
        )
        ask_clicked = st.form_submit_button("Consultar procedimentos", type="primary")

    if ask_clicked:
        st.session_state.pop("rag_result", None)
        if len(question.strip()) < 2:
            st.warning("Digite uma pergunta com pelo menos 2 caracteres.")
        else:
            try:
                with st.spinner("Consultando os procedimentos..."):
                    result = chamar_api("/rag/ask", {"pergunta": question.strip()})
                st.session_state["rag_result"] = result
            except requests.Timeout:
                st.error("A consulta excedeu o tempo limite. Se esta for a primeira pergunta, tente novamente após a inicialização do modelo.")
            except requests.RequestException as error:
                st.error(str(error) if isinstance(error, requests.HTTPError) else "Não foi possível conectar à API.")
            except ValueError:
                st.error("A API retornou uma resposta inválida.")

    rag_result = st.session_state.get("rag_result")
    if rag_result:
        st.markdown("**Resposta**")
        # st.text escapa conteúdo do modelo e não renderiza HTML/Markdown não confiável.
        st.text(rag_result.get("resposta", ""))
        sources = rag_result.get("fontes", [])
        if sources:
            st.caption("Fontes: " + ", ".join(str(source) for source in sources))
        st.caption("Método: " + str(rag_result.get("metodo_resposta", "desconhecido")))
        score = rag_result.get("score_similaridade")
        if score is not None:
            st.caption(f"Similaridade informada pelo assistente: {float(score):.3f}")

st.divider()
st.subheader("Como o pipeline Spark processa as inspeções")
st.caption(
    "Fluxo ETL opcional para estudo e escalabilidade. O caminho padrão do projeto "
    "continua usando Pandas; o Spark não é necessário para os dados sintéticos atuais."
)
st.graphviz_chart(
    r'''digraph SparkETL {
        graph [rankdir=LR, bgcolor="transparent", pad="0.2", nodesep="0.45", ranksep="0.6"];
        node [shape=box, style="rounded,filled", fontname="sans-serif", fontsize=11, color="#64748b", fillcolor="#f8fafc", fontcolor="#0f172a", margin="0.16,0.10"];
        edge [color="#475569", penwidth=1.5, arrowsize=0.8];
        csv [label="CSV de inspeções\n(data/raw)", fillcolor="#e0f2fe"];
        driver [label="Spark Driver\nSpark SQL + regras\nvalida schema e planeja tarefas", fillcolor="#ede9fe"];
        tasks [label="Execução por partições\nlocal[2] neste projeto\nparalelismo demonstrativo", fillcolor="#fef3c7"];
        valid [label="Inspeções válidas\nParquet\ncolunas do schema preservadas", fillcolor="#dcfce7"];
        invalid [label="Inconsistências\nParquet + motivo da rejeição", fillcolor="#fee2e2"];
        metrics [label="Agregações\npor turno e produto", fillcolor="#dbeafe"];
        csv -> driver -> tasks;
        tasks -> valid;
        tasks -> invalid;
        tasks -> metrics;
    }''',
    width="stretch",
)
with st.expander("Como executar o ETL Spark"):
    st.code(
        "python src/gerar_dados.py\n"
        "docker compose --profile spark run --rm spark-etl",
        language="bash",
    )
    st.write(
        "As saídas ficam em `data/processed/spark/`: dados válidos, "
        "inconsistências e indicadores agregados em Parquet. O perfil Spark "
        "é separado para não aumentar as imagens nem o consumo do Compose padrão."
    )
