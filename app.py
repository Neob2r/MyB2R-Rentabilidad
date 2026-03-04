import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Configuración premium de la página
st.set_page_config(page_title="MyB2R Pro | Investment Suite", layout="wide", page_icon="🏠")

# Estilo personalizado para las métricas
st.markdown("""
    <style>
    [data-testid="stMetricValue"] { font-size: 28px; color: #00CC96; }
    .main { background-color: #f8f9fa; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏠 MyB2R Pro: Análisis de Rentabilidad")
st.markdown("---")

# --- PILAR 1: ENTRADA DE DATOS (BARRA LATERAL) ---
st.sidebar.header("📍 1. Costes de Adquisición")
precio = st.sidebar.number_input("Precio del Inmueble (€)", value=100000, step=1000)
itp_total = st.sidebar.number_input("ITP (Importe exacto en €)", value=7000, step=100)
notaria_gest_reg = st.sidebar.number_input("Notaría, Gestoría y Registro (€)", value=1500)
comision_inmo = st.sidebar.number_input("Comisión Inmobiliaria (€)", value=0)
varios_gastos = st.sidebar.number_input("Casilla 'Varios' (€)", value=0)

st.sidebar.header("🛠️ Reforma y Mobiliario")
reforma_total = st.sidebar.number_input("Presupuesto Reforma/Muebles (€)", value=5000)

st.sidebar.header("🏦 Financiación")
pct_financiacion = st.sidebar.slider("% de Financiación", 0, 100, 80)
interes = st.sidebar.number_input("Interés Anual (%)", value=3.0, format="%.2f")
plazo = st.sidebar.number_input("Plazo Hipoteca (Años)", value=30)

st.sidebar.header("💰 Explotación Mensual")
alquiler_mensual = st.sidebar.number_input("Alquiler Mensual Bruto (€)", value=750)
comunidad_ibi_seguros = st.sidebar.number_input("Gastos Fijos (Comunidad, IBI, Seguros) (€)", value=120)
reserva_mante = st.sidebar.slider("% Reserva Mantenimiento/Vacancia", 0, 15, 5)

# --- CÁLCULOS LÓGICOS ---
# Inversión inicial
total_gastos_compra = itp_total + notaria_gest_reg + comision_inmo + varios_gastos
total_inversion = precio + total_gastos_compra + reforma_total
capital_prestado = precio * (pct_financiacion / 100)
fondos_propios = total_inversion - capital_prestado

# Hipoteca mensual (Fórmula de amortización francesa)
r = interes / 100 / 12
n = plazo * 12
if r > 0:
    cuota_hipoteca = capital_prestado * (r * (1 + r)**n) / ((1 + r)**n - 1)
else:
    cuota_hipoteca = capital_prestado / n

# Cashflow
reserva_euros = alquiler_mensual * (reserva_mante / 100)
cashflow_neto = alquiler_mensual - cuota_hipoteca - comunidad_ibi_seguros - reserva_euros
rentabilidad_neta_roe = ((cashflow_neto * 12) / fondos_propios) * 100
dscr = alquiler_mensual / (cuota_hipoteca + comunidad_ibi_seguros) if (cuota_hipoteca + comunidad_ibi_seguros) > 0 else 0

# --- PILAR 2: DASHBOARD DE RESULTADOS ---
col1, col2, col3, col4 = st.columns(4)
col1.metric("Cashflow Neto", f"{cashflow_neto:.2f} €/mes")
col2.metric("ROE (Rent. s/ Cash)", f"{rentabilidad_neta_roe:.2f} %")
col3.metric("Aportación Inicial", f"{fondos_propios:.0f} €")
col4.metric("Ratio Cobertura (DSCR)", f"{dscr:.2f}")

st.markdown("---")

# --- PILAR 3: GRÁFICOS ---
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("📊 Distribución del Alquiler")
    datos_donut = {
        "Concepto": ["Hipoteca", "Gastos Fijos", "Reservas", "Cashflow Neto"],
        "Importe": [cuota_hipoteca, comunidad_ibi_seguros, reserva_euros, max(0, cashflow_neto)]
    }
    df_donut = pd.DataFrame(datos_donut)
    fig_donut = px.pie(df_donut, values='Importe', names='Concepto', hole=0.5,
                       color_discrete_sequence=['#FF6B6B', '#4D96FF', '#FFD93D', '#6BCB77'])
    st.plotly_chart(fig_donut, use_container_width=True)

with col_right:
    st.subheader("💰 Desglose Inversión Inicial")
    datos_barras = {
        "Categoría": ["Entrada Casa", "Impuestos (ITP)", "Reforma", "Notaría/Otros", "Comisión/Varios"],
        "Inversión (€)": [precio - capital_prestado, itp_total, reforma_total, notaria_gest_reg, comision_inmo + varios_gastos]
    }
    df_barras = pd.DataFrame(datos_barras)
    fig_barras = px.bar(df_barras, x="Categoría", y="Inversión (€)", text_auto='.2s',
                        color_discrete_sequence=['#1f77b4'])
    st.plotly_chart(fig_barras, use_container_width=True)

# Mensaje final profesional
st.info(f"💡 El punto de equilibrio de esta operación está en un alquiler de **{(cuota_hipoteca + comunidad_ibi_seguros + reserva_euros):.2f} €**.")
