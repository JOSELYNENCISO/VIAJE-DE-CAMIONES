import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# =========================
# CONFIGURACIÓN DASHBOARD
# =========================
st.set_page_config(page_title="Dashboard de Taladros", layout="wide")

st.title("⛏️ Dashboard de Malla de Voladura - Carguío por Camión")

# =========================
# CARGA DE ARCHIVO
# =========================
archivo = st.file_uploader("Sube tu archivo Excel", type=["xlsx"])

if archivo:
    df = pd.read_excel(archivo)

    # =========================
    # LIMPIEZA
    # =========================
    df.columns = df.columns.str.strip()
    df["Camion"] = df["Camion"].astype(str).str.strip()

    df["Viaje"] = df["Viaje"].astype(str).str.replace("V", "")
    df["Viaje"] = pd.to_numeric(df["Viaje"], errors='coerce')

    df = df.dropna(subset=["X", "Y", "Camion", "Viaje"])

    # =========================
    # SIDEBAR FILTROS
    # =========================
    st.sidebar.header("🔎 Filtros")

    camiones = st.sidebar.multiselect(
        "Selecciona Camión",
        options=df["Camion"].unique(),
        default=df["Camion"].unique()
    )

    viajes = st.sidebar.multiselect(
        "Selecciona Viaje",
        options=sorted(df["Viaje"].unique()),
        default=sorted(df["Viaje"].unique())
    )

    df = df[(df["Camion"].isin(camiones)) & (df["Viaje"].isin(viajes))]

    # =========================
    # KPIs
    # =========================
    col1, col2, col3 = st.columns(3)

    col1.metric("Total Taladros", len(df))
    col2.metric("Camiones Activos", df["Camion"].nunique())
    col3.metric("Viajes Activos", df["Viaje"].nunique())

    st.markdown("---")

    # =========================
    # MAPA DE TALADROS
    # =========================
    st.subheader("📍 Plano de Taladros")

    colores_camion = {
        "PEQ13": "#4E79A7",
        "PEQ14": "#59A14F",
        "PEQ15": "#F28E2B",
        "PEQ02": "#E15759",
        "PEQ03": "#76B7B2",
        "PEQ16": "#B07AA1"
    }

    tamaño_viaje = {1: 60, 2: 90, 3: 130, 4: 170}

    fig, ax = plt.subplots(figsize=(10, 10))

    for camion in df["Camion"].unique():
        for viaje in df["Viaje"].unique():

            sub = df[(df["Camion"] == camion) & (df["Viaje"] == viaje)]

            if sub.empty:
                continue

            ax.scatter(
                sub["X"], sub["Y"],
                c=colores_camion.get(camion, "black"),
                s=tamaño_viaje.get(viaje, 80),
                alpha=0.75,
                edgecolors='black'
            )

    # IDs (opcional)
    offset = (df["Y"].max() - df["Y"].min()) * 0.01

    for _, row in df.iterrows():
        ax.text(row["X"], row["Y"] + offset, str(row["ID"]), fontsize=6)

    ax.set_title("Distribución de Taladros por Camión y Viaje")
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.grid(True, linestyle='--', alpha=0.3)
    ax.set_aspect('equal')

    st.pyplot(fig)

    # =========================
    # RESUMEN POR CAMIÓN
    # =========================
    st.subheader("🚛 Taladros por Camión")
    resumen = df.groupby("Camion")['ID'].count().reset_index()
    resumen.columns = ["Camión", "Taladros"]

    st.dataframe(resumen)

else:
    st.info("Sube un archivo Excel para visualizar el dashboard")
