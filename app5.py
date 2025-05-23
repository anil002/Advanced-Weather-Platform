import streamlit as st
import requests
import aiohttp
import asyncio
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import folium
from streamlit_folium import st_folium
from streamlit_option_menu import option_menu
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from prophet import Prophet
import os
import json
import re

# API Configuration
API_KEY = "0bd1fea75e7146198e2182136252205"
BASE_URL = "http://api.weatherapi.com/v1"

# Translation Dictionary (Updated to remove PIN code references)
TRANSLATIONS = {
    "English": {
        "title": "Advanced Weather Platform",
        "search_location": "Search Location (City)",
        "search_button": "Search",
        "forecast_days": "Forecast Days (1-14)",
        "historical_start": "Historical Start Date",
        "historical_end": "Historical End Date",
        "sector": "Sector",
        "dashboard": "Dashboard",
        "current": "Current Weather",
        "forecast": "Weather Forecast",
        "historical": "Historical Weather",
        "astronomy": "Astronomy",
        "alerts": "Weather Alerts",
        "map": "Interactive Map",
        "dss": "Decision Support System",
        "recommendations": "Recommendations",
        "download_report": "Download DSS Report",
        "no_alerts": "No active weather alerts for {location}.",
        "gdd": "Growing Degree Days",
        "avg_temp": "Average Temperature",
        "max_wind": "Max Wind Speed",
        "rate_limit_error": "API rate limit exceeded. Please try again later.",
        "refresh_data": "Refresh Data",
        "notification_log": "Notification Log",
        "clear_search": "Clear Search",
        "search_error": "Error searching for {query}. Please try a different city.",
        "search_loading": "Searching for {query}...",
        "search_history": "Recent Searches",
        "search_placeholder": "Enter city name",
    },
    "Hindi": {
        "title": "उन्नत मौसम मंच",
        "search_location": "स्थान खोजें (शहर)",
        "search_button": "खोजें",
        "forecast_days": "पूर्वानुमान दिन (1-14)",
        "historical_start": "ऐतिहासिक प्रारंभ तिथि",
        "historical_end": "ऐतिहासिक समाप्ति तिथि",
        "sector": "क्षेत्र",
        "dashboard": "डैशबोर्ड",
        "current": "वर्तमान मौसम",
        "forecast": "मौसम पूर्वानुमान",
        "historical": "ऐतिहासिक मौसम",
        "astronomy": "खगोल विज्ञान",
        "alerts": "मौसम चेतावनियाँ",
        "map": "इंटरैक्टिव नक्शा",
        "dss": "निर्णय समर्थन प्रणाली",
        "recommendations": "अनुशंसाएँ",
        "download_report": "DSS रिपोर्ट डाउनलोड करें",
        "no_alerts": "{location} के लिए कोई सक्रिय मौसम चेतावनी नहीं।",
        "gdd": "विकास डिग्री दिन",
        "avg_temp": "औसत तापमान",
        "max_wind": "अधिकतम हवा की गति",
        "rate_limit_error": "API दर सीमा पार हो गई। कृपया बाद में पुनः प्रयास करें।",
        "refresh_data": "डेटा ताज़ा करें",
        "notification_log": "अधिसूचना लॉग",
        "clear_search": "खोज साफ़ करें",
        "search_error": "{query} के लिए खोज में त्रुटि। कृपया एक अलग शहर आज़माएँ।",
        "search_loading": "{query} के लिए खोज की जा रही है...",
        "search_history": "हाल की खोजें",
        "search_placeholder": "शहर का नाम दर्ज करें",
    },
    "Spanish": {
        "title": "Plataforma Meteorológica Avanzada",
        "search_location": "Buscar Ubicación (Ciudad)",
        "search_button": "Buscar",
        "forecast_days": "Días de Pronóstico (1-14)",
        "historical_start": "Fecha de Inicio Histórica",
        "historical_end": "Fecha de Fin Histórica",
        "sector": "Sector",
        "dashboard": "Tablero",
        "current": "Clima Actual",
        "forecast": "Pronóstico del Clima",
        "historical": "Clima Histórico",
        "astronomy": "Astronomía",
        "alerts": "Alertas Meteorológicas",
        "map": "Mapa Interactivo",
        "dss": "Sistema de Soporte de Decisiones",
        "recommendations": "Recomendaciones",
        "download_report": "Descargar Informe DSS",
        "no_alerts": "No hay alertas meteorológicas activas para {location}.",
        "gdd": "Días de Grado de Crecimiento",
        "avg_temp": "Temperatura Promedio",
        "max_wind": "Velocidad Máxima del Viento",
        "rate_limit_error": "Límite de tasa de API excedido. Intenta de nuevo más tarde.",
        "refresh_data": "Actualizar Datos",
        "notification_log": "Registro de Notificaciones",
        "clear_search": "Limpiar Búsqueda",
        "search_error": "Error al buscar {query}. Prueba con otra ciudad.",
        "search_loading": "Buscando {query}...",
        "search_history": "Búsquedas Recientes",
        "search_placeholder": "Ingrese nombre de ciudad",
    },
    "French": {
        "title": "Plateforme Météorologique Avancée",
        "search_location": "Rechercher un lieu (Ville)",
        "search_button": "Rechercher",
        "forecast_days": "Jours de prévision (1-14)",
        "historical_start": "Date de début historique",
        "historical_end": "Date de fin historique",
        "sector": "Secteur",
        "dashboard": "Tableau de bord",
        "current": "Météo actuelle",
        "forecast": "Prévisions météorologiques",
        "historical": "Météo historique",
        "astronomy": "Astronomie",
        "alerts": "Alertes météorologiques",
        "map": "Carte interactive",
        "dss": "Système de support à la décision",
        "recommendations": "Recommandations",
        "download_report": "Télécharger le rapport DSS",
        "no_alerts": "Aucune alerte météorologique active pour {location}.",
        "gdd": "Jours de degré de croissance",
        "avg_temp": "Température moyenne",
        "max_wind": "Vitesse maximale du vent",
        "rate_limit_error": "Limite de taux d'API dépassée. Réessayez plus tard.",
        "refresh_data": "Actualiser les données",
        "notification_log": "Journal des notifications",
        "clear_search": "Effacer la recherche",
        "search_error": "Erreur lors de la recherche de {query}. Essayez une autre ville.",
        "search_loading": "Recherche de {query}...",
        "search_history": "Recherches récentes",
        "search_placeholder": "Entrez le nom de la ville",
    }
}

# Async API Calls
async def fetch_weather_data_async(endpoint, params, session, retries=3):
    params["key"] = API_KEY
    for attempt in range(retries):
        try:
            async with session.get(f"{BASE_URL}/{endpoint}.json", params=params) as response:
                if response.status == 429:
                    st.error(TRANSLATIONS[language]["rate_limit_error"])
                    return None
                response.raise_for_status()
                return await response.json()
        except Exception as e:
            if attempt == retries - 1:
                st.error(f"Error fetching {endpoint} data: {str(e)}")
                return None
            await asyncio.sleep(2 ** attempt)  # Exponential backoff

async def fetch_location_data(location, endpoint, params_template, session):
    params = {**params_template, "q": location}
    return await fetch_weather_data_async(endpoint, params, session)

@st.cache_data(ttl=60)
def fetch_weather_data_sync(_location, endpoint, params):
    if not _location:
        return None
    async def fetch_single():
        async with aiohttp.ClientSession() as session:
            return await fetch_location_data(_location, endpoint, params, session)
    return asyncio.run(fetch_single())

# Location Autocomplete (Updated to remove PIN code handling)
@st.cache_data(ttl=60)
def fetch_locations(_query):
    if not _query or len(_query.strip()) < 2:
        st.warning(TRANSLATIONS[language]["search_error"].format(query=_query))
        st.session_state.notification_log.append(f"Query too short: {_query}")
        return "New Delhi, India"
    
    query = _query.strip()
    # Validate input for city names (alphanumeric, spaces, commas, hyphens)
    if not re.match(r'^[a-zA-Z\s,-]+$', query):
        st.error(TRANSLATIONS[language]["search_error"].format(query=_query))
        st.session_state.notification_log.append(f"Invalid input format: {_query}")
        return "New Delhi, India"
    
    try:
        data = fetch_weather_data_sync(query, "search", {})
        if data and isinstance(data, list) and data:
            location = f"{data[0]['name']}, {data[0]['region']}, {data[0]['country']}"
            st.session_state.notification_log.append(f"Fetched location: {location} for query: {query}")
            return location
        st.error(TRANSLATIONS[language]["search_error"].format(query=_query))
        st.session_state.notification_log.append(f"No results for query: {_query}")
        return "New Delhi, India"
    except Exception as e:
        st.error(TRANSLATIONS[language]["search_error"].format(query=_query))
        st.session_state.notification_log.append(f"Location search failed for {_query}: {str(e)}")
        return "New Delhi, India"

# Advanced Analytics
def calculate_gdd(temp_df, base_temp=10):
    return ((temp_df['Temperature (°C)'] + temp_df['Temperature (°C)'].shift(1)).fillna(temp_df['Temperature (°C)']) / 2 - base_temp).clip(lower=0).sum()

def calculate_heat_index(temp_c, rh):
    temp_f = temp_c * 9/5 + 32
    hi = (-42.379 + 2.04901523*temp_f + 10.14333127*rh - 0.22475541*temp_f*rh - 0.00683783*temp_f*temp_f
          - 0.05481717*rh*rh + 0.00122874*temp_f*temp_f*rh + 0.00085282*temp_f*rh*rh - 0.00000199*temp_f*temp_f*rh*rh)
    return (hi - 32) * 5/9 if hi > 80 else temp_c

def calculate_wind_chill(temp_c, wind_kph):
    wind_mph = wind_kph * 0.621371
    temp_f = temp_c * 9/5 + 32
    if temp_f <= 50 and wind_mph > 3:
        wc = 35.74 + 0.6215*temp_f - 35.75*(wind_mph**0.16) + 0.4275*temp_f*(wind_mph**0.16)
        return (wc - 32) * 5/9
    return temp_c

def calculate_wbgt(temp_c, rh):
    return 0.7 * (temp_c + 0.98 * (rh / 100) * (6.11 * 10 ** (7.5 * temp_c / (237.7 + temp_c)))) + 0.3 * temp_c

@st.cache_resource
def train_precip_model(X, y):
    model = RandomForestClassifier(n_estimators=100)
    model.fit(X, y)
    return model

def predict_precip_prob(forecast_df):
    X = forecast_df[['Temperature (°C)', 'Humidity (%)', 'Cloud (%)', 'Wind (kph)']].fillna(0)
    y = (forecast_df['Precipitation (mm)'] > 0).astype(int)
    if len(X) > 1 and y.sum() > 0:
        model = train_precip_model(X, y)
        return model.predict_proba(X)[:, 1]
    return np.zeros(len(X))

@st.cache_resource
def train_prophet_model(df):
    model = Prophet(daily_seasonality=True)
    model.fit(df)
    return model

def forecast_temperature(historical_df):
    df = historical_df[['Date', 'Temperature (°C)']].rename(columns={'Date': 'ds', 'Temperature (°C)': 'y'})
    if len(df) < 24:
        st.warning("Insufficient data for temperature forecast.")
        return pd.DataFrame()
    model = train_prophet_model(df)
    future = model.make_future_dataframe(periods=24*7, freq='H')
    forecast = model.predict(future)
    return forecast[['ds', 'yhat']].rename(columns={'ds': 'Date', 'yhat': 'Predicted Temp (°C)'})

# Streamlit App Configuration
st.set_page_config(page_title="Advanced Weather Platform", layout="wide", initial_sidebar_state="expanded")
st.markdown("""
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
    <style>
        .main {background-color: #f0f2f6;}
        .metric-card {background-color: #ffffff; padding: 15px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 15px;}
        .tooltip:hover .tooltip-text {visibility: visible; opacity: 1;}
        .tooltip-text {visibility: hidden; opacity: 0; transition: opacity 0.3s; background-color: #333; color: #fff; padding: 5px; border-radius: 4px; position: absolute; z-index: 1;}
        .sidebar .sidebar-content {background-color: #e6f3ff;}
        .notification {background-color: #ffcc00; padding: 10px; border-radius: 5px; margin-bottom: 10px;}
        .search-bar {border: 1px solid #ccc; border-radius: 5px; padding: 8px;}
    </style>
""", unsafe_allow_html=True)

# Initialize Session State
if "current_location" not in st.session_state:
    st.session_state.current_location = "New Delhi, India"
if "notification_log" not in st.session_state:
    st.session_state.notification_log = []
if "location_query" not in st.session_state:
    st.session_state.location_query = ""
if "search_history" not in st.session_state:
    st.session_state.search_history = []

# Sidebar
st.sidebar.header("Platform Settings")
theme = st.sidebar.selectbox("Theme", ["Light", "Dark"], key="theme")
if theme == "Dark":
    st.markdown("<style>body {background-color: #1a1a1a; color: #ffffff;}</style>", unsafe_allow_html=True)

language = st.sidebar.selectbox("Language", ["English", "Hindi", "Spanish", "French"], key="language")

# Location Search
st.sidebar.subheader(TRANSLATIONS[language]["search_location"])
location_query = st.sidebar.text_input("", 
                                     value=st.session_state.location_query, 
                                     key="location_query_input", 
                                     placeholder=TRANSLATIONS[language]["search_placeholder"])
col1, col2 = st.sidebar.columns(2)
with col1:
    if st.button(TRANSLATIONS[language]["search_button"], key="search"):
        st.cache_data.clear()
        if location_query:
            with st.spinner(TRANSLATIONS[language]["search_loading"].format(query=location_query)):
                new_location = fetch_locations(location_query)
                st.session_state.current_location = new_location
                st.session_state.location_query = ""
                if location_query not in st.session_state.search_history:
                    st.session_state.search_history.append(location_query)
                    st.session_state.search_history = st.session_state.search_history[-5:]
                st.session_state.notification_log.append(f"Search successful for {location_query} at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                st.rerun()
with col2:
    if st.button(TRANSLATIONS[language]["clear_search"], key="clear_search"):
        st.session_state.location_query = ""
        st.session_state.current_location = "New Delhi, India"
        st.rerun()

# Display Current Location
st.sidebar.markdown(f"**Current Location:** {st.session_state.current_location}")

# Search History
if st.session_state.search_history:
    with st.sidebar.expander(TRANSLATIONS[language]["search_history"], expanded=False):
        for query in st.session_state.search_history[::-1]:
            if st.button(query, key=f"history_{query}"):
                st.session_state.location_query = query
                with st.spinner(TRANSLATIONS[language]["search_loading"].format(query=query)):
                    new_location = fetch_locations(query)
                    st.session_state.current_location = new_location
                    st.session_state.location_query = ""
                    st.session_state.notification_log.append(f"History search successful for {query} at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                    st.rerun()

days_forecast = st.sidebar.slider(TRANSLATIONS[language]["forecast_days"], 1, 14, 7, key="forecast_days")
historical_start = st.sidebar.date_input(TRANSLATIONS[language]["historical_start"], value=datetime.today() - timedelta(days=7), key="historical_start")
historical_end = st.sidebar.date_input(TRANSLATIONS[language]["historical_end"], value=datetime.today() - timedelta(days=1), key="historical_end")
if historical_start > historical_end:
    st.sidebar.error("Start date must be before end date.")
sector = st.sidebar.selectbox(TRANSLATIONS[language]["sector"], ["Agriculture", "Transportation", "Construction", "Energy", "Tourism", "Emergency Management", "Health"], key="sector")

# Sector Thresholds
st.sidebar.subheader("Customize Thresholds")
thresholds = {
    "Agriculture": {
        "temp_high": st.sidebar.slider("High Temp (°C)", 15, 40, 20, key="agriculture_temp_high"),
        "humidity_high": st.sidebar.slider("High Humidity (%)", 50, 90, 70, key="agriculture_humidity_high")
    },
    "Transportation": {
        "wind_high": st.sidebar.slider("High Wind (kph)", 40, 100, 60, key="transportation_wind_high"),
        "vis_low": st.sidebar.slider("Low Visibility (km)", 1, 5, 2, key="transportation_vis_low")
    },
    "Construction": {
        "wbgt_high": st.sidebar.slider("High WBGT (°C)", 25, 35, 30, key="construction_wbgt_high"),
        "uv_high": st.sidebar.slider("High UV Index", 6, 10, 8, key="construction_uv_high")
    },
    "Energy": {
        "cloud_low": st.sidebar.slider("Low Cloud (%)", 10, 50, 30, key="energy_cloud_low"),
        "wind_high": st.sidebar.slider("High Wind (kph)", 15, 40, 20, key="energy_wind_high")
    },
    "Tourism": {
        "temp_high": st.sidebar.slider("High Temp (°C)", 20, 35, 30, key="tourism_temp_high"),
        "precip_low": st.sidebar.slider("Low Precip Prob (%)", 10, 50, 20, key="tourism_precip_low")
    },
    "Emergency Management": {
        "precip_high": st.sidebar.slider("High Precip (mm)", 20, 100, 50, key="emergency_precip_high"),
        "wind_high": st.sidebar.slider("High Wind (kph)", 60, 120, 80, key="emergency_wind_high")
    },
    "Health": {
        "wbgt_high": st.sidebar.slider("High WBGT (°C)", 25, 35, 30, key="health_wbgt_high"),
        "pm25_high": st.sidebar.slider("High PM2.5", 25, 100, 35, key="health_pm25_high")
    }
}

# Real-Time Refresh
if st.sidebar.button(TRANSLATIONS[language]["refresh_data"], key="refresh_data"):
    st.cache_data.clear()
    st.session_state.notification_log.append(f"Data refreshed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    st.rerun()

# Notification Log Display
if st.session_state.notification_log:
    with st.sidebar.expander(TRANSLATIONS[language]["notification_log"], expanded=False):
        for log in st.session_state.notification_log[-10:]:
            st.write(log)

# Tabs
with st.container():
    selected = option_menu(
        menu_title=None,
        options=[TRANSLATIONS[language][tab] for tab in ["dashboard", "current", "forecast", "historical", "astronomy", "alerts", "map", "dss"]],
        icons=["house", "cloud", "calendar", "history", "moon", "alert-circle", "map", "gear"],
        orientation="horizontal",
        styles={"nav-link-selected": {"background-color": "#007bff"}}
    )

# Dashboard
if selected == TRANSLATIONS[language]["dashboard"]:
    st.header(TRANSLATIONS[language]["title"])
    location = st.session_state.current_location.split(",")[0]
    st.subheader(f"Summary for {location}")
    current_data = fetch_weather_data_sync(st.session_state.current_location, "current", {"aqi": "yes"})
    if current_data:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
            st.image(f"http:{current_data['current']['condition']['icon']}", width=100)
            st.metric("Temperature", f"{current_data['current']['temp_c']} °C", help=TRANSLATIONS[language]["avg_temp"])
            st.metric("Condition", current_data['current']['condition']['text'])
            st.markdown("</div>", unsafe_allow_html=True)
        with col2:
            st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
            st.metric("Humidity", f"{current_data['current']['humidity']}%")
            st.metric("Wind", f"{current_data['current']['wind_kph']} kph", help=TRANSLATIONS[language]["max_wind"])
            st.metric("UV Index", current_data['current']['uv'])
            st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.error(f"Failed to fetch data for {location}.")

# Current Weather
if selected == TRANSLATIONS[language]["current"]:
    st.header(TRANSLATIONS[language]["current"])
    location = st.session_state.current_location.split(",")[0]
    st.subheader(f"Current Weather for {location}")
    current_data = fetch_weather_data_sync(st.session_state.current_location, "current", {"aqi": "yes"})
    if current_data:
        loc = current_data['location']
        curr = current_data['current']
        st.write(f"{loc['name']}, {loc['region']}, {loc['country']} ({loc['localtime']})")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
            st.image(f"http:{curr['condition']['icon']}", width=100)
            st.metric("Temperature", f"{curr['temp_c']} °C / {curr['temp_f']} °F", help=TRANSLATIONS[language]["avg_temp"])
            st.metric("Feels Like", f"{curr['feelslike_c']} °C")
            st.markdown("</div>", unsafe_allow_html=True)
        with col2:
            st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
            st.metric("Humidity", f"{curr['humidity']}%")
            st.metric("Wind", f"{curr['wind_kph']} kph, {curr['wind_dir']}", help=TRANSLATIONS[language]["max_wind"])
            st.metric("Visibility", f"{curr['vis_km']} km")
            st.markdown("</div>", unsafe_allow_html=True)
        with col3:
            st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
            st.metric("Pressure", f"{curr['pressure_mb']} mb")
            st.metric("UV Index", curr['uv'])
            st.metric("Air Quality (PM2.5)", curr.get('air_quality', {}).get('pm2_5', 'N/A'))
            st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.error(f"Failed to fetch data for {location}.")

# Forecast
if selected == TRANSLATIONS[language]["forecast"]:
    st.header(TRANSLATIONS[language]["forecast"])
    location = st.session_state.current_location.split(",")[0]
    st.subheader(f"Forecast for {location}")
    forecast_data = fetch_weather_data_sync(st.session_state.current_location, "forecast", {"days": days_forecast, "aqi": "yes", "alerts": "yes"})
    if forecast_data:
        forecast_df = []
        for day in forecast_data['forecast']['forecastday']:
            date = day['date']
            for hour in day['hour']:
                forecast_df.append({
                    "Location": location,
                    "Date": date,
                    "Time": hour['time'],
                    "Temperature (°C)": hour['temp_c'],
                    "Feels Like (°C)": hour['feelslike_c'],
                    "Precipitation (mm)": hour['precip_mm'],
                    "Precip Probability (%)": hour['chance_of_rain'],
                    "Wind (kph)": hour['wind_kph'],
                    "Wind Direction": hour['wind_dir'],
                    "Humidity (%)": hour['humidity'],
                    "UV Index": hour['uv'],
                    "Cloud (%)": hour['cloud'],
                    "Visibility (km)": hour['vis_km'],
                    "Dew Point (°C)": hour['dewpoint_c'],
                    "Air Quality (PM2.5)": hour.get('air_quality', {}).get('pm2_5', 0)
                })
        forecast_df = pd.DataFrame(forecast_df)
        forecast_df['Time'] = pd.to_datetime(forecast_df['Time'])
        forecast_df['Precip Prob (ML)'] = predict_precip_prob(forecast_df) * 100

        st.subheader("Daily Summary")
        daily_summary = forecast_df.groupby(['Location', 'Date']).agg({
            'Temperature (°C)': ['mean', 'max', 'min'],
            'Precipitation (mm)': 'sum',
            'Precip Probability (%)': 'max',
            'Wind (kph)': 'mean',
            'UV Index': 'max'
        }).reset_index()
        daily_summary.columns = ['Location', 'Date', 'Avg Temp (°C)', 'Max Temp (°C)', 'Min Temp (°C)', 
                                'Total Precip (mm)', 'Max Precip Prob (%)', 'Avg Wind (kph)', 'Max UV']
        st.dataframe(daily_summary)

        # Dynamic Visualization
        st.subheader("Dynamic Forecast Chart")
        metrics = st.multiselect("Select Metrics to Plot", 
                                ['Temperature (°C)', 'Precipitation (mm)', 'Wind (kph)', 'Humidity (%)', 'UV Index'], 
                                default=['Temperature (°C)', 'Precipitation (mm)'], key=f"metrics_{location}")
        fig_dynamic = go.Figure()
        for metric in metrics:
            fig_dynamic.add_trace(go.Scatter(x=forecast_df['Time'], y=forecast_df[metric], mode='lines', name=metric))
        fig_dynamic.update_layout(title=f"Forecast Trends - {location}", xaxis_title="Time", yaxis_title="Value")
        st.plotly_chart(fig_dynamic, use_container_width=True)

        # Export Chart
        st.download_button("Download Forecast Chart", fig_dynamic.to_json(), f"forecast_chart_{location}.json", "application/json")

        st.subheader("Temperature Heatmap")
        heatmap_data = forecast_df.pivot_table(values='Temperature (°C)', index=forecast_df['Time'].dt.hour, columns='Date')
        color_scale = st.selectbox("Heatmap Color Scale", ["Viridis", "Plasma", "Inferno"], key=f"heatmap_{location}")
        fig_heatmap = px.imshow(heatmap_data, title=f"Temperature Heatmap (°C) - {location}", 
                               labels={'x': 'Date', 'y': 'Hour', 'color': 'Temperature (°C)'}, color_continuous_scale=color_scale)
        st.plotly_chart(fig_heatmap, use_container_width=True)

        st.download_button(f"Download Forecast Data - {location}", forecast_df.to_csv(index=False), 
                         f"forecast_{location}.csv", "text/csv")
    else:
        st.error(f"Failed to fetch forecast data for {location}.")

# Historical Data
if selected == TRANSLATIONS[language]["historical"]:
    st.header(TRANSLATIONS[language]["historical"])
    location = st.session_state.current_location.split(",")[0]
    st.subheader(f"Historical Data for {location}")
    with st.spinner(f"Fetching historical data for {location}..."):
        historical_df = []
        date_range = [historical_start + timedelta(days=x) for x in range((historical_end - historical_start).days + 1)]
        for date in date_range:
            historical_data = fetch_weather_data_sync(st.session_state.current_location, "history", {"dt": date.strftime("%Y-%m-%d")})
            if historical_data and 'forecast' in historical_data:
                for hour in historical_data['forecast']['forecastday'][0]['hour']:
                    historical_df.append({
                        "Location": location,
                        "Date": hour['time'],
                        "Temperature (°C)": hour['temp_c'],
                        "Precipitation (mm)": hour['precip_mm'],
                        "Humidity (%)": hour['humidity'],
                        "Wind (kph)": hour['wind_kph'],
                        "Wind Direction": hour['wind_dir'],
                        "Cloud (%)": hour['cloud'],
                        "Dew Point (°C)": hour['dewpoint_c'],
                        "UV Index": hour['uv']
                    })
        if historical_df:
            df = pd.DataFrame(historical_df)
            df['Date'] = pd.to_datetime(df['Date'])
            df['Temp Moving Avg'] = df['Temperature (°C)'].rolling(window=24).mean()
            df['Temp Anomaly'] = df['Temperature (°C)'] - df['Temp Moving Avg']
            df['Heat Index (°C)'] = df.apply(lambda x: calculate_heat_index(x['Temperature (°C)'], x['Humidity (%)']), axis=1)
            df['Wind Chill (°C)'] = df.apply(lambda x: calculate_wind_chill(x['Temperature (°C)'], x['Wind (kph)']), axis=1)
            df['WBGT (°C)'] = df.apply(lambda x: calculate_wbgt(x['Temperature (°C)'], x['Humidity (%)']), axis=1)

            st.subheader("Historical Analytics")
            st.write(f"{TRANSLATIONS[language]['gdd']}: {calculate_gdd(df):.1f}")
            st.write(f"{TRANSLATIONS[language]['avg_temp']}: {df['Temperature (°C)'].mean():.1f} °C")
            st.write(f"{TRANSLATIONS[language]['max_wind']}: {df['Wind (kph)'].max():.1f} kph")

            fig_hist = go.Figure()
            fig_hist.add_trace(go.Scatter(x=df['Date'], y=df['Temperature (°C)'], mode='lines', name=f'Temp - {location}'))
            fig_hist.add_trace(go.Scatter(x=df['Date'], y=df['Precipitation (mm)'], mode='lines', name=f'Precip - {location}', yaxis='y2'))
            fig_hist.update_layout(
                title="Historical Weather Trends",
                xaxis=dict(title="Date"),
                yaxis=dict(title="Temperature (°C)"),
                yaxis2=dict(title="Precipitation (mm)", overlaying="y", side="right")
            )
            st.plotly_chart(fig_hist, use_container_width=True)

            st.download_button(f"Download Historical Data - {location}", df.to_csv(index=False), f"historical_{location}.csv", "text/csv")
        else:
            st.error(f"Failed to fetch historical data for {location}.")

# Astronomy
if selected == TRANSLATIONS[language]["astronomy"]:
    st.header(TRANSLATIONS[language]["astronomy"])
    location = st.session_state.current_location.split(",")[0]
    st.subheader(f"Astronomy for {location}")
    astro_data = fetch_weather_data_sync(st.session_state.current_location, "astronomy", {"dt": datetime.today().strftime("%Y-%m-%d")})
    if astro_data:
        astro = astro_data['astronomy']['astro']
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
            st.metric("Sunrise", astro['sunrise'])
            st.metric("Sunset", astro['sunset'])
            st.markdown("</div>", unsafe_allow_html=True)
        with col2:
            st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
            st.metric("Moon Phase", astro['moon_phase'])
            st.metric("Moon Illumination", f"{astro['moon_illumination']}%")
            st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.error(f"Failed to fetch astronomy data for {location}.")

# Alerts
if selected == TRANSLATIONS[language]["alerts"]:
    st.header(TRANSLATIONS[language]["alerts"])
    location = st.session_state.current_location.split(",")[0]
    st.subheader(f"Alerts for {location}")
    alert_data = fetch_weather_data_sync(st.session_state.current_location, "forecast", {"alerts": "yes"})
    if alert_data and 'alerts' in alert_data and alert_data['alerts']['alert']:
        for alert in alert_data['alerts']['alert']:
            st.warning(f"**{alert['headline']}**")
            st.write(f"Description: {alert['desc']}")
            st.write(f"Effective: {alert['effective']} to {alert['expires']}")
            st.session_state.notification_log.append(f"Alert for {location}: {alert['headline']} at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    else:
        st.info(TRANSLATIONS[language]["no_alerts"].format(location=location))

# Map
if selected == TRANSLATIONS[language]["map"]:
    st.header(TRANSLATIONS[language]["map"])
    location = st.session_state.current_location.split(",")[0]
    st.subheader(f"Map for {location}")
    current_data = fetch_weather_data_sync(st.session_state.current_location, "current", {})
    if current_data:
        m = folium.Map(location=[current_data['location']['lat'], current_data['location']['lon']], zoom_start=10)
        folium.Marker(
            [current_data['location']['lat'], current_data['location']['lon']],
            popup=f"{current_data['location']['name']}: {current_data['current']['temp_c']} °C, {current_data['current']['condition']['text']}",
            tooltip="Click for details",
            icon=folium.Icon(color="blue")
        ).add_to(m)
        st_folium(m, width=700, height=400)
    else:
        st.error(f"Failed to fetch map data for {location}.")

# Decision Support System
if selected == TRANSLATIONS[language]["dss"]:
    st.header(f"{TRANSLATIONS[language]['dss']}: {sector}")
    location = st.session_state.current_location.split(",")[0]
    st.subheader(f"Recommendations for {location}")
    recommendations = []
    current_data = fetch_weather_data_sync(st.session_state.current_location, "current", {"aqi": "yes"})
    forecast_data = fetch_weather_data_sync(st.session_state.current_location, "forecast", {"days": days_forecast, "aqi": "yes", "alerts": "yes"})
    if current_data and forecast_data:
        curr = current_data['current']
        forecast_days = forecast_data['forecast']['forecastday']
        temp_c = curr['temp_c']
        humidity = curr['humidity']
        wind_kph = curr['wind_kph']
        precip_prob = forecast_days[0]['day']['daily_chance_of_rain']
        uv_index = curr['uv']
        pm25 = curr.get('air_quality', {}).get('pm2_5', 0)
        wbgt = calculate_wbgt(temp_c, humidity)
        heat_index = calculate_heat_index(temp_c, humidity)
        wind_chill = calculate_wind_chill(temp_c, wind_kph)

        # Real-Time Alerts
        if precip_prob > 90 or wind_kph > 80 or uv_index > 8:
            alert_msg = f"⚠️ Critical Weather Alert for {location}: High risk conditions detected!"
            st.markdown(f"<div class='notification'>{alert_msg}</div>", unsafe_allow_html=True)
            st.session_state.notification_log.append(f"{alert_msg} at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        if sector == "Agriculture":
            gdd = calculate_gdd(pd.DataFrame([{"Temperature (°C)": temp_c}]))
            pest_risk = "High" if humidity > thresholds["Agriculture"]["humidity_high"] and temp_c > thresholds["Agriculture"]["temp_high"] else "Low"
            irrigation = "Required" if precip_prob < 30 and humidity < 50 else "Not Required"
            recommendations.extend([
                f"Irrigation: {irrigation} (Precip Prob: {precip_prob}%)",
                f"Pest Risk: {pest_risk} (Humidity: {humidity}%, Temp: {temp_c}°C)",
                f"Crop Growth: GDD = {gdd:.1f}"
            ])
            st.write(f"- Irrigation: {irrigation}")
            st.write(f"- Pest Risk: {pest_risk}")
            st.write(f"- Crop Growth: {TRANSLATIONS[language]['gdd']} = {gdd:.1f}")

        elif sector == "Transportation":
            road_risk = "High" if curr['vis_km'] < thresholds["Transportation"]["vis_low"] or precip_prob > 70 or wind_kph > thresholds["Transportation"]["wind_high"] else "Low"
            flight_risk = "High" if wind_kph > thresholds["Transportation"]["wind_high"] or curr['cloud'] > 80 else "Low"
            maritime_risk = "High" if wind_kph > thresholds["Transportation"]["wind_high"] + 20 else "Low"
            recommendations.extend([
                f"Road Safety: {road_risk} (Visibility: {curr['vis_km']} km)",
                f"Flight Operations: {flight_risk} (Wind: {wind_kph} kph)",
                f"Maritime Advisory: {maritime_risk} (Max Wind: {forecast_days[0]['day']['maxwind_kph']} kph)"
            ])
            st.write(f"- Road Safety: {road_risk}")
            st.write(f"- Flight Operations: {flight_risk}")
            st.write(f"- Maritime Advisory: {maritime_risk}")

        elif sector == "Construction":
            work_safety = "Unsafe" if wind_kph > thresholds["Construction"]["wbgt_high"] or precip_prob > 80 or uv_index > thresholds["Construction"]["uv_high"] or wbgt > thresholds["Construction"]["wbgt_high"] else "Safe"
            optimal_hours = "Morning" if temp_c > thresholds["Construction"]["wbgt_high"] else "All Day"
            recommendations.extend([
                f"Work Safety: {work_safety} (WBGT: {wbgt:.1f}°C)",
                f"Optimal Work Hours: {optimal_hours} (Temp: {temp_c}°C)"
            ])
            st.write(f"- Work Safety: {work_safety}")
            st.write(f"- Optimal Work Hours: {optimal_hours}")

        elif sector == "Energy":
            solar_output = "High" if curr['cloud'] < thresholds["Energy"]["cloud_low"] and uv_index > 6 else "Low"
            wind_output = "High" if wind_kph > thresholds["Energy"]["wind_high"] else "Low"
            demand = "High" if heat_index > 30 or wind_chill < 0 else "Normal"
            recommendations.extend([
                f"Solar Output: {solar_output} (Cloud: {curr['cloud']}%)",
                f"Wind Output: {wind_output} (Wind: {wind_kph} kph)",
                f"Energy Demand: {demand} (Heat Index: {heat_index:.1f}°C)"
            ])
            st.write(f"- Solar Output: {solar_output}")
            st.write(f"- Wind Output: {wind_output}")
            st.write(f"- Energy Demand: {demand}")

        elif sector == "Tourism":
            beach_suitability = "Good" if temp_c > thresholds["Tourism"]["temp_high"] and precip_prob < thresholds["Tourism"]["precip_low"] and uv_index < 8 else "Poor"
            hiking_suitability = "Good" if temp_c < thresholds["Tourism"]["temp_high"] + 5 and wind_kph < 40 and precip_prob < thresholds["Tourism"]["precip_low"] + 10 else "Poor"
            recommendations.extend([
                f"Beach Activities: {beach_suitability} (Temp: {temp_c}°C)",
                f"Hiking: {hiking_suitability} (Wind: {wind_kph} kph)"
            ])
            st.write(f"- Beach Activities: {beach_suitability}")
            st.write(f"- Hiking: {hiking_suitability}")

        elif sector == "Emergency Management":
            flood_risk = "High" if forecast_days[0]['day']['totalprecip_mm'] > thresholds["Emergency Management"]["precip_high"] or precip_prob > 90 else "Low"
            storm_risk = "High" if wind_kph > thresholds["Emergency Management"]["wind_high"] else "Low"
            recommendations.extend([
                f"Flood Risk: {flood_risk} (Precip: {forecast_days[0]['day']['totalprecip_mm']} mm)",
                f"Storm Risk: {storm_risk} (Wind: {wind_kph} kph)"
            ])
            st.write(f"- Flood Risk: {flood_risk}")
            st.write(f"- Storm Risk: {storm_risk}")

        elif sector == "Health":
            heat_risk = "High" if heat_index > thresholds["Health"]["wbgt_high"] or wbgt > thresholds["Health"]["wbgt_high"] else "Low"
            respiratory_risk = "High" if pm25 > thresholds["Health"]["pm25_high"] or humidity > 80 else "Low"
            recommendations.extend([
                f"Heatstroke Risk: {heat_risk} (WBGT: {wbgt:.1f}°C)",
                f"Respiratory Risk: {respiratory_risk} (PM2.5: {pm25})"
            ])
            st.write(f"- Heatstroke Risk: {heat_risk}")
            st.write(f"- Respiratory Risk: {respiratory_risk}")

        # Risk Gauge
        st.subheader("Risk Indicator")
        risk_score = (precip_prob / 100 + uv_index / 10 + wind_kph / 100 + pm25 / 100 + wbgt / 50) / 5 * 100
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=risk_score,
            title={'text': f"Risk Score - {location}"},
            gauge={'axis': {'range': [0, 100]}, 'threshold': {'value': 70, 'line': {'color': "red"}}}
        ))
        st.plotly_chart(fig_gauge, use_container_width=True)

        # LaTeX Report
        latex_content = f"""
\\documentclass{{article}}
\\usepackage{{geometry}}
\\usepackage[T1]{{fontenc}}
\\usepackage{{noto}}
\\begin{{document}}
\\section*{{{TRANSLATIONS[language]["dss"]}: {sector}}}
\\textbf{{Date}}: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\\\\
\\textbf{{Location}}: {location}\\\\
\\textbf{{{TRANSLATIONS[language]["recommendations"]}}}:\\\\
{''.join([f"- {rec}\\n" for rec in recommendations])}
\\end{{document}}
"""
        st.download_button(TRANSLATIONS[language]["download_report"], latex_content, f"dss_report_{sector.lower()}.tex", "text/latex")
        st.download_button("Download DSS Report (Text)", "\n".join(recommendations), f"dss_report_{sector.lower()}.txt", "text/plain")
    else:
        st.error(f"Failed to fetch DSS data for {location}.")

# Footer
st.markdown("Powered by [WeatherAPI.com](https://www.weatherapi.com/) | Built with Streamlit")
st.markdown("Prepared by: Dr. Anil Kumar Singh | Linkdien:https://www.linkedin.com/in/anil-kumar-singh-phd-b192554a/ ")
