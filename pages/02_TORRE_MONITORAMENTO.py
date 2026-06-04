import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_autorefresh import st_autorefresh
from datetime import datetime

st.set_page_config(
    page_title="TORRE DE MONITORAMENTO - SHOPEE",
    page_icon="",
    layout="wide"
)

st_autorefresh(interval=60000, key="refresh")

st.markdown("""
<style>
.stApp {
    background-color: #030B1C;
}

h1, h2, h3 {
    color: white;
}

.alert-card {
    padding: 22px;
    border-radius: 16px;
    font-size: 18px;
    font-weight: 800;
    text-align: center;
    margin-top: 10px;
    margin-bottom: 10px;
}

.alert-red {
    background-color: #4a151c;
    border: 1px solid #ef4444;
    color: #ffb4b4;
}

.alert-yellow {
    background-color: #3f3f12;
    border: 1px solid #facc15;
    color: #fff08a;
}

.alert-green {
    background-color: #0f3d2e;
    border: 1px solid #22c55e;
    color: #9fffc2;
}

.alert-orange {
    background-color: #43220c;
    border: 1px solid #fb923c;
    color: #ffd1a3;
}

.alert-blue {
    background-color: #082f49;
    border: 1px solid #38bdf8;
    color: #bae6fd;
}
</style>
""", unsafe_allow_html=True)

# ===============================
# CABEÇALHO
# ===============================

st.markdown("""
<div style="
background: linear-gradient(90deg,#08152B,#0B2447);
padding:25px;
border-radius:18px;
border:1px solid #16345F;
margin-bottom:15px;
">

<h1 style="
color:white;
font-size:42px;
margin:0;
font-weight:800;
">
TORRE DE MONITORAMENTO
</h1>

<p style="
color:#38BDF8;
font-size:20px;
margin-top:8px;
margin-bottom:0;
font-weight:600;
">
• Painel Operacional em Tempo Real
</p>

</div>
""", unsafe_allow_html=True)

st.markdown(f"""
<div style="
background:#08152B;
padding:12px;
border-radius:10px;
border:1px solid #16345F;
color:#38BDF8;
font-weight:600;
margin-bottom:15px;
">
🕒 Última atualização: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
</div>
""", unsafe_allow_html=True)

# ===============================
# BASE PRINCIPAL
# ===============================

url = "https://docs.google.com/spreadsheets/d/12sUgHfdYhBB7X59IfoWNM7zckhH7oqZKxbV62cBPbX8/export?format=csv&gid=262199424"

df = pd.read_csv(url)
df.columns = df.columns.str.strip()

ignicao = df.iloc[:, 9].astype(str).str.strip().str.upper()
status_sm = df.iloc[:, 10].astype(str).str.strip().str.upper()
status_viagem = df.iloc[:, 14].astype(str).str.strip().str.upper()

status_validos = [
    "NO PRAZO",
    "ATRASADA",
    "RISCO DE ATRASO"
]

no_prazo = len(status_viagem[status_viagem == "NO PRAZO"])
atrasada = len(status_viagem[status_viagem == "ATRASADA"])
risco_atraso = len(status_viagem[status_viagem == "RISCO DE ATRASO"])

carros_parados = df[
    (ignicao == "D") &
    (status_viagem.isin(status_validos))
]

qtd_carros_parados = len(carros_parados)

viagens_sem_sm = df[
    (status_sm == "SEM SM") &
    (status_viagem.isin(status_validos))
]

qtd_viagens_sem_sm = len(viagens_sem_sm)

# ===============================
# BASE ROTAS CRÍTICAS
# ===============================

url_rotas = "https://docs.google.com/spreadsheets/d/1uVVVgnD-bBS7OGbJ9XVp5tXwVshU_5jloJS_t2q7rrU/export?format=csv&gid=0"

df_rotas = pd.read_csv(url_rotas)
df_rotas.columns = df_rotas.columns.str.strip()

status_rotas = df_rotas["STATUS"].astype(str).str.strip().str.upper()

resumo_rotas = pd.DataFrame({
    "STATUS": [
        "ATRASADA",
        "RISCO DE ATRASO",
        "NO PRAZO"
    ],
    "QUANTIDADE": [
        (status_rotas == "ATRASADA").sum(),
        (status_rotas == "RISCO DE ATRASO").sum(),
        (status_rotas == "NO PRAZO").sum()
    ]
})

# ===============================
# ALERTAS OPERACIONAIS
# ===============================

st.divider()
st.subheader("🔔 ALERTAS OPERACIONAIS")

alerta1, alerta2, alerta3, alerta4, alerta5 = st.columns(5)

with alerta1:
    st.markdown(f"""
    <div class="alert-card alert-red">
        🚨<br>{atrasada}<br>VIAGENS ATRASADAS
    </div>
    """, unsafe_allow_html=True)

with alerta2:
    st.markdown(f"""
    <div class="alert-card alert-yellow">
        ⚠️<br>{risco_atraso}<br>RISCO DE ATRASO
    </div>
    """, unsafe_allow_html=True)

with alerta3:
    st.markdown(f"""
    <div class="alert-card alert-green">
        ✅<br>{no_prazo}<br>NO PRAZO
    </div>
    """, unsafe_allow_html=True)

with alerta4:
    st.markdown(f"""
    <div class="alert-card alert-blue">
        🛰️<br>{qtd_viagens_sem_sm}<br>VIAGENS SEM SM
    </div>
    """, unsafe_allow_html=True)

with alerta5:
    st.markdown(f"""
    <div class="alert-card alert-orange">
        🛑<br>{qtd_carros_parados}<br>CARROS PARADOS
    </div>
    """, unsafe_allow_html=True)

st.divider()

# ===============================
# GRÁFICOS
# ===============================

col_graf1, col_graf2 = st.columns(2)

with col_graf1:
    st.subheader("📊 ROTAS CRÍTICAS")

    fig_rotas = px.bar(
        resumo_rotas,
        x="STATUS",
        y="QUANTIDADE",
        text="QUANTIDADE",
        title="ROTAS CRÍTICAS"
    )

    fig_rotas.update_traces(textposition="outside")

    fig_rotas.update_layout(
        template="plotly_dark",
        height=450,
        showlegend=False,
        xaxis_title="",
        yaxis_title="Quantidade",
        paper_bgcolor="#08152B",
        plot_bgcolor="#08152B",
        font=dict(color="white")
    )

    st.plotly_chart(
        fig_rotas,
        use_container_width=True,
        config={"displayModeBar": False}
    )

with col_graf2:
    st.subheader("🚨 Status - Viagens Geral")

    status_dashboard = pd.DataFrame({
        "STATUS": [
            "ATRASADA",
            "RISCO DE ATRASO",
            "NO PRAZO"
        ],
        "VOLUME": [
            atrasada,
            risco_atraso,
            no_prazo
        ]
    })

    fig_status = px.bar(
        status_dashboard,
        x="STATUS",
        y="VOLUME",
        text="VOLUME",
        title="STATUS DAS VIAGENS"
    )

    fig_status.update_traces(textposition="outside")

    fig_status.update_layout(
        template="plotly_dark",
        height=450,
        showlegend=False,
        xaxis_title="",
        yaxis_title="Volume",
        paper_bgcolor="#08152B",
        plot_bgcolor="#08152B",
        font=dict(color="white")
    )

    st.plotly_chart(
        fig_status,
        use_container_width=True,
        config={"displayModeBar": False}
    )

st.divider()

# ===============================
# PAINEL SEM SM
# ===============================

st.subheader("🛰️ Painel de viagens SEM SM")

if qtd_viagens_sem_sm > 0:
    painel_sem_sm = viagens_sem_sm.iloc[:, [0, 2, 4, 10, 14]].copy()

    painel_sem_sm.columns = [
        "LT",
        "CAVALO",
        "TELEFONE",
        "SM",
        "STATUS"
    ]

    st.dataframe(
        painel_sem_sm,
        use_container_width=True,
        height=300
    )
else:
    st.success("✅ Nenhuma viagem SEM SM.")

st.divider()

# ===============================
# PAINEL CARROS PARADOS
# ===============================

st.subheader("🛑 Painel de carros parados")

if qtd_carros_parados > 0:
    painel_parados = carros_parados.iloc[:, [0, 2, 4]].copy()

    painel_parados.columns = [
        "LT",
        "CAVALO",
        "TELEFONE"
    ]

    st.dataframe(
        painel_parados,
        use_container_width=True,
        height=300
    )
else:
    st.success("✅ Nenhum carro parado.")

st.divider()

# ===============================
# VIAGENS CRÍTICAS
# ===============================

st.subheader("🚨 VIAGENS CRÍTICAS")

url_criticas = "https://docs.google.com/spreadsheets/d/1uVVVgnD-bBS7OGbJ9XVp5tXwVshU_5jloJS_t2q7rrU/export?format=csv&gid=0"

df_criticas = pd.read_csv(url_criticas)
df_criticas.columns = df_criticas.columns.str.strip()

df_criticas["STATUS"] = df_criticas["STATUS"].astype(str).str.strip().str.upper()

viagens_criticas = df_criticas[
    df_criticas["STATUS"].isin([
        "ATRASADA",
        "RISCO DE ATRASO"
    ])
].copy()

colunas_exibir = [
    "LH",
    "MOTORISTA",
    "CAVALO",
    "CARRETA",
    "CONTATO",
    "ORIGEM",
    "DESTINO",
    "ETA DESTINO",
    "STATUS",
    "REPORT",
    "OCORRÊNCIA",
    "OBSERVAÇÃO"
]

viagens_criticas = viagens_criticas[
    [col for col in colunas_exibir if col in viagens_criticas.columns]
]

st.dataframe(
    viagens_criticas,
    use_container_width=True,
    height=350
)

st.divider()

# ===============================
# BASE COMPLETA
# ===============================

st.subheader("📋 BASE OPERACIONAL COMPLETA")

st.dataframe(
    df,
    use_container_width=True,
    height=350
)

st.success("✅ Sistema operacional iniciado com sucesso!")
