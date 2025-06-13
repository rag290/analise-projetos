import streamlit as st
import pandas as pd
import numpy as np
import datetime

st.set_page_config(page_title="Dashboard Rentabilidade", layout="wide")
st.title("📊 Dashboard de Rentabilidade de Projetos")

# 📥 Carregar dados
df = pd.read_excel("rentabilidade.xlsx")
df.columns = df.columns.str.strip()
df = df[df["Mes"].notna()]

# 🗓️ Mapear meses para ordenação
meses_abreviados = {
    'Jan': 1, 'Fev': 2, 'Mar': 3, 'Abr': 4, 'Mai': 5, 'Jun': 6,
    'Jul': 7, 'Ago': 8, 'Set': 9, 'Out': 10, 'Nov': 11, 'Dez': 12
}
df["Mes_Num"] = df["Mes"].map(meses_abreviados)
df = df.sort_values(by="Mes_Num")

# 🎛️ Filtros
col1, col2 = st.columns(2)
anos = sorted(df["Ano"].dropna().unique(), reverse=True)
ano_select = col1.selectbox("Ano", anos)

meses_lista = sorted(df[df["Ano"] == ano_select]["Mes"].unique(), key=lambda m: meses_abreviados[m])
meses_opcoes = ["Tudo"] + meses_lista
meses_selecionados = col2.multiselect("Meses", meses_opcoes, default=["Tudo"])

col3, col4 = st.columns(2)
clientes = sorted(df["Nome Cliente"].dropna().unique())
projetos = sorted(df["Nome Projecto"].dropna().unique())

cliente_select = col3.multiselect("Cliente", ["Tudo"] + clientes, default=["Tudo"])
projeto_select = col4.multiselect("Projeto", ["Tudo"] + projetos, default=["Tudo"])

clientes_filtrados = clientes if "Tudo" in cliente_select else cliente_select
projetos_filtrados = projetos if "Tudo" in projeto_select else projeto_select
meses_filtrados = meses_lista if "Tudo" in meses_selecionados else meses_selecionados

df_base = df[
    (df["Ano"] == ano_select) &
    (df["Mes"].isin(meses_filtrados)) &
    (df["Nome Cliente"].isin(clientes_filtrados)) &
    (df["Nome Projecto"].isin(projetos_filtrados))
].copy()

for col in ["Total Proveitos", "Total Custos"]:
    df_base[col] = pd.to_numeric(df_base[col], errors="coerce").fillna(0)

df_base["Margem (€)"] = df_base["Total Proveitos"] - df_base["Total Custos"]
df_base["Rentabilidade (%)"] = df_base.apply(
    lambda row: (row["Margem (€)"] / row["Total Proveitos"] * 100)
    if row["Total Proveitos"] > 0 else -100 if row["Total Custos"] > 0 else 0,
    axis=1
)

# Indicadores
total_proveitos = df_base["Total Proveitos"].sum()
total_custos = df_base["Total Custos"].sum()
margem_total = total_proveitos - total_custos
rentabilidade_total = (margem_total / total_proveitos * 100) if total_proveitos > 0 else -100 if total_custos > 0 else 0

col1, col2, col3, col4 = st.columns(4)
col1.metric("💰 Total Proveitos", f"R$ {total_proveitos:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
col2.metric("💸 Total Custos", f"R$ {total_custos:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
col3.metric("📐 Margem Acumulada", f"R$ {margem_total:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
col4.metric("📊 Rentabilidade Acumulada", f"{rentabilidade_total:.2f}%")









# 🕗 Sugestão de Alocação de Horas (8h/dia)
# st.markdown("##")  # Corrigido: linha comentada ou remova se não for necessária







# 📋 Tabela de Rentabilidade dos Projetos
st.markdown("### Seção")

df_exibicao = df_base[[
    "Mes", "Nome Cliente", "Nome Projecto", "Total Proveitos", "Total Custos", "Margem (€)", "Rentabilidade (%)"
]].copy().sort_values(by="Rentabilidade (%)", ascending=False)

df_exibicao["Total Proveitos"] = df_exibicao["Total Proveitos"].map(lambda x: f"€ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
df_exibicao["Total Custos"] = df_exibicao["Total Custos"].map(lambda x: f"€ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
df_exibicao["Margem (€)"] = df_exibicao["Margem (€)"].map(lambda x: f"€ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
df_exibicao["Rentabilidade (%)"] = df_exibicao["Rentabilidade (%)"].map(lambda x: f"{x:.2f}%")

st.dataframe(df_exibicao.reset_index(drop=True), use_container_width=True)

st.markdown("### 🕗 Sugestão de Alocação de Horas (8h/dia)")
mes_atual = datetime.datetime.now().strftime("%b")
mes_atual_pt = {'Jan':'Jan', 'Feb':'Fev', 'Mar':'Mar', 'Apr':'Abr', 'May':'Mai', 'Jun':'Jun',
                'Jul':'Jul', 'Aug':'Ago', 'Sep':'Set', 'Oct':'Out', 'Nov':'Nov', 'Dec':'Dez'}[mes_atual]
df_mes_corrente = df[df["Mes"] == mes_atual_pt].copy()

df_mes_corrente["Margem (€)"] = df_mes_corrente["Total Proveitos"] - df_mes_corrente["Total Custos"]
df_mes_corrente["Rentabilidade (%)"] = df_mes_corrente.apply(
    lambda row: (row["Margem (€)"] / row["Total Proveitos"] * 100)
    if row["Total Proveitos"] > 0 else -100 if row["Total Custos"] > 0 else 0,
    axis=1
)
df_mes_corrente = df_mes_corrente[df_mes_corrente["Total Proveitos"] > 0].copy()

# ✴️ Calcular capacidade de absorção
custo_dia = 262
custo_hora = custo_dia / 8
df_mes_corrente["Dias Suportados"] = df_mes_corrente["Margem (€)"] / custo_dia
df_mes_corrente["Dias Suportados"] = df_mes_corrente["Dias Suportados"].apply(lambda x: max(0, round(x, 1)))

# 🎯 Alocação ponderada por rentabilidade x margem
df_mes_corrente["Peso Alocacao"] = df_mes_corrente["Rentabilidade (%)"].clip(lower=0) * df_mes_corrente["Margem (€)"]
soma_peso = df_mes_corrente["Peso Alocacao"].sum()
df_mes_corrente["Horas Sugeridas"] = (df_mes_corrente["Peso Alocacao"] / soma_peso * 8) if soma_peso > 0 else 0
df_mes_corrente["Horas Sugeridas"] = df_mes_corrente["Horas Sugeridas"].apply(lambda x: round(x * 2) / 2)

df_mes_corrente["Custo Simulado"] = df_mes_corrente["Horas Sugeridas"] * custo_hora
df_mes_corrente["Novo Custo Total"] = df_mes_corrente["Total Custos"] + df_mes_corrente["Custo Simulado"]
df_mes_corrente["Rentabilidade Ajustada (%)"] = df_mes_corrente.apply(
    lambda row: ((row["Total Proveitos"] - row["Novo Custo Total"]) / row["Total Proveitos"]) * 100
    if row["Total Proveitos"] > 0 else -100 if row["Total Custos"] > 0 else 0,
    axis=1
)

df_horas = df_mes_corrente[[
    "Nome Cliente", "Nome Projecto", "Margem (€)", "Rentabilidade (%)", "Dias Suportados", "Horas Sugeridas", "Rentabilidade Ajustada (%)"
]].copy()

df_horas["Margem (€)"] = df_horas["Margem (€)"].map(lambda x: f"€ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
df_horas["Rentabilidade (%)"] = df_horas["Rentabilidade (%)"].map(lambda x: f"{x:.2f}%")
df_horas["Rentabilidade Ajustada (%)"] = df_horas["Rentabilidade Ajustada (%)"].map(lambda x: f"{x:.2f}%")
df_horas["Horas Sugeridas"] = df_mes_corrente["Horas Sugeridas"].map(lambda x: f"{x:.1f}h")

st.dataframe(df_horas.reset_index(drop=True), use_container_width=True)
