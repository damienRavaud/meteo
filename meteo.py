import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import requests
import time

st.set_page_config(layout="wide", page_title="Visualisation Météo Deux-Sèvres")

# communes + coordonnées
COMMUNES_DEUX_SEVRES = [
    {"nom": "Niort", "lat": 46.3239, "lon": -0.4615},
    {"nom": "Bressuire", "lat": 46.8641, "lon": -0.4958},
    {"nom": "Parthenay", "lat": 46.6472, "lon": -0.2564},
    {"nom": "Thouars", "lat": 47.0153, "lon": -0.2128},
    {"nom": "Mauléon", "lat": 46.9028, "lon": -0.6625},
    {"nom": "Saint-Maixent-l'École", "lat": 46.4167, "lon": -0.1667},
    {"nom": "Airvault", "lat": 46.8556, "lon": -0.2025},
    {"nom": "Chef-Boutonne", "lat": 46.2833, "lon": -0.3167},
    {"nom": "Prahecq", "lat": 46.2833, "lon": -0.4333},
    {"nom": "La Crèche", "lat": 46.3833, "lon": -0.3500},
    {"nom": "Mauzé-sur-le-Mignon", "lat": 46.2167, "lon": -0.6167},
    {"nom": "Coulon", "lat": 46.3167, "lon": -0.6833},
    {"nom": "Chauray", "lat": 46.3667, "lon": -0.4167},
    {"nom": "Bessines", "lat": 46.3167, "lon": -0.3833},
    {"nom": "Saint-Symphorien", "lat": 46.4667, "lon": -0.3167},
    {"nom": "Echiré", "lat": 46.3500, "lon": -0.4000},
    {"nom": "Saint-Gelais", "lat": 46.4000, "lon": -0.3667},
    {"nom": "Fors", "lat": 46.2833, "lon": -0.4500},
    {"nom": "Frontenay-Rohan-Rohan", "lat": 46.2667, "lon": -0.4167},
    {"nom": "Saint-Georges-de-Rex", "lat": 46.2500, "lon": -0.5500},
]

# Modèles météo connus
MODELS = {
    "AROME": "arome_france",
    "ARPEGE": "arpege_europe",
    "ICON_EU": "icon_eu",
    "GFS": "gfs_global"
}

# charger données API
@st.cache_data(ttl=3600)  # Cache de 1 heure
def load_data_from_api(model_name="AROME"):
    model_key = MODELS[model_name]
    forecast_days = 16
    
    all_long_term_data = []
    all_hourly_data = []
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    total_communes = len(COMMUNES_DEUX_SEVRES)
    
    for index, ville in enumerate(COMMUNES_DEUX_SEVRES):
        status_text.text(f"Chargement des données pour {ville['nom']}... ({index + 1}/{total_communes})")
        progress_bar.progress((index + 1) / total_communes)
        
        URL = f"https://api.open-meteo.com/v1/forecast?latitude={ville['lat']}&longitude={ville['lon']}&models={model_key}&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,wind_speed_10m_max,wind_gusts_10m_max,sunrise,sunset,uv_index_max,daylight_duration,precipitation_probability_max&hourly=temperature_2m,relative_humidity_2m,wind_speed_10m,wind_direction_10m,cloudcover,precipitation_probability&timezone=Europe/Paris&forecast_days={forecast_days}"
        
        try:
            response = requests.get(URL, timeout=10)
            data = response.json()
            
            # DataFrame day
            df_long_term = pd.DataFrame({
                "Ville": [ville['nom']] * len(data["daily"]["time"]),
                "Latitude": [ville['lat']] * len(data["daily"]["time"]),
                "Longitude": [ville['lon']] * len(data["daily"]["time"]),
                "Date": data["daily"]["time"],
                "Température Max (°C)": data["daily"]["temperature_2m_max"],
                "Température Min (°C)": data["daily"]["temperature_2m_min"],
                "Précipitations (mm)": data["daily"]["precipitation_sum"],
                "Probabilité de Précipitations (%)": data["daily"]["precipitation_probability_max"],
                "Vitesse du vent Max (km/h)": data["daily"]["wind_speed_10m_max"],
                "Rafales Max (km/h)": data["daily"]["wind_gusts_10m_max"],
                "Lever du soleil": data["daily"]["sunrise"],
                "Coucher du soleil": data["daily"]["sunset"],
                "Durée du jour (secondes)": data["daily"]["daylight_duration"],
                "Indice UV Max": data["daily"]["uv_index_max"]
            })
            
            # DataFrame heure
            df_hourly = pd.DataFrame({
                "Ville": [ville['nom']] * len(data["hourly"]["time"]),
                "Date et Heure": data["hourly"]["time"],
                "Température (°C)": data["hourly"]["temperature_2m"],
                "Humidité (%)": data["hourly"]["relative_humidity_2m"],
                "Vitesse du vent (km/h)": data["hourly"]["wind_speed_10m"],
                "Direction du vent (°)": data["hourly"]["wind_direction_10m"],
                "Couverture nuageuse (%)": data["hourly"]["cloudcover"],
                "Probabilité de Précipitations (%)": data["hourly"]["precipitation_probability"]
            })
            
            all_long_term_data.append(df_long_term)
            all_hourly_data.append(df_hourly)
            
            # pause pour ne pas surcharger l'API
            time.sleep(0.01)
            
        except Exception as e:
            st.warning(f"Erreur pour {ville['nom']}: {e}")
    
    progress_bar.empty()
    status_text.empty()
    
    # assemble les données
    df_long_term = pd.concat(all_long_term_data, ignore_index=True)
    df_hourly = pd.concat(all_hourly_data, ignore_index=True)
    
    # Conversion des dates
    df_long_term["Date"] = pd.to_datetime(df_long_term["Date"])
    df_hourly["Date et Heure"] = pd.to_datetime(df_hourly["Date et Heure"])
    
    return df_long_term, df_hourly

# interface user
st.title("📊 Visualisation Météo Deux-Sèvres")

# onglet pour choisir modele
selected_model = st.sidebar.selectbox("Modèle météorologique", list(MODELS.keys()))

# Bouton d'actualisation
if st.sidebar.button("🔄 Rafraîchir les données"):
    st.cache_data.clear()
    st.rerun()

# Affichage de l'heure de last MAJ
st.sidebar.info(f"💡 Les données sont mises en cache pendant 1 heure pour optimiser les performances.")

# Chargement des données
with st.spinner("Chargement des données météorologiques..."):
    df_long_term, df_hourly = load_data_from_api(selected_model)

if df_long_term is not None and df_hourly is not None:
    st.success(f"✅ Données chargées : {len(df_long_term)} prévisions journalières et {len(df_hourly)} prévisions horaires")
    
    # Récupération des dates dispo
    available_dates = df_long_term["Date"].dt.date.unique()
    
    # Création du slider pour les dates
    selected_date_idx = st.slider("Sélectionner la date", 0, len(available_dates)-1, 0)
    selected_date = available_dates[selected_date_idx]
    st.write(f"Date sélectionnée: **{selected_date}**")
    
    # Filtrage des données pour la date sélectionnée
    daily_data = df_long_term[df_long_term["Date"].dt.date == selected_date]
    hourly_data = df_hourly[df_hourly["Date et Heure"].dt.date == selected_date]
    
    # ===================== CHIFFRES CLÉS =====================
    st.header("🔑 Chiffres clés du jour")
    
    # Mise en page en colonnes pour les chiffres clés
    col1, col2, col3, col4 = st.columns(4)
    
    # Température max
    max_temp = daily_data["Température Max (°C)"].max()
    if pd.notna(max_temp):
        ville_max_temp = daily_data.loc[daily_data["Température Max (°C)"].idxmax(), "Ville"]
    else:
        max_temp = 0
        ville_max_temp = "Non disponible"
    col1.metric("Température maximale", f"{max_temp:.1f} °C", f"à {ville_max_temp}")
    
    # Température min
    min_temp = daily_data["Température Min (°C)"].min()
    if pd.notna(min_temp):
        ville_min_temp = daily_data.loc[daily_data["Température Min (°C)"].idxmin(), "Ville"]
    else:
        min_temp = 0
        ville_min_temp = "Non disponible"
    col2.metric("Température minimale", f"{min_temp:.1f} °C", f"à {ville_min_temp}")
    
    # Vent max
    max_wind = daily_data["Rafales Max (km/h)"].max()
    if pd.notna(max_wind):
        ville_max_wind = daily_data.loc[daily_data["Rafales Max (km/h)"].idxmax(), "Ville"]
    else:
        max_wind = 0
        ville_max_wind = "Non disponible"
    col3.metric("Rafales maximales", f"{max_wind:.1f} km/h", f"à {ville_max_wind}")
    
    # UV max
    max_uv = daily_data["Indice UV Max"].max()
    if pd.notna(max_uv):
        ville_max_uv = daily_data.loc[daily_data["Indice UV Max"].idxmax(), "Ville"]
    else:
        max_uv = 0
        ville_max_uv = "Non disponible"
    col4.metric("Indice UV maximal", f"{max_uv:.1f}", f"à {ville_max_uv}")
    
    # Seconde ligne de chiffres clés
    col1, col2, col3, col4 = st.columns(4)
    
    # Précipitations max
    max_precip = daily_data["Précipitations (mm)"].max()
    if pd.notna(max_precip):
        ville_max_precip = daily_data.loc[daily_data["Précipitations (mm)"].idxmax(), "Ville"]
    else:
        max_precip = 0
        ville_max_precip = "Non disponible"
    col1.metric("Précipitations maximales", f"{max_precip:.1f} mm", f"à {ville_max_precip}")
    
    # Proba précipitations max
    max_precip_prob = daily_data["Probabilité de Précipitations (%)"].max()
    if pd.notna(max_precip_prob):
        ville_max_precip_prob = daily_data.loc[daily_data["Probabilité de Précipitations (%)"].idxmax(), "Ville"]
    else:
        max_precip_prob = 0
        ville_max_precip_prob = "Non disponible"
    col2.metric("Probabilité précipitations", f"{max_precip_prob:.0f}%", f"à {ville_max_precip_prob}")
    
    # Durée du jour
    avg_daylight = daily_data["Durée du jour (secondes)"].mean() / 3600
    col3.metric("Durée moyenne du jour", f"{avg_daylight:.1f} heures", "")
    
    # Heures d'ensoleillement
    if not daily_data.empty and "Lever du soleil" in daily_data.columns and "Coucher du soleil" in daily_data.columns:
        if pd.notna(daily_data["Lever du soleil"].iloc[0]) and pd.notna(daily_data["Coucher du soleil"].iloc[0]):
            sunrise = datetime.strptime(daily_data["Lever du soleil"].iloc[0], "%Y-%m-%dT%H:%M").strftime("%H:%M")
            sunset = datetime.strptime(daily_data["Coucher du soleil"].iloc[0], "%Y-%m-%dT%H:%M").strftime("%H:%M")
            col4.metric("Lever/Coucher du soleil", f"{sunrise} - {sunset}", "")
        else:
            col4.metric("Lever/Coucher du soleil", "Non disponible", "")
    else:
        col4.metric("Lever/Coucher du soleil", "Non disponible", "")
        
    # ===================== PRÉVISIONS GÉNÉRALES =====================
    st.header("🌐 Prévisions générales du département")
    
    # dataframe pour les moyennes par date
    departement_forecast = df_long_term.groupby("Date").agg({
        "Température Max (°C)": "mean",
        "Température Min (°C)": "mean",
        "Précipitations (mm)": "mean",
        "Probabilité de Précipitations (%)": "mean",
        "Vitesse du vent Max (km/h)": "mean",
        "Rafales Max (km/h)": "mean",
        "Indice UV Max": "mean"
    }).reset_index()

    # Conversion en numérique (sécurité)
    for col in departement_forecast.columns:
        if col != "Date":
            departement_forecast[col] = pd.to_numeric(departement_forecast[col], errors='coerce')
        
    # Arrondir les valeurs
    for col in departement_forecast.columns:
        if col != "Date":
            departement_forecast[col] = departement_forecast[col].round(1)
    
    # Création onglets
    gen_tab1, gen_tab2, gen_tab3, gen_tab4 = st.tabs(["Vue d'ensemble", "Températures", "Précipitations", "Vent"])
    
    with gen_tab1:
        st.subheader("Tendances sur les 7 prochains jours")
        
        next_7_days = departement_forecast.iloc[:7]
        trend_cols = st.columns(min(7, len(next_7_days)))
        
        for i, (idx, row) in enumerate(next_7_days.iterrows()):
            if i < len(trend_cols):
                date_str = row["Date"].strftime("%d/%m")
                
                icon = "🌧️" if pd.notna(row["Précipitations (mm)"]) and row["Précipitations (mm)"] > 1 else "☀️" if pd.notna(row["Indice UV Max"]) and row["Indice UV Max"] > 5 else "⛅"
                if pd.notna(row["Rafales Max (km/h)"]) and row["Rafales Max (km/h)"] > 50:
                    icon = "💨"
                
                precip_value = row['Précipitations (mm)'] if pd.notna(row['Précipitations (mm)']) else 0
                precip_prob = row['Probabilité de Précipitations (%)'] if pd.notna(row['Probabilité de Précipitations (%)']) else 0
                
                trend_cols[i].metric(
                    f"{date_str} {icon}",
                    f"{row['Température Max (°C)']}°C / {row['Température Min (°C)']}°C",
                    f"{precip_value}mm ({precip_prob:.0f}%)"
                )
        
        # Heatmap
        st.subheader("Aperçu général des 16 prochains jours")
        
        heatmap_data = departement_forecast.copy()
        heatmap_data["Date_str"] = heatmap_data["Date"].dt.strftime("%d/%m")
        heatmap_data["Température moyenne"] = (heatmap_data["Température Max (°C)"] + heatmap_data["Température Min (°C)"]) / 2
        
        fig_heatmap = px.imshow(
            heatmap_data[["Température moyenne", "Précipitations (mm)", "Rafales Max (km/h)", "Indice UV Max"]].T,
            x=heatmap_data["Date_str"],
            y=["Température", "Précipitations", "Vent", "UV"],
            color_continuous_scale="RdYlBu_r",
            aspect="auto",
            title="Conditions météorologiques générales (intensité relative)"
        )
        
        fig_heatmap.update_layout(height=250)
        st.plotly_chart(fig_heatmap, use_container_width=True)
        
    with gen_tab2:
        # Graphique des températures moy
        fig_dept_temp = go.Figure()
        
        fig_dept_temp.add_trace(go.Scatter(
            x=departement_forecast["Date"],
            y=departement_forecast["Température Max (°C)"],
            mode='lines+markers',
            name='Température Max moyenne',
            line=dict(color='red')
        ))
        
        fig_dept_temp.add_trace(go.Scatter(
            x=departement_forecast["Date"],
            y=departement_forecast["Température Min (°C)"],
            mode='lines+markers',
            name='Température Min moyenne',
            line=dict(color='blue')
        ))
        
        # Zone de confort thermique
        fig_dept_temp.add_trace(go.Scatter(
            x=departement_forecast["Date"],
            y=[25] * len(departement_forecast),
            mode='lines',
            line=dict(color="rgba(0,255,0,0.2)", width=0),
            showlegend=False
        ))
        
        fig_dept_temp.add_trace(go.Scatter(
            x=departement_forecast["Date"],
            y=[18] * len(departement_forecast),
            mode='lines',
            line=dict(color="rgba(0,255,0,0.2)", width=0),
            fill='tonexty',
            fillcolor='rgba(0,255,0,0.1)',
            name='Zone de confort'
        ))
        
        fig_dept_temp.update_layout(
            title="Prévisions de températures moyennes - Deux-Sèvres",
            xaxis_title="Date",
            yaxis_title="Température (°C)",
            hovermode="x unified"
        )
        
        st.plotly_chart(fig_dept_temp, use_container_width=True)
        
        # Histo écarts de température
        ecart_temp = departement_forecast["Température Max (°C)"] - departement_forecast["Température Min (°C)"]
        
        fig_ecart = px.bar(
            x=departement_forecast["Date"],
            y=ecart_temp,
            labels={"x": "Date", "y": "Écart (°C)"},
            title="Écart journalier de température (Max - Min)"
        )
        
        st.plotly_chart(fig_ecart, use_container_width=True)
        
    with gen_tab3:
        # précipitations
        fig_dept_precip = go.Figure()
        
        fig_dept_precip.add_trace(go.Bar(
            x=departement_forecast["Date"],
            y=departement_forecast["Précipitations (mm)"],
            name='Précipitations moyennes',
            marker_color='royalblue'
        ))
        
        fig_dept_precip.add_trace(go.Scatter(
            x=departement_forecast["Date"],
            y=departement_forecast["Probabilité de Précipitations (%)"],
            mode='lines+markers',
            name='Probabilité moyenne',
            marker=dict(color='darkblue'),
            yaxis="y2"
        ))
        
        precipitations_cumulees = departement_forecast["Précipitations (mm)"].cumsum()
        
        fig_dept_precip.add_trace(go.Scatter(
            x=departement_forecast["Date"],
            y=precipitations_cumulees,
            mode='lines',
            name='Cumul précipitations',
            line=dict(color='purple', dash='dot'),
            yaxis="y3"
        ))
        
        fig_dept_precip.update_layout(
            title="Prévisions de précipitations moyennes - Deux-Sèvres",
            xaxis_title="Date",
            yaxis_title="Précipitations (mm)",
            yaxis2=dict(
                title="Probabilité (%)",
                overlaying="y",
                side="right",
                range=[0, 100]
            ),
            yaxis3=dict(
                title="Cumul (mm)",
                overlaying="y",
                side="right",
                anchor="free",
                position=1.0,
                range=[0, max(precipitations_cumulees) * 1.1]
            ),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(r=50),
            hovermode="x unified"
        )
        
        st.plotly_chart(fig_dept_precip, use_container_width=True)
        
        # Catégorisation des jours
        precip_categories = pd.cut(
            departement_forecast["Précipitations (mm)"],
            bins=[-0.1, 0.2, 1, 5, 10, 100],
            labels=["Sec", "Bruine", "Léger", "Modéré", "Fort"]
        )
        
        category_counts = precip_categories.value_counts().sort_index()
        
        fig_precip_pie = px.pie(
            values=category_counts.values,
            names=category_counts.index,
            title="Répartition des jours selon les précipitations",
            color_discrete_sequence=px.colors.sequential.Blues[1:]
        )
        
        st.plotly_chart(fig_precip_pie, use_container_width=True)
        
    with gen_tab4:
        # Graphique vent
        fig_dept_wind = go.Figure()
        
        fig_dept_wind.add_trace(go.Bar(
            x=departement_forecast["Date"],
            y=departement_forecast["Vitesse du vent Max (km/h)"],
            name='Vitesse du vent Max moyenne',
            marker_color='green'
        ))
        
        fig_dept_wind.add_trace(go.Scatter(
            x=departement_forecast["Date"],
            y=departement_forecast["Rafales Max (km/h)"],
            mode='lines+markers',
            name='Rafales Max moyennes',
            marker=dict(color='darkgreen')
        ))
        
        # Seuils vent
        wind_thresholds = {
            "Vent fort": 50,
            "Vent très fort": 75
        }
        
        for label, val in wind_thresholds.items():
            fig_dept_wind.add_shape(
                type="line",
                x0=departement_forecast["Date"].min(),
                y0=val,
                x1=departement_forecast["Date"].max(),
                y1=val,
                line=dict(color="red", width=1, dash="dash"),
            )
            
            fig_dept_wind.add_annotation(
                x=departement_forecast["Date"].max(),
                y=val,
                text=label,
                showarrow=False,
                yshift=5,
                xshift=-5,
                font=dict(color="red")
            )
        
        fig_dept_wind.update_layout(
            title="Prévisions de vent moyen - Deux-Sèvres",
            xaxis_title="Date",
            yaxis_title="Vitesse (km/h)",
            hovermode="x unified"
        )
        
        st.plotly_chart(fig_dept_wind, use_container_width=True)
    
    # ===================== CARTES =====================
    st.header("🗺️ Cartographie")
    
    map_param_options = {
        "Température Max (°C)": "Température Max (°C)",
        "Température Min (°C)": "Température Min (°C)",
        "Précipitations (mm)": "Précipitations (mm)",
        "Probabilité de Précipitations (%)": "Probabilité de Précipitations (%)",
        "Rafales de vent (km/h)": "Rafales Max (km/h)",
        "Indice UV": "Indice UV Max"
    }
    
    map_param = st.selectbox("Paramètre à visualiser", list(map_param_options.keys()))
    param_column = map_param_options[map_param]
    
    fig = px.scatter_mapbox(daily_data, 
                          lat="Latitude", 
                          lon="Longitude", 
                          color=param_column,
                          size=param_column,
                          hover_name="Ville", 
                          hover_data=[param_column],
                          color_continuous_scale=px.colors.sequential.Plasma,
                          size_max=15,
                          zoom=8,
                          title=f"{map_param} par commune - {selected_date}")
    
    fig.update_layout(mapbox_style="carto-positron", height=600)
    st.plotly_chart(fig, use_container_width=True)
    
    # ===================== ÉVOLUTION HORAIRE =====================
    st.header("⏱️ Évolution horaire")

    date_range = st.slider(
        "Sélectionner la plage de dates pour l'évolution horaire", 
        0, 
        min(len(available_dates)-1, 6),
        (0, min(len(available_dates)-1, 2))
    )

    selected_date_range = available_dates[date_range[0]:date_range[1]+1]
    st.write(f"Période sélectionnée: Du **{selected_date_range[0]}** au **{selected_date_range[-1]}**")

    hourly_data_range = df_hourly[df_hourly["Date et Heure"].dt.date.isin(selected_date_range)]

    available_cities = sorted(hourly_data_range["Ville"].unique())
    city_options = ["Toutes les communes"] + available_cities
    selected_cities = st.multiselect("Sélectionner des communes", city_options, default=[city_options[0]])

    if "Toutes les communes" in selected_cities:
        filtered_hourly = hourly_data_range
        if len(selected_cities) > 1:
            st.info("L'option 'Toutes les communes' est sélectionnée. Les autres sélections sont ignorées.")
    else:
        filtered_hourly = hourly_data_range[hourly_data_range["Ville"].isin(selected_cities)]

    if not filtered_hourly.empty:
        fig_temp = px.line(filtered_hourly, 
                        x="Date et Heure", 
                        y="Température (°C)", 
                        color="Ville",
                        title=f"Évolution des températures - Du {selected_date_range[0]} au {selected_date_range[-1]}")
        
        for date in selected_date_range[1:]:
            midnight = pd.Timestamp(date).replace(hour=0, minute=0)
            fig_temp.add_vline(x=midnight, line_width=1, line_dash="dash", line_color="gray")
        
        st.plotly_chart(fig_temp, use_container_width=True)
        
        col1, col2 = st.columns(2)
        
        fig_hum = px.line(filtered_hourly, 
                        x="Date et Heure", 
                        y="Humidité (%)", 
                        color="Ville",
                        title=f"Évolution de l'humidité")
        
        for date in selected_date_range[1:]:
            midnight = pd.Timestamp(date).replace(hour=0, minute=0)
            fig_hum.add_vline(x=midnight, line_width=1, line_dash="dash", line_color="gray")
        
        col1.plotly_chart(fig_hum, use_container_width=True)
        
        fig_wind = px.line(filtered_hourly, 
                        x="Date et Heure", 
                        y="Vitesse du vent (km/h)", 
                        color="Ville",
                        title=f"Évolution du vent")
        
        for date in selected_date_range[1:]:
            midnight = pd.Timestamp(date).replace(hour=0, minute=0)
            fig_wind.add_vline(x=midnight, line_width=1, line_dash="dash", line_color="gray")
        
        col2.plotly_chart(fig_wind, use_container_width=True)
        
        col1, col2 = st.columns(2)
        
        if len(selected_cities) == 1 and selected_cities[0] != "Toutes les communes":
            city_data = filtered_hourly[filtered_hourly["Ville"] == selected_cities[0]]
            
            # Rose des vents
            if "Direction du vent (°)" in city_data.columns and not city_data["Direction du vent (°)"].isna().all():
                wind_dir_bins = [0, 22.5, 45, 67.5, 90, 112.5, 135, 157.5, 180, 202.5, 225, 247.5, 270, 292.5, 315, 337.5, 360]
                wind_dir_labels = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW", "N"]
                
                city_data_copy = city_data.copy()
                city_data_copy["Direction"] = pd.cut(city_data_copy["Direction du vent (°)"], bins=wind_dir_bins, labels=wind_dir_labels[:-1])
                dir_counts = city_data_copy.groupby("Direction")["Vitesse du vent (km/h)"].mean().reset_index()
                
                fig_windrose = px.bar_polar(dir_counts, 
                                        r="Vitesse du vent (km/h)", 
                                        theta="Direction",
                                        title=f"Rose des vents - {selected_cities[0]}")
                
                col1.plotly_chart(fig_windrose, use_container_width=True)
            else:
                col1.warning("Données de direction du vent non disponibles pour cette ville.")
            
            # Couverture nuageuse
            if "Couverture nuageuse (%)" in city_data.columns and not city_data["Couverture nuageuse (%)"].isna().all():
                fig_clouds = go.Figure()
                fig_clouds.add_trace(go.Scatter(
                    x=city_data["Date et Heure"],
                    y=city_data["Couverture nuageuse (%)"],
                    mode='lines+markers',
                    name='Couverture nuageuse',
                    fill='tozeroy'
                ))
                
                for date in selected_date_range[1:]:
                    midnight = pd.Timestamp(date).replace(hour=0, minute=0)
                    fig_clouds.add_vline(x=midnight, line_width=1, line_dash="dash", line_color="gray")
                
                fig_clouds.update_layout(title=f"Couverture nuageuse - {selected_cities[0]}")
                col2.plotly_chart(fig_clouds, use_container_width=True)
            else:
                col2.warning("Données de couverture nuageuse non disponibles pour cette ville.")
        elif "Toutes les communes" in selected_cities:
            col1.subheader("Statistiques de vent moyennes")
            
            hourly_avg = filtered_hourly.groupby("Date et Heure")["Vitesse du vent (km/h)"].agg(["mean", "min", "max"]).reset_index()
            
            fig_wind_stats = go.Figure()
            fig_wind_stats.add_trace(go.Scatter(
                x=hourly_avg["Date et Heure"],
                y=hourly_avg["mean"],
                mode='lines',
                name='Moyenne',
                line=dict(color='green')
            ))
            
            fig_wind_stats.add_trace(go.Scatter(
                x=hourly_avg["Date et Heure"],
                y=hourly_avg["max"],
                mode='lines',
                name='Maximum',
                line=dict(width=0),
                showlegend=False
            ))
            
            fig_wind_stats.add_trace(go.Scatter(
                x=hourly_avg["Date et Heure"],
                y=hourly_avg["min"],
                mode='lines',
                name='Minimum',
                fill='tonexty',
                fillcolor='rgba(0,128,0,0.2)',
                line=dict(width=0),
                showlegend=False
            ))
            
            for date in selected_date_range[1:]:
                midnight = pd.Timestamp(date).replace(hour=0, minute=0)
                fig_wind_stats.add_vline(x=midnight, line_width=1, line_dash="dash", line_color="gray")
            
            col1.plotly_chart(fig_wind_stats, use_container_width=True)
            
            if "Couverture nuageuse (%)" in filtered_hourly.columns and not filtered_hourly["Couverture nuageuse (%)"].isna().all():
                col2.subheader("Couverture nuageuse moyenne")
                
                cloud_avg = filtered_hourly.groupby("Date et Heure")["Couverture nuageuse (%)"].mean().reset_index()
                
                fig_cloud_avg = go.Figure()
                fig_cloud_avg.add_trace(go.Scatter(
                    x=cloud_avg["Date et Heure"],
                    y=cloud_avg["Couverture nuageuse (%)"],
                    mode='lines',
                    fill='tozeroy',
                    name='Couverture nuageuse moyenne'
                ))
                
                for date in selected_date_range[1:]:
                    midnight = pd.Timestamp(date).replace(hour=0, minute=0)
                    fig_cloud_avg.add_vline(x=midnight, line_width=1, line_dash="dash", line_color="gray")
                
                col2.plotly_chart(fig_cloud_avg, use_container_width=True)
            else:
                col2.warning("Données de couverture nuageuse non disponibles.")
    else:
        st.warning("Aucune donnée disponible pour la sélection actuelle.")

    # ===================== PRÉVISIONS À 16 JOURS =====================
    st.header("📅 Prévisions sur 16 jours")

    available_cities_long = sorted(df_long_term["Ville"].unique())
    city_options_long = ["Toutes les communes"] + available_cities_long
    city_forecast = st.selectbox("Commune pour les prévisions", city_options_long)

    if city_forecast == "Toutes les communes":
        city_long_term = departement_forecast
        title_suffix = "Moyenne départementale"
    else:
        city_long_term = df_long_term[df_long_term["Ville"] == city_forecast]
        title_suffix = city_forecast

    tab1, tab2, tab3 = st.tabs(["Températures", "Précipitations", "Vent"])

    with tab1:
        fig_forecast_temp = go.Figure()
        
        fig_forecast_temp.add_trace(go.Scatter(
            x=city_long_term["Date"],
            y=city_long_term["Température Max (°C)"],
            mode='lines+markers',
            name='Température Max',
            line=dict(color='red')
        ))
        
        fig_forecast_temp.add_trace(go.Scatter(
            x=city_long_term["Date"],
            y=city_long_term["Température Min (°C)"],
            mode='lines+markers',
            name='Température Min',
            line=dict(color='blue')
        ))
        
        fig_forecast_temp.update_layout(
            title=f"Prévisions de températures - {title_suffix}",
            xaxis_title="Date",
            yaxis_title="Température (°C)",
            hovermode="x unified"
        )
        
        st.plotly_chart(fig_forecast_temp, use_container_width=True)

    with tab2:
        fig_forecast_precip = go.Figure()
        
        fig_forecast_precip.add_trace(go.Bar(
            x=city_long_term["Date"],
            y=city_long_term["Précipitations (mm)"],
            name='Précipitations',
            marker_color='royalblue'
        ))
        
        fig_forecast_precip.add_trace(go.Scatter(
            x=city_long_term["Date"],
            y=city_long_term["Probabilité de Précipitations (%)"],
            mode='lines+markers',
            name='Probabilité de précipitations',
            marker=dict(color='darkblue'),
            yaxis="y2"
        ))
        
        fig_forecast_precip.update_layout(
            title=f"Prévisions de précipitations - {title_suffix}",
            xaxis_title="Date",
            yaxis_title="Précipitations (mm)",
            yaxis2=dict(
                title="Probabilité (%)",
                overlaying="y",
                side="right",
                range=[0, 100]
            ),
            hovermode="x unified"
        )
        
        st.plotly_chart(fig_forecast_precip, use_container_width=True)

    with tab3:
        fig_forecast_wind = go.Figure()
        
        fig_forecast_wind.add_trace(go.Bar(
            x=city_long_term["Date"],
            y=city_long_term["Vitesse du vent Max (km/h)"],
            name='Vitesse du vent Max',
            marker_color='green'
        ))
        
        fig_forecast_wind.add_trace(go.Scatter(
            x=city_long_term["Date"],
            y=city_long_term["Rafales Max (km/h)"],
            mode='lines+markers',
            name='Rafales Max',
            marker=dict(color='darkgreen')
        ))
        
        fig_forecast_wind.update_layout(
            title=f"Prévisions de vent - {title_suffix}",
            xaxis_title="Date",
            yaxis_title="Vitesse (km/h)",
            hovermode="x unified"
        )
        
        st.plotly_chart(fig_forecast_wind, use_container_width=True)
            
else:

    st.error("Impossible de charger les données depuis l'API Open-Meteo.")

