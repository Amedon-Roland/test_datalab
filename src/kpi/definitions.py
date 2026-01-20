"""
Définitions des KPI (Indicateurs Clés de Performance).
========================================================

Ce module contient les définitions structurées de tous les KPI
nécessaires au pilotage du service public de délivrance de documents.

Auteur: Data Analyst - Togo Datalab
Date: Janvier 2026
"""

from typing import Dict, List, Any
from dataclasses import dataclass


@dataclass
class KPIDefinition:
    """Structure de définition d'un KPI."""
    nom: str
    categorie: str
    objectif_metier: str
    description: str
    regle_calcul: str
    requete_sql: str
    unite: str
    seuil_vert: float = None
    seuil_orange: float = None
    seuil_rouge: float = None
    tendance_positive: str = "hausse"  # "hausse" ou "baisse"


# =============================================================================
# DÉFINITIONS DES KPI
# =============================================================================

KPI_DEFINITIONS: Dict[str, KPIDefinition] = {
    
    # =========================================================================
    # KPI DE PERFORMANCE OPÉRATIONNELLE
    # =========================================================================
    
    "delai_moyen_traitement": KPIDefinition(
        nom="Délai Moyen de Traitement",
        categorie="Performance opérationnelle",
        objectif_metier=(
            "Mesurer l'efficacité du processus de traitement des demandes "
            "et identifier les goulets d'étranglement"
        ),
        description=(
            "Durée moyenne en jours entre le dépôt d'une demande et sa "
            "finalisation (délivrance ou rejet). Un délai faible indique "
            "un processus efficace et une bonne expérience usager."
        ),
        regle_calcul=(
            "Somme des délais de traitement / Nombre total de demandes traitées"
        ),
        requete_sql="""
-- KPI: Délai Moyen de Traitement
SELECT 
    ROUND(AVG(delai_traitement_jours), 2) AS delai_moyen_jours,
    ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY delai_traitement_jours), 2) AS delai_median_jours,
    COUNT(*) AS nombre_demandes
FROM demandes_service_public
WHERE statut_demande IN ('Traitee', 'Rejetée');

-- Par région
SELECT 
    region,
    ROUND(AVG(delai_traitement_jours), 2) AS delai_moyen_jours,
    COUNT(*) AS nombre_demandes
FROM demandes_service_public
WHERE statut_demande IN ('Traitee', 'Rejetée')
GROUP BY region
ORDER BY delai_moyen_jours DESC;
        """,
        unite="jours",
        seuil_vert=14,
        seuil_orange=21,
        seuil_rouge=30,
        tendance_positive="baisse"
    ),
    
    "taux_utilisation_capacite": KPIDefinition(
        nom="Taux d'Utilisation de la Capacité",
        categorie="Performance opérationnelle",
        objectif_metier=(
            "Optimiser l'allocation des ressources humaines et matérielles "
            "en identifiant les centres sous ou sur-utilisés"
        ),
        description=(
            "Ratio entre le volume de demandes traitées et la capacité "
            "théorique maximale du centre. Un taux optimal se situe entre "
            "70% et 90% pour permettre absorption des pics d'activité."
        ),
        regle_calcul=(
            "(Nombre de demandes traitées par jour / Capacité journalière théorique) × 100"
        ),
        requete_sql="""
-- KPI: Taux d'Utilisation de la Capacité
SELECT 
    c.centre_id,
    c.nom_centre,
    c.region,
    c.personnel_capacite_jour AS capacite_theorique,
    ROUND(AVG(l.nombre_traite), 2) AS volume_moyen_jour,
    ROUND(AVG(l.nombre_traite) * 100.0 / c.personnel_capacite_jour, 2) AS taux_utilisation_pct
FROM centres_service c
LEFT JOIN logs_activite l ON c.centre_id = l.centre_id
WHERE l.type_operation = 'Traitement'
GROUP BY c.centre_id, c.nom_centre, c.region, c.personnel_capacite_jour
ORDER BY taux_utilisation_pct DESC;

-- Résumé global
SELECT 
    ROUND(AVG(taux_util), 2) AS taux_utilisation_moyen
FROM (
    SELECT 
        AVG(l.nombre_traite) * 100.0 / c.personnel_capacite_jour AS taux_util
    FROM centres_service c
    LEFT JOIN logs_activite l ON c.centre_id = l.centre_id
    WHERE l.type_operation = 'Traitement'
    GROUP BY c.centre_id, c.personnel_capacite_jour
) sub;
        """,
        unite="%",
        seuil_vert=85,
        seuil_orange=70,
        seuil_rouge=50,
        tendance_positive="hausse"
    ),
    
    # =========================================================================
    # KPI D'ACCESSIBILITÉ ET COUVERTURE TERRITORIALE
    # =========================================================================
    
    "ratio_population_centre": KPIDefinition(
        nom="Ratio Population par Centre",
        categorie="Accessibilité / Couverture territoriale",
        objectif_metier=(
            "Évaluer l'équité de la distribution des centres de service "
            "par rapport à la population desservie"
        ),
        description=(
            "Nombre moyen d'habitants par centre de service dans une zone. "
            "Un ratio élevé indique une couverture insuffisante et un besoin "
            "potentiel d'ouverture de nouveaux centres."
        ),
        regle_calcul=(
            "Population totale de la zone / Nombre de centres actifs dans la zone"
        ),
        requete_sql="""
-- KPI: Ratio Population par Centre
SELECT 
    se.region,
    SUM(se.population) AS population_totale,
    COUNT(DISTINCT c.centre_id) AS nombre_centres,
    ROUND(SUM(se.population) * 1.0 / COUNT(DISTINCT c.centre_id), 0) AS ratio_pop_centre
FROM donnees_socioeconomiques se
LEFT JOIN centres_service c ON se.region = c.region AND c.statut_centre = 'Actif'
GROUP BY se.region
ORDER BY ratio_pop_centre DESC;

-- Ratio global
SELECT 
    ROUND(SUM(population) * 1.0 / 
        (SELECT COUNT(*) FROM centres_service WHERE statut_centre = 'Actif'), 0) 
    AS ratio_pop_centre_national
FROM donnees_socioeconomiques;
        """,
        unite="habitants/centre",
        seuil_vert=50000,
        seuil_orange=80000,
        seuil_rouge=100000,
        tendance_positive="baisse"
    ),
    
    "couverture_communale": KPIDefinition(
        nom="Taux de Couverture Communale",
        categorie="Accessibilité / Couverture territoriale",
        objectif_metier=(
            "Mesurer la proportion de communes disposant d'au moins un "
            "point d'accès au service public"
        ),
        description=(
            "Pourcentage de communes ayant un centre de service actif. "
            "Un taux de 100% garantit un accès équitable à l'ensemble "
            "de la population sur le territoire."
        ),
        regle_calcul=(
            "(Nombre de communes avec au moins 1 centre / Nombre total de communes) × 100"
        ),
        requete_sql="""
-- KPI: Taux de Couverture Communale
SELECT 
    region,
    COUNT(DISTINCT dc.commune) AS total_communes,
    COUNT(DISTINCT CASE WHEN c.centre_id IS NOT NULL THEN dc.commune END) AS communes_couvertes,
    ROUND(
        COUNT(DISTINCT CASE WHEN c.centre_id IS NOT NULL THEN dc.commune END) * 100.0 
        / COUNT(DISTINCT dc.commune), 2
    ) AS taux_couverture_pct
FROM details_communes dc
LEFT JOIN centres_service c ON dc.commune = c.commune AND c.statut_centre = 'Actif'
GROUP BY region
ORDER BY taux_couverture_pct;

-- Taux national
SELECT 
    ROUND(
        COUNT(DISTINCT CASE WHEN c.centre_id IS NOT NULL THEN dc.commune END) * 100.0 
        / COUNT(DISTINCT dc.commune), 2
    ) AS taux_couverture_national
FROM details_communes dc
LEFT JOIN centres_service c ON dc.commune = c.commune AND c.statut_centre = 'Actif';
        """,
        unite="%",
        seuil_vert=80,
        seuil_orange=60,
        seuil_rouge=40,
        tendance_positive="hausse"
    ),
    
    # =========================================================================
    # KPI DE QUALITÉ DE SERVICE
    # =========================================================================
    
    "taux_rejet": KPIDefinition(
        nom="Taux de Rejet des Demandes",
        categorie="Qualité de service",
        objectif_metier=(
            "Identifier les problèmes de qualité des dossiers et les besoins "
            "d'accompagnement des usagers"
        ),
        description=(
            "Pourcentage de demandes rejetées par rapport au total des demandes. "
            "Un taux élevé peut indiquer un besoin de simplification des procédures "
            "ou d'amélioration de l'information aux usagers."
        ),
        regle_calcul=(
            "(Nombre de demandes rejetées / Nombre total de demandes) × 100"
        ),
        requete_sql="""
-- KPI: Taux de Rejet Global
SELECT 
    ROUND(AVG(taux_rejet) * 100, 2) AS taux_rejet_moyen_pct,
    ROUND(SUM(nombre_demandes * taux_rejet) / SUM(nombre_demandes) * 100, 2) AS taux_rejet_pondere_pct
FROM demandes_service_public;

-- Par type de document
SELECT 
    type_document,
    ROUND(AVG(taux_rejet) * 100, 2) AS taux_rejet_pct,
    SUM(nombre_demandes) AS total_demandes
FROM demandes_service_public
GROUP BY type_document
ORDER BY taux_rejet_pct DESC;

-- Par motif de rejet (depuis les logs)
SELECT 
    raison_rejet,
    SUM(nombre_rejete) AS total_rejets,
    ROUND(SUM(nombre_rejete) * 100.0 / 
        (SELECT SUM(nombre_rejete) FROM logs_activite WHERE raison_rejet != 'N/A'), 2
    ) AS proportion_pct
FROM logs_activite
WHERE raison_rejet != 'N/A'
GROUP BY raison_rejet
ORDER BY total_rejets DESC;
        """,
        unite="%",
        seuil_vert=5,
        seuil_orange=10,
        seuil_rouge=15,
        tendance_positive="baisse"
    ),
    
    "temps_attente_moyen": KPIDefinition(
        nom="Temps d'Attente Moyen en Centre",
        categorie="Qualité de service",
        objectif_metier=(
            "Améliorer l'expérience usager en réduisant le temps passé "
            "dans les files d'attente"
        ),
        description=(
            "Durée moyenne d'attente des usagers avant d'être pris en charge "
            "dans un centre de service. Ce KPI reflète directement la qualité "
            "perçue du service par les citoyens."
        ),
        regle_calcul=(
            "Somme des temps d'attente / Nombre total d'usagers reçus"
        ),
        requete_sql="""
-- KPI: Temps d'Attente Moyen
SELECT 
    ROUND(AVG(temps_attente_moyen_minutes), 2) AS temps_attente_moyen_min,
    ROUND(MIN(temps_attente_moyen_minutes), 2) AS temps_min,
    ROUND(MAX(temps_attente_moyen_minutes), 2) AS temps_max
FROM logs_activite
WHERE type_operation = 'Traitement';

-- Par centre
SELECT 
    l.centre_id,
    c.nom_centre,
    c.region,
    ROUND(AVG(l.temps_attente_moyen_minutes), 2) AS temps_attente_moyen_min,
    COUNT(*) AS nombre_jours_observation
FROM logs_activite l
JOIN centres_service c ON l.centre_id = c.centre_id
WHERE l.type_operation = 'Traitement'
GROUP BY l.centre_id, c.nom_centre, c.region
ORDER BY temps_attente_moyen_min DESC;
        """,
        unite="minutes",
        seuil_vert=30,
        seuil_orange=60,
        seuil_rouge=90,
        tendance_positive="baisse"
    ),
    
    # =========================================================================
    # KPI D'EFFICIENCE ET CHARGE
    # =========================================================================
    
    "productivite_agent": KPIDefinition(
        nom="Productivité par Agent",
        categorie="Efficience / Charge",
        objectif_metier=(
            "Mesurer l'efficacité des agents et identifier les besoins "
            "en formation ou en réorganisation"
        ),
        description=(
            "Nombre moyen de demandes traitées par agent et par jour. "
            "Permet d'évaluer la performance opérationnelle et de planifier "
            "les besoins en ressources humaines."
        ),
        regle_calcul=(
            "Nombre total de demandes traitées / (Nombre d'agents × Nombre de jours ouvrés)"
        ),
        requete_sql="""
-- KPI: Productivité par Agent
SELECT 
    l.centre_id,
    c.nom_centre,
    ROUND(AVG(l.nombre_traite * 1.0 / l.personnel_present), 2) AS demandes_par_agent_jour,
    AVG(l.personnel_present) AS effectif_moyen
FROM logs_activite l
JOIN centres_service c ON l.centre_id = c.centre_id
WHERE l.type_operation = 'Traitement' 
  AND l.personnel_present > 0
GROUP BY l.centre_id, c.nom_centre
ORDER BY demandes_par_agent_jour DESC;

-- Productivité moyenne nationale
SELECT 
    ROUND(AVG(nombre_traite * 1.0 / personnel_present), 2) AS productivite_moyenne_nationale
FROM logs_activite
WHERE type_operation = 'Traitement' 
  AND personnel_present > 0;
        """,
        unite="demandes/agent/jour",
        seuil_vert=25,
        seuil_orange=15,
        seuil_rouge=10,
        tendance_positive="hausse"
    ),
    
    "indice_charge": KPIDefinition(
        nom="Indice de Charge",
        categorie="Efficience / Charge",
        objectif_metier=(
            "Équilibrer la charge de travail entre les centres et "
            "anticiper les besoins de renforcement"
        ),
        description=(
            "Ratio entre la demande (volume de demandes) et l'offre "
            "(capacité des centres) par zone géographique. Un indice >1 "
            "indique une surcharge, <1 une sous-utilisation."
        ),
        regle_calcul=(
            "Volume de demandes par zone / Capacité totale des centres de la zone"
        ),
        requete_sql="""
-- KPI: Indice de Charge par Région
SELECT 
    d.region,
    SUM(d.nombre_demandes) AS volume_demandes,
    SUM(c.personnel_capacite_jour) AS capacite_totale,
    ROUND(SUM(d.nombre_demandes) * 1.0 / NULLIF(SUM(c.personnel_capacite_jour), 0), 3) AS indice_charge
FROM demandes_service_public d
LEFT JOIN centres_service c ON d.region = c.region AND c.statut_centre = 'Actif'
GROUP BY d.region
ORDER BY indice_charge DESC;

-- Indice de charge national
SELECT 
    ROUND(
        SUM(nombre_demandes) * 1.0 / 
        (SELECT SUM(personnel_capacite_jour) FROM centres_service WHERE statut_centre = 'Actif'),
        3
    ) AS indice_charge_national
FROM demandes_service_public;
        """,
        unite="ratio",
        seuil_vert=0.8,
        seuil_orange=1.0,
        seuil_rouge=1.2,
        tendance_positive="baisse"
    ),
}


# =============================================================================
# FONCTIONS UTILITAIRES
# =============================================================================

def get_kpi_by_category(category: str) -> Dict[str, KPIDefinition]:
    """
    Retourne les KPI d'une catégorie donnée.
    
    Args:
        category: Nom de la catégorie
    
    Returns:
        Dictionnaire des KPI de la catégorie
    """
    return {
        key: kpi for key, kpi in KPI_DEFINITIONS.items() 
        if kpi.categorie == category
    }


def get_all_categories() -> List[str]:
    """
    Retourne la liste des catégories de KPI.
    
    Returns:
        Liste des catégories uniques
    """
    return list(set(kpi.categorie for kpi in KPI_DEFINITIONS.values()))


def export_kpi_definitions_to_markdown() -> str:
    """
    Exporte les définitions de KPI au format Markdown.
    
    Returns:
        Contenu Markdown formaté
    """
    md = ["# Tableau des KPI\n"]
    md.append("| Nom du KPI | Objectif métier | Description / Interprétation | Règle de calcul | Requête SQL |\n")
    md.append("|:-----------|:----------------|:-----------------------------|:----------------|:------------|\n")
    
    for key, kpi in KPI_DEFINITIONS.items():
        md.append(
            f"| **{kpi.nom}** | {kpi.objectif_metier[:100]}... | "
            f"{kpi.description[:100]}... | {kpi.regle_calcul} | "
            f"*(Voir documentation)* |\n"
        )
    
    return "".join(md)


def export_kpi_definitions_to_excel_format() -> List[Dict]:
    """
    Exporte les définitions de KPI pour Excel.
    
    Returns:
        Liste de dictionnaires pour export Excel
    """
    return [
        {
            "Nom du KPI": kpi.nom,
            "Catégorie": kpi.categorie,
            "Objectif métier": kpi.objectif_metier,
            "Description / Interprétation": kpi.description,
            "Règle de calcul": kpi.regle_calcul,
            "Requête SQL": kpi.requete_sql.strip(),
            "Unité": kpi.unite,
            "Seuil Vert": kpi.seuil_vert,
            "Seuil Orange": kpi.seuil_orange,
            "Seuil Rouge": kpi.seuil_rouge
        }
        for kpi in KPI_DEFINITIONS.values()
    ]
