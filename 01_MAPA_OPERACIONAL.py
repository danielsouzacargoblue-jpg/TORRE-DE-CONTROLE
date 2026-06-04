import streamlit as st
import pandas as pd
from datetime import datetime
from zoneinfo import ZoneInfo

st.set_page_config(
    page_title="MAPA OPERACIONAL",
    page_icon="🗺️",
    layout="wide"
)

USUARIO = "monitoramento"
SENHA = "Shopee2026"

if "logado" not in st.session_state:
    st.session_state.logado = False

if not st.session_state.logado:

    st.title("🔐 Login")

    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        if usuario == USUARIO and senha == SENHA:
            st.session_state.logado = True
            st.rerun()
        else:
            st.error("Usuário ou senha inválidos")

    st.stop()

URL_MONITORAMENTO = "https://docs.google.com/spreadsheets/d/12sUgHfdYhBB7X59IfoWNM7zckhH7oqZKxbV62cBPbX8/export?format=csv&gid=262199424"
URL_KM = "https://docs.google.com/spreadsheets/d/1Py0PjWt5ywfY5IaRraFRd2LTHWLXDk-XKF0v7SfgxVA/export?format=csv&gid=0"
URL_RASTER = "https://docs.google.com/spreadsheets/d/1_a0GbZj33z5u-tim_lSr__u1RCczfHgk_N6dX_NMfLY/export?format=csv&gid=0"

st.markdown("""
<style>
.stApp {
    background-color: #010D24;
}

h1, h2, h3, p, span, label {
    color: white !important;
}

.block-container {
    padding-top: 1rem;
}
</style>
""", unsafe_allow_html=True)

st.title("🗺️ MAPA OPERACIONAL")
st.caption("Monitoramento")

agora = datetime.now(ZoneInfo("America/Sao_Paulo"))

st.info(
    f"Última atualização: {agora.strftime('%d/%m/%Y %H:%M:%S')}"
)

def limpar_placa(valor):
    if pd.isna(valor):
        return ""
    return str(valor).upper().strip().replace("-", "")

def primeira_info(a, b):
    if pd.notna(a) and str(a).strip() not in ["", "nan", "None", ""]:
        return a
    return b

def formatar_raster(valor):
    if pd.isna(valor):
        return "SEM SM"

    texto = str(valor).strip()

    if texto == "" or texto.upper() in ["NAN", "NONE", "SEM SM"]:
        return "SEM SM"

    texto = texto.replace(".", "").replace(",", ".")

    try:
        numero = float(texto)
        return f"{numero:.2f}".replace(".", ",")
    except:
        return valor

try:
    df_monitoramento = pd.read_csv(URL_MONITORAMENTO)
    df_km = pd.read_csv(URL_KM)
    df_raster = pd.read_csv(URL_RASTER)

    df_monitoramento.columns = df_monitoramento.columns.astype(str).str.strip().str.upper()
    df_km.columns = df_km.columns.astype(str).str.strip().str.upper()
    df_raster.columns = df_raster.columns.astype(str).str.strip().str.upper()

    status_validos = [
        "ATRASADA",
        "RISCO DE ATRASO",
        "NO PRAZO"
    ]

    df_monitoramento = df_monitoramento[
        df_monitoramento.iloc[:, 14]
        .astype(str)
        .str.upper()
        .str.strip()
        .isin(status_validos)
    ]

    df_base = pd.DataFrame()
    df_base["LH"] = df_monitoramento.iloc[:, 0]
    df_base["STATUS"] = df_monitoramento.iloc[:, 14]
    df_base["CAVALO"] = df_monitoramento.iloc[:, 2]
    df_base["CARRETA"] = df_monitoramento.iloc[:, 3]
    df_base["ETA_DESTINO"] = df_monitoramento.iloc[:, 12]
    df_base["OCORRÊNCIAS"] = df_monitoramento.iloc[:, 16]

    df_base["PLACA_CAVALO_CHAVE"] = df_base["CAVALO"].apply(limpar_placa)
    df_base["PLACA_CARRETA_CHAVE"] = df_base["CARRETA"].apply(limpar_placa)

    df_km["PLACA_CHAVE"] = df_km["PLACA"].apply(limpar_placa)

    col_km = "KM_RESTANTE" if "KM_RESTANTE" in df_km.columns else "KM"
    col_ref = "REFERENCIA" if "REFERENCIA" in df_km.columns else "REFERÊNCIA"

    df_km_base = df_km[["PLACA_CHAVE", col_km, col_ref]].copy()
    df_km_base = df_km_base.rename(columns={
        col_km: "RASTER",
        col_ref: "REFERÊNCIA"
    })

    df_final = df_base.merge(
        df_km_base,
        left_on="PLACA_CAVALO_CHAVE",
        right_on="PLACA_CHAVE",
        how="left"
    ).drop(columns=["PLACA_CHAVE"], errors="ignore")

    df_final = df_final.merge(
        df_km_base,
        left_on="PLACA_CARRETA_CHAVE",
        right_on="PLACA_CHAVE",
        how="left",
        suffixes=("", "_CARRETA")
    )

    df_final["RASTER"] = df_final.apply(
        lambda x: primeira_info(x["RASTER"], x["RASTER_CARRETA"]),
        axis=1
    )

    df_final["REFERÊNCIA"] = df_final.apply(
        lambda x: primeira_info(x["REFERÊNCIA"], x["REFERÊNCIA_CARRETA"]),
        axis=1
    )

    df_raster["PLACA_CHAVE"] = df_raster["PLACA"].apply(limpar_placa)

    col_ignicao = "IGNICAO" if "IGNICAO" in df_raster.columns else "IGNIÇÃO"

    df_ignicao = df_raster[["PLACA_CHAVE", col_ignicao]].copy()
    df_ignicao = df_ignicao.rename(columns={col_ignicao: "IGNIÇÃO"})

    df_final = df_final.merge(
        df_ignicao,
        left_on="PLACA_CAVALO_CHAVE",
        right_on="PLACA_CHAVE",
        how="left"
    ).drop(columns=["PLACA_CHAVE"], errors="ignore")

    df_final = df_final.merge(
        df_ignicao,
        left_on="PLACA_CARRETA_CHAVE",
        right_on="PLACA_CHAVE",
        how="left",
        suffixes=("", "_CARRETA")
    )

    df_final["IGNIÇÃO"] = df_final.apply(
        lambda x: primeira_info(x["IGNIÇÃO"], x["IGNIÇÃO_CARRETA"]),
        axis=1
    )

    df_final = df_final.drop(
        columns=[
            "PLACA_CHAVE",
            "RASTER_CARRETA",
            "REFERÊNCIA_CARRETA",
            "IGNIÇÃO_CARRETA",
            "PLACA_CAVALO_CHAVE",
            "PLACA_CARRETA_CHAVE"
        ],
        errors="ignore"
    )

    df_final = df_final[[
        "LH",
        "STATUS",
        "CAVALO",
        "CARRETA",
        "IGNIÇÃO",
        "RASTER",
        "ETA_DESTINO",
        "OCORRÊNCIAS",
        "REFERÊNCIA"
    ]]

    df_final["IGNIÇÃO"] = df_final["IGNIÇÃO"].fillna("?")
    df_final["RASTER"] = df_final["RASTER"].fillna("SEM SM").apply(formatar_raster)
    df_final["ETA_DESTINO"] = df_final["ETA_DESTINO"].fillna("")
    df_final["OCORRÊNCIAS"] = df_final["OCORRÊNCIAS"].fillna("")
    df_final["REFERÊNCIA"] = df_final["REFERÊNCIA"].fillna("")

    df_final["ETA_ORDEM"] = pd.to_datetime(
        df_final["ETA_DESTINO"],
        dayfirst=True,
        errors="coerce"
    )

    df_final = df_final.sort_values(
        by="ETA_ORDEM",
        ascending=True
    )

    df_final = df_final.drop(columns=["ETA_ORDEM"])

    qtd_atrasada = len(df_final[df_final["STATUS"] == "ATRASADA"])
    qtd_risco = len(df_final[df_final["STATUS"] == "RISCO DE ATRASO"])
    qtd_prazo = len(df_final[df_final["STATUS"] == "NO PRAZO"])
    qtd_total = len(df_final)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("ATRASADAS", qtd_atrasada)
    col2.metric("RISCO DE ATRASO", qtd_risco)
    col3.metric("NO PRAZO", qtd_prazo)
    col4.metric("TOTAL", qtd_total)

    st.subheader("STATUS DAS VIAGENS")

    grafico_status = pd.DataFrame({
        "STATUS": ["ATRASADA", "RISCO DE ATRASO", "NO PRAZO"],
        "TOTAL": [qtd_atrasada, qtd_risco, qtd_prazo]
    })

    st.bar_chart(
        grafico_status,
        x="STATUS",
        y="TOTAL",
        use_container_width=True
    )

    st.subheader("MONITORAMENTO OPERACIONAL")

    def colorir_status_e_ignicao(valor):
        if valor == "ATRASADA":
            return "background-color: #b00000; color: white; font-weight: bold;"

        if valor == "RISCO DE ATRASO":
            return "background-color: #ffd700; color: black; font-weight: bold;"

        if valor == "NO PRAZO":
            return "background-color: #00b050; color: white; font-weight: bold;"

        if valor == "D":
            return "background-color: #b00000; color: white; font-weight: bold;"

        if valor == "L":
            return "background-color: #00b050; color: white; font-weight: bold;"

        return ""

    styled_df = df_final.style.map(
        colorir_status_e_ignicao,
        subset=["STATUS", "IGNIÇÃO"]
    )

    st.dataframe(
        styled_df,
        use_container_width=True,
        height=700
    )

except Exception as erro:
    st.error(f"Erro ao carregar planilhas: {erro}")
