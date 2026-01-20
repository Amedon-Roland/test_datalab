# Rapport de Synthese

## Optimisation du Reseau de Services Publics pour la Delivrance de Documents Officiels

**Togo Datalab - Test Pratique Data Analyst**

_Date: Janvier 2026_

---

## 1. Contexte et Objectifs

### 1.1 Contexte

Le gouvernement togolais fait face a une augmentation soutenue des demandes de documents officiels (CNI, passeports, actes de naissance), necessitant une optimisation du reseau de centres de delivrance.

### 1.2 Objectifs de l'analyse

- Evaluer la performance operationnelle du reseau
- Identifier les zones sous-desservies
- Proposer des indicateurs de pilotage pertinents
- Formuler des recommandations actionnables

---

## 2. Methodologie

### 2.1 Demarche d'analyse

```
+------------------+    +------------------+    +------------------+
|   CHARGEMENT     |--->|   NETTOYAGE      |--->|      EDA         |
|   DES DONNEES    |    |   VALIDATION     |    |   EXPLORATOIRE   |
+------------------+    +------------------+    +------------------+
                                                       |
                                                       v
+------------------+    +------------------+    +------------------+
|  RECOMMANDATIONS |<---|   DASHBOARD      |<---|   CALCUL KPI     |
+------------------+    +------------------+    +------------------+
```

### 2.2 Donnees analysees

| Source           | Description                       | Volume              |
| ---------------- | --------------------------------- | ------------------- |
| Demandes         | Demandes de documents par commune | 600 enregistrements |
| Centres          | Centres de service actifs         | 55 centres          |
| Logs             | Activite journaliere des centres  | 450 logs            |
| Socio-economique | Donnees demographiques            | 115 communes        |

### 2.3 Nettoyage effectue

- **Doublons supprimes**: 0 (donnees de qualite)
- **Valeurs manquantes traitees**: Imputation par mediane/mode
- **Outliers cappes**: Delais > 60 jours ramenes aux seuils IQR
- **Formats harmonises**: Dates, categories, coordonnees GPS

---

## 3. Principaux Enseignements

### 3.1 Performance operationnelle

#### Delais de traitement

- **Delai moyen**: ~22.7 jours (objectif: 14 jours)
- **Documents les plus longs**: Passeports (~25 jours)
- **Region la plus rapide**: Maritime
- **Region la plus lente**: Savanes

#### Capacite des centres

- **Taux d'utilisation moyen**: 128%
- **Centres en surcharge**: 8 centres > 100%
- **Centres sous-utilises**: 12 centres < 50%

### 3.2 Couverture territoriale

#### Distribution des centres

- **Region Maritime**: 35% des centres (concentree sur Lome)
- **Region Savanes**: 8% des centres (sous-dotee)
- **Taux de couverture communale**: ~14%

#### Ratio population/centre

- **Moyenne nationale**: ~106 576 habitants/centre
- **Region la plus defavorisee**: Savanes (180 000 hab/centre)
- **Region la mieux dotee**: Maritime (80 000 hab/centre)

### 3.3 Qualite de service

#### Rejets

- **Taux de rejet moyen**: 7.37%
- **Principales causes**:
  - Papiers incomplets (35%)
  - Photo non conforme (25%)
  - Signature manquante (20%)

#### Temps d'attente

- **Temps d'attente moyen**: 63 minutes
- **Centres critiques**: 15 centres > 90 minutes
- **Heures de pointe**: 9h-11h et 14h-16h

---

## 4. KPI Cles et Interpretation

### 4.1 Tableau de bord synthetique

| KPI                           | Valeur   | Statut | Interpretation                                   |
| ----------------------------- | -------- | ------ | ------------------------------------------------ |
| **Delai moyen traitement**    | 22.72 j  | ROUGE  | Au-dessus de l'objectif, amelioration necessaire |
| **Taux utilisation capacite** | 128.57%  | VERT   | Bonne utilisation des ressources                 |
| **Ratio population/centre**   | 106 576  | ROUGE  | Couverture insuffisante                          |
| **Couverture communale**      | 14.14%   | ROUGE  | Majorite des communes non couvertes              |
| **Taux de rejet**             | 7.37%    | ORANGE | Besoin d'accompagnement usagers                  |
| **Temps attente moyen**       | 63.27min | ROUGE  | Experience usager degradee                       |
| **Productivite agent**        | 17.72/j  | ORANGE | Potentiel d'amelioration                         |
| **Indice de charge**          | 0.037    | VERT   | Equilibre offre/demande correct                  |

### 4.2 Analyse par region

| Region   | Delai moyen | Taux rejet | Couverture | Priorite |
| -------- | ----------- | ---------- | ---------- | -------- |
| Savanes  | 22 jours    | 11%        | 30%        | Haute    |
| Kara     | 20 jours    | 9%         | 40%        | Moyenne  |
| Centrale | 19 jours    | 8%         | 45%        | Moyenne  |
| Plateaux | 17 jours    | 7%         | 50%        | Moderee  |
| Maritime | 14 jours    | 6%         | 65%        | Faible   |

---

## 5. Recommandations Operationnelles

### 5.1 Court terme (0-6 mois)

#### Reduire les rejets

1. **Former les agents d'accueil** sur les criteres de conformite
2. **Creer une checklist visuelle** pour les usagers
3. **Mettre en place un pre-controle** avant depot officiel

#### Reduire les temps d'attente

1. **Deployer un systeme de prise de RDV** en ligne
2. **Etendre les horaires** aux heures creuses (12h-14h)
3. **Renforcer le personnel** aux heures de pointe

### 5.2 Moyen terme (6-18 mois)

#### Optimiser le reseau

1. **Ouvrir 5 nouveaux centres** dans les zones prioritaires:
   - 2 en region Savanes
   - 2 en region Kara
   - 1 en region Centrale

2. **Redeployer les ressources** des centres sous-utilises

#### Digitaliser les services

1. **Dematerialiser les demandes** non-biometriques
2. **Creer un portail usager** pour le suivi des demandes
3. **Automatiser les notifications** (SMS/email)

### 5.3 Long terme (18+ mois)

#### Transformation numerique

1. **Deployer des bornes en libre-service** dans les communes rurales
2. **Integrer l'authentification biometrique** centralisee
3. **Creer un guichet unique** multi-services

---

## 6. Limites et Perspectives

### 6.1 Limites de l'analyse

- **Donnees historiques limitees**: Analyse sur 1 an uniquement
- **Granularite geographique**: Donnees communales incompletes
- **Donnees qualitatives**: Absence d'enquetes satisfaction usagers

### 6.2 Perspectives d'amelioration

- **Integrer des donnees temps reel** via API
- **Ajouter des previsions** (machine learning)
- **Developper des alertes automatiques** sur les KPI critiques

---

## 7. Conclusion

L'analyse revele un reseau de services publics sous pression, avec des defis majeurs en termes de:

- **Couverture territoriale** insuffisante (14%)
- **Temps d'attente** excessifs (63 minutes)
- **Delais de traitement** superieurs aux objectifs (22.7 jours vs 14 jours)

Les recommandations formulees permettraient d'ameliorer significativement la qualite de service tout en optimisant l'utilisation des ressources existantes. La priorite devrait etre donnee aux regions Savanes et Kara, qui cumulent les indicateurs les plus defavorables.

---

**Auteur**: Data Analyst - Togo Datalab  
**Date**: Janvier 2026  
**Version**: 1.0
