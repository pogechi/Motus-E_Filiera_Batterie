import streamlit as st
import folium
from folium.plugins import TagFilterButton, OverlappingMarkerSpiderfier
from streamlit_folium import st_folium
import numpy as np
import pandas as pd

data = "Filiera batterie Motus-E Italia.xlsx"
df = pd.read_excel(data, engine="openpyxl")
df = df.replace([None,np.nan], value=" ")
df[["Lat","Lon"]] = df["Lat,Lon"].str.split(",", expand=True)
df["Lat"] = pd.to_numeric(df["Lat"], errors="coerce")
df["Lon"] = pd.to_numeric(df["Lon"], errors="coerce")

m = folium.Map((41.89, 12.48), zoom_start=6, 
               tiles="cartodb positron",
               max_bounds=True,
               scrollWheelZoom=False,
               min_lat=35.83205927016135,
               max_lat=48.155920623358526,
               min_lon=-4.812802161016015,
               max_lon=26.461693176182866)
geo_json_data = "it.json"
folium.GeoJson(geo_json_data,
              style_function=lambda feature: {
                  "fillColor": "#00c9a9",
                  "color": "black",
                  "weight": 1,
                  "dashArray": "5, 5",
              },
              highlight_function=lambda feature: {"fillColor": "#edfdf9"}).add_to(m)

categories = list(pd.read_excel(data, sheet_name="Dati")["Filiera"])
motus_logo = "https://www.motus-e.org/wp-content/uploads/2022/01/logo-dark.png"

for azienda, lat, lon, tag1, tag2, tag3, attivo, link in zip(df["Azienda"], df["Lat"], df["Lon"], df["Filiera 1"], df["Filiera 2"], df["Filiera 3"], df["In produzione"], df["Sito Web"]):

    text = f"""<h1><a href="{link}" target="_blank"><span style="font-family:'Montserrat';color:#006fb8">{azienda}</span></a></h1>
        <br><span style="font-family:'Montserrat'">
        -{tag1}<br>"""
    if tag2 != " ":
        text += f"-{tag2}<br>"
    if tag3 != " ":
        text += f"-{tag3}<br>"

    if attivo == "Sì":
        color = "green"
    else:
        color = "lightgray"
        text += f"<br><i>>>In costruzione<<</i>"
    text += "</span>"

    
    popup = folium.Popup(text, max_width=200)
    
    folium.Marker(location=[lat,lon], popup=popup, tags=[tag1, tag2, tag3], 
                  tooltip=azienda, icon=folium.Icon(icon="flash", color=color)).add_to(m)

oms = OverlappingMarkerSpiderfier(
    keep_spiderfied=False,  # Markers remain spiderfied after clicking
    nearby_distance=20,  # Distance for clustering markers in pixel
    circle_spiral_switchover=10,  # Threshold for switching between circle and spiral
    leg_weight=2.0  # Line thickness for spider legs
    )
oms.add_to(m)

TagFilterButton(categories, clear_text="Deseleziona tutto").add_to(m)
folium.FitOverlays().add_to(m)





st.title("🔋 La filiera delle batterie in Italia 🇮🇹")

st_data = st_folium(m, width=700, height=500)