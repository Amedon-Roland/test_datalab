"""
Module de validation des donnees.
===================================

Classe DataValidator pour verifier la qualite et l'integrite
des donnees apres nettoyage.

Auteur: Data Analyst - Togo Datalab
Date: Janvier 2026
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Union, Tuple
from dataclasses import dataclass
import logging

from ..utils.constants import REGIONS, TYPES_DOCUMENTS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Resultat d'une validation."""
    rule: str
    dataset: str
    passed: bool
    message: str
    severity: str = "info"  # "info", "warning", "error"
    details: Dict = None


class DataValidator:
    """
    Validateur de qualite des donnees.
    
    Cette classe fournit des methodes pour verifier la qualite,
    la coherence et l'integrite des donnees.
    
    Attributes:
        results: Liste des resultats de validation
        
    Example:
        >>> validator = DataValidator()
        >>> validator.validate_all(datasets)
        >>> validator.print_summary()
    """
    
    def __init__(self):
        """Initialise le validateur."""
        self.results: List[ValidationResult] = []
    
    def clear_results(self) -> None:
        """Reinitialise les resultats."""
        self.results = []
    
    def _add_result(self, 
                    rule: str,
                    dataset: str,
                    passed: bool,
                    message: str,
                    severity: str = "info",
                    details: Dict = None) -> None:
        """Ajoute un resultat de validation."""
        self.results.append(ValidationResult(
            rule=rule,
            dataset=dataset,
            passed=passed,
            message=message,
            severity=severity,
            details=details
        ))
    
    # =========================================================================
    # REGLES DE VALIDATION GENERIQUES
    # =========================================================================
    
    def check_not_empty(self, 
                        df: pd.DataFrame, 
                        name: str = "dataset") -> bool:
        """Verifie que le DataFrame n'est pas vide."""
        passed = len(df) > 0
        self._add_result(
            rule="not_empty",
            dataset=name,
            passed=passed,
            message=f"contient {len(df)} lignes" if passed else "DataFrame vide",
            severity="error" if not passed else "info"
        )
        return passed
    
    def check_required_columns(self,
                               df: pd.DataFrame,
                               required: List[str],
                               name: str = "dataset") -> bool:
        """Verifie la presence des colonnes requises."""
        missing = [col for col in required if col not in df.columns]
        passed = len(missing) == 0
        
        self._add_result(
            rule="required_columns",
            dataset=name,
            passed=passed,
            message="toutes les colonnes requises presentes" if passed 
                    else f"colonnes manquantes: {missing}",
            severity="error" if not passed else "info",
            details={"missing_columns": missing} if missing else None
        )
        return passed
    
    def check_no_duplicates(self,
                            df: pd.DataFrame,
                            subset: List[str] = None,
                            name: str = "dataset") -> bool:
        """Verifie l'absence de doublons."""
        duplicates = df.duplicated(subset=subset).sum()
        passed = duplicates == 0
        
        self._add_result(
            rule="no_duplicates",
            dataset=name,
            passed=passed,
            message="pas de doublons" if passed 
                    else f"{duplicates} doublons trouves",
            severity="warning" if not passed else "info",
            details={"duplicate_count": duplicates}
        )
        return passed
    
    def check_missing_values(self,
                             df: pd.DataFrame,
                             max_pct: float = 0.05,
                             name: str = "dataset") -> bool:
        """Verifie le taux de valeurs manquantes."""
        missing_pct = df.isna().sum() / len(df)
        problem_cols = missing_pct[missing_pct > max_pct]
        passed = len(problem_cols) == 0
        
        self._add_result(
            rule="missing_values",
            dataset=name,
            passed=passed,
            message="valeurs manquantes sous controle" if passed 
                    else f"{len(problem_cols)} colonnes avec >{max_pct*100}% de valeurs manquantes",
            severity="warning" if not passed else "info",
            details={"problem_columns": problem_cols.to_dict()} if not passed else None
        )
        return passed
    
    def check_value_range(self,
                          df: pd.DataFrame,
                          column: str,
                          min_val: float = None,
                          max_val: float = None,
                          name: str = "dataset") -> bool:
        """Verifie que les valeurs sont dans une plage."""
        if column not in df.columns:
            return True
        
        values = df[column].dropna()
        violations = 0
        
        if min_val is not None:
            violations += (values < min_val).sum()
        if max_val is not None:
            violations += (values > max_val).sum()
        
        passed = violations == 0
        
        self._add_result(
            rule="value_range",
            dataset=f"{name}.{column}",
            passed=passed,
            message="valeurs dans les limites" if passed 
                    else f"{violations} valeurs hors limites [{min_val}, {max_val}]",
            severity="warning" if not passed else "info"
        )
        return passed
    
    def check_categorical_values(self,
                                 df: pd.DataFrame,
                                 column: str,
                                 valid_values: List[str],
                                 name: str = "dataset") -> bool:
        """Verifie que les valeurs categorielles sont valides."""
        if column not in df.columns:
            return True
        
        values = df[column].dropna().unique()
        invalid = [v for v in values if v not in valid_values]
        passed = len(invalid) == 0
        
        self._add_result(
            rule="categorical_values",
            dataset=f"{name}.{column}",
            passed=passed,
            message="toutes les valeurs sont valides" if passed 
                    else f"{len(invalid)} valeurs invalides: {invalid[:5]}",
            severity="warning" if not passed else "info"
        )
        return passed
    
    def check_referential_integrity(self,
                                    df_child: pd.DataFrame,
                                    df_parent: pd.DataFrame,
                                    child_col: str,
                                    parent_col: str,
                                    child_name: str = "enfant",
                                    parent_name: str = "parent") -> bool:
        """Verifie l'integrite referentielle."""
        child_values = set(df_child[child_col].dropna().unique())
        parent_values = set(df_parent[parent_col].dropna().unique())
        
        orphans = child_values - parent_values
        passed = len(orphans) == 0
        
        self._add_result(
            rule="referential_integrity",
            dataset=f"{child_name}.{child_col}",
            passed=passed,
            message="integrite referentielle OK" if passed 
                    else f"{len(orphans)} valeurs orphelines",
            severity="warning" if not passed else "info",
            details={"orphan_values": list(orphans)[:10]} if orphans else None
        )
        return passed
    
    # =========================================================================
    # VALIDATIONS SPECIFIQUES PAR DATASET
    # =========================================================================
    
    def validate_demandes(self, df: pd.DataFrame) -> Dict[str, bool]:
        """Valide le dataset des demandes."""
        logger.info("[VALID] Validation: demandes_service_public")
        
        results = {}
        
        # Presence des donnees
        results['not_empty'] = self.check_not_empty(df, "demandes")
        
        # Colonnes requises
        required_cols = [
            'region', 'type_document', 'nombre_demandes', 
            'delai_traitement_jours', 'taux_rejet'
        ]
        results['required_columns'] = self.check_required_columns(
            df, required_cols, "demandes"
        )
        
        # Doublons
        results['no_duplicates'] = self.check_no_duplicates(df, name="demandes")
        
        # Valeurs categorielles
        results['valid_regions'] = self.check_categorical_values(
            df, 'region', REGIONS, "demandes"
        )
        results['valid_documents'] = self.check_categorical_values(
            df, 'type_document', TYPES_DOCUMENTS, "demandes"
        )
        
        # Plages de valeurs
        results['nombre_demandes_range'] = self.check_value_range(
            df, 'nombre_demandes', min_val=0, max_val=10000, name="demandes"
        )
        results['delai_range'] = self.check_value_range(
            df, 'delai_traitement_jours', min_val=0, max_val=365, name="demandes"
        )
        results['taux_rejet_range'] = self.check_value_range(
            df, 'taux_rejet', min_val=0, max_val=1, name="demandes"
        )
        
        # Valeurs manquantes
        results['missing_values'] = self.check_missing_values(
            df, max_pct=0.10, name="demandes"
        )
        
        return results
    
    def validate_centres(self, df: pd.DataFrame) -> Dict[str, bool]:
        """Valide le dataset des centres."""
        logger.info("[VALID] Validation: centres_service")
        
        results = {}
        
        results['not_empty'] = self.check_not_empty(df, "centres")
        
        required_cols = ['centre_id', 'nom_centre', 'region', 'commune']
        results['required_columns'] = self.check_required_columns(
            df, required_cols, "centres"
        )
        
        results['no_duplicates'] = self.check_no_duplicates(
            df, subset=['centre_id'], name="centres"
        )
        
        # Coordonnees GPS
        results['latitude_range'] = self.check_value_range(
            df, 'latitude', min_val=5, max_val=12, name="centres"
        )
        results['longitude_range'] = self.check_value_range(
            df, 'longitude', min_val=-0.5, max_val=2.5, name="centres"
        )
        results['capacite_range'] = self.check_value_range(
            df, 'personnel_capacite_jour', min_val=1, max_val=500, name="centres"
        )
        
        return results
    
    def validate_all(self, 
                     datasets: Dict[str, pd.DataFrame]) -> Dict[str, Dict[str, bool]]:
        """
        Valide tous les datasets.
        
        Args:
            datasets: Dictionnaire des DataFrames
        
        Returns:
            Dictionnaire des resultats par dataset
        """
        all_results = {}
        
        if 'demandes' in datasets:
            all_results['demandes'] = self.validate_demandes(datasets['demandes'])
        
        if 'centres' in datasets:
            all_results['centres'] = self.validate_centres(datasets['centres'])
        
        # Validation generique pour les autres datasets
        for name, df in datasets.items():
            if name not in all_results:
                all_results[name] = {
                    'not_empty': self.check_not_empty(df, name),
                    'missing_values': self.check_missing_values(df, max_pct=0.15, name=name)
                }
        
        return all_results
    
    def get_summary(self) -> pd.DataFrame:
        """Retourne un resume des validations."""
        return pd.DataFrame([
            {
                "Dataset": r.dataset,
                "Regle": r.rule,
                "Statut": "OK" if r.passed else "ECHEC",
                "Message": r.message,
                "Severite": r.severity
            }
            for r in self.results
        ])
    
    def print_summary(self) -> None:
        """Affiche un resume des validations."""
        passed = sum(1 for r in self.results if r.passed)
        warnings = sum(1 for r in self.results 
                       if not r.passed and r.severity == "warning")
        errors = sum(1 for r in self.results 
                     if not r.passed and r.severity == "error")
        
        print("\n" + "=" * 60)
        print("RESUME DE VALIDATION")
        print("=" * 60)
        print(f"[OK] Succes: {passed}")
        print(f"[WARN] Avertissements: {warnings}")
        print(f"[ERROR] Erreurs: {errors}")
        print("=" * 60 + "\n")
        
        for r in self.results:
            status = "OK" if r.passed else ("WARN" if r.severity == "warning" else "ERROR")
            print(f"  [{status}] {r.dataset}: {r.message}")
