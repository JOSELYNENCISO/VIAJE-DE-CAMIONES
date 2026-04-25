import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.lines import Line2D

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
    df["Viaje"] = pd.to_numeric(df["Viaje"], errors="coerce")

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
    # COLORES
    # =========================
    colores_camion = {
        "PEQ13": "#4E79A7",
        "PEQ14": "#59A14F",
        "PEQ15": "#F28E2B",
        "PEQ02": "#E15759",
        "PEQ03": "#76B7B2",
        "PEQ16": "#B07AA1"
    }

    # =========================
    # MAPA
    # =========================
    st.subheader("📍 Plano de Taladros")

    fig, ax = plt.subplots(figsize=(10, 10))

    for camion in df["Camion"].unique():
        sub_camion = df[df["Camion"] == camion]
        color = colores_camion.get(camion, "black")

        for _, row in sub_camion.iterrows():

            # Forma por viaje
            marker = "o" if row["Viaje"] == 1 else "^"

            ax.scatter(
                row["X"], row["Y"],
                c=color,
                marker=marker,
                s=90,
                alpha=0.85,
                edgecolors="black"
            )

            # ID ARRIBA DEL PUNTO
            ax.text(
                row["X"], row["Y"] + 0.5,
                str(row["ID"]),
                fontsize=6,
                ha="center",
                va="bottom"
            )

    # =========================
    # LEYENDA COMPLETA
    # =========================
    legend_camiones = [
        Patch(facecolor=color, edgecolor="black", label=f"Camión {camion}")
        for camion, color in colores_camion.items()
        if camion in df["Camion"].values
    ]

    legend_viajes = [
        Line2D([0], [0], marker='o', color='w', label='Viaje 1 (Círculo)',
               markerfacecolor='gray', markersize=8),
        Line2D([0], [0], marker='^', color='w', label='Viaje 2+ (Triángulo)',
               markerfacecolor='gray', markersize=8)
    ]

    ax.legend(
        handles=legend_camiones + legend_viajes,
        title="Leyenda",
        bbox_to_anchor=(1.05, 1),
        loc="upper left"
    )

    # =========================
    # ESTILO
    # =========================
    ax.set_title("Distribución de Taladros por Camión y Viaje", fontsize=14, fontweight="bold")
    ax.set_xlabel("X")
    ax.set_ylabel("Y")

    # ❌ SIN GRILLA
    ax.grid(False)

    ax.set_aspect("equal")

    st.pyplot(fig)

    # =========================
    # RESUMEN
    # =========================
    st.subheader("🚛 Taladros por Camión")

    resumen = df.groupby("Camion")["ID"].count().reset_index()
    resumen.columns = ["Camión", "Taladros"]

    st.dataframe(resumen)

else:
    st.info("Sube un archivo Excel para visualizar el dashboard")
