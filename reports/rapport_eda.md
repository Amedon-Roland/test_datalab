# Rapport d'Analyse Exploratoire des Données (EDA)

## 1. Structure des Données

| Dataset       | Lignes | Colonnes | Colonnes numériques | Colonnes textuelles | Colonnes dates | Valeurs manquantes (%) | Doublons | Mémoire (MB) |
| :------------ | -----: | -------: | ------------------: | ------------------: | -------------: | ---------------------: | -------: | -----------: |
| demandes      |    600 |       20 |                   8 |                  11 |              1 |                      0 |        0 |         0.49 |
| centres       |     55 |       16 |                   4 |                  11 |              1 |                      0 |        0 |         0.04 |
| logs          |    450 |       14 |                   5 |                   8 |              1 |                    2.9 |        0 |         0.24 |
| socioeco      |    115 |       11 |                   8 |                   3 |              0 |                      0 |        0 |         0.03 |
| communes      |    200 |       13 |                   6 |                   7 |              0 |                      0 |        0 |          0.1 |
| developpement |     33 |       15 |                  12 |                   3 |              0 |                      0 |        0 |         0.01 |
| documents_ext |     64 |        9 |                   5 |                   4 |              0 |                      0 |        0 |         0.02 |
| routes        |     40 |       14 |                   6 |                   8 |              0 |                      0 |        0 |         0.02 |

## 2. Statistiques Clés

### Demandes

- **Total des demandes:** 64 904
- **Délai moyen:** 22.7 jours
- **Délai médian:** 22.0 jours
- **Taux de rejet moyen:** 7.4%

## 3. Principaux Constats

- [WARN] logs: 2 colonnes avec >10% de valeurs manquantes
- [WARN] Delai moyen eleve: 22.7 jours

## 4. Conclusion

L'analyse exploratoire a permis d'identifier la structure des données, de détecter les anomalies et de mettre en évidence les premières tendances. Les données sont prêtes pour l'analyse approfondie et le calcul des KPI.
