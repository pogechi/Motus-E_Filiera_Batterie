import streamlit as st
import folium
from folium.plugins import TagFilterButton, OverlappingMarkerSpiderfier
from streamlit_folium import st_folium
import numpy as np
import pandas as pd

st.set_page_config(page_title="Filiera italiana batterie", page_icon="🔋", layout="wide")

data = "Filiera batterie Motus-E Italia.xlsx"
df = pd.read_excel(data, engine="openpyxl")
df = df.replace([None,np.nan], value=" ")
df[["Lat","Lon"]] = df["Lat,Lon"].str.split(",", expand=True)
df["Lat"] = pd.to_numeric(df["Lat"], errors="coerce")
df["Lon"] = pd.to_numeric(df["Lon"], errors="coerce")

m = folium.Map((41.89, 12.48), zoom_start=7, 
               tiles="cartodb positron",
               max_bounds=True,
               scrollWheelZoom=False,
               min_lat=35,
               max_lat=50,
               min_lon=-4,
               max_lon=27)
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

st.logo("motuselogo.png", size="large", link="https://www.motus-e.org/")

st.title("🔋 La filiera delle batterie in Italia 🇮🇹")

st.markdown("""La **filiera italiana delle batterie** è un ecosistema articolato 
che include produttori di pacchi batteria, aziende specializzate in macchinari 
e realtà dedicate a componenti elettronici e materiali chimici. Il settore mostra 
margini di crescita, in particolare nel riciclo, dove sono ancora poche le aziende 
che lavorano sul recupero della black mass e per la seconda vita delle batterie; 
completano il quadro i fornitori di servizi di testing e consorzi EPR. 
\nIn verde sono contrassegnate le aziende già operative in Italia mentre in grigio le realtà prossime 
all’avvio delle attività. Puoi usare l’icona del filtro sulla mappa per esplorare le 
aziende lungo l\'intera filiera delle batterie.""")

st_data = st_folium(m, width=1400, height=700)

st.subheader("📊 Alcuni numeri sulla filiera italiana delle batterie")
row = st.container(horizontal=True)

aziende_censite = len(df)
aziende_al_nord = len(df[df["Lat"] > 44])
specializzazione = df["Filiera 1"].value_counts().index[0]

with row:
    st.metric(label="Aziende censite", value=aziende_censite, delta=None, border=True)
    st.metric(label="Aziende in Nord Italia", value=f"{aziende_al_nord / aziende_censite:.0%}", delta=None, border=True)
    st.metric(label="Specializzazione principale", value=specializzazione, delta=None, border=True)

st.divider()

st.markdown("""**Non vedi la tua azienda sulla mappa?**
Segnalacela tramite questo breve modulo: ci occuperemo noi di inserirla nella filiera. 

\n👉 [Compila il form di segnalazione](https://forms.gle/WTkos5SfKXcT1Vme8)""")

st.divider()

st.caption("Realizzato per [Motus-E](https://www.motus-e.org/) da [Teraton](https://www.teraton.tech/)")