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
