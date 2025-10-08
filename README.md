## 🌤️ Application de Visualisation et de Prédiction Météo — Deux-Sèvres

### 📖 Description

Cette application permet de **visualiser et de prédire les conditions météorologiques** sur le **territoire des Deux-Sèvres (79)**.  
Elle offre une interface interactive développée avec **Streamlit**, permettant d’explorer les tendances météo, les températures, les précipitations et bien plus encore grâce à des graphiques dynamiques réalisés avec **Plotly**.

----------

### 🚀 Fonctionnalités principales

-  🔭 **Comparaison des modèles météo** : GFS, AROME, ARPEGE, ICONEU 

- 📅 **Visualisation des prévisions par date**
    
-   🌡️ Affichage des **températures minimales et maximales**
    
-   🌧️ Estimation des **précipitations et probabilités de pluie**
    
-   💨 Suivi de la **vitesse du vent et des rafales**
    
-   ☀️ Affichage de l’**indice UV maximal**
    
-   📊 Graphiques interactifs avec **Plotly Express**
    
-   🗺️ Analyse spécifique au **territoire des Deux-Sèvres**
    

----------

### 🧠 Modèles utilisés

| Modèle  | Description rapide | Résolution | Horizon de prévision |
|----------|--------------------|-------------|----------------------|
| **GFS** | Modèle global américain utilisé pour les tendances à moyen terme | ~25 km | Jusqu’à 16 jours |
| **AROME** | Modèle haute résolution de Météo-France pour le court terme | ~1,3 km | 48 heures |
| **ARPEGE** | Modèle global de Météo-France pour l’Europe et le monde | ~10 km | 4 à 5 jours |
| **ICONEU** | Modèle européen haute résolution du DWD (Allemagne) | ~7 km | 5 à 7 jours |



### 🧩 Technologies utilisées

-   [Python 3.10+](https://www.python.org/)
    
-   Streamlit
    
-   Plotly
    
-   Pandas
    
-   NumPy
    

----------

### ⚙️ Installation

#### 1. Cloner le dépôt

`git clone https://github.com/damienRavaud/meteo.git` 

#### 2. Créer un environnement virtuel (optionnel mais recommandé)

`python -m venv venv source venv/bin/activate # Sur macOS/Linux venv\Scripts\activate # Sur Windows` 

#### 3. Installer les dépendances

`pip install -r requirements.txt` 

----------

### 🖥️ Lancer l’application

`streamlit run meteo.py` 

Ensuite, ouvre ton navigateur à l’adresse :  
👉 **[http://localhost:8501](http://localhost:8501)**

----------

### 📂 Structure du projet

meteo/  
├── meteo.py             # Script principal Streamlit  
├── requirements.txt     # Liste des dépendances  
└── README.md            # Documentation du projet  
----------

### 🌍 Déploiement sur Streamlit Cloud

1.  Pousse ton dépôt sur GitHub.
    
2.  Va sur streamlit.io/cloud.
    
3.  Clique sur **“New app”** et sélectionne ton dépôt.
    
4.  Indique le chemin vers `meteo.py` et c’est tout ! 🎉
    

----------

### Auteur

👤 **Damien Ravaud**  
💼 Chargé de projet innovant Smart Grid — Gérédis
