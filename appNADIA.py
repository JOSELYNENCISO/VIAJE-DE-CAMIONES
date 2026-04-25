import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
from io import BytesIO

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
    # COLORES CORPORATIVOS
    # =========================
    colores_camion = {
        "PEQ13": "#1F4E79",
        "PEQ14": "#2E7D32",
        "PEQ15": "#EF6C00",
        "PEQ02": "#C62828",
        "PEQ03": "#00838F",
        "PEQ16": "#6A1B9A"
    }

    # =========================
    # MAPA
    # =========================
    st.subheader("📍 Plano de Taladros")

    fig, ax = plt.subplots(figsize=(10, 10))

    for camion in df["Camion"].unique():
        sub_camion = df[df["Camion"] == camion]
        color = colores_camion.get(camion, "gray")

        for _, row in sub_camion.iterrows():

            marker = "o" if row["Viaje"] == 1 else "^"

            ax.scatter(
                row["X"], row["Y"],
                c=color,
                marker=marker,
                s=95,
                alpha=0.9,
                linewidths=0
            )

            ax.text(
                row["X"], row["Y"] + 1.0,
                str(row["ID"]),
                fontsize=6,
                ha="center",
                va="bottom"
            )

    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_xlabel("")
    ax.set_ylabel("")
    ax.axis("off")

    # =========================
    # LEYENDA
    # =========================
    legend_camiones = [
        Patch(facecolor=color, edgecolor="none", label=f"Camión {camion}")
        for camion, color in colores_camion.items()
        if camion in df["Camion"].values
    ]

    legend_viajes = [
        Line2D([0], [0], marker='o', color='w', label='Viaje 1 (Círculo)', markerfacecolor='gray', markersize=8),
        Line2D([0], [0], marker='^', color='w', label='Viaje 2+ (Triángulo)', markerfacecolor='gray', markersize=8)
    ]

    ax.legend(
        handles=legend_camiones + legend_viajes,
        title="Leyenda",
        bbox_to_anchor=(1.05, 1),
        loc="upper left"
    )

    st.pyplot(fig)

    # =========================
    # DESCARGA HD
    # =========================
    buffer = BytesIO()
    fig.savefig(buffer, format="png", dpi=300, bbox_inches="tight")
    buffer.seek(0)

    st.download_button(
        label="📥 Descargar gráfico en HD",
        data=buffer,
        file_name="malla_voladura_hd.png",
        mime="image/png"
    )

    # =========================
    # RESUMEN
    # =========================
    st.subheader("🚛 Resumen de Carguío por Camión y Viaje")

    resumen = df.groupby(["Camion", "Viaje"])['ID'].count().reset_index()
    resumen.columns = ["Camión", "Viaje", "Taladros"]

    resumen_pivot = resumen.pivot(index="Camión", columns="Viaje", values="Taladros").fillna(0)

    st.dataframe(resumen_pivot)

else:
    st.info("Sube un archivo Excel para visualizar el dashboard")