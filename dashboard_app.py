"""
Dashboard Services Publics - Togo Datalab
==========================================

Dashboard de pilotage pour le reseau de services publics.
Ministere de l'Economie Numerique et de la Transformation Digitale

Usage:
    streamlit run dashboard_app.py

Auteur: Togo Datalab
Date: Janvier 2026
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import sys

# Configuration de la page
st.set_page_config(
    page_title="MENTD - Services Publics",
    page_icon="🇹🇬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Ajouter le chemin src
sys.path.insert(0, str(Path(__file__).parent))

from src.data.loader import DataLoader
from src.data.cleaner import DataCleaner
from src.kpi.calculator import KPICalculator
from src.kpi.definitions import KPI_DEFINITIONS
from src.utils.constants import REGIONS

# Couleurs du theme
VERT = "#2E7D32"
ORANGE = "#F9A825"
ROUGE = "#C62828"
BLEU_FONCE = "#0D1B2A"


# =============================================================================
# FONCTIONS DE CHARGEMENT
# =============================================================================

@st.cache_data
def load_and_prepare_data():
    """Charge et prepare les donnees."""
    loader = DataLoader(Path(__file__).parent)
    raw_data = loader.load_all(verbose=False)
    cleaner = DataCleaner()
    cleaned_data = cleaner.clean_all(raw_data)
    return cleaned_data


@st.cache_data
def calculate_kpis(_data):
    """Calcule les KPI."""
    calculator = KPICalculator(_data)
    calculator.calculate_all()
    return calculator


def get_status_color(status):
    """Retourne la couleur selon le statut."""
    return {"vert": VERT, "orange": ORANGE, "rouge": ROUGE}.get(status, "#6c757d")


def get_status_label(status):
    """Retourne le label selon le statut."""
    return {"vert": "Conforme", "orange": "Attention", "rouge": "Critique"}.get(status, "N/A")


# =============================================================================
# PAGE: TABLEAU DE BORD
# =============================================================================

def page_tableau_de_bord(data, calculator):
    """Page principale du tableau de bord."""
    
    # Titre avec logo
    col_logo, col_title = st.columns([1, 5])
    
    logo_path = Path(__file__).parent / "Logo-MENTD-1.jpg"
    if logo_path.exists():
        col_logo.image(str(logo_path), width=100)
    
    col_title.title("Dashboard Services Publics")
    col_title.caption("Ministere de l'Economie Numerique et de la Transformation Digitale - Republique Togolaise")
    
    st.divider()
    
    # =========================================================================
    # METRIQUES PRINCIPALES
    # =========================================================================
    
    st.subheader("Statistiques Generales")
    
    col1, col2, col3, col4 = st.columns(4)
    
    # Total demandes
    if 'demandes' in data:
        total_demandes = int(data['demandes']['nombre_demandes'].sum())
        col1.metric("Total Demandes", f"{total_demandes:,}")
    
    # Delai moyen
    delai_result = calculator.results.get("delai_moyen_traitement")
    if delai_result:
        col2.metric("Delai Moyen", f"{delai_result.valeur} jours")
    
    # Taux de rejet
    rejet_result = calculator.results.get("taux_rejet")
    if rejet_result:
        col3.metric("Taux de Rejet", f"{rejet_result.valeur}%")
    
    # Centres actifs
    if 'centres' in data:
        nb_centres = len(data['centres'][data['centres']['statut_centre'] == 'Actif'])
        col4.metric("Centres Actifs", nb_centres)
    
    st.divider()
    
    # =========================================================================
    # KPI DETAILLES
    # =========================================================================
    
    st.subheader("Indicateurs Cles de Performance (KPI)")
    
    # Afficher les KPI en 2 lignes de 4
    kpi_list = list(calculator.results.items())
    
    # Premiere ligne
    cols = st.columns(4)
    for idx, (kpi_id, result) in enumerate(kpi_list[:4]):
        with cols[idx]:
            status_color = get_status_color(result.statut)
            status_label = get_status_label(result.statut)
            
            # Container avec bordure coloree
            with st.container(border=True):
                st.markdown(f"**{result.nom}**")
                st.metric(
                    label="Valeur actuelle",
                    value=f"{result.valeur}" if result.valeur is not None else "N/A",
                    delta=None
                )
                st.caption(f"Unite: {result.unite}")
                
                # Badge de statut
                if result.statut == "vert":
                    st.success(f"Statut: {status_label}")
                elif result.statut == "orange":
                    st.warning(f"Statut: {status_label}")
                else:
                    st.error(f"Statut: {status_label}")
    
    # Deuxieme ligne
    cols = st.columns(4)
    for idx, (kpi_id, result) in enumerate(kpi_list[4:8]):
        with cols[idx]:
            status_color = get_status_color(result.statut)
            status_label = get_status_label(result.statut)
            
            with st.container(border=True):
                st.markdown(f"**{result.nom}**")
                st.metric(
                    label="Valeur actuelle",
                    value=f"{result.valeur}" if result.valeur is not None else "N/A",
                    delta=None
                )
                st.caption(f"Unite: {result.unite}")
                
                if result.statut == "vert":
                    st.success(f"Statut: {status_label}")
                elif result.statut == "orange":
                    st.warning(f"Statut: {status_label}")
                else:
                    st.error(f"Statut: {status_label}")
    
    st.divider()
    
    # =========================================================================
    # GRAPHIQUES
    # =========================================================================
    
    st.subheader("Analyse Visuelle")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("##### Demandes par Region")
        
        if 'demandes' in data:
            df = data['demandes']
            region_data = df.groupby('region')['nombre_demandes'].sum().reset_index()
            region_data = region_data.sort_values('nombre_demandes', ascending=True)
            
            fig = px.bar(
                region_data,
                x='nombre_demandes',
                y='region',
                orientation='h',
                color='nombre_demandes',
                color_continuous_scale='Greens'
            )
            fig.update_layout(
                showlegend=False,
                xaxis_title="Nombre de demandes",
                yaxis_title="",
                height=350,
                coloraxis_showscale=False
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("##### Repartition par Type de Document")
        
        if 'demandes' in data:
            df = data['demandes']
            type_data = df.groupby('type_document')['nombre_demandes'].sum().reset_index()
            
            fig = px.pie(
                type_data,
                values='nombre_demandes',
                names='type_document',
                hole=0.4,
                color_discrete_sequence=px.colors.sequential.Greens_r
            )
            fig.update_layout(height=350)
            fig.update_traces(textposition='outside', textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)
    
    st.divider()
    
    # =========================================================================
    # ALERTES
    # =========================================================================
    
    st.subheader("Alertes et Recommandations")
    
    nb_rouge = 0
    nb_orange = 0
    
    for kpi_id, result in calculator.results.items():
        if result.statut == "rouge":
            st.error(f"**{result.nom}**: {result.valeur} {result.unite} - Action urgente requise")
            nb_rouge += 1
        elif result.statut == "orange":
            st.warning(f"**{result.nom}**: {result.valeur} {result.unite} - A surveiller")
            nb_orange += 1
    
    if nb_rouge == 0 and nb_orange == 0:
        st.success("Tous les indicateurs sont dans la zone verte. Continuez a surveiller les performances.")
    
    # Resume
    col1, col2, col3 = st.columns(3)
    col1.metric("KPI Conformes", sum(1 for r in calculator.results.values() if r.statut == "vert"))
    col2.metric("KPI a Surveiller", sum(1 for r in calculator.results.values() if r.statut == "orange"))
    col3.metric("KPI Critiques", sum(1 for r in calculator.results.values() if r.statut == "rouge"))


# =============================================================================
# PAGE: ANALYSE REGIONALE
# =============================================================================

def page_analyse_regionale(data, calculator):
    """Page d'analyse par region."""
    
    st.title("Analyse Regionale")
    st.caption("Performance detaillee par region administrative")
    
    st.divider()
    
    if 'demandes' not in data:
        st.warning("Donnees des demandes non disponibles")
        return
    
    df = data['demandes']
    
    # Selection de region
    regions = ["Toutes les regions"] + list(df['region'].unique())
    selected_region = st.selectbox("Filtrer par region", regions)
    
    if selected_region != "Toutes les regions":
        df_filtered = df[df['region'] == selected_region]
    else:
        df_filtered = df
    
    st.divider()
    
    # Metriques de la region
    col1, col2, col3, col4 = st.columns(4)
    
    col1.metric("Volume de demandes", f"{int(df_filtered['nombre_demandes'].sum()):,}")
    col2.metric("Delai moyen", f"{df_filtered['delai_traitement_jours'].mean():.1f} jours")
    col3.metric("Taux rejet moyen", f"{df_filtered['taux_rejet'].mean()*100:.1f}%")
    col4.metric("Nb enregistrements", len(df_filtered))
    
    st.divider()
    
    # Tableau recapitulatif
    st.subheader("Performance par Region")
    
    region_stats = df.groupby('region').agg({
        'nombre_demandes': 'sum',
        'delai_traitement_jours': 'mean',
        'taux_rejet': 'mean'
    }).round(2)
    
    region_stats.columns = ['Total Demandes', 'Delai Moyen (j)', 'Taux Rejet']
    region_stats['Taux Rejet'] = (region_stats['Taux Rejet'] * 100).round(1).astype(str) + '%'
    region_stats = region_stats.reset_index()
    
    st.dataframe(region_stats, use_container_width=True, hide_index=True)
    
    st.divider()
    
    # Graphiques
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("##### Delai par Region")
        
        delai_data = df.groupby('region')['delai_traitement_jours'].mean().reset_index()
        delai_data = delai_data.sort_values('delai_traitement_jours')
        
        fig = go.Figure()
        
        colors = [VERT if d <= 14 else (ORANGE if d <= 21 else ROUGE) 
                  for d in delai_data['delai_traitement_jours']]
        
        fig.add_trace(go.Bar(
            x=delai_data['delai_traitement_jours'],
            y=delai_data['region'],
            orientation='h',
            marker_color=colors
        ))
        
        # Lignes de seuil
        fig.add_vline(x=14, line_dash="dash", line_color=VERT, 
                      annotation_text="Objectif (14j)")
        fig.add_vline(x=21, line_dash="dash", line_color=ROUGE,
                      annotation_text="Critique (21j)")
        
        fig.update_layout(
            xaxis_title="Delai moyen (jours)",
            yaxis_title="",
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("##### Volume par Region")
        
        volume_data = df.groupby('region')['nombre_demandes'].sum().reset_index()
        
        fig = px.pie(
            volume_data,
            values='nombre_demandes',
            names='region',
            hole=0.3,
            color_discrete_sequence=px.colors.sequential.Greens_r
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)


# =============================================================================
# PAGE: DETAILS KPI
# =============================================================================

def page_details_kpi(data, calculator):
    """Page de details des KPI."""
    
    st.title("Details des Indicateurs")
    st.caption("Informations completes sur chaque KPI")
    
    st.divider()
    
    # Selection du KPI
    kpi_options = {kpi_id: f"{kpi_def.nom}" for kpi_id, kpi_def in KPI_DEFINITIONS.items()}
    
    selected_kpi = st.selectbox(
        "Selectionner un indicateur",
        list(kpi_options.keys()),
        format_func=lambda x: kpi_options[x]
    )
    
    if selected_kpi:
        kpi_def = KPI_DEFINITIONS[selected_kpi]
        result = calculator.results.get(selected_kpi)
        
        st.divider()
        
        # Informations principales
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader(kpi_def.nom)
            
            st.markdown(f"**Categorie:** {kpi_def.categorie}")
            st.markdown(f"**Objectif metier:** {kpi_def.objectif_metier}")
            st.markdown(f"**Description:** {kpi_def.description}")
            st.markdown(f"**Regle de calcul:** `{kpi_def.regle_calcul}`")
        
        with col2:
            if result:
                st.metric(
                    label="Valeur Actuelle",
                    value=f"{result.valeur} {result.unite}"
                )
                
                if result.statut == "vert":
                    st.success("Statut: Conforme")
                elif result.statut == "orange":
                    st.warning("Statut: Attention")
                else:
                    st.error("Statut: Critique")
        
        st.divider()
        
        # Seuils de performance
        st.subheader("Seuils de Performance")
        
        col1, col2, col3 = st.columns(3)
        
        tendance = kpi_def.tendance_positive
        
        with col1:
            st.success(f"VERT: {'<=' if tendance == 'baisse' else '>='} {kpi_def.seuil_vert} {kpi_def.unite}")
        
        with col2:
            st.warning(f"ORANGE: {'<=' if tendance == 'baisse' else '>='} {kpi_def.seuil_orange} {kpi_def.unite}")
        
        with col3:
            st.error(f"ROUGE: {'>' if tendance == 'baisse' else '<'} {kpi_def.seuil_rouge} {kpi_def.unite}")
        
        # Requete SQL
        with st.expander("Voir la requete SQL"):
            st.code(kpi_def.requete_sql, language='sql')
        
        # Details si disponibles
        if result and result.details:
            st.divider()
            st.subheader("Details par Dimension")
            
            for key, value in result.details.items():
                if isinstance(value, dict) and len(value) > 0 and len(value) < 20:
                    with st.expander(f"{key.replace('_', ' ').title()}"):
                        df_detail = pd.DataFrame([
                            {"Dimension": k, "Valeur": v} 
                            for k, v in value.items()
                        ])
                        st.dataframe(df_detail, use_container_width=True, hide_index=True)


# =============================================================================
# PAGE: EXPLORATION
# =============================================================================

def page_exploration(data):
    """Page d'exploration des donnees."""
    
    st.title("Exploration des Donnees")
    st.caption("Acces direct aux datasets")
    
    st.divider()
    
    # Selection du dataset
    dataset_name = st.selectbox("Selectionner un dataset", list(data.keys()))
    
    if dataset_name:
        df = data[dataset_name]
        
        # Informations generales
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Lignes", f"{len(df):,}")
        col2.metric("Colonnes", len(df.columns))
        col3.metric("Memoire", f"{df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
        col4.metric("Valeurs manquantes", f"{df.isna().sum().sum():,}")
        
        st.divider()
        
        # Filtres
        col1, col2 = st.columns(2)
        
        with col1:
            selected_cols = st.multiselect(
                "Colonnes a afficher",
                df.columns.tolist(),
                default=df.columns.tolist()[:8]
            )
        
        with col2:
            n_rows = st.slider("Nombre de lignes", 10, min(500, len(df)), 100)
        
        # Apercu
        st.subheader("Apercu des donnees")
        if selected_cols:
            st.dataframe(df[selected_cols].head(n_rows), use_container_width=True)
        
        st.divider()
        
        # Statistiques
        st.subheader("Statistiques descriptives")
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        if numeric_cols:
            st.dataframe(df[numeric_cols].describe().round(2), use_container_width=True)
        
        # Visualisation
        st.divider()
        st.subheader("Visualisation")
        
        col_to_plot = st.selectbox("Variable a visualiser", df.columns.tolist())
        
        if col_to_plot:
            if df[col_to_plot].dtype in ['int64', 'float64']:
                fig = px.histogram(df, x=col_to_plot, nbins=30, 
                                   color_discrete_sequence=[VERT])
            else:
                value_counts = df[col_to_plot].value_counts().head(15)
                fig = px.bar(x=value_counts.index, y=value_counts.values,
                            color_discrete_sequence=[VERT])
                fig.update_layout(xaxis_title=col_to_plot, yaxis_title="Frequence")
            
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)


# =============================================================================
# PAGE: CENTRES
# =============================================================================

def page_centres(data, calculator):
    """Page d'analyse des centres."""
    
    st.title("Analyse des Centres")
    st.caption("Performance et repartition des centres de service")
    
    st.divider()
    
    if 'centres' not in data:
        st.warning("Donnees des centres non disponibles")
        return
    
    centres = data['centres']
    
    # Filtres
    col1, col2 = st.columns(2)
    
    with col1:
        regions = ["Toutes"] + list(centres['region'].unique())
        selected_region = st.selectbox("Region", regions)
    
    with col2:
        statuts = ["Tous", "Actif", "Inactif"]
        selected_statut = st.selectbox("Statut", statuts)
    
    # Appliquer les filtres
    df_filtered = centres.copy()
    if selected_region != "Toutes":
        df_filtered = df_filtered[df_filtered['region'] == selected_region]
    if selected_statut != "Tous":
        df_filtered = df_filtered[df_filtered['statut_centre'] == selected_statut]
    
    st.divider()
    
    # Metriques
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Centres", len(df_filtered))
    col2.metric("Centres Actifs", len(df_filtered[df_filtered['statut_centre'] == 'Actif']))
    col3.metric("Capacite Totale", f"{int(df_filtered['personnel_capacite_jour'].sum()):,}")
    col4.metric("Capacite Moyenne", f"{df_filtered['personnel_capacite_jour'].mean():.0f}")
    
    st.divider()
    
    # Tableau des centres
    st.subheader("Liste des Centres")
    
    cols_affichage = ['nom_centre', 'region', 'type_centre', 'personnel_capacite_jour', 'statut_centre']
    cols_affichage = [c for c in cols_affichage if c in df_filtered.columns]
    
    st.dataframe(df_filtered[cols_affichage], use_container_width=True, hide_index=True)
    
    st.divider()
    
    # Graphiques
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("##### Centres par Region")
        region_count = centres.groupby('region').size().reset_index(name='count')
        
        fig = px.bar(region_count, x='region', y='count', 
                    color='count', color_continuous_scale='Greens')
        fig.update_layout(height=350, coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("##### Repartition par Type")
        type_count = centres['type_centre'].value_counts()
        
        fig = px.pie(values=type_count.values, names=type_count.index,
                    color_discrete_sequence=px.colors.sequential.Greens_r)
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)


# =============================================================================
# APPLICATION PRINCIPALE
# =============================================================================

def main():
    """Point d'entree principal."""
    
    # =========================================================================
    # SIDEBAR
    # =========================================================================
    
    with st.sidebar:
        # Logo
        logo_path = Path(__file__).parent / "Logo-MENTD-1.jpg"
        if logo_path.exists():
            st.image(str(logo_path), width=150)
        
        st.title("Navigation")
        
        pages = {
            "Tableau de Bord": "dashboard",
            "Analyse Regionale": "regional",
            "Analyse Centres": "centres",
            "Details KPI": "kpi_details",
            "Exploration Donnees": "explorer"
        }
        
        selected_page = st.radio("", list(pages.keys()), label_visibility="collapsed")
        
        st.divider()
        
        st.markdown("### A propos")
        st.markdown("""
        **Togo Datalab**  
        Dashboard de pilotage des services publics.
        
        *Version 2.0*  
        *Janvier 2026*
        """)
    
    # =========================================================================
    # CHARGEMENT DES DONNEES
    # =========================================================================
    
    with st.spinner("Chargement des donnees..."):
        data = load_and_prepare_data()
        calculator = calculate_kpis(data)
    
    # =========================================================================
    # AFFICHAGE DE LA PAGE
    # =========================================================================
    
    page_key = pages[selected_page]
    
    if page_key == "dashboard":
        page_tableau_de_bord(data, calculator)
    elif page_key == "regional":
        page_analyse_regionale(data, calculator)
    elif page_key == "centres":
        page_centres(data, calculator)
    elif page_key == "kpi_details":
        page_details_kpi(data, calculator)
    elif page_key == "explorer":
        page_exploration(data)


if __name__ == "__main__":
    main()
