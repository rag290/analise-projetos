
import streamlit as st
import pandas as pd
import numpy as np
import datetime

# -------------------- Autenticação --------------------
st.set_page_config(page_title="Dashboard Rentabilidade", layout="wide")
st.title("📊 Dashboard de Rentabilidade de Projetos")

# Senha de acesso
senha = st.sidebar.text_input("🔐 Insira a senha", type="password")
if senha != "123":
    st.warning("Acesso restrito. Insira a senha correta.")
    st.stop()

# -------------------- Upload --------------------
arquivo = st.file_uploader("📥 Faça upload do arquivo rentabilidade.xlsx", type=["xlsx"])
if not arquivo:
    st.info("Por favor, envie um arquivo Excel (.xlsx) para continuar.")
    st.stop()

df = pd.read_excel(arquivo)
df.columns = df.columns.str.strip()
df = df[df["Mes"].notna()]

# -------------------- Preparação --------------------
meses_abreviados = {
    'Jan': 1, 'Fev': 2, 'Mar': 3, 'Abr': 4, 'Mai': 5, 'Jun': 6,
    'Jul': 7, 'Ago': 8, 'Set': 9, 'Out': 10, 'Nov': 11, 'Dez': 12
}
df["Mes_Num"] = df["Mes"].map(meses_abreviados)
df = df.sort_values(by="Mes_Num")

# -------------------- Filtros --------------------
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

# -------------------- Indicadores --------------------
total_proveitos = df_base["Total Proveitos"].sum()
total_custos = df_base["Total Custos"].sum()
margem_total = total_proveitos - total_custos
rentabilidade_total = (margem_total / total_proveitos * 100) if total_proveitos > 0 else -100 if total_custos > 0 else 0

col1, col2, col3, col4 = st.columns(4)
col1.metric("💰 Total Proveitos", f"€ {total_proveitos:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
col2.metric("💸 Total Custos", f"€ {total_custos:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
col3.metric("📐 Margem Acumulada", f"€ {margem_total:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
col4.metric("📊 Rentabilidade Acumulada", f"{rentabilidade_total:.2f}%")

# -------------------- Tabela de Rentabilidade --------------------
st.markdown("### 📋 Análise de Rentabilidade dos Projetos")

if "Tudo" in meses_selecionados:
    df_rent = df_base.groupby(["Nome Cliente", "Nome Projecto"], as_index=False).agg({
        "Total Proveitos": "sum",
        "Total Custos": "sum",
        "Margem (€)": "sum"
    })
    df_rent["Rentabilidade (%)"] = df_rent.apply(
        lambda row: (row["Margem (€)"] / row["Total Proveitos"] * 100)
        if row["Total Proveitos"] > 0 else 0,
        axis=1
    )
else:
    df_rent = df_base[[
        "Mes", "Mes_Num", "Nome Cliente", "Nome Projecto",
        "Total Proveitos", "Total Custos", "Margem (€)", "Rentabilidade (%)"
    ]].copy()
    df_rent = df_rent.sort_values(by=["Mes_Num", "Rentabilidade (%)"], ascending=[True, False])
    df_rent.drop(columns=["Mes_Num"], inplace=True)

df_rent["Total Proveitos"] = df_rent["Total Proveitos"].map(lambda x: f"€ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
df_rent["Total Custos"] = df_rent["Total Custos"].map(lambda x: f"€ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
df_rent["Margem (€)"] = df_rent["Margem (€)"].map(lambda x: f"€ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
df_rent["Rentabilidade (%)"] = df_rent["Rentabilidade (%)"].map(lambda x: f"{x:.2f}%")

st.dataframe(df_rent.reset_index(drop=True), use_container_width=True)
