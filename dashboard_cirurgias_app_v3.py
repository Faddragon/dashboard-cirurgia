# Para rodar:
# streamlit run dashboard_cirurgias_app_v3.py

import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Dashboard Cirurgias CCP - IAVC", layout="wide")

@st.cache_data
def carregar_dados():
    df = pd.read_excel("cirurgias_cp_MM.xlsx")
    df['DATA'] = pd.to_datetime(df['DATA'], errors='coerce')
    df['ANO_MES'] = df['DATA'].dt.to_period('M').astype(str)
    df['CHEFE'] = df['CHEFE'].str.upper().str.strip()
    df['CIRURGIA_GRUPO'] = df['CIRURGIA_GRUPO'].str.upper().str.strip()
    df['GRUPO_MESTRE'] = df['GRUPO_MESTRE'].str.upper().str.strip()
    return df

df = carregar_dados()

# Apenas VISÃO GERAL incluída por enquanto (ver anterior para outras abas)
pagina = st.sidebar.radio("🗂️ Selecione a página:", [
    "📊 Visão Geral"
])

if pagina == "📊 Visão Geral":
    st.title("📊 Dashboard de Cirurgias - CCP (Janeiro - Junho 2025)")

    meses_disponiveis = sorted(df['ANO_MES'].dropna().unique())
    meses_selecionados = st.multiselect(
        "🗓️ Selecione os mês(es) para exibição:",
        options=meses_disponiveis,
        default=meses_disponiveis
    )
    df = df[df['ANO_MES'].isin(meses_selecionados)]

    st.subheader("📈 Número de Procedimentos por Mês")
    df_mes = df.groupby("ANO_MES").size().reset_index(name="Quantidade")
    fig_linha = px.line(df_mes, x="ANO_MES", y="Quantidade", markers=True)
    fig_linha.update_traces(line_color='royalblue')
    st.plotly_chart(fig_linha, use_container_width=True)

    st.subheader("🏥 Cirurgias")
    df_grupo = df["CIRURGIA_GRUPO"].value_counts().reset_index()
    df_grupo.columns = ["Tipo de Cirurgia", "Quantidade"]
    fig_grupo = px.bar(
        df_grupo, x="Quantidade", y="Tipo de Cirurgia", orientation="h", text="Quantidade",
        color="Tipo de Cirurgia", height=600
    )
    fig_grupo.update_traces(marker_line_width=1.2, textposition='outside')
    fig_grupo.update_layout(
        template="simple_white", xaxis_title="Número de Cirurgias", font=dict(size=14),
        yaxis=dict(autorange="reversed")
    )
    st.plotly_chart(fig_grupo, use_container_width=True)

    st.subheader("👨‍⚕️ Cirurgias por Cirurgião Chefe")
    df_chefe = df["CHEFE"].value_counts().reset_index()
    df_chefe.columns = ["Chefe", "Quantidade"]
    fig_chefe = px.bar(df_chefe, x="Quantidade", y="Chefe", orientation="h", text="Quantidade", color="Chefe")
    st.plotly_chart(fig_chefe, use_container_width=True)

    st.subheader("🧠 Cirurgias por Patologia")
    df_mestre = df["GRUPO_MESTRE"].value_counts().reset_index()
    df_mestre.columns = ["Grupo Patológico", "Quantidade"]
    fig_mestre = px.pie(df_mestre, names="Grupo Patológico", values="Quantidade", hole=0.3)
    st.plotly_chart(fig_mestre, use_container_width=True)

    st.subheader("⏱️ Estatísticas de Duração por Tipo de Cirurgia")
    df_estatisticas = df.groupby("CIRURGIA_GRUPO")["DURACAO_HORAS"].agg(["count", "min", "max", "mean", "std"]).reset_index()
    df_estatisticas.columns = ["Tipo de Cirurgia", "N", "Mínimo (h)", "Máximo (h)", "Média (h)", "Desvio Padrão (h)"]
    st.dataframe(df_estatisticas)

    st.subheader("🕒 Duração Cirúrgica por Grupo Patológico")
    df_tempo = df.groupby("GRUPO_MESTRE")["DURACAO_HORAS"].agg(["min", "max", "mean"]).reset_index().round(2)
    df_tempo.columns = ["Grupo Patológico", "Mínimo (h)", "Máximo (h)", "Média (h)"]
    fig_duracao = px.bar(df_tempo, x="Média (h)", y="Grupo Patológico", orientation="h",
                         hover_data=["Mínimo (h)", "Máximo (h)"], color="Grupo Patológico")
    fig_duracao.update_layout(template="simple_white", showlegend=False, height=500)
    st.plotly_chart(fig_duracao, use_container_width=True)

    st.subheader("💉 Casos com Anestesia LOCAL por Mês")
    df_local = df[df['ANEST'] == 'LOCAL']
    df_local_mes = df_local.groupby('ANO_MES').size().reset_index(name='Quantidade')
    fig_local_mes = px.bar(df_local_mes, x='ANO_MES', y='Quantidade', text='Quantidade')
    fig_local_mes.update_layout(template='simple_white', height=400)
    st.plotly_chart(fig_local_mes, use_container_width=True)

    st.subheader("🧪 Casos com Anestesia LOCAL sem Traqueostomia")
    df_local_sem_traq = df[(df['ANEST'] == 'LOCAL') & (~df['CIRURGIA_GRUPO'].str.contains('TRAQUEOSTOMIA', case=False, na=False))]
    df_local_sem_traq_mes = df_local_sem_traq.groupby('ANO_MES').size().reset_index(name='Quantidade')
    fig_sem_traq_mes = px.bar(df_local_sem_traq_mes, x='ANO_MES', y='Quantidade', text='Quantidade')
    fig_sem_traq_mes.update_traces(marker_color='seagreen')
    fig_sem_traq_mes.update_layout(template='simple_white', height=400)
    st.plotly_chart(fig_sem_traq_mes, use_container_width=True)

    st.subheader("🔎 Buscar Paciente por Número MV")
    mv_input = st.text_input("Digite o número MV do paciente (exato):")
    if mv_input:
        resultado = df[df['MV'].astype(str) == mv_input.strip()]
        if not resultado.empty:
            st.success(f"Encontrado {len(resultado)} registro(s) com MV = {mv_input}")
            st.dataframe(resultado)
        else:
            st.warning("Nenhum paciente encontrado com esse número MV.")

