"""
Constantes et configurations globales du projet.
==================================================

Ce module centralise toutes les constantes utilisées dans le projet,
incluant les paramètres de configuration, les palettes de couleurs,
et les valeurs de référence métier.

Auteur: Data Analyst - Togo Datalab
Date: Janvier 2026
"""

from typing import Dict, List, Tuple

# =============================================================================
# RÉGIONS ADMINISTRATIVES DU TOGO
# =============================================================================

REGIONS: List[str] = [
    "Maritime",
    "Plateaux", 
    "Centrale",
    "Kara",
    "Savanes"
]

REGIONS_INFO: Dict[str, Dict] = {
    "Maritime": {"chef_lieu": "Lomé", "code": "MR", "population_approx": 2500000},
    "Plateaux": {"chef_lieu": "Atakpamé", "code": "PL", "population_approx": 1375000},
    "Centrale": {"chef_lieu": "Sokodé", "code": "CE", "population_approx": 617000},
    "Kara": {"chef_lieu": "Kara", "code": "KR", "population_approx": 769000},
    "Savanes": {"chef_lieu": "Dapaong", "code": "SV", "population_approx": 828000},
}

# =============================================================================
# TYPES DE DOCUMENTS
# =============================================================================

TYPES_DOCUMENTS: List[str] = [
    "Carte d'identité",
    "Passeport",
    "Acte de naissance",
    "Livre de famille",
    "Casier judiciaire",
    "Certificat de nationalité"
]

CATEGORIES_DOCUMENTS: Dict[str, str] = {
    "Carte d'identité": "Identité",
    "Passeport": "Voyage",
    "Acte de naissance": "Civil",
    "Livre de famille": "Civil",
    "Casier judiciaire": "Judiciaire",
    "Certificat de nationalité": "Identité"
}

# =============================================================================
# PARAMÈTRES DE RÉFÉRENCE MÉTIER (SEUILS ET OBJECTIFS)
# =============================================================================

# Délais de traitement cibles (en jours)
DELAI_CIBLE: Dict[str, int] = {
    "Carte d'identité": 14,
    "Passeport": 21,
    "Acte de naissance": 7,
    "Livre de famille": 14,
    "Casier judiciaire": 14,
    "Certificat de nationalité": 10
}

# Seuils de performance
SEUILS_PERFORMANCE = {
    "delai_excellent": 7,      # jours
    "delai_acceptable": 21,    # jours
    "delai_critique": 30,      # jours
    "taux_rejet_acceptable": 0.05,  # 5%
    "taux_rejet_alerte": 0.10,      # 10%
    "taux_rejet_critique": 0.15,    # 15%
    "temps_attente_acceptable": 60,  # minutes
    "temps_attente_critique": 120,   # minutes
}

# Distance maximale acceptable pour accéder à un centre (en km)
DISTANCE_ACCESSIBILITE_KM = 50

# =============================================================================
# PALETTE DE COULEURS PROFESSIONNELLE
# =============================================================================

COLOR_PALETTE: Dict[str, str] = {
    # Couleurs principales
    "primary": "#1E3A5F",       # Bleu foncé (couleur principale)
    "secondary": "#48A9A6",     # Vert d'eau
    "accent": "#E76F51",        # Orange/Corail
    
    # Couleurs des régions
    "maritime": "#2E86AB",      # Bleu océan
    "plateaux": "#A23B72",      # Violet
    "centrale": "#F18F01",      # Orange
    "kara": "#C73E1D",          # Rouge brique
    "savanes": "#3B9A4E",       # Vert
    
    # États et statuts
    "success": "#28A745",       # Vert succès
    "warning": "#FFC107",       # Jaune alerte
    "danger": "#DC3545",        # Rouge danger
    "info": "#17A2B8",          # Bleu info
    
    # Neutres
    "dark": "#2D3436",          # Gris foncé
    "light": "#F8F9FA",         # Gris clair
    "white": "#FFFFFF",
    "black": "#000000",
}

# Palette séquentielle pour les heatmaps
COLOR_SEQUENTIAL: List[str] = [
    "#FEF9E7", "#FCF3CF", "#F9E79F", "#F7DC6F", "#F4D03F",
    "#F1C40F", "#D4AC0D", "#B7950B", "#9A7D0A", "#7D6608"
]

# Palette divergente
COLOR_DIVERGENT: List[str] = [
    "#D73027", "#F46D43", "#FDAE61", "#FEE090", "#FFFFBF",
    "#E0F3F8", "#ABD9E9", "#74ADD1", "#4575B4", "#313695"
]

# =============================================================================
# CONFIGURATION DES FICHIERS DE DONNÉES
# =============================================================================

DATA_FILES: Dict[str, str] = {
    "centres": "centres_service.csv",
    "demandes": "demandes_service_public.csv",
    "communes": "details_communes.csv",
    "socioeco": "donnees_socioeconomiques.csv",
    "logs": "logs_activite.csv",
    "developpement": "developpement.csv",
    "documents_ext": "documents_administratifs_ext.csv",
    "routes": "reseau_routier_togo_ext.csv"
}

# Mapping des colonnes principales par fichier
COLUMN_MAPPINGS: Dict[str, Dict[str, str]] = {
    "centres": {
        "id": "centre_id",
        "nom": "nom_centre",
        "type": "type_centre",
        "capacite": "personnel_capacite_jour"
    },
    "demandes": {
        "id": "demande_id",
        "type_doc": "type_document",
        "delai": "delai_traitement_jours",
        "taux_rejet": "taux_rejet"
    }
}

# =============================================================================
# FORMATS D'AFFICHAGE
# =============================================================================

DATE_FORMAT = "%Y-%m-%d"
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
CURRENCY_SYMBOL = "FCFA"
DECIMAL_PLACES = 2

# =============================================================================
# CONFIGURATION DES GRAPHIQUES
# =============================================================================

CHART_CONFIG = {
    "figure_size": (12, 6),
    "dpi": 100,
    "font_family": "DejaVu Sans",
    "title_fontsize": 14,
    "label_fontsize": 11,
    "tick_fontsize": 9,
    "legend_fontsize": 10,
    "grid_alpha": 0.3,
}

# =============================================================================
# MESSAGES ET LABELS
# =============================================================================

LABELS_FR: Dict[str, str] = {
    "region": "Région",
    "prefecture": "Préfecture",
    "commune": "Commune",
    "type_document": "Type de document",
    "nombre_demandes": "Nombre de demandes",
    "delai_traitement": "Délai de traitement (jours)",
    "taux_rejet": "Taux de rejet (%)",
    "population": "Population",
    "capacite": "Capacité journalière",
}
