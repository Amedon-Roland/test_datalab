# Optimisation du Reseau de Services Publics - Togo Datalab

**Test Pratique Data Analyst - Delivrance de Documents Officiels**

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-red.svg)](https://streamlit.io)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## Description du Projet

Ce projet analyse et optimise le reseau de services publics togolais pour la delivrance de documents officiels (CNI, passeports, actes de naissance). L'objectif est de fournir aux decideurs des indicateurs de pilotage pertinents et des recommandations actionnables.

## Objectifs

- **Analyser** les donnees de demandes, centres et activites
- **Nettoyer** et preparer des donnees fiables
- **Definir** des KPI metier pertinents
- **Creer** un dashboard interactif de pilotage
- **Formuler** des recommandations operationnelles

---

## Structure du Projet

```
test_datalab/
|-- src/                              # Code source principal
|   |-- data/                         # Modules de gestion des donnees
|   |   |-- loader.py                 # Chargement des donnees
|   |   |-- cleaner.py                # Nettoyage des donnees
|   |   +-- validator.py              # Validation de qualite
|   |-- utils/                        # Utilitaires communs
|   |   |-- constants.py              # Constantes et configuration
|   |   +-- helpers.py                # Fonctions utilitaires
|   |-- analysis/                     # Modules d'analyse
|   |   +-- eda.py                    # Analyse exploratoire
|   |-- kpi/                          # Indicateurs de performance
|   |   |-- definitions.py            # Definitions des KPI
|   |   +-- calculator.py             # Calcul des KPI
|   +-- dashboard/                    # Composants dashboard
|
|-- notebooks/                        # Jupyter Notebooks
|   |-- 01_exploration_donnees.ipynb  # EDA
|   |-- 02_nettoyage_donnees.ipynb    # Nettoyage
|   +-- 03_calcul_kpi.ipynb           # KPI
|
|-- data/                             # Donnees
|   |-- raw/                          # Donnees brutes
|   +-- processed/                    # Donnees nettoyees
|
|-- outputs/                          # Fichiers generes
|   |-- visualizations/               # Graphiques et cartes
|   +-- exports/                      # Donnees exportees
|
|-- reports/                          # Rapports generes
|   |-- rapport_eda.md                # Rapport d'analyse exploratoire
|   |-- tableau_kpi.md                # Tableau des KPI
|   |-- rapport_synthese.md           # Rapport de synthese
|   +-- rapport_nettoyage.csv         # Journal du nettoyage
|
|-- main.py                           # Script principal
|-- dashboard_app.py                  # Application Streamlit
|-- requirements.txt                  # Dependances Python
+-- README.md                         # Documentation
```

---

## Installation et Execution

### Prerequis

- Python 3.11 ou superieur
- pip (gestionnaire de packages Python)

### Installation

```bash
# Cloner ou telecharger le projet
cd test_datalab

# Creer un environnement virtuel
python -m venv venv

# Activer l'environnement
# Linux/Mac:
source venv/bin/activate
# Windows:
.\venv\Scripts\activate

# Installer les dependances
pip install -r requirements.txt
```

### Execution

#### Script Principal (Analyse complete)

```bash
python main.py
```

Ce script execute:

1. Chargement des donnees
2. Validation et nettoyage
3. Analyse exploratoire (EDA)
4. Calcul des KPI
5. Export des resultats

#### Dashboard Interactif

```bash
streamlit run dashboard_app.py
```

Puis ouvrir `http://localhost:8501` dans un navigateur.

---

## Donnees Analysees

| Fichier                        | Description            | Lignes |
| ------------------------------ | ---------------------- | ------ |
| `demandes_service_public.csv`  | Demandes de documents  | 600    |
| `centres_service.csv`          | Centres de delivrance  | 55     |
| `logs_activite.csv`            | Logs operationnels     | 450    |
| `donnees_socioeconomiques.csv` | Donnees demographiques | 115    |
| `details_communes.csv`         | Informations communes  | 200    |

---

## Indicateurs Cles de Performance (KPI)

### Performance Operationnelle

| KPI                             | Description                 | Objectif   |
| ------------------------------- | --------------------------- | ---------- |
| **Delai Moyen de Traitement**   | Duree moyenne de traitement | < 14 jours |
| **Taux d'Utilisation Capacite** | Utilisation des centres     | 70-90%     |

### Accessibilite / Couverture Territoriale

| KPI                         | Description          | Objectif |
| --------------------------- | -------------------- | -------- |
| **Ratio Population/Centre** | Habitants par centre | < 50 000 |
| **Couverture Communale**    | Communes desservies  | > 80%    |

### Qualite de Service

| KPI                       | Description       | Objectif |
| ------------------------- | ----------------- | -------- |
| **Taux de Rejet**         | Demandes rejetees | < 5%     |
| **Temps d'Attente Moyen** | Attente en centre | < 30 min |

### Efficience / Charge

| KPI                    | Description         | Objectif |
| ---------------------- | ------------------- | -------- |
| **Productivite Agent** | Demandes/agent/jour | > 25     |
| **Indice de Charge**   | Demande vs Capacite | < 1.0    |

---

## Dashboard

Le dashboard Streamlit comprend:

### Vue Synthetique Executive

- Metriques cles globales
- Cartes KPI avec statuts colores
- Graphiques de repartition

### Vue Operationnelle

- Performance par centre
- Filtres dynamiques (region, type)
- Tableaux detailles

### Vue Territoriale

- Analyse par region
- Couverture par region
- Zones sous-desservies

---

## Livrables

1. **Repository Git structure** [OK]
   - Code source organise
   - Documentation complete

2. **Notebooks d'EDA et nettoyage** [OK]
   - `notebooks/01_exploration_donnees.ipynb`
   - `notebooks/02_nettoyage_donnees.ipynb`
   - `notebooks/03_calcul_kpi.ipynb`

3. **Tableau des KPI** [OK]
   - `reports/tableau_kpi.md`
   - `outputs/exports/definitions_kpi.xlsx`

4. **Dashboard interactif** [OK]
   - `dashboard_app.py`

5. **Rapport de synthese** [OK]
   - `reports/rapport_synthese.md`

---

## Auteur

**Data Analyst - Togo Datalab**

Ministere de l'Economie Numerique et de la Transformation Digitale
Republique Togolaise

---

## Licence

Ce projet est developpe dans le cadre du test pratique Togo Datalab.
