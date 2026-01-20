"""
Module d'Analyse Exploratoire des Données (EDA).
=================================================

Classe ExploratoryAnalysis pour effectuer une analyse complète
des données et générer des insights.

Auteur: Data Analyst - Togo Datalab
Date: Janvier 2026
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
import warnings

from ..utils.constants import (
    COLOR_PALETTE, REGIONS, TYPES_DOCUMENTS, 
    CHART_CONFIG, LABELS_FR
)
from ..utils.helpers import (
    format_number, format_percentage, get_distribution_stats,
    detect_outliers_iqr
)

# Configuration matplotlib
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['figure.figsize'] = CHART_CONFIG['figure_size']
plt.rcParams['figure.dpi'] = CHART_CONFIG['dpi']
plt.rcParams['font.family'] = CHART_CONFIG['font_family']

warnings.filterwarnings('ignore')


class ExploratoryAnalysis:
    """
    Classe pour l'analyse exploratoire des données.
    
    Fournit des méthodes pour:
    - Analyser la structure des données
    - Détecter les anomalies
    - Visualiser les distributions
    - Identifier les patterns temporels et spatiaux
    
    Attributes:
        datasets: Dictionnaire des DataFrames à analyser
        output_path: Chemin de sortie pour les visualisations
        
    Example:
        >>> eda = ExploratoryAnalysis(datasets, "./outputs/visualizations")
        >>> eda.run_full_analysis()
    """
    
    def __init__(self, 
                 datasets: Dict[str, pd.DataFrame],
                 output_path: str = "./outputs/visualizations"):
        """
        Initialise l'analyse exploratoire.
        
        Args:
            datasets: Dictionnaire des DataFrames
            output_path: Chemin pour sauvegarder les visualisations
        """
        self.datasets = datasets
        self.output_path = Path(output_path)
        self.output_path.mkdir(parents=True, exist_ok=True)
        
        # Résultats d'analyse
        self.insights: List[str] = []
        self.statistics: Dict[str, Dict] = {}
    
    # =========================================================================
    # ANALYSE STRUCTURELLE
    # =========================================================================
    
    def analyze_structure(self) -> pd.DataFrame:
        """
        Analyse la structure de tous les datasets.
        
        Returns:
            DataFrame récapitulatif de la structure
        """
        structure_info = []
        
        for name, df in self.datasets.items():
            # Types de colonnes
            num_cols = len(df.select_dtypes(include=[np.number]).columns)
            cat_cols = len(df.select_dtypes(include=['object', 'category']).columns)
            date_cols = len(df.select_dtypes(include=['datetime64']).columns)
            
            # Valeurs manquantes
            missing_total = df.isna().sum().sum()
            missing_pct = missing_total / df.size * 100
            
            # Doublons
            duplicates = df.duplicated().sum()
            
            structure_info.append({
                "Dataset": name,
                "Lignes": len(df),
                "Colonnes": len(df.columns),
                "Colonnes numériques": num_cols,
                "Colonnes textuelles": cat_cols,
                "Colonnes dates": date_cols,
                "Valeurs manquantes (%)": round(missing_pct, 2),
                "Doublons": duplicates,
                "Mémoire (MB)": round(df.memory_usage(deep=True).sum() / 1024**2, 2)
            })
        
        return pd.DataFrame(structure_info)
    
    def analyze_missing_values(self) -> Dict[str, pd.DataFrame]:
        """
        Analyse détaillée des valeurs manquantes par dataset.
        
        Returns:
            Dictionnaire de DataFrames avec les statistiques de valeurs manquantes
        """
        missing_analysis = {}
        
        for name, df in self.datasets.items():
            missing_stats = pd.DataFrame({
                "Colonne": df.columns,
                "Type": df.dtypes.values,
                "Valeurs non-nulles": df.notna().sum().values,
                "Valeurs manquantes": df.isna().sum().values,
                "% Manquant": (df.isna().sum() / len(df) * 100).round(2).values
            })
            
            missing_stats = missing_stats.sort_values(
                "% Manquant", ascending=False
            ).reset_index(drop=True)
            
            missing_analysis[name] = missing_stats
            
            # Insights
            high_missing = missing_stats[missing_stats["% Manquant"] > 10]
            if len(high_missing) > 0:
                self.insights.append(
                    f"[WARN] {name}: {len(high_missing)} colonnes avec >10% de valeurs manquantes"
                )
        
        return missing_analysis
    
    def analyze_duplicates(self) -> Dict[str, Dict]:
        """
        Analyse des doublons dans chaque dataset.
        
        Returns:
            Dictionnaire avec statistiques de doublons
        """
        duplicates_info = {}
        
        for name, df in self.datasets.items():
            full_duplicates = df.duplicated().sum()
            
            # Doublons par colonnes ID si existantes
            id_columns = [col for col in df.columns if 'id' in col.lower()]
            
            duplicates_info[name] = {
                "doublons_complets": full_duplicates,
                "pourcentage": round(full_duplicates / len(df) * 100, 2),
                "colonnes_id": id_columns
            }
            
            for id_col in id_columns:
                dup_count = df[id_col].duplicated().sum()
                duplicates_info[name][f"doublons_{id_col}"] = dup_count
        
        return duplicates_info
    
    # =========================================================================
    # ANALYSE DES DISTRIBUTIONS
    # =========================================================================
    
    def analyze_numeric_distributions(self, 
                                      dataset_name: str) -> pd.DataFrame:
        """
        Analyse les distributions des variables numériques.
        
        Args:
            dataset_name: Nom du dataset à analyser
        
        Returns:
            DataFrame avec statistiques descriptives
        """
        df = self.datasets[dataset_name]
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        stats_list = []
        for col in numeric_cols:
            stats = get_distribution_stats(df[col])
            stats["Colonne"] = col
            stats_list.append(stats)
        
        return pd.DataFrame(stats_list)[[
            "Colonne", "count", "missing_pct", "mean", "median", "std",
            "min", "q1", "q3", "max", "skewness", "cv"
        ]]
    
    def analyze_categorical_distributions(self,
                                          dataset_name: str,
                                          max_categories: int = 20) -> Dict[str, pd.DataFrame]:
        """
        Analyse les distributions des variables catégorielles.
        
        Args:
            dataset_name: Nom du dataset
            max_categories: Nombre max de catégories à afficher
        
        Returns:
            Dictionnaire avec les distributions par variable
        """
        df = self.datasets[dataset_name]
        cat_cols = df.select_dtypes(include=['object', 'category']).columns
        
        distributions = {}
        
        for col in cat_cols:
            value_counts = df[col].value_counts()
            
            if len(value_counts) > max_categories:
                value_counts = value_counts.head(max_categories)
            
            distributions[col] = pd.DataFrame({
                "Valeur": value_counts.index,
                "Effectif": value_counts.values,
                "Pourcentage": (value_counts / len(df) * 100).round(2).values
            })
        
        return distributions
    
    # =========================================================================
    # ANALYSES SPÉCIFIQUES MÉTIER
    # =========================================================================
    
    def analyze_demandes(self) -> Dict[str, Any]:
        """
        Analyse spécifique des demandes de documents.
        
        Returns:
            Dictionnaire avec les résultats d'analyse
        """
        if 'demandes' not in self.datasets:
            return {}
        
        df = self.datasets['demandes']
        
        analysis = {
            "total_demandes": df['nombre_demandes'].sum() if 'nombre_demandes' in df.columns else len(df),
            "demandes_par_region": {},
            "demandes_par_type": {},
            "delais": {},
            "rejets": {},
            "temporel": {}
        }
        
        # Par région
        if 'region' in df.columns and 'nombre_demandes' in df.columns:
            analysis["demandes_par_region"] = df.groupby('region')['nombre_demandes'].sum().to_dict()
        
        # Par type de document
        if 'type_document' in df.columns and 'nombre_demandes' in df.columns:
            analysis["demandes_par_type"] = df.groupby('type_document')['nombre_demandes'].sum().to_dict()
        
        # Délais
        if 'delai_traitement_jours' in df.columns:
            analysis["delais"] = {
                "moyen": df['delai_traitement_jours'].mean(),
                "median": df['delai_traitement_jours'].median(),
                "min": df['delai_traitement_jours'].min(),
                "max": df['delai_traitement_jours'].max(),
                "ecart_type": df['delai_traitement_jours'].std()
            }
            
            # Insights sur les delais
            if analysis["delais"]["moyen"] > 21:
                self.insights.append(
                    f"[WARN] Delai moyen eleve: {analysis['delais']['moyen']:.1f} jours"
                )
        
        # Rejets
        if 'taux_rejet' in df.columns:
            analysis["rejets"] = {
                "taux_moyen": df['taux_rejet'].mean(),
                "taux_max": df['taux_rejet'].max()
            }
            
            if analysis["rejets"]["taux_moyen"] > 0.10:
                self.insights.append(
                    f"[WARN] Taux de rejet moyen eleve: {analysis['rejets']['taux_moyen']*100:.1f}%"
                )
        
        # Analyse temporelle
        if 'date_demande' in df.columns:
            df_temp = df.copy()
            if not pd.api.types.is_datetime64_any_dtype(df_temp['date_demande']):
                df_temp['date_demande'] = pd.to_datetime(df_temp['date_demande'], errors='coerce')
            
            df_temp['mois'] = df_temp['date_demande'].dt.month
            
            if 'nombre_demandes' in df_temp.columns:
                monthly = df_temp.groupby('mois')['nombre_demandes'].sum()
                analysis["temporel"]["par_mois"] = monthly.to_dict()
        
        self.statistics['demandes'] = analysis
        return analysis
    
    def analyze_centres(self) -> Dict[str, Any]:
        """
        Analyse spécifique des centres de service.
        
        Returns:
            Dictionnaire avec les résultats d'analyse
        """
        if 'centres' not in self.datasets:
            return {}
        
        df = self.datasets['centres']
        
        analysis = {
            "total_centres": len(df),
            "par_region": {},
            "par_type": {},
            "capacite": {},
            "couverture": {}
        }
        
        # Par région
        if 'region' in df.columns:
            analysis["par_region"] = df['region'].value_counts().to_dict()
        
        # Par type
        if 'type_centre' in df.columns:
            analysis["par_type"] = df['type_centre'].value_counts().to_dict()
        
        # Capacité
        if 'personnel_capacite_jour' in df.columns:
            analysis["capacite"] = {
                "totale": df['personnel_capacite_jour'].sum(),
                "moyenne": df['personnel_capacite_jour'].mean(),
                "min": df['personnel_capacite_jour'].min(),
                "max": df['personnel_capacite_jour'].max()
            }
        
        # Distribution géographique
        if 'latitude' in df.columns and 'longitude' in df.columns:
            analysis["couverture"] = {
                "lat_min": df['latitude'].min(),
                "lat_max": df['latitude'].max(),
                "lon_min": df['longitude'].min(),
                "lon_max": df['longitude'].max()
            }
        
        self.statistics['centres'] = analysis
        return analysis
    
    def analyze_logs(self) -> Dict[str, Any]:
        """
        Analyse spécifique des logs d'activité.
        
        Returns:
            Dictionnaire avec les résultats d'analyse
        """
        if 'logs' not in self.datasets:
            return {}
        
        df = self.datasets['logs']
        
        # Filtrer uniquement les opérations de traitement
        df_traitement = df[df['type_operation'] == 'Traitement'] if 'type_operation' in df.columns else df
        
        analysis = {
            "total_operations": len(df),
            "operations_traitement": len(df_traitement),
            "performance": {},
            "rejets": {},
            "incidents": {}
        }
        
        if len(df_traitement) > 0:
            # Performance
            if 'nombre_traite' in df_traitement.columns:
                analysis["performance"]["total_traite"] = df_traitement['nombre_traite'].sum()
                analysis["performance"]["moyenne_jour"] = df_traitement['nombre_traite'].mean()
            
            if 'delai_effectif' in df_traitement.columns:
                analysis["performance"]["delai_moyen"] = df_traitement['delai_effectif'].mean()
            
            if 'temps_attente_moyen_minutes' in df_traitement.columns:
                analysis["performance"]["attente_moyenne"] = df_traitement['temps_attente_moyen_minutes'].mean()
            
            # Rejets
            if 'nombre_rejete' in df_traitement.columns:
                analysis["rejets"]["total"] = df_traitement['nombre_rejete'].sum()
                if 'nombre_traite' in df_traitement.columns:
                    total_traite = df_traitement['nombre_traite'].sum()
                    if total_traite > 0:
                        analysis["rejets"]["taux"] = analysis["rejets"]["total"] / total_traite
            
            # Raisons de rejet
            if 'raison_rejet' in df_traitement.columns:
                raisons = df_traitement[df_traitement['raison_rejet'] != 'N/A']['raison_rejet']
                if len(raisons) > 0:
                    analysis["rejets"]["raisons"] = raisons.value_counts().to_dict()
        
        # Incidents
        if 'incident_technique' in df.columns:
            incidents = df[df['incident_technique'] == 'Oui']
            analysis["incidents"]["total"] = len(incidents)
            analysis["incidents"]["pourcentage"] = len(incidents) / len(df) * 100
        
        self.statistics['logs'] = analysis
        return analysis
    
    # =========================================================================
    # VISUALISATIONS
    # =========================================================================
    
    def plot_missing_values_heatmap(self, 
                                    dataset_name: str,
                                    save: bool = True) -> plt.Figure:
        """
        Génère une heatmap des valeurs manquantes.
        
        Args:
            dataset_name: Nom du dataset
            save: Sauvegarder la figure
        
        Returns:
            Figure matplotlib
        """
        df = self.datasets[dataset_name]
        
        fig, ax = plt.subplots(figsize=(14, 8))
        
        # Matrice de valeurs manquantes
        missing_matrix = df.isna().astype(int)
        
        sns.heatmap(
            missing_matrix.T,
            cmap=['#2ecc71', '#e74c3c'],
            cbar_kws={'label': 'Manquant (1) / Présent (0)'},
            ax=ax
        )
        
        ax.set_title(f"Cartographie des valeurs manquantes - {dataset_name}", 
                     fontsize=14, fontweight='bold')
        ax.set_xlabel("Observations")
        ax.set_ylabel("Variables")
        
        plt.tight_layout()
        
        if save:
            filepath = self.output_path / f"missing_values_{dataset_name}.png"
            fig.savefig(filepath, dpi=150, bbox_inches='tight')
        
        return fig
    
    def plot_distribution(self,
                          dataset_name: str,
                          column: str,
                          kind: str = "auto",
                          save: bool = True) -> plt.Figure:
        """
        Visualise la distribution d'une variable.
        
        Args:
            dataset_name: Nom du dataset
            column: Nom de la colonne
            kind: Type de graphique ("hist", "box", "violin", "auto")
            save: Sauvegarder la figure
        
        Returns:
            Figure matplotlib
        """
        df = self.datasets[dataset_name]
        
        if column not in df.columns:
            raise ValueError(f"Colonne '{column}' non trouvée")
        
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        
        if np.issubdtype(df[column].dtype, np.number):
            # Histogramme
            axes[0].hist(
                df[column].dropna(), 
                bins=30, 
                color=COLOR_PALETTE['primary'],
                edgecolor='white',
                alpha=0.8
            )
            axes[0].axvline(
                df[column].mean(), 
                color=COLOR_PALETTE['danger'], 
                linestyle='--',
                label=f'Moyenne: {df[column].mean():.2f}'
            )
            axes[0].axvline(
                df[column].median(), 
                color=COLOR_PALETTE['warning'], 
                linestyle='-.',
                label=f'Médiane: {df[column].median():.2f}'
            )
            axes[0].set_xlabel(column)
            axes[0].set_ylabel("Fréquence")
            axes[0].set_title(f"Distribution de {column}")
            axes[0].legend()
            
            # Boxplot
            bp = axes[1].boxplot(
                df[column].dropna(),
                patch_artist=True,
                boxprops=dict(facecolor=COLOR_PALETTE['secondary'], alpha=0.7)
            )
            axes[1].set_ylabel(column)
            axes[1].set_title(f"Boxplot de {column}")
            
        else:
            # Variable catégorielle
            value_counts = df[column].value_counts().head(15)
            
            bars = axes[0].barh(
                value_counts.index, 
                value_counts.values,
                color=COLOR_PALETTE['primary'],
                alpha=0.8
            )
            axes[0].set_xlabel("Effectif")
            axes[0].set_title(f"Distribution de {column}")
            
            # Pie chart
            axes[1].pie(
                value_counts.values[:8],
                labels=value_counts.index[:8],
                autopct='%1.1f%%',
                colors=list(COLOR_PALETTE.values())[:8]
            )
            axes[1].set_title(f"Répartition de {column}")
        
        plt.suptitle(f"Analyse de {column} - {dataset_name}", 
                     fontsize=14, fontweight='bold', y=1.02)
        plt.tight_layout()
        
        if save:
            filepath = self.output_path / f"distribution_{dataset_name}_{column}.png"
            fig.savefig(filepath, dpi=150, bbox_inches='tight')
        
        return fig
    
    def plot_demandes_by_region(self, save: bool = True) -> plt.Figure:
        """
        Visualise les demandes par région.
        
        Args:
            save: Sauvegarder la figure
        
        Returns:
            Figure matplotlib
        """
        if 'demandes' not in self.datasets:
            raise ValueError("Dataset 'demandes' non disponible")
        
        df = self.datasets['demandes']
        
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))
        
        # Nombre de demandes par région
        if 'nombre_demandes' in df.columns:
            region_data = df.groupby('region')['nombre_demandes'].sum().sort_values(ascending=True)
        else:
            region_data = df['region'].value_counts().sort_values(ascending=True)
        
        colors = [COLOR_PALETTE.get(r.lower(), COLOR_PALETTE['primary']) for r in region_data.index]
        
        axes[0].barh(region_data.index, region_data.values, color=colors)
        axes[0].set_xlabel("Nombre de demandes")
        axes[0].set_title("Demandes par région")
        
        # Ajouter valeurs
        for i, v in enumerate(region_data.values):
            axes[0].text(v + 0.01 * max(region_data.values), i, 
                        format_number(int(v)), va='center', fontsize=9)
        
        # Délai moyen par région
        if 'delai_traitement_jours' in df.columns:
            delai_data = df.groupby('region')['delai_traitement_jours'].mean().sort_values()
            
            bars = axes[1].barh(delai_data.index, delai_data.values, 
                               color=[COLOR_PALETTE.get(r.lower(), COLOR_PALETTE['secondary']) 
                                     for r in delai_data.index])
            axes[1].axvline(21, color=COLOR_PALETTE['danger'], linestyle='--', 
                           label='Seuil critique (21j)')
            axes[1].set_xlabel("Délai moyen (jours)")
            axes[1].set_title("Délai moyen de traitement par région")
            axes[1].legend()
        
        plt.suptitle("Analyse des demandes par région", 
                     fontsize=14, fontweight='bold', y=1.02)
        plt.tight_layout()
        
        if save:
            filepath = self.output_path / "demandes_par_region.png"
            fig.savefig(filepath, dpi=150, bbox_inches='tight')
        
        return fig
    
    def plot_demandes_by_document_type(self, save: bool = True) -> plt.Figure:
        """
        Visualise les demandes par type de document.
        
        Args:
            save: Sauvegarder la figure
        
        Returns:
            Figure matplotlib
        """
        if 'demandes' not in self.datasets:
            raise ValueError("Dataset 'demandes' non disponible")
        
        df = self.datasets['demandes']
        
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        
        # 1. Répartition par type de document
        if 'nombre_demandes' in df.columns:
            type_data = df.groupby('type_document')['nombre_demandes'].sum()
        else:
            type_data = df['type_document'].value_counts()
        
        axes[0, 0].pie(
            type_data.values,
            labels=type_data.index,
            autopct='%1.1f%%',
            colors=list(COLOR_PALETTE.values())[:len(type_data)],
            explode=[0.02] * len(type_data)
        )
        axes[0, 0].set_title("Répartition par type de document")
        
        # 2. Délai par type
        if 'delai_traitement_jours' in df.columns:
            delai_by_type = df.groupby('type_document')['delai_traitement_jours'].mean().sort_values()
            
            axes[0, 1].barh(delai_by_type.index, delai_by_type.values,
                           color=COLOR_PALETTE['secondary'])
            axes[0, 1].axvline(14, color=COLOR_PALETTE['warning'], linestyle='--',
                              label='Objectif (14j)')
            axes[0, 1].axvline(21, color=COLOR_PALETTE['danger'], linestyle='--',
                              label='Seuil critique (21j)')
            axes[0, 1].set_xlabel("Délai moyen (jours)")
            axes[0, 1].set_title("Délai moyen par type de document")
            axes[0, 1].legend()
        
        # 3. Taux de rejet par type
        if 'taux_rejet' in df.columns:
            rejet_by_type = df.groupby('type_document')['taux_rejet'].mean().sort_values() * 100
            
            colors = ['#2ecc71' if v < 10 else ('#f39c12' if v < 15 else '#e74c3c') 
                     for v in rejet_by_type.values]
            
            axes[1, 0].barh(rejet_by_type.index, rejet_by_type.values, color=colors)
            axes[1, 0].axvline(10, color=COLOR_PALETTE['warning'], linestyle='--',
                              label='Seuil alerte (10%)')
            axes[1, 0].set_xlabel("Taux de rejet (%)")
            axes[1, 0].set_title("Taux de rejet par type de document")
            axes[1, 0].legend()
        
        # 4. Volume et délai combinés
        if 'nombre_demandes' in df.columns and 'delai_traitement_jours' in df.columns:
            grouped = df.groupby('type_document').agg({
                'nombre_demandes': 'sum',
                'delai_traitement_jours': 'mean'
            })
            
            scatter = axes[1, 1].scatter(
                grouped['nombre_demandes'],
                grouped['delai_traitement_jours'],
                s=grouped['nombre_demandes'] / 100,
                c=range(len(grouped)),
                cmap='viridis',
                alpha=0.7
            )
            
            for idx, row in grouped.iterrows():
                axes[1, 1].annotate(
                    idx[:15], 
                    (row['nombre_demandes'], row['delai_traitement_jours']),
                    fontsize=8
                )
            
            axes[1, 1].set_xlabel("Volume de demandes")
            axes[1, 1].set_ylabel("Délai moyen (jours)")
            axes[1, 1].set_title("Volume vs Délai par type")
        
        plt.suptitle("Analyse par type de document", 
                     fontsize=14, fontweight='bold', y=1.02)
        plt.tight_layout()
        
        if save:
            filepath = self.output_path / "demandes_par_type.png"
            fig.savefig(filepath, dpi=150, bbox_inches='tight')
        
        return fig
    
    def plot_temporal_analysis(self, save: bool = True) -> plt.Figure:
        """
        Analyse temporelle des demandes.
        
        Args:
            save: Sauvegarder la figure
        
        Returns:
            Figure matplotlib
        """
        if 'demandes' not in self.datasets:
            raise ValueError("Dataset 'demandes' non disponible")
        
        df = self.datasets['demandes'].copy()
        
        # S'assurer que la date est au bon format
        if 'date_demande' in df.columns:
            if not pd.api.types.is_datetime64_any_dtype(df['date_demande']):
                df['date_demande'] = pd.to_datetime(df['date_demande'], errors='coerce')
        
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        
        # 1. Evolution mensuelle
        if 'date_demande' in df.columns and 'nombre_demandes' in df.columns:
            df['mois'] = df['date_demande'].dt.to_period('M')
            monthly = df.groupby('mois')['nombre_demandes'].sum()
            
            axes[0, 0].plot(range(len(monthly)), monthly.values, 
                           marker='o', color=COLOR_PALETTE['primary'])
            axes[0, 0].fill_between(range(len(monthly)), monthly.values, 
                                   alpha=0.3, color=COLOR_PALETTE['primary'])
            axes[0, 0].set_xticks(range(len(monthly)))
            axes[0, 0].set_xticklabels([str(m) for m in monthly.index], rotation=45)
            axes[0, 0].set_ylabel("Nombre de demandes")
            axes[0, 0].set_title("Évolution mensuelle des demandes")
        
        # 2. Par jour de la semaine
        if 'date_demande' in df.columns:
            df['jour_semaine'] = df['date_demande'].dt.dayofweek
            jours_fr = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']
            
            if 'nombre_demandes' in df.columns:
                by_day = df.groupby('jour_semaine')['nombre_demandes'].mean()
            else:
                by_day = df['jour_semaine'].value_counts().sort_index()
            
            axes[0, 1].bar(jours_fr[:len(by_day)], by_day.values, 
                          color=COLOR_PALETTE['secondary'])
            axes[0, 1].set_ylabel("Volume moyen")
            axes[0, 1].set_title("Demandes par jour de la semaine")
            axes[0, 1].tick_params(axis='x', rotation=45)
        
        # 3. Évolution du délai moyen
        if 'date_demande' in df.columns and 'delai_traitement_jours' in df.columns:
            monthly_delai = df.groupby('mois')['delai_traitement_jours'].mean()
            
            axes[1, 0].plot(range(len(monthly_delai)), monthly_delai.values,
                           marker='s', color=COLOR_PALETTE['accent'])
            axes[1, 0].axhline(14, color=COLOR_PALETTE['warning'], linestyle='--',
                              label='Objectif (14j)')
            axes[1, 0].axhline(21, color=COLOR_PALETTE['danger'], linestyle='--',
                              label='Seuil critique (21j)')
            axes[1, 0].set_xticks(range(len(monthly_delai)))
            axes[1, 0].set_xticklabels([str(m) for m in monthly_delai.index], rotation=45)
            axes[1, 0].set_ylabel("Délai moyen (jours)")
            axes[1, 0].set_title("Évolution du délai moyen")
            axes[1, 0].legend()
        
        # 4. Évolution du taux de rejet
        if 'date_demande' in df.columns and 'taux_rejet' in df.columns:
            monthly_rejet = df.groupby('mois')['taux_rejet'].mean() * 100
            
            axes[1, 1].bar(range(len(monthly_rejet)), monthly_rejet.values,
                          color=COLOR_PALETTE['danger'], alpha=0.7)
            axes[1, 1].axhline(10, color=COLOR_PALETTE['warning'], linestyle='--',
                              label='Seuil alerte (10%)')
            axes[1, 1].set_xticks(range(len(monthly_rejet)))
            axes[1, 1].set_xticklabels([str(m) for m in monthly_rejet.index], rotation=45)
            axes[1, 1].set_ylabel("Taux de rejet (%)")
            axes[1, 1].set_title("Évolution du taux de rejet")
            axes[1, 1].legend()
        
        plt.suptitle("Analyse temporelle des demandes", 
                     fontsize=14, fontweight='bold', y=1.02)
        plt.tight_layout()
        
        if save:
            filepath = self.output_path / "analyse_temporelle.png"
            fig.savefig(filepath, dpi=150, bbox_inches='tight')
        
        return fig
    
    # =========================================================================
    # GÉNÉRATION DE RAPPORT
    # =========================================================================
    
    def run_full_analysis(self) -> Dict[str, Any]:
        """
        Exécute l'analyse exploratoire complète.
        
        Returns:
            Dictionnaire avec tous les résultats d'analyse
        """
        print("\n" + "=" * 60)
        print("ANALYSE EXPLORATOIRE DES DONNÉES (EDA)")
        print("=" * 60 + "\n")
        
        results = {
            "structure": self.analyze_structure(),
            "missing_values": self.analyze_missing_values(),
            "duplicates": self.analyze_duplicates()
        }
        
        # Analyses specifiques
        if 'demandes' in self.datasets:
            print("[ANALYSE] Analyse des demandes...")
            results["demandes_analysis"] = self.analyze_demandes()
            
            # Graphiques
            self.plot_demandes_by_region()
            self.plot_demandes_by_document_type()
            self.plot_temporal_analysis()
        
        if 'centres' in self.datasets:
            print("[ANALYSE] Analyse des centres...")
            results["centres_analysis"] = self.analyze_centres()
        
        if 'logs' in self.datasets:
            print("[ANALYSE] Analyse des logs...")
            results["logs_analysis"] = self.analyze_logs()
        
        # Résumé des insights
        results["insights"] = self.insights
        
        print("\n" + "-" * 60)
        print(f"[OK] Analyse terminee")
        print(f"[INFO] {len(self.insights)} insights identifies")
        print(f"[INFO] Visualisations sauvegardees dans: {self.output_path}")
        
        return results
    
    def generate_eda_report(self, output_path: str = None) -> str:
        """
        Génère un rapport markdown de l'EDA.
        
        Args:
            output_path: Chemin du fichier de sortie
        
        Returns:
            Contenu du rapport en markdown
        """
        report = []
        report.append("# Rapport d'Analyse Exploratoire des Données (EDA)\n")
        report.append(f"*Date: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}*\n\n")
        
        # Structure des données
        report.append("## 1. Structure des Données\n")
        structure = self.analyze_structure()
        report.append(structure.to_markdown(index=False))
        report.append("\n\n")
        
        # Statistiques clés
        if self.statistics:
            report.append("## 2. Statistiques Clés\n")
            
            if 'demandes' in self.statistics:
                stats = self.statistics['demandes']
                report.append("### Demandes\n")
                report.append(f"- **Total des demandes:** {format_number(stats.get('total_demandes', 0))}\n")
                
                if stats.get('delais'):
                    report.append(f"- **Délai moyen:** {stats['delais'].get('moyen', 0):.1f} jours\n")
                    report.append(f"- **Délai médian:** {stats['delais'].get('median', 0):.1f} jours\n")
                
                if stats.get('rejets'):
                    report.append(f"- **Taux de rejet moyen:** {stats['rejets'].get('taux_moyen', 0)*100:.1f}%\n")
            
            report.append("\n")
        
        # Insights
        report.append("## 3. Principaux Constats\n")
        if self.insights:
            for insight in self.insights:
                report.append(f"- {insight}\n")
        else:
            report.append("- Aucun insight critique identifié\n")
        
        report.append("\n")
        
        # Conclusion
        report.append("## 4. Conclusion\n")
        report.append("L'analyse exploratoire a permis d'identifier la structure des données, ")
        report.append("de détecter les anomalies et de mettre en évidence les premières tendances. ")
        report.append("Les données sont prêtes pour l'analyse approfondie et le calcul des KPI.\n")
        
        content = "".join(report)
        
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"[OK] Rapport EDA sauvegarde: {output_path}")
        
        return content
