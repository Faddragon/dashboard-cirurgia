# Para rodar:
# streamlit run dashboard_cirurgias_app_v2.py

import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Dashboard Cirurgias CCP - IAVC", layout="wide")
st.title("📊 Dashboard de Cirurgias - CCP (Janeiro - Abril 2025)")

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

# 🎯 Lista fixa de complicações
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

# Seletor de páginas no menu lateral
pagina = st.sidebar.radio("🗂️ Selecione a página:", [
    "📊 Visão Geral",
    "🦋 Tireoidectomia Total"
])
# =====================================
# ABA 1 - Visão Geral
# =====================================
if pagina == "📊 Visão Geral":
    # (seu conteúdo atual do dashboard vem aqui)
    # tudo o que já está no seu código original
    pass  # substitua esse pass pelo restante do seu código

# =====================================
# ABA 2 - Complicações Tireoidectomia Total
# =====================================
elif pagina == "🦋 Tireoidectomia Total":
    st.header("🦋 Complicações após Tireoidectomia Total")

    # 📌 Disfonia
    st.subheader("🎤 Disfonia (n = 9)")
    dados_disfonia = pd.DataFrame({
        "MV": [199740, 207727, 108751, 203208, 206345, 215084, 205099, 218961, 216728],
        "Laringoscopia Alterada?": ["Sim"] * 9,
        "Melhora?": ["Sim", "Não", "Sim", "Não", "Não", "Não", "Não", "Não", "Não"],
        "Tempo até Melhora (dias)": ["62", None, "46", None, None, None, None, None, None]
    })
    st.dataframe(dados_disfonia)

    # 📌 Hematoma
    st.subheader("🩸 Hematoma (n = 1)")
    st.write("- MV: 210328")

    # 📌 Parestesia / Hipocalcemia / Hipoparatireoidismo
    st.subheader("🧪 Hipoparatireoidismo / Parestesia (n = 2)")
    dados_hipopara = pd.DataFrame({
        "MV": [128177, 215897],
        "Comentário": [
            "Somente parestesia sem alteração de PTH",
            "Somente parestesia sem alteração de PTH"
        ]
    })
    st.dataframe(dados_hipopara)

    # 📌 Seroma
    st.subheader("💧 Seroma (n = 4)")
    mv_seroma = [210319, 207683, 216790, 209340]
    st.write("MV dos casos com seroma:")
    st.write(", ".join(map(str, mv_seroma)))


meses_disponiveis = sorted(df['ANO_MES'].dropna().unique())

meses_selecionados = st.multiselect(
    "🗓️ Selecione os mês(es) para exibição:",
    options=meses_disponiveis,
    default=meses_disponiveis
)

df = df[df['ANO_MES'].isin(meses_selecionados)]

# 📊 Gráficos principais
col1, _ = st.columns(2)

with col1:
    st.subheader("📈 Número de Procedimentos por Mês")
    df_mes = df.groupby("ANO_MES").size().reset_index(name="Quantidade")
    fig_linha = px.line(df_mes, x="ANO_MES", y="Quantidade", markers=True)
    fig_linha.update_traces(line_color='royalblue')
    st.plotly_chart(fig_linha, use_container_width=True)

# 🔽 Gráfico de barras abaixo
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

# ⏱️ Estatísticas de duração por tipo de cirurgia
st.subheader("⏱️ Estatísticas de Duração por Tipo de Cirurgia")
df_estatisticas = df.groupby("CIRURGIA_GRUPO")["DURACAO_HORAS"].agg(["count", "min", "max", "mean", "std"]).reset_index()
df_estatisticas.columns = ["Tipo de Cirurgia", "N", "Mínimo (h)", "Máximo (h)", "Média (h)", "Desvio Padrão (h)"]
st.dataframe(df_estatisticas)

# 🕒 Duração por grupo patológico
st.subheader("🕒 Duração Cirúrgica por Grupo Patológico")
df_tempo = df.groupby("GRUPO_MESTRE")["DURACAO_HORAS"].agg(["min", "max", "mean"]).reset_index().round(2)
df_tempo.columns = ["Grupo Patológico", "Mínimo (h)", "Máximo (h)", "Média (h)"]

fig_duracao = px.bar(
    df_tempo,
    x="Média (h)",
    y="Grupo Patológico",
    orientation="h",
    hover_data=["Mínimo (h)", "Máximo (h)", "Média (h)"],
    color="Grupo Patológico",
    title="Duração Média das Cirurgias por Grupo Patológico"
)

fig_duracao.update_layout(
    xaxis_title="Tempo médio (horas)",
    yaxis_title="Grupo Patológico",
    template="simple_white",
    showlegend=False,
    height=500
)

st.plotly_chart(fig_duracao, use_container_width=True)

# 💉 Anestesia LOCAL
st.subheader("💉 Casos com Anestesia LOCAL")
total_local = len(df[df['ANEST'] == 'LOCAL'])
st.metric(label="Total de casos com anestesia LOCAL", value=total_local)

df['LOCAL_SEM_TRAQUEOSTOMIA'] = (
    (df['ANEST'] == 'LOCAL') & (~df['CIRURGIA_GRUPO'].str.contains("TRAQUEOSTOMIA", case=False, na=False))
)
df['LOCAL_SEM_TRAQUEOSTOMIA'] = df['LOCAL_SEM_TRAQUEOSTOMIA'].map({True: 'SIM', False: 'NÃO'})

st.subheader("🧪 Anestesia LOCAL sem contar as Traqueostomias")
total_sem_traq = (df['LOCAL_SEM_TRAQUEOSTOMIA'] == 'SIM').sum()
st.metric(label="Total LOCAL sem traqueostomia", value=total_sem_traq)

df_local_sem_traq = df[df['LOCAL_SEM_TRAQUEOSTOMIA'] == 'SIM']
subgrupo_counts = df_local_sem_traq['CIRURGIA_GRUPO'].value_counts().reset_index()
subgrupo_counts.columns = ['Subgrupo Cirúrgico', 'Quantidade']

fig_local = px.bar(
    subgrupo_counts,
    x='Quantidade',
    y='Subgrupo Cirúrgico',
    orientation='h',
    text='Quantidade',
    color='Subgrupo Cirúrgico',
    title='Distribuição das Cirurgias com Anestesia LOCAL sem Traqueostomia'
)

fig_local.update_layout(
    xaxis_title='Número de Casos',
    yaxis_title='Subgrupo Cirúrgico',
    template='simple_white',
    height=500,
    showlegend=False
)

st.plotly_chart(fig_local, use_container_width=True)

# 🚨 Complicações selecionadas
if comp_selecionadas:
    st.subheader("🚨 Casos com Complicações Selecionadas")
    colunas_complicacoes = [col for col in df.columns if col.upper() in comp_selecionadas]
    df_comp = df[df[colunas_complicacoes].apply(lambda row: any(row == 'SIM'), axis=1)]
    st.write(f"Total de casos com complicações selecionadas: {len(df_comp)}")
    st.dataframe(df_comp)

# 🕐 Tabela de tempo por subgrupo (LOCAL sem traqueostomia)
df_local_sem_traq = df[df['LOCAL_SEM_TRAQUEOSTOMIA'] == 'SIM']
tabela_tempo_subgrupo = df_local_sem_traq.groupby('CIRURGIA_GRUPO')['DURACAO_HORAS'].agg(['count', 'mean', 'min', 'max']).reset_index()
tabela_tempo_subgrupo.columns = ['Subgrupo Cirúrgico', 'N', 'Média (h)', 'Mínimo (h)', 'Máximo (h)']
tabela_tempo_subgrupo = tabela_tempo_subgrupo.round(2)

st.subheader("🕐 Tempo Cirúrgico por Subgrupo (Anestesia Local sem Traqueostomia)")
st.dataframe(tabela_tempo_subgrupo, use_container_width=True)

# 🔎 Buscar por número MV
st.subheader("🔎 Buscar Paciente por Número MV")
mv_input = st.text_input("Digite o número MV do paciente (exato):")

if mv_input:
    resultado = df[df['MV'].astype(str) == mv_input.strip()]
    if not resultado.empty:
        st.success(f"Encontrado {len(resultado)} registro(s) com MV = {mv_input}")
        st.dataframe(resultado)
    else:
        st.warning("Nenhum paciente encontrado com esse número MV.")

st.markdown("---")
st.caption("")

