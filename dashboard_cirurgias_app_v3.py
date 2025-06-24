
#Para rodar, 
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

# Layout com colunas
col1, col2 = st.columns(2)

# Gráfico de tendência (linha) para número de procedimentos por mês
with col1:
    st.subheader("📈 Número de Procedimentos por Mês")
    df_mes = df.groupby("ANO_MES").size().reset_index(name="Quantidade")
    fig_linha = px.line(df_mes, x="ANO_MES", y="Quantidade", markers=True)
    fig_linha.update_traces(line_color='royalblue')
    st.plotly_chart(fig_linha, use_container_width=True)

# Número de cirurgias por chefe com múltiplas cores
st.subheader("👨‍⚕️ Cirurgias por Cirurgião Chefe")
df_chefe = df["CHEFE"].value_counts().reset_index()
df_chefe.columns = ["Chefe", "Quantidade"]
fig_chefe = px.bar(df_chefe, x="Quantidade", y="Chefe", orientation="h", text="Quantidade", color="Chefe")
st.plotly_chart(fig_chefe, use_container_width=True)

# Cirurgias por grupo com múltiplas cores
with col2:
    st.subheader("🏥 Cirurgias")
    df_grupo = df["CIRURGIA_GRUPO"].value_counts().reset_index()
    df_grupo.columns = ["Tipo de Cirurgia", "Quantidade"]
    fig_grupo = px.bar(df_grupo, x="Quantidade", y="Tipo de Cirurgia", orientation="h", text="Quantidade", color="Tipo de Cirurgia")
    st.plotly_chart(fig_grupo, use_container_width=True)

# Cirurgias por patologia (grupo mestre)
st.subheader("🧠 Cirurgias por Patologia")
df_mestre = df["GRUPO_MESTRE"].value_counts().reset_index()
df_mestre.columns = ["Grupo Patológico", "Quantidade"]
fig_mestre = px.pie(df_mestre, names="Grupo Patológico", values="Quantidade", hole=0.3)
st.plotly_chart(fig_mestre, use_container_width=True)

# Tabela de duração por tipo de cirurgia com estatísticas
st.subheader("⏱️ Estatísticas de Duração por Tipo de Cirurgia")
df_estatisticas = df.groupby("CIRURGIA_GRUPO")["DURACAO_HORAS"].agg(["count", "min", "max", "mean", "std"]).reset_index()
df_estatisticas.columns = ["Tipo de Cirurgia", "N", "Mínimo (h)", "Máximo (h)", "Média (h)", "Desvio Padrão (h)"]
st.dataframe(df_estatisticas)

# 📊 Tempo cirúrgico por grupo mestre com hover interativo
st.subheader("🕒 Duração Cirúrgica por Grupo Patológico")

# Agrupar estatísticas
df_tempo = df.groupby("GRUPO_MESTRE")["DURACAO_HORAS"].agg(["min", "max", "mean"]).reset_index()
df_tempo = df_tempo.round(2)
df_tempo.columns = ["Grupo Patológico", "Mínimo (h)", "Máximo (h)", "Média (h)"]

# Gráfico de barras com média e hover mostrando tudo
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



st.subheader("💉 Casos com Anestesia LOCAL")

# Total geral
total_local = len(df[df['ANEST'] == 'LOCAL'])
st.metric(label="Total de casos com anestesia LOCAL", value=total_local)

# Criar variável LOCAL_SEM_TRAQUEOSTOMIA
df['LOCAL_SEM_TRAQUEOSTOMIA'] = (
    (df['ANEST'] == 'LOCAL') & (~df['CIRURGIA_GRUPO'].str.contains("TRAQUEOSTOMIA", case=False, na=False))
)
df['LOCAL_SEM_TRAQUEOSTOMIA'] = df['LOCAL_SEM_TRAQUEOSTOMIA'].map({True: 'SIM', False: 'NÃO'})

st.subheader("🧪 Anestesia LOCAL sem Traqueostomia")

# Total de casos com anestesia local sem traqueostomia
total_sem_traq = (df['LOCAL_SEM_TRAQUEOSTOMIA'] == 'SIM').sum()
st.metric(label="Total LOCAL sem traqueostomia", value=total_sem_traq)

# Agrupar por tipo de cirurgia
df_local_sem_traq = df[df['LOCAL_SEM_TRAQUEOSTOMIA'] == 'SIM']
subgrupo_counts = df_local_sem_traq['CIRURGIA_GRUPO'].value_counts().reset_index()
subgrupo_counts.columns = ['Subgrupo Cirúrgico', 'Quantidade']

# Gráfico
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

#✅ 1. Filtrar os casos relevantes

df_local_sem_traq = df[df['LOCAL_SEM_TRAQUEOSTOMIA'] == 'SIM']
tabela_tempo_subgrupo = df_local_sem_traq.groupby('CIRURGIA_GRUPO')['DURACAO_HORAS'].agg(['count', 'mean', 'min', 'max']).reset_index()
tabela_tempo_subgrupo.columns = ['Subgrupo Cirúrgico', 'N', 'Média (h)', 'Mínimo (h)', 'Máximo (h)']
tabela_tempo_subgrupo = tabela_tempo_subgrupo.round(2)
st.subheader("🕐 Tempo Cirúrgico por Subgrupo (Anestesia Local sem Traqueostomia)")
st.dataframe(tabela_tempo_subgrupo, use_container_width=True)



# 🔎 Seção de busca por número MV
st.subheader("🔎 Buscar Paciente por Número MV")

# Campo de entrada do usuário
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
