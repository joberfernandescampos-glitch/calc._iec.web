import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# Configuração da página do Streamlit
st.set_page_config(page_title="Calculadora de Curvas IEC", layout="centered")
st.title("⚡JÓBER FERNANDES - Curvas IEC (Proteção)")

# Dicionário com os parâmetros das curvas IEC (IEC 60255)
CURVAS_IEC = {
    "IEC Normal Inversa (NI)": (0.14, 0.02),
    "IEC Muito Inversa (MI)": (13.5, 1.0),
    "IEC Extremamente Inversa (EI)": (80.0, 2.0),
    "IEC Longo Tempo Inversa (LTI)": (120.0, 1.0)
}

# --- PAINEL LATERAL DE ENTRADAS ---
st.sidebar.header("📋 Parâmetros de Entrada")

# 1. Seleção da Curva IEC
curva_selecionada = st.sidebar.selectbox("Selecione a Curva IEC:", list(CURVAS_IEC.keys()))
k, alpha = CURVAS_IEC[curva_selecionada]

# 2. Entradas de Corrente e Ajuste
i_falta = st.sidebar.number_input("Corrente de Falta (I) [A]:", min_value=0.1, value=150.0, step=10.0)
i_partida = st.sidebar.number_input("Corrente de Partida/Pick-up (I_p) [A]:", min_value=0.1, value=50.0, step=5.0)
dial = st.sidebar.number_input("Dial de Tempo (TMS):", min_value=0.01, max_value=10.0, value=0.1, step=0.05)

# --- CÁLCULO DO PONTO DE OPERAÇÃO ---
multiplo_i = i_falta / i_partida

st.subheader("📊 Resultados do Ponto de Operação")

if multiplo_i <= 1.0:
    st.error(f"A corrente de falta ({i_falta}A) é menor ou igual à corrente de partida ({i_partida}A). O relé não irá partir (Múltiplo M = {multiplo_i:.2f}).")
    tempo_operacao = None
else:
    # Fórmula IEC: t = TMS * (k / (M^alpha - 1))
    tempo_operacao = dial * (k / (multiplo_i**alpha - 1))
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Múltiplo de Partida (M)", f"{multiplo_i:.2f} x")
    col2.metric("Tempo de Atuação (t)", f"{tempo_operacao:.3f} s")
    col3.metric("Constantes Usadas", f"k={k}, α={alpha}")

# --- PLOTAGEM DA CURVA CARACTERÍSTICA ---
st.subheader("📈 Gráfico da Curva de Proteção")

# Gerando múltiplos de corrente de 1.1 até 20 para desenhar a curva
m_valores = np.linspace(1.1, 20.0, 500)
tempos_curva = dial * (k / (m_valores**alpha - 1))

# Criando o gráfico com Matplotlib
fig, ax = plt.subplots(figsize=(8, 5))
ax.plot(m_valores, tempos_curva, label=f"Curva {curva_selecionada}", color="blue", linewidth=2)

# Se houver um ponto de operação válido, plota ele no gráfico
if tempo_operacao is not None and multiplo_i <= 20.0:
    ax.scatter([multiplo_i], [tempo_operacao], color="red", s=100, zorder=5, 
               label=f"Ponto de Falta ({multiplo_i:.2f}x, {tempo_operacao:.2f}s)")
    ax.axhline(y=tempo_operacao, color="red", linestyle="--", alpha=0.5)
    ax.axvline(x=multiplo_i, color="red", linestyle="--", alpha=0.5)

# Customização técnica do Gráfico (Escala Bilogarítmica tradicional de relés)
ax.set_yscale('log')
ax.set_title(f"Tempo Inverso - {curva_selecionada}", fontsize=12, fontweight='bold')
ax.set_xlabel("Múltiplo da Corrente de Partida (I / I_p)", fontsize=10)
ax.set_ylabel("Tempo de Atuação (segundos) - Escala Log", fontsize=10)
ax.grid(True, which="both", linestyle=":", alpha=0.6)
ax.legend()

# Exibe o gráfico na página Web do Streamlit
st.pyplot(fig)
