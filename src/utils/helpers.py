"""
Fonctions utilitaires réutilisables.
=====================================

Ce module contient des fonctions helpers utilisées dans tout le projet
pour le formatage, les calculs statistiques de base et diverses opérations communes.

Auteur: Data Analyst - Togo Datalab
Date: Janvier 2026
"""

import pandas as pd
import numpy as np
from typing import Union, Optional, List, Any
from datetime import datetime, timedelta
import warnings

from .constants import CURRENCY_SYMBOL, DECIMAL_PLACES, DATE_FORMAT


# =============================================================================
# FONCTIONS DE FORMATAGE
# =============================================================================

def format_number(value: Union[int, float], 
                  decimal_places: int = 0,
                  thousands_sep: str = " ") -> str:
    """
    Formate un nombre avec séparateur de milliers.
    
    Args:
        value: Valeur numérique à formater
        decimal_places: Nombre de décimales (défaut: 0)
        thousands_sep: Séparateur de milliers (défaut: espace)
    
    Returns:
        Chaîne formatée
        
    Example:
        >>> format_number(1234567.89, decimal_places=2)
        '1 234 567,89'
    """
    if pd.isna(value):
        return "N/A"
    
    if decimal_places > 0:
        formatted = f"{value:,.{decimal_places}f}"
    else:
        formatted = f"{int(value):,}"
    
    # Remplacer les séparateurs par défaut par les séparateurs français
    formatted = formatted.replace(",", thousands_sep)
    formatted = formatted.replace(".", ",")
    
    return formatted


def format_percentage(value: Union[int, float], 
                      decimal_places: int = 1,
                      multiply: bool = True) -> str:
    """
    Formate une valeur en pourcentage.
    
    Args:
        value: Valeur à formater
        decimal_places: Nombre de décimales
        multiply: Si True, multiplie par 100 (pour les ratios 0-1)
    
    Returns:
        Chaîne formatée avec symbole %
        
    Example:
        >>> format_percentage(0.1234)
        '12,3%'
    """
    if pd.isna(value):
        return "N/A"
    
    if multiply:
        value = value * 100
    
    return f"{value:.{decimal_places}f}%".replace(".", ",")


def format_currency(value: Union[int, float],
                    symbol: str = CURRENCY_SYMBOL,
                    decimal_places: int = 0) -> str:
    """
    Formate une valeur monétaire.
    
    Args:
        value: Montant à formater
        symbol: Symbole de la devise
        decimal_places: Nombre de décimales
    
    Returns:
        Chaîne formatée avec devise
        
    Example:
        >>> format_currency(1500000)
        '1 500 000 FCFA'
    """
    if pd.isna(value):
        return "N/A"
    
    formatted_value = format_number(value, decimal_places)
    return f"{formatted_value} {symbol}"


def format_duration(days: Union[int, float]) -> str:
    """
    Formate une durée en jours de manière lisible.
    
    Args:
        days: Nombre de jours
    
    Returns:
        Chaîne formatée (ex: "2 semaines 3 jours")
    """
    if pd.isna(days):
        return "N/A"
    
    days = int(days)
    
    if days == 0:
        return "Même jour"
    elif days == 1:
        return "1 jour"
    elif days < 7:
        return f"{days} jours"
    elif days < 30:
        weeks = days // 7
        remaining_days = days % 7
        if remaining_days == 0:
            return f"{weeks} semaine{'s' if weeks > 1 else ''}"
        return f"{weeks} sem. {remaining_days} j"
    else:
        months = days // 30
        remaining_days = days % 30
        if remaining_days == 0:
            return f"{months} mois"
        return f"{months} mois {remaining_days} j"


# =============================================================================
# FONCTIONS STATISTIQUES
# =============================================================================

def calculate_growth_rate(current: float, previous: float) -> Optional[float]:
    """
    Calcule le taux de croissance entre deux valeurs.
    
    Args:
        current: Valeur actuelle
        previous: Valeur précédente
    
    Returns:
        Taux de croissance (ratio, pas pourcentage)
    """
    if previous == 0 or pd.isna(previous) or pd.isna(current):
        return None
    return (current - previous) / previous


def calculate_percentile(series: pd.Series, percentile: float) -> float:
    """
    Calcule un percentile d'une série.
    
    Args:
        series: Série pandas
        percentile: Percentile souhaité (0-100)
    
    Returns:
        Valeur du percentile
    """
    return series.quantile(percentile / 100)


def calculate_coefficient_variation(series: pd.Series) -> Optional[float]:
    """
    Calcule le coefficient de variation (écart-type / moyenne).
    
    Args:
        series: Série pandas
    
    Returns:
        Coefficient de variation
    """
    mean = series.mean()
    if mean == 0 or pd.isna(mean):
        return None
    return series.std() / mean


def detect_outliers_iqr(series: pd.Series, 
                        multiplier: float = 1.5) -> pd.Series:
    """
    Détecte les valeurs aberrantes avec la méthode IQR.
    
    Args:
        series: Série pandas
        multiplier: Multiplicateur IQR (défaut: 1.5)
    
    Returns:
        Série booléenne (True = outlier)
    """
    Q1 = series.quantile(0.25)
    Q3 = series.quantile(0.75)
    IQR = Q3 - Q1
    
    lower_bound = Q1 - multiplier * IQR
    upper_bound = Q3 + multiplier * IQR
    
    return (series < lower_bound) | (series > upper_bound)


def get_distribution_stats(series: pd.Series) -> dict:
    """
    Calcule les statistiques descriptives complètes d'une série.
    
    Args:
        series: Série pandas numérique
    
    Returns:
        Dictionnaire avec toutes les statistiques
    """
    return {
        "count": series.count(),
        "missing": series.isna().sum(),
        "missing_pct": series.isna().mean(),
        "mean": series.mean(),
        "median": series.median(),
        "std": series.std(),
        "min": series.min(),
        "max": series.max(),
        "q1": series.quantile(0.25),
        "q3": series.quantile(0.75),
        "iqr": series.quantile(0.75) - series.quantile(0.25),
        "skewness": series.skew(),
        "kurtosis": series.kurtosis(),
        "cv": calculate_coefficient_variation(series)
    }


# =============================================================================
# FONCTIONS DE MANIPULATION DE DONNÉES
# =============================================================================

def safe_divide(numerator: Union[float, pd.Series], 
                denominator: Union[float, pd.Series],
                default: float = 0.0) -> Union[float, pd.Series]:
    """
    Division sûre évitant les erreurs de division par zéro.
    
    Args:
        numerator: Numérateur
        denominator: Dénominateur
        default: Valeur par défaut si division impossible
    
    Returns:
        Résultat de la division ou valeur par défaut
    """
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        
        if isinstance(denominator, pd.Series):
            result = numerator / denominator
            result = result.replace([np.inf, -np.inf], default)
            result = result.fillna(default)
        else:
            if denominator == 0 or pd.isna(denominator):
                return default
            result = numerator / denominator
    
    return result


def categorize_value(value: float, 
                     thresholds: List[float],
                     labels: List[str]) -> str:
    """
    Catégorise une valeur selon des seuils.
    
    Args:
        value: Valeur à catégoriser
        thresholds: Liste des seuils (triés croissants)
        labels: Labels pour chaque catégorie (len = len(thresholds) + 1)
    
    Returns:
        Label de la catégorie
        
    Example:
        >>> categorize_value(15, [10, 20, 30], ["Faible", "Moyen", "Élevé", "Critique"])
        'Moyen'
    """
    if pd.isna(value):
        return "N/A"
    
    for i, threshold in enumerate(thresholds):
        if value <= threshold:
            return labels[i]
    
    return labels[-1]


def parse_date_flexible(date_string: str) -> Optional[datetime]:
    """
    Parse une date avec plusieurs formats possibles.
    
    Args:
        date_string: Chaîne de date
    
    Returns:
        Objet datetime ou None
    """
    formats = [
        "%Y-%m-%d",
        "%d/%m/%Y",
        "%d-%m-%Y",
        "%Y/%m/%d",
        "%d.%m.%Y"
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(str(date_string), fmt)
        except (ValueError, TypeError):
            continue
    
    return None


def get_period_label(date: datetime, 
                     period_type: str = "month") -> str:
    """
    Génère un label de période pour une date.
    
    Args:
        date: Objet datetime
        period_type: Type de période ("month", "quarter", "semester", "year")
    
    Returns:
        Label de la période
    """
    if period_type == "month":
        months_fr = ["Jan", "Fév", "Mar", "Avr", "Mai", "Juin",
                     "Juil", "Août", "Sep", "Oct", "Nov", "Déc"]
        return f"{months_fr[date.month - 1]} {date.year}"
    
    elif period_type == "quarter":
        quarter = (date.month - 1) // 3 + 1
        return f"T{quarter} {date.year}"
    
    elif period_type == "semester":
        semester = 1 if date.month <= 6 else 2
        return f"S{semester} {date.year}"
    
    elif period_type == "year":
        return str(date.year)
    
    return str(date)


# =============================================================================
# FONCTIONS DE VALIDATION
# =============================================================================

def validate_dataframe(df: pd.DataFrame,
                       required_columns: List[str],
                       name: str = "DataFrame") -> bool:
    """
    Valide qu'un DataFrame contient les colonnes requises.
    
    Args:
        df: DataFrame à valider
        required_columns: Liste des colonnes obligatoires
        name: Nom du DataFrame pour le message d'erreur
    
    Returns:
        True si valide
        
    Raises:
        ValueError: Si colonnes manquantes
    """
    missing = set(required_columns) - set(df.columns)
    
    if missing:
        raise ValueError(
            f"{name}: Colonnes manquantes: {', '.join(missing)}"
        )
    
    return True


def ensure_numeric(series: pd.Series, 
                   column_name: str = "colonne") -> pd.Series:
    """
    Convertit une série en numérique, avec gestion des erreurs.
    
    Args:
        series: Série à convertir
        column_name: Nom de la colonne pour le message
    
    Returns:
        Série numérique
    """
    try:
        return pd.to_numeric(series, errors='coerce')
    except Exception as e:
        warnings.warn(f"Conversion numérique de '{column_name}' échouée: {e}")
        return series


# =============================================================================
# FONCTIONS D'AGRÉGATION
# =============================================================================

def aggregate_by_groups(df: pd.DataFrame,
                        group_cols: List[str],
                        agg_config: dict) -> pd.DataFrame:
    """
    Agrège un DataFrame selon une configuration.
    
    Args:
        df: DataFrame source
        group_cols: Colonnes de groupement
        agg_config: Configuration d'agrégation {col: func ou [funcs]}
    
    Returns:
        DataFrame agrégé
    """
    result = df.groupby(group_cols, as_index=False).agg(agg_config)
    
    # Aplatir les noms de colonnes multi-niveau si nécessaire
    if isinstance(result.columns, pd.MultiIndex):
        result.columns = ['_'.join(col).strip('_') for col in result.columns.values]
    
    return result


def create_crosstab_pct(df: pd.DataFrame,
                        row_col: str,
                        col_col: str,
                        normalize: str = "index") -> pd.DataFrame:
    """
    Crée un tableau croisé en pourcentages.
    
    Args:
        df: DataFrame source
        row_col: Colonne pour les lignes
        col_col: Colonne pour les colonnes
        normalize: Axe de normalisation ("index", "columns", "all")
    
    Returns:
        DataFrame du tableau croisé en pourcentages
    """
    ct = pd.crosstab(df[row_col], df[col_col], normalize=normalize)
    return ct * 100
