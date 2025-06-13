import streamlit as st
import pandas as pd
import numpy as np
import datetime

st.set_page_config(page_title="Dashboard Rentabilidade", layout="wide")
st.title("📊 Dashboard de Rentabilidade de Projetos")

# 🔐 Autenticação simples
senha = st.text_input("Digite a senha para acessar o dashboard:", type="password")
if senha != "meuacesso123":
    st.warning("🔐 Acesso restrito. Digite a senha correta.")
    st.stop()

# 📤 Upload do Excel
arquivo = st.file_uploader("📤 Faça upload do arquivo rentabilidade.xlsx", type=["xlsx"])
if not arquivo:
    st.info("Aguardando upload do arquivo Excel.")
    st.stop()

# ✅ Leitura do Excel enviado
df = pd.read_excel(arquivo)
df.columns = df.columns.str.strip()
df = df[df["Mes"].notna()]



# 🕗 Tabela de sugestão de alocação de horas (8h/dia)
st.markdown("### 🕗 Sugestão de Alocação de Horas (8h/dia)")

# Filtra mês atual
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

# Cálculo de alocação
custo_dia = 262
custo_hora = custo_dia / 8
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
    "Nome Cliente", "Nome Projecto", "Margem (€)", "Rentabilidade (%)", "Horas Sugeridas", "Rentabilidade Ajustada (%)"
]].copy()

df_horas["Margem (€)"] = df_horas["Margem (€)"].map(lambda x: f"€ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
df_horas["Rentabilidade (%)"] = df_horas["Rentabilidade (%)"].map(lambda x: f"{x:.2f}%")
df_horas["Rentabilidade Ajustada (%)"] = df_horas["Rentabilidade Ajustada (%)"].map(lambda x: f"{x:.2f}%")
df_horas["Horas Sugeridas"] = df_mes_corrente["Horas Sugeridas"].map(lambda x: f"{x:.1f}h")

# Estilo com destaque
def destacar_linha(row):
    try:
        horas = float(str(row["Horas Sugeridas"]).replace("h", "").replace(",", "."))
        if horas > 0:
            return ['background-color: lightgreen'] * len(row)
    except:
        pass
    return [''] * len(row)

st.dataframe(df_horas.reset_index(drop=True).style.apply(destacar_linha, axis=1), use_container_width=True)
