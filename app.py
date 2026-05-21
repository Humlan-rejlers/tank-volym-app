import streamlit as st
import numpy as np
import plotly.graph_objects as go
import math
import pandas as pd

st.title("Tankvolymskalkylator med justerbar botten och topp")

# --- INPUTS ---
botten_form = st.selectbox("Bottenform", ["Platt", "Konisk", "Sfärisk", "Elliptisk"])
topp_form = st.selectbox("Toppform", ["Platt", "Konisk", "Sfärisk", "Kupol"])
r = st.slider("Radie (m)", 0.1, 5.0, 1.0)
h_cylinder = st.slider("Cylindervolym höjd (m)", 0.1, 10.0, 2.0)
h_botten = st.slider("Bottenhöjd (m)", 0.0, 5.0, 0.5)
h_topp = st.slider("Topphöjd (m)", 0.0, 5.0, 0.5)

# --- VOLYMBERÄKNING ---
def berakna_volym(botten_form, topp_form, r, h_cylinder, h_botten, h_topp):
    if botten_form == 'Platt':
        V_botten = math.pi * r**2 * h_botten
    elif botten_form == 'Konisk':
        V_botten = (1/3) * math.pi * r**2 * h_botten
    elif botten_form == 'Sfärisk':
        V_botten = (2/3) * math.pi * r**3
    else:  # Elliptisk
        V_botten = (2/3) * math.pi * r**2 * h_botten

    if topp_form == 'Platt':
        V_topp = math.pi * r**2 * h_topp
    elif topp_form == 'Konisk':
        V_topp = (1/3) * math.pi * r**2 * h_topp
    elif topp_form == 'Sfärisk':
        V_topp = (2/3) * math.pi * r**3
    else:  # Kupol
        V_topp = (2/3) * math.pi * r**2 * h_topp

    V_cylinder = math.pi * r**2 * h_cylinder
    return V_botten + V_cylinder + V_topp

V_total = berakna_volym(botten_form, topp_form, r, h_cylinder, h_botten, h_topp)
st.subheader(f"Total tankvolym: {V_total:.2f} m³")

# --- 3D VISUALISERING ---
def skapa_tank():
    z_cyl = np.linspace(h_botten, h_botten+h_cylinder, 30)
    theta = np.linspace(0, 2*np.pi, 50)
    theta, z_cyl = np.meshgrid(theta, z_cyl)
    x_cyl = r * np.cos(theta)
    y_cyl = r * np.sin(theta)
    fig = go.Figure()
    fig.add_trace(go.Surface(x=x_cyl, y=y_cyl, z=z_cyl, colorscale='Blues', opacity=0.7))

    # Botten
    z_bot = np.linspace(0, h_botten, 2)
    theta_bot = np.linspace(0, 2*np.pi, 50)
    theta_bot, z_bot = np.meshgrid(theta_bot, z_bot)
    if botten_form == 'Platt':
        x_bot = r * np.cos(theta_bot)
        y_bot = r * np.sin(theta_bot)
    elif botten_form == 'Konisk':
        x_bot = r * (z_bot/h_botten) * np.cos(theta_bot)
        y_bot = r * (z_bot/h_botten) * np.sin(theta_bot)
    elif botten_form == 'Sfärisk':
        x_bot = r * np.sin(np.pi/2 * z_bot/h_botten) * np.cos(theta_bot)
        y_bot = r * np.sin(np.pi/2 * z_bot/h_botten) * np.sin(theta_bot)
    else:
        x_bot = r * np.sqrt(z_bot/h_botten) * np.cos(theta_bot)
        y_bot = r * np.sqrt(z_bot/h_botten) * np.sin(theta_bot)
    fig.add_trace(go.Surface(x=x_bot, y=y_bot, z=z_bot, colorscale='Reds', opacity=0.7))

    # Topp
    z_top = np.linspace(0, h_topp, 2)
    theta_top = np.linspace(0, 2*np.pi, 50)
    theta_top, z_top = np.meshgrid(theta_top, z_top)
    if topp_form == 'Platt':
        x_top = r * np.cos(theta_top)
        y_top = r * np.sin(theta_top)
        z_top = h_botten + h_cylinder + z_top
    elif topp_form == 'Konisk':
        x_top = r * (1 - z_top/h_topp) * np.cos(theta_top)
        y_top = r * (1 - z_top/h_topp) * np.sin(theta_top)
        z_top = h_botten + h_cylinder + z_top
    elif topp_form == 'Sfärisk':
        x_top = r * np.sin(np.pi/2 * (1 - z_top/h_topp)) * np.cos(theta_top)
        y_top = r * np.sin(np.pi/2 * (1 - z_top/h_topp)) * np.sin(theta_top)
        z_top = h_botten + h_cylinder + h_topp * (1 - np.cos(np.pi/2 * z_top/h_topp))
    else:  # Kupol
        x_top = r * np.sqrt(z_top/h_topp) * np.cos(theta_top)
        y_top = r * np.sqrt(z_top/h_topp) * np.sin(theta_top)
        z_top = h_botten + h_cylinder + z_top
    fig.add_trace(go.Surface(x=x_top, y=y_top, z=z_top, colorscale='Greens', opacity=0.7))

    fig.update_layout(scene=dict(aspectmode='data'), margin=dict(l=0,r=0,t=0,b=0))
    return fig

st.plotly_chart(skapa_tank(), use_container_width=True)

# --- EXPORT TILL CSV ---
if st.button("Exportera parametrar till CSV"):
    data = {
        "Bottenform": [botten_form],
        "Toppform": [topp_form],
        "Radie (m)": [r],
        "Cylinderhöjd (m)": [h_cylinder],
        "Bottenhöjd (m)": [h_botten],
        "Topphöjd (m)": [h_topp],
        "Total Volym (m³)": [V_total]
    }
    df = pd.DataFrame(data)
    df.to_csv("tank_parametrar.csv", index=False)
    st.success("CSV-fil skapad: tank_parametrar.csv")
    st.download_button("Ladda ner CSV", df.to_csv(index=False), "tank_parametrar.csv", "text/csv")
