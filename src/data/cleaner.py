"""
Module de nettoyage des donnees.
=================================

Classe DataCleaner pour le nettoyage, la transformation et la 
standardisation des donnees brutes.

Auteur: Data Analyst - Togo Datalab
Date: Janvier 2026
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Union, Tuple, Any
from datetime import datetime
import logging
import warnings

from ..utils.helpers import detect_outliers_iqr, ensure_numeric
from ..utils.constants import REGIONS, TYPES_DOCUMENTS

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataCleaner:
    """
    Gestionnaire de nettoyage des donnees.
    
    Cette classe fournit des methodes pour nettoyer, transformer
    et preparer les donnees pour l'analyse.
    
    Attributes:
        cleaning_log: Journal des operations de nettoyage effectuees
        
    Example:
        >>> cleaner = DataCleaner()
        >>> df_clean = cleaner.clean_demandes(df_raw)
    """
    
    def __init__(self):
        """Initialise le DataCleaner avec un journal vide."""
        self.cleaning_log: List[Dict] = []
        self._start_time = None
    
    def _log_operation(self, 
                       operation: str, 
                       dataset: str,
                       details: Dict[str, Any]) -> None:
        """
        Enregistre une operation de nettoyage.
        
        Args:
            operation: Nom de l'operation
            dataset: Nom du dataset concerne
            details: Details de l'operation
        """
        self.cleaning_log.append({
            "timestamp": datetime.now().isoformat(),
            "operation": operation,
            "dataset": dataset,
            **details
        })
    
    # =========================================================================
    # METHODES DE NETTOYAGE GENERIQUES
    # =========================================================================
    
    def remove_duplicates(self, 
                          df: pd.DataFrame,
                          subset: List[str] = None,
                          keep: str = "first",
                          name: str = "dataset") -> pd.DataFrame:
        """
        Supprime les doublons d'un DataFrame.
        
        Args:
            df: DataFrame a nettoyer
            subset: Colonnes a considerer pour identifier les doublons
            keep: Quelle occurrence garder ("first", "last", False)
            name: Nom du dataset pour le logging
        
        Returns:
            DataFrame sans doublons
        """
        initial_count = len(df)
        df_clean = df.drop_duplicates(subset=subset, keep=keep)
        removed_count = initial_count - len(df_clean)
        
        if removed_count > 0:
            self._log_operation(
                "remove_duplicates",
                name,
                {
                    "rows_removed": removed_count,
                    "percentage": round(removed_count / initial_count * 100, 2),
                    "subset": subset
                }
            )
            logger.info(
                f"[CLEAN] {name}: {removed_count} doublons supprimes "
                f"({removed_count/initial_count*100:.1f}%)"
            )
        
        return df_clean
    
    def handle_missing_values(self,
                              df: pd.DataFrame,
                              strategy: Dict[str, str],
                              name: str = "dataset") -> pd.DataFrame:
        """
        Gere les valeurs manquantes selon une strategie par colonne.
        
        Args:
            df: DataFrame a traiter
            strategy: Dict {colonne: methode}
                      Methodes: "drop", "mean", "median", "mode", "ffill", 
                               "bfill", "zero", ou une valeur specifique
            name: Nom du dataset pour le logging
        
        Returns:
            DataFrame avec valeurs manquantes traitees
        """
        df_clean = df.copy()
        
        for column, method in strategy.items():
            if column not in df_clean.columns:
                logger.warning(f"[WARN] Colonne '{column}' non trouvee")
                continue
            
            missing_before = df_clean[column].isna().sum()
            
            if missing_before == 0:
                continue
            
            if method == "drop":
                df_clean = df_clean.dropna(subset=[column])
            elif method == "mean":
                df_clean[column].fillna(df_clean[column].mean(), inplace=True)
            elif method == "median":
                df_clean[column].fillna(df_clean[column].median(), inplace=True)
            elif method == "mode":
                df_clean[column].fillna(df_clean[column].mode().iloc[0], inplace=True)
            elif method == "ffill":
                df_clean[column].fillna(method='ffill', inplace=True)
            elif method == "bfill":
                df_clean[column].fillna(method='bfill', inplace=True)
            elif method == "zero":
                df_clean[column].fillna(0, inplace=True)
            else:
                # Valeur specifique
                df_clean[column].fillna(method, inplace=True)
            
            missing_after = df_clean[column].isna().sum()
            
            self._log_operation(
                "handle_missing",
                name,
                {
                    "column": column,
                    "method": method,
                    "missing_before": missing_before,
                    "missing_after": missing_after,
                    "treated": missing_before - missing_after
                }
            )
        
        return df_clean
    
    def standardize_text_columns(self,
                                 df: pd.DataFrame,
                                 columns: List[str],
                                 operations: List[str] = None,
                                 name: str = "dataset") -> pd.DataFrame:
        """
        Standardise les colonnes textuelles.
        
        Args:
            df: DataFrame a traiter
            columns: Colonnes a standardiser
            operations: Liste des operations a appliquer
                       ["strip", "lower", "upper", "title", "remove_accents"]
            name: Nom du dataset
        
        Returns:
            DataFrame avec colonnes standardisees
        """
        if operations is None:
            operations = ["strip"]
        
        df_clean = df.copy()
        
        for column in columns:
            if column not in df_clean.columns:
                continue
            
            if df_clean[column].dtype != 'object':
                continue
            
            for op in operations:
                if op == "strip":
                    df_clean[column] = df_clean[column].str.strip()
                elif op == "lower":
                    df_clean[column] = df_clean[column].str.lower()
                elif op == "upper":
                    df_clean[column] = df_clean[column].str.upper()
                elif op == "title":
                    df_clean[column] = df_clean[column].str.title()
        
        self._log_operation(
            "standardize_text",
            name,
            {"columns": columns, "operations": operations}
        )
        
        return df_clean
    
    def convert_date_columns(self,
                             df: pd.DataFrame,
                             columns: List[str],
                             format: str = None,
                             name: str = "dataset") -> pd.DataFrame:
        """
        Convertit les colonnes en datetime.
        
        Args:
            df: DataFrame a traiter
            columns: Colonnes a convertir
            format: Format de date (optionnel, auto-detection sinon)
            name: Nom du dataset
        
        Returns:
            DataFrame avec colonnes converties
        """
        df_clean = df.copy()
        
        for column in columns:
            if column not in df_clean.columns:
                continue
            
            try:
                if format:
                    df_clean[column] = pd.to_datetime(
                        df_clean[column], format=format, errors='coerce'
                    )
                else:
                    df_clean[column] = pd.to_datetime(
                        df_clean[column], errors='coerce', dayfirst=True
                    )
                
                invalid_count = df_clean[column].isna().sum()
                
                self._log_operation(
                    "convert_date",
                    name,
                    {
                        "column": column,
                        "format": format,
                        "invalid_dates": invalid_count
                    }
                )
                
            except Exception as e:
                logger.warning(f"[WARN] Conversion de date echouee pour '{column}': {e}")
        
        return df_clean
    
    def handle_outliers(self,
                        df: pd.DataFrame,
                        columns: List[str],
                        method: str = "iqr",
                        action: str = "cap",
                        multiplier: float = 1.5,
                        name: str = "dataset") -> pd.DataFrame:
        """
        Traite les valeurs aberrantes.
        
        Args:
            df: DataFrame a traiter
            columns: Colonnes numeriques a traiter
            method: Methode de detection ("iqr", "zscore")
            action: Action ("cap", "remove", "nan")
            multiplier: Multiplicateur pour les seuils
            name: Nom du dataset
        
        Returns:
            DataFrame avec outliers traites
        """
        df_clean = df.copy()
        
        for column in columns:
            if column not in df_clean.columns:
                continue
            
            if not np.issubdtype(df_clean[column].dtype, np.number):
                continue
            
            outliers_mask = detect_outliers_iqr(df_clean[column], multiplier)
            outliers_count = outliers_mask.sum()
            
            if outliers_count == 0:
                continue
            
            if action == "cap":
                Q1 = df_clean[column].quantile(0.25)
                Q3 = df_clean[column].quantile(0.75)
                IQR = Q3 - Q1
                lower = Q1 - multiplier * IQR
                upper = Q3 + multiplier * IQR
                df_clean[column] = df_clean[column].clip(lower=lower, upper=upper)
                
            elif action == "remove":
                df_clean = df_clean[~outliers_mask]
                
            elif action == "nan":
                df_clean.loc[outliers_mask, column] = np.nan
            
            self._log_operation(
                "handle_outliers",
                name,
                {
                    "column": column,
                    "method": method,
                    "action": action,
                    "outliers_count": outliers_count,
                    "percentage": round(outliers_count / len(df) * 100, 2)
                }
            )
            
            logger.info(
                f"[CLEAN] {name}.{column}: {outliers_count} outliers traites ({action})"
            )
        
        return df_clean
    
    def validate_categorical_values(self,
                                    df: pd.DataFrame,
                                    column: str,
                                    valid_values: List[str],
                                    action: str = "coerce",
                                    replacement: str = "Autre",
                                    name: str = "dataset") -> pd.DataFrame:
        """
        Valide les valeurs categorielles contre une liste autorisee.
        
        Args:
            df: DataFrame a traiter
            column: Colonne a valider
            valid_values: Liste des valeurs autorisees
            action: "coerce" (remplacer) ou "remove" (supprimer)
            replacement: Valeur de remplacement si action="coerce"
            name: Nom du dataset
        
        Returns:
            DataFrame avec valeurs validees
        """
        df_clean = df.copy()
        
        if column not in df_clean.columns:
            return df_clean
        
        invalid_mask = ~df_clean[column].isin(valid_values 
                                              + [np.nan, None, ""])
        invalid_count = invalid_mask.sum()
        
        if invalid_count > 0:
            invalid_values = df_clean.loc[invalid_mask, column].unique()
            
            if action == "coerce":
                df_clean.loc[invalid_mask, column] = replacement
            elif action == "remove":
                df_clean = df_clean[~invalid_mask]
            
            self._log_operation(
                "validate_categorical",
                name,
                {
                    "column": column,
                    "action": action,
                    "invalid_count": invalid_count,
                    "invalid_values": list(invalid_values)[:10]
                }
            )
            
            logger.info(
                f"[VALID] {name}.{column}: {invalid_count} valeurs invalides traitees"
            )
        
        return df_clean
    
    # =========================================================================
    # METHODES DE NETTOYAGE SPECIFIQUES PAR DATASET
    # =========================================================================
    
    def clean_demandes(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Nettoie le dataset des demandes de documents.
        
        Pipeline de nettoyage:
        1. Suppression des doublons
        2. Standardisation des textes
        3. Conversion des dates
        4. Validation des categories
        5. Traitement des valeurs aberrantes
        6. Gestion des valeurs manquantes
        
        Args:
            df: DataFrame brut des demandes
        
        Returns:
            DataFrame nettoye
        """
        logger.info("\n" + "=" * 60)
        logger.info("NETTOYAGE: demandes_service_public")
        logger.info("=" * 60)
        
        df_clean = df.copy()
        
        # 1. Suppression des doublons
        df_clean = self.remove_duplicates(df_clean, name="demandes")
        
        # 2. Standardisation des textes
        text_columns = ['region', 'prefecture', 'commune', 'quartier',
                        'type_document', 'motif_demande', 'statut_demande']
        df_clean = self.standardize_text_columns(
            df_clean, text_columns, ["strip"], name="demandes"
        )
        
        # 3. Conversion des dates
        df_clean = self.convert_date_columns(
            df_clean, ['date_demande'], name="demandes"
        )
        
        # 4. Validation des categories
        df_clean = self.validate_categorical_values(
            df_clean, 'region', REGIONS, name="demandes"
        )
        df_clean = self.validate_categorical_values(
            df_clean, 'type_document', TYPES_DOCUMENTS, name="demandes"
        )
        
        # 5. Traitement des outliers sur les delais
        df_clean = self.handle_outliers(
            df_clean, 
            ['delai_traitement_jours', 'nombre_demandes'],
            action="cap",
            name="demandes"
        )
        
        # 6. Valeurs manquantes
        df_clean = self.handle_missing_values(
            df_clean,
            {
                'taux_rejet': 'median',
                'age_demandeur': 'median',
                'sexe_demandeur': 'mode'
            },
            name="demandes"
        )
        
        # 7. Corrections additionnelles
        if 'taux_rejet' in df_clean.columns:
            df_clean['taux_rejet'] = df_clean['taux_rejet'].clip(0, 1)
        
        # Creation de colonnes derivees utiles
        if 'date_demande' in df_clean.columns:
            df_clean['annee'] = df_clean['date_demande'].dt.year
            df_clean['mois'] = df_clean['date_demande'].dt.month
            df_clean['trimestre'] = df_clean['date_demande'].dt.quarter
            df_clean['jour_semaine'] = df_clean['date_demande'].dt.dayofweek
        
        logger.info(f"[OK] Nettoyage termine: {len(df_clean)} lignes")
        
        return df_clean
    
    def clean_centres(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Nettoie le dataset des centres de service.
        
        Args:
            df: DataFrame brut des centres
        
        Returns:
            DataFrame nettoye
        """
        logger.info("\n" + "=" * 60)
        logger.info("NETTOYAGE: centres_service")
        logger.info("=" * 60)
        
        df_clean = df.copy()
        
        # Suppression des doublons
        df_clean = self.remove_duplicates(
            df_clean, subset=['centre_id'], name="centres"
        )
        
        # Standardisation des textes
        text_columns = ['nom_centre', 'type_centre', 'region', 
                        'prefecture', 'commune', 'statut_centre']
        df_clean = self.standardize_text_columns(
            df_clean, text_columns, ["strip"], name="centres"
        )
        
        # Conversion des dates
        df_clean = self.convert_date_columns(
            df_clean, ['date_ouverture'], name="centres"
        )
        
        # Validation des coordonnees GPS
        if 'latitude' in df_clean.columns:
            invalid_lat = (df_clean['latitude'] < 5) | (df_clean['latitude'] > 12)
            if invalid_lat.sum() > 0:
                logger.warning(
                    f"[WARN] {invalid_lat.sum()} coordonnees latitude suspectes"
                )
        
        if 'longitude' in df_clean.columns:
            invalid_lon = (df_clean['longitude'] < -0.5) | (df_clean['longitude'] > 2.5)
            if invalid_lon.sum() > 0:
                logger.warning(
                    f"[WARN] {invalid_lon.sum()} coordonnees longitude suspectes"
                )
        
        # Validation de la capacite
        if 'personnel_capacite_jour' in df_clean.columns:
            df_clean['personnel_capacite_jour'] = df_clean[
                'personnel_capacite_jour'
            ].clip(lower=1)
        
        logger.info(f"[OK] Nettoyage termine: {len(df_clean)} centres")
        
        return df_clean
    
    def clean_logs_activite(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Nettoie le dataset des logs d'activite.
        
        Args:
            df: DataFrame brut des logs
        
        Returns:
            DataFrame nettoye
        """
        logger.info("\n" + "=" * 60)
        logger.info("NETTOYAGE: logs_activite")
        logger.info("=" * 60)
        
        df_clean = df.copy()
        
        # Suppression doublons
        df_clean = self.remove_duplicates(
            df_clean, subset=['log_id'], name="logs"
        )
        
        # Conversion dates
        df_clean = self.convert_date_columns(
            df_clean, ['date_operation'], name="logs"
        )
        
        # Traitement des valeurs manquantes pour les operations non-traitement
        maintenance_mask = df_clean['type_operation'].isin(['Maintenance', 'Inventaire'])
        
        for col in ['nombre_traite', 'nombre_rejete', 'delai_effectif']:
            if col in df_clean.columns:
                df_clean.loc[maintenance_mask, col] = df_clean.loc[
                    maintenance_mask, col
                ].fillna(0)
        
        logger.info(f"[OK] Nettoyage termine: {len(df_clean)} logs")
        
        return df_clean
    
    def clean_socioeconomiques(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Nettoie le dataset socio-economique.
        
        Args:
            df: DataFrame brut
        
        Returns:
            DataFrame nettoye
        """
        logger.info("\n" + "=" * 60)
        logger.info("NETTOYAGE: donnees_socioeconomiques")
        logger.info("=" * 60)
        
        df_clean = df.copy()
        
        # Suppression doublons par commune
        df_clean = self.remove_duplicates(
            df_clean, subset=['commune'], name="socioeco"
        )
        
        # Standardisation texte
        df_clean = self.standardize_text_columns(
            df_clean, 
            ['region', 'prefecture', 'commune'], 
            ["strip"],
            name="socioeco"
        )
        
        # Validation des pourcentages (entre 0 et 1)
        pct_columns = ['taux_urbanisation', 'taux_alphabetisation']
        for col in pct_columns:
            if col in df_clean.columns:
                df_clean[col] = df_clean[col].clip(0, 1)
        
        logger.info(f"[OK] Nettoyage termine: {len(df_clean)} communes")
        
        return df_clean
    
    def clean_all(self, datasets: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
        """
        Nettoie tous les datasets.
        
        Args:
            datasets: Dictionnaire des DataFrames bruts
        
        Returns:
            Dictionnaire des DataFrames nettoyes
        """
        cleaned = {}
        
        if 'demandes' in datasets:
            cleaned['demandes'] = self.clean_demandes(datasets['demandes'])
        
        if 'centres' in datasets:
            cleaned['centres'] = self.clean_centres(datasets['centres'])
        
        if 'logs' in datasets:
            cleaned['logs'] = self.clean_logs_activite(datasets['logs'])
        
        if 'socioeco' in datasets:
            cleaned['socioeco'] = self.clean_socioeconomiques(datasets['socioeco'])
        
        # Copier les autres datasets sans nettoyage specifique
        for name, df in datasets.items():
            if name not in cleaned:
                cleaned[name] = df.copy()
        
        return cleaned
    
    def get_cleaning_report(self) -> pd.DataFrame:
        """
        Genere un rapport des operations de nettoyage.
        
        Returns:
            DataFrame avec le journal des operations
        """
        if not self.cleaning_log:
            return pd.DataFrame()
        
        return pd.DataFrame(self.cleaning_log)
    
    def export_cleaning_report(self, output_path: str) -> None:
        """
        Exporte le rapport de nettoyage.
        
        Args:
            output_path: Chemin du fichier de sortie
        """
        report = self.get_cleaning_report()
        if len(report) > 0:
            report.to_csv(output_path, index=False, encoding='utf-8')
            logger.info(f"[OK] Rapport de nettoyage exporte: {output_path}")
