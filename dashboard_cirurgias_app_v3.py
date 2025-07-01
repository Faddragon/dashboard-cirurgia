# Para rodar:
# streamlit run dashboard_cirurgias_app_v3.py

import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Dashboard Cirurgias CCP - IAVC", layout="wide")

# ⬇️ Dados
@st.cache_data
def carregar_dados():
    df = pd.read_excel("cirurgias_cp_1ºtrim_limpos.xlsx")
    df['DATA'] = pd.to_datetime(df['DATA'], errors='coerce')
    df['ANO_MES'] = df['DATA'].dt.to_period('M').astype(str)
    df['CHEFE'] = df['CHEFE'].str.upper().str.strip()
    df['CIRURGIA_GRUPO'] = df['CIRURGIA_GRUPO'].str.upper().str.strip()
    df['GRUPO_MESTRE'] = df['GRUPO_MESTRE'].str.upper().str.strip()
    return df

df = carregar_dados()

# ⬅️ Menu lateral com abas
pagina = st.sidebar.radio("🗂️ Selecione a página:", [
    "📊 Visão Geral",
    "🦋 Tireoidectomia Total"
])

# =====================================
# 📊 VISÃO GERAL
# =====================================
if pagina == "📊 Visão Geral":
    st.title("📊 Dashboard de Cirurgias - CCP (Janeiro - Abril 2025)")

    # 🎯 Lista de complicações (só nesta aba)
    complicacoes_disponiveis = [
        "HEMATOMA",
        "SEROMA EM TIREOIDECTOMIA",
        "HIPOPARATIREOIDISMO EM TIREOIDECTOMIA",
        "DISFONIA EM TIREOIDECTOMIA",
        "INFECÇÃO EM TIREOIDECTOMIA",
        "ÓBITOS GERAIS",
        "FISTULAS",
        "PARALISIA FACIAL EM PAROTIDECTOMIA"
    ]

    # 🎛️ Filtro por mês
    meses_disponiveis = sorted(df['ANO_MES'].dropna().unique())
    meses_selecionados = st.multiselect(
        "🗓️ Selecione os mês(es) para exibição:",
        options=meses_disponiveis,
        default=meses_disponiveis
    )
    df = df[df['ANO_MES'].isin(meses_selecionados)]

    # 📈 Gráfico de procedimentos por mês
    col1, _ = st.columns(2)
    with col1:
        st.subheader("📈 Número de Procedimentos por Mês")
        df_mes = df.groupby("ANO_MES").size().reset_index(name="Quantidade")
        fig_linha = px.line(df_mes, x="ANO_MES", y="Quantidade", markers=True)
        fig_linha.update_traces(line_color='royalblue')
        st.plotly_chart(fig_linha, use_container_width=True)

    # 🏥 Cirurgias por grupo
    st.subheader("🏥 Cirurgias")
    df_grupo = df["CIRURGIA_GRUPO"].value_counts().reset_index()
    df_grupo.columns = ["Tipo de Cirurgia", "Quantidade"]
    fig_grupo = px.bar(df_grupo, x="Quantidade", y="Tipo de Cirurgia", orientation="h", text="Quantidade", color="Tipo de Cirurgia")
    st.plotly_chart(fig_grupo, use_container_width=True)

    # 👨‍⚕️ Cirurgias por chefe
    st.subheader("👨‍⚕️ Cirurgias por Cirurgião Chefe")
    df_chefe = df["CHEFE"].value_counts().reset_index()
    df_chefe.columns = ["Chefe", "Quantidade"]
    fig_chefe = px.bar(df_chefe, x="Quantidade", y="Chefe", orientation="h", text="Quantidade", color="Chefe")
    st.plotly_chart(fig_chefe, use_container_width=True)

    # 🧠 Cirurgias por patologia
    st.subheader("🧠 Cirurgias por Patologia")
    df_mestre = df["GRUPO_MESTRE"].value_counts().reset_index()
    df_mestre.columns = ["Grupo Patológico", "Quantidade"]
    fig_mestre = px.pie(df_mestre, names="Grupo Patológico", values="Quantidade", hole=0.3)
    st.plotly_chart(fig_mestre, use_container_width=True)

    # ⏱️ Duração por tipo de cirurgia
    st.subheader("⏱️ Estatísticas de Duração por Tipo de Cirurgia")
    df_estatisticas = df.groupby("CIRURGIA_GRUPO")["DURACAO_HORAS"].agg(["count", "min", "max", "mean", "std"]).reset_index()
    df_estatisticas.columns = ["Tipo de Cirurgia", "N", "Mínimo (h)", "Máximo (h)", "Média (h)", "Desvio Padrão (h)"]
    st.dataframe(df_estatisticas)

    # 🕒 Duração por grupo mestre
    st.subheader("🕒 Duração Cirúrgica por Grupo Patológico")
    df_tempo = df.groupby("GRUPO_MESTRE")["DURACAO_HORAS"].agg(["min", "max", "mean"]).reset_index().round(2)
    df_tempo.columns = ["Grupo Patológico", "Mínimo (h)", "Máximo (h)", "Média (h)"]
    fig_duracao = px.bar(df_tempo, x="Média (h)", y="Grupo Patológico", orientation="h", hover_data=["Mínimo (h)", "Máximo (h)"], color="Grupo Patológico")
    fig_duracao.update_layout(template="simple_white", showlegend=False, height=500)
    st.plotly_chart(fig_duracao, use_container_width=True)

    # 💉 Anestesia LOCAL por mês
    st.subheader("💉 Casos com Anestesia LOCAL por Mês")
    df_local = df[df['ANEST'] == 'LOCAL']
    df_local_mes = df_local.groupby('ANO_MES').size().reset_index(name='Quantidade')
    fig_local_mes = px.bar(
        df_local_mes,
        x='ANO_MES',
        y='Quantidade',
        text='Quantidade',
        labels={'ANO_MES': 'Mês', 'Quantidade': 'Número de Casos'}
    )
    fig_local_mes.update_layout(
        xaxis={'categoryorder': 'category ascending'},
        template='simple_white',
        height=400
    )
    st.plotly_chart(fig_local_mes, use_container_width=True)

    # 🧪 Anestesia LOCAL sem Traqueostomia por mês
    st.subheader("🧪 Casos com Anestesia LOCAL sem Traqueostomia por Mês")
    df_local_sem_traq = df[
        (df['ANEST'] == 'LOCAL') &
        (~df['CIRURGIA_GRUPO'].str.contains('TRAQUEOSTOMIA', case=False, na=False))
    ]
    df_local_sem_traq_mes = df_local_sem_traq.groupby('ANO_MES').size().reset_index(name='Quantidade')
    fig_sem_traq_mes = px.bar(
        df_local_sem_traq_mes,
        x='ANO_MES',
        y='Quantidade',
        text='Quantidade',
        labels={'ANO_MES': 'Mês', 'Quantidade': 'Número de Casos'}
    )
    fig_local_mes.update_traces(marker_color='crimson')
    fig_local_mes.update_layout(
        xaxis={'categoryorder': 'category ascending'},
        template='simple_white',
        height=400
    )
    st.plotly_chart(fig_local_mes, use_container_width=True)
    )
    st.plotly_chart(fig_sem_traq_mes, use_container_width=True)


    # 🔍 Busca por MV
    st.subheader("🔎 Buscar Paciente por Número MV")
    mv_input = st.text_input("Digite o número MV do paciente (exato):")
    if mv_input:
        resultado = df[df['MV'].astype(str) == mv_input.strip()]
        if not resultado.empty:
            st.success(f"Encontrado {len(resultado)} registro(s) com MV = {mv_input}")
            st.dataframe(resultado)
        else:
            st.warning("Nenhum paciente encontrado com esse número MV.")

# =====================================
# 🦋 TIREOIDECTOMIA TOTAL
# =====================================
elif pagina == "🦋 Tireoidectomia Total":
    st.title("🦋 Complicações após Tireoidectomia Total")

    # 🎤 Disfonia
    st.subheader("🎤 Disfonia (n = 9)")
    dados_disfonia = pd.DataFrame({
        "MV": [199740, 207727, 108751, 203208, 206345, 215084, 205099, 218961, 216728],
        "Melhora?": ["Sim", "Não", "Sim", "Não", "Não", "Não", "Não", "Não", "Não"],
        "Tempo até Melhora (dias)": ["62", None, "46", None, None, None, None, None, None]
    })

    # Função de destaque condicional
    def highlight_sim(val):
        return 'background-color: red; color: white;' if val == "Sim" else ''

    # Aplicar estilo e exibir
    st.dataframe(dados_disfonia.style.applymap(highlight_sim, subset=["Melhora?"]))


    # 🩸 Hematoma
    st.subheader("🩸 Hematoma (n = 1)")
    st.write("- MV: 210328")

    # 🧪 Hipoparatireoidismo / parestesia
    st.subheader("🧪 Hipoparatireoidismo / Parestesia (n = 2)")
    dados_hipopara = pd.DataFrame({
        "MV": [128177, 215897],
        "Comentário": [
            "Somente parestesia sem alteração de PTH",
            "Somente parestesia sem alteração de PTH"
        ]
    })
    st.dataframe(dados_hipopara)

    # 💧 Seroma
    st.subheader("💧 Seroma (n = 4)")
    mv_seroma = [210319, 207683, 216790, 209340]
    st.write("MV dos casos com seroma:")
    st.write(", ".join(map(str, mv_seroma)))
