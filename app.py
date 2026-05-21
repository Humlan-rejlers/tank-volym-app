import streamlit as st
import numpy as np
import plotly.graph_objects as go
import math
import pandas as pd

st.title("Tankvolymskalkylator – korrekt 3D-visualisering")

# --- INPUTS ---
botten_form = st.selectbox("Bottenform", ["Platt", "Konisk", "Sfärisk", "Elliptisk"])
topp_form = st.selectbox("Toppform", ["Platt", "Konisk", "Sfärisk", "Kupol"])
r = st.slider("Radie (m)", 0.1, 5.0, 1.0)
h_cylinder = st.slider("Cylinderhöjd (m)", 0.1, 10.0, 2.0)
h_botten = st.slider("Bottenhöjd (m)", 0.0, 5.0, 0.5)
h_topp = st.slider("Topphöjd (m)", 0.0, 5.0, 0.5)

# --- Volymberäkning ---
def berakna_volym(botten_form, topp_form, r, h_cylinder, h_botten, h_topp):
    V_botten = 0
    V_topp = 0
    if botten_form == "Platt":
        V_botten = math.pi * r**2 * h_botten
    elif botten_form == "Konisk":
        V_botten = (1/3) * math.pi * r**2 * h_botten
    elif botten_form == "Sfärisk":
        V_botten = (2/3) * math.pi * r**3
    else:
        V_botten = (2/3) * math.pi * r**2 * h_botten

    if topp_form == "Platt":
        V_topp = math.pi * r**2 * h_topp
    elif topp_form == "Konisk":
        V_topp = (1/3) * math.pi * r**2 * h_topp
    elif topp_form == "Sfärisk":
        V_topp = (2/3) * math.pi * r**3
    else:
        V_topp = (2/3) * math.pi * r**2 * h_topp

    V_cylinder = math.pi * r**2 * h_cylinder
    return V_botten + V_cylinder + V_topp

V_total = berakna_volym(botten_form, topp_form, r, h_cylinder, h_botten, h_topp)
st.subheader(f"Total tankvolym: {V_total:.2f} m³")

# --- Funktion för att generera yta ---
def generera_yta(form, r, höjd, z_offset=0, position="botten"):
    theta = np.linspace(0, 2*np.pi, 50)
    if form == "Platt":
        z = np.linspace(0, höjd, 10)  # minst 10 lager för Surface
        theta, z = np.meshgrid(theta, z)
        x = r * np.cos(theta)
        y = r * np.sin(theta)
        z += z_offset
    elif form == "Konisk":
        z = np.linspace(0, höjd, 20)
        theta, z = np.meshgrid(theta, z)
        if position == "botten":
            x = r * (z / höjd) * np.cos(theta)
            y = r * (z / höjd) * np.sin(theta)
            z += z_offset
        else:
            x = r * (1 - z / höjd) * np.cos(theta)
            y = r * (1 - z / höjd) * np.sin(theta)
            z += z_offset
    elif form == "Sfärisk":
        phi = np.linspace(0, np.pi/2, 20)
        phi, theta = np.meshgrid(phi, theta)
        x = r * np.sin(phi) * np.cos(theta)
        y = r * np.sin(phi) * np.sin(theta)
        if position == "botten":
            z = z_offset - r * np.cos(phi)
        else:
            z = z_offset + r * (1 - np.cos(phi))
    elif form == "Elliptisk":
        z = np.linspace(0, höjd, 20)
        theta, z = np.meshgrid(theta, z)
        x = r * np.sqrt(z / höjd) * np.cos(theta)
        y = r * np.sqrt(z / höjd) * np.sin(theta)
        z += z_offset
    elif form == "Kupol":
        z = np.linspace(0, höjd, 20)
        theta, z = np.meshgrid(theta, z)
        x = r * np.sqrt(z / höjd) * np.cos(theta)
        y = r * np.sqrt(z / höjd) * np.sin(theta)
        z += z_offset
    return x, y, z

# --- Skapa 3D-graf ---
fig = go.Figure()

# Cylinder
x_cyl, y_cyl, z_cyl = generera_yta("Platt", r, h_cylinder, z_offset=h_botten, position="cylinder")
fig.add_trace(go.Surface(x=x_cyl, y=y_cyl, z=z_cyl, colorscale="Blues", opacity=0.7))

# Botten
x_bot, y_bot, z_bot = generera_yta(botten_form, r, h_botten, z_offset=0, position="botten")
fig.add_trace(go.Surface(x=x_bot, y=y_bot, z=z_bot, colorscale="Reds", opacity=0.7))

# Topp
x_top, y_top, z_top = generera_yta(topp_form, r, h_topp, z_offset=h_botten + h_cylinder, position="topp")
fig.add_trace(go.Surface(x=x_top, y=y_top, z=z_top, colorscale="Greens", opacity=0.7))

fig.update_layout(scene=dict(aspectmode="data"), margin=dict(l=0,r=0,t=0,b=0))
st.plotly_chart(fig, use_container_width=True)

# --- CSV-export ---
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
    st.download_button("Ladda ner CSV", df.to_csv(index=False), "tank_parametrar.csv", "text/csv")
