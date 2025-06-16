
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

df_rent = df_base[[ 
    "Mes", "Mes_Num", "Nome Cliente", "Nome Projecto", 
    "Total Proveitos", "Total Custos"
]].copy()

df_rent["Margem (€)"] = df_rent["Total Proveitos"] - df_rent["Total Custos"]

if "Tudo" in meses_selecionados:
    # Agrupar por projeto + cliente
    df_rent = df_rent.groupby(["Nome Cliente", "Nome Projecto"], as_index=False).agg({
        "Total Proveitos": "sum",
        "Total Custos": "sum",
        "Margem (€)": "sum"
    })
    df_rent["Rentabilidade (%)"] = df_rent.apply(
        lambda row: (row["Margem (€)"] / row["Total Proveitos"] * 100)
        if row["Total Proveitos"] > 0 else -100 if row["Total Custos"] > 0 else 0,
        axis=1
    )
    df_rent = df_rent[[
        "Nome Cliente", "Nome Projecto", "Total Proveitos", "Total Custos", "Margem (€)", "Rentabilidade (%)"
    ]].copy()
else:
    df_rent["Rentabilidade (%)"] = df_rent.apply(
        lambda row: (row["Margem (€)"] / row["Total Proveitos"] * 100)
        if row["Total Proveitos"] > 0 else -100 if row["Total Custos"] > 0 else 0,
        axis=1
    )
    df_rent = df_rent.sort_values(by=["Mes_Num", "Rentabilidade (%)"], ascending=[True, False])
    df_rent.drop(columns=["Mes_Num"], inplace=True)

# Formatação
df_rent["Total Proveitos"] = df_rent["Total Proveitos"].map(lambda x: f"€ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
df_rent["Total Custos"] = df_rent["Total Custos"].map(lambda x: f"€ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
df_rent["Margem (€)"] = df_rent["Margem (€)"].map(lambda x: f"€ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
df_rent["Rentabilidade (%)"] = df_rent["Rentabilidade (%)"].map(lambda x: f"{x:.2f}%")

# Função de destaque condicional
def destacar_rentabilidade(row):
    try:
        valor = float(str(row["Rentabilidade (%)"]).replace("%", "").replace(",", "."))
        if valor <= 30:
            return ['background-color: #f8d7da'] * len(row)  # vermelho claro
    except:
        pass
    return [''] * len(row)

# Apresentação com destaque
st.dataframe(
    df_rent.reset_index(drop=True).style.apply(destacar_rentabilidade, axis=1),
    use_container_width=True
)


# -------------------- Tabela de Alocação --------------------
st.markdown("### 🕗 Alocação diária de horas de gestão")

mes_atual = datetime.datetime.now().strftime("%b")
mes_atual_pt = {'Jan':'Jan', 'Feb':'Fev', 'Mar':'Mar', 'Apr':'Abr', 'May':'Mai', 'Jun':'Jun',
                'Jul':'Jul', 'Aug':'Ago', 'Sep':'Set', 'Oct':'Out', 'Nov':'Nov', 'Dec':'Dez'}[mes_atual]
df_mes_corrente = df[df["Mes"] == mes_atual_pt].copy()

df_mes_corrente["Total Proveitos"] = pd.to_numeric(df_mes_corrente["Total Proveitos"], errors="coerce").fillna(0)
df_mes_corrente["Total Custos"] = pd.to_numeric(df_mes_corrente["Total Custos"], errors="coerce").fillna(0)
df_mes_corrente["Margem (€)"] = df_mes_corrente["Total Proveitos"] - df_mes_corrente["Total Custos"]
df_mes_corrente["Rentabilidade (%)"] = df_mes_corrente.apply(
    lambda row: (row["Margem (€)"] / row["Total Proveitos"] * 100)
    if row["Total Proveitos"] > 0 else -100 if row["Total Custos"] > 0 else 0,
    axis=1
)
df_mes_corrente = df_mes_corrente[df_mes_corrente["Margem (€)"] >= 262].copy()

custo_dia = 262
custo_hora = custo_dia / 8
df_mes_corrente["Dias Suportados"] = df_mes_corrente["Margem (€)"] / custo_dia
df_mes_corrente["Dias Suportados"] = df_mes_corrente["Dias Suportados"].apply(lambda x: max(0, round(x, 1)))

df_mes_corrente["Peso Alocacao"] = df_mes_corrente["Rentabilidade (%)"].clip(lower=0) * df_mes_corrente["Margem (€)"]
soma_peso = df_mes_corrente["Peso Alocacao"].sum()

if soma_peso > 0:
    df_mes_corrente["Horas Precisas"] = df_mes_corrente["Peso Alocacao"] / soma_peso * 8
    df_mes_corrente["Horas Arredondadas"] = df_mes_corrente["Horas Precisas"].apply(lambda x: round(x * 2) / 2)

    soma_ajustada = df_mes_corrente["Horas Arredondadas"].sum()
    diferenca = round(8.0 - soma_ajustada, 2)

    if abs(diferenca) > 0:
        df_mes_corrente["Delta"] = df_mes_corrente["Horas Precisas"] - df_mes_corrente["Horas Arredondadas"]
        idx_ajuste = df_mes_corrente["Delta"].abs().idxmax()
        df_mes_corrente.loc[idx_ajuste, "Horas Arredondadas"] += diferenca
        df_mes_corrente["Horas Arredondadas"] = df_mes_corrente["Horas Arredondadas"].apply(lambda x: round(x * 2) / 2)

    df_mes_corrente["Horas Sugeridas"] = df_mes_corrente["Horas Arredondadas"]
else:
    df_mes_corrente["Horas Sugeridas"] = 0


df_mes_corrente["Custo Simulado"] = df_mes_corrente["Horas Sugeridas"] * custo_hora
df_mes_corrente["Novo Custo Total"] = df_mes_corrente["Total Custos"] + df_mes_corrente["Custo Simulado"]
df_mes_corrente["Rentabilidade Ajustada (%)"] = df_mes_corrente.apply(
    lambda row: ((row["Total Proveitos"] - row["Novo Custo Total"]) / row["Total Proveitos"]) * 100
    if row["Total Proveitos"] > 0 else -100 if row["Total Custos"] > 0 else 0,
    axis=1
)

df_horas = df_mes_corrente[[ "Nome Cliente", "Nome Projecto", "Margem (€)", "Rentabilidade (%)", "Dias Suportados", "Horas Sugeridas", "Rentabilidade Ajustada (%)" ]].copy()
df_horas["Margem (€)"] = df_horas["Margem (€)"].map(lambda x: f"€ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
df_horas["Rentabilidade (%)"] = df_horas["Rentabilidade (%)"].map(lambda x: f"{x:.2f}%")
df_horas["Rentabilidade Ajustada (%)"] = df_horas["Rentabilidade Ajustada (%)"].map(lambda x: f"{x:.2f}%")
df_horas["Horas Sugeridas"] = df_mes_corrente["Horas Sugeridas"].map(lambda x: f"{x:.1f}h")

# Adiciona destaque para projetos com horas alocadas > 0
def destacar_linha(row):
    try:
        horas = float(str(row["Horas Sugeridas"]).replace("h", "").replace(",", "."))
        if horas > 0:
            return ['background-color: lightgreen'] * len(row)
    except:
        pass
    return [''] * len(row)

st.dataframe(df_horas.reset_index(drop=True).style.apply(destacar_linha, axis=1), use_container_width=True)




