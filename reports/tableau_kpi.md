# Tableau des Indicateurs Cles de Performance (KPI)

*Optimisation du reseau de services publics - Togo Datalab*

---

## Resume des KPI

| Nom du KPI | Categorie | Valeur | Statut | Objectif metier |
|:-----------|:----------|:-------|:-------|:----------------|
| **Délai Moyen de Traitement** | Performance opérationnelle | 22.72 jours | ROUGE | Mesurer l'efficacité du processus de traitement des demandes et identifier les g... |
| **Taux d'Utilisation de la Capacité** | Performance opérationnelle | 128.57 % | VERT | Optimiser l'allocation des ressources humaines et matérielles en identifiant les... |
| **Ratio Population par Centre** | Accessibilité / Couverture territoriale | 106576 habitants/centre | ROUGE | Évaluer l'équité de la distribution des centres de service par rapport à la popu... |
| **Taux de Couverture Communale** | Accessibilité / Couverture territoriale | 14.14 % | ROUGE | Mesurer la proportion de communes disposant d'au moins un point d'accès au servi... |
| **Taux de Rejet des Demandes** | Qualité de service | 7.37 % | ORANGE | Identifier les problèmes de qualité des dossiers et les besoins d'accompagnement... |
| **Temps d'Attente Moyen en Centre** | Qualité de service | 63.27 minutes | ROUGE | Améliorer l'expérience usager en réduisant le temps passé dans les files d'atten... |
| **Productivité par Agent** | Efficience / Charge | 17.72 demandes/agent/jour | ORANGE | Mesurer l'efficacité des agents et identifier les besoins en formation ou en réo... |
| **Indice de Charge** | Efficience / Charge | 0.037 ratio | VERT | Équilibrer la charge de travail entre les centres et anticiper les besoins de re... |

---

## Details des KPI

### Délai Moyen de Traitement

**Categorie:** Performance opérationnelle

**Objectif metier:** Mesurer l'efficacité du processus de traitement des demandes et identifier les goulets d'étranglement

**Description:** Durée moyenne en jours entre le dépôt d'une demande et sa finalisation (délivrance ou rejet). Un délai faible indique un processus efficace et une bonne expérience usager.

**Regle de calcul:** `Somme des délais de traitement / Nombre total de demandes traitées`

**Valeur actuelle:** 22.72 jours [ROUGE]

**Seuils:**
- VERT: <= 14 jours
- ORANGE: <= 21 jours
- ROUGE: > 30 jours

<details>
<summary>Requete SQL</summary>

```sql
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
```

</details>

---

### Taux d'Utilisation de la Capacité

**Categorie:** Performance opérationnelle

**Objectif metier:** Optimiser l'allocation des ressources humaines et matérielles en identifiant les centres sous ou sur-utilisés

**Description:** Ratio entre le volume de demandes traitées et la capacité théorique maximale du centre. Un taux optimal se situe entre 70% et 90% pour permettre absorption des pics d'activité.

**Regle de calcul:** `(Nombre de demandes traitées par jour / Capacité journalière théorique) × 100`

**Valeur actuelle:** 128.57 % [VERT]

**Seuils:**
- VERT: >= 85 %
- ORANGE: >= 70 %
- ROUGE: < 50 %

<details>
<summary>Requete SQL</summary>

```sql
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
```

</details>

---

### Ratio Population par Centre

**Categorie:** Accessibilité / Couverture territoriale

**Objectif metier:** Évaluer l'équité de la distribution des centres de service par rapport à la population desservie

**Description:** Nombre moyen d'habitants par centre de service dans une zone. Un ratio élevé indique une couverture insuffisante et un besoin potentiel d'ouverture de nouveaux centres.

**Regle de calcul:** `Population totale de la zone / Nombre de centres actifs dans la zone`

**Valeur actuelle:** 106576 habitants/centre [ROUGE]

**Seuils:**
- VERT: <= 50000 habitants/centre
- ORANGE: <= 80000 habitants/centre
- ROUGE: > 100000 habitants/centre

<details>
<summary>Requete SQL</summary>

```sql
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
```

</details>

---

### Taux de Couverture Communale

**Categorie:** Accessibilité / Couverture territoriale

**Objectif metier:** Mesurer la proportion de communes disposant d'au moins un point d'accès au service public

**Description:** Pourcentage de communes ayant un centre de service actif. Un taux de 100% garantit un accès équitable à l'ensemble de la population sur le territoire.

**Regle de calcul:** `(Nombre de communes avec au moins 1 centre / Nombre total de communes) × 100`

**Valeur actuelle:** 14.14 % [ROUGE]

**Seuils:**
- VERT: >= 80 %
- ORANGE: >= 60 %
- ROUGE: < 40 %

<details>
<summary>Requete SQL</summary>

```sql
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
```

</details>

---

### Taux de Rejet des Demandes

**Categorie:** Qualité de service

**Objectif metier:** Identifier les problèmes de qualité des dossiers et les besoins d'accompagnement des usagers

**Description:** Pourcentage de demandes rejetées par rapport au total des demandes. Un taux élevé peut indiquer un besoin de simplification des procédures ou d'amélioration de l'information aux usagers.

**Regle de calcul:** `(Nombre de demandes rejetées / Nombre total de demandes) × 100`

**Valeur actuelle:** 7.37 % [ORANGE]

**Seuils:**
- VERT: <= 5 %
- ORANGE: <= 10 %
- ROUGE: > 15 %

<details>
<summary>Requete SQL</summary>

```sql
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
```

</details>

---

### Temps d'Attente Moyen en Centre

**Categorie:** Qualité de service

**Objectif metier:** Améliorer l'expérience usager en réduisant le temps passé dans les files d'attente

**Description:** Durée moyenne d'attente des usagers avant d'être pris en charge dans un centre de service. Ce KPI reflète directement la qualité perçue du service par les citoyens.

**Regle de calcul:** `Somme des temps d'attente / Nombre total d'usagers reçus`

**Valeur actuelle:** 63.27 minutes [ROUGE]

**Seuils:**
- VERT: <= 30 minutes
- ORANGE: <= 60 minutes
- ROUGE: > 90 minutes

<details>
<summary>Requete SQL</summary>

```sql
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
```

</details>

---

### Productivité par Agent

**Categorie:** Efficience / Charge

**Objectif metier:** Mesurer l'efficacité des agents et identifier les besoins en formation ou en réorganisation

**Description:** Nombre moyen de demandes traitées par agent et par jour. Permet d'évaluer la performance opérationnelle et de planifier les besoins en ressources humaines.

**Regle de calcul:** `Nombre total de demandes traitées / (Nombre d'agents × Nombre de jours ouvrés)`

**Valeur actuelle:** 17.72 demandes/agent/jour [ORANGE]

**Seuils:**
- VERT: >= 25 demandes/agent/jour
- ORANGE: >= 15 demandes/agent/jour
- ROUGE: < 10 demandes/agent/jour

<details>
<summary>Requete SQL</summary>

```sql
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
```

</details>

---

### Indice de Charge

**Categorie:** Efficience / Charge

**Objectif metier:** Équilibrer la charge de travail entre les centres et anticiper les besoins de renforcement

**Description:** Ratio entre la demande (volume de demandes) et l'offre (capacité des centres) par zone géographique. Un indice >1 indique une surcharge, <1 une sous-utilisation.

**Regle de calcul:** `Volume de demandes par zone / Capacité totale des centres de la zone`

**Valeur actuelle:** 0.037 ratio [VERT]

**Seuils:**
- VERT: <= 0.8 ratio
- ORANGE: <= 1.0 ratio
- ROUGE: > 1.2 ratio

<details>
<summary>Requete SQL</summary>

```sql
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
```

</details>

---

