"""
Module de chargement des donnees.
==================================

Classe DataLoader pour charger et preparer les donnees brutes
depuis les fichiers CSV du projet.

Auteur: Data Analyst - Togo Datalab
Date: Janvier 2026
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Optional, List, Union
import logging

from ..utils.constants import DATA_FILES

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataLoader:
    """
    Gestionnaire de chargement des donnees.
    
    Cette classe centralise le chargement de tous les fichiers de donnees
    et fournit un acces unifie a l'ensemble des datasets.
    
    Attributes:
        data_path: Chemin vers le dossier contenant les donnees
        datasets: Dictionnaire des DataFrames charges
        
    Example:
        >>> loader = DataLoader("./data")
        >>> loader.load_all()
        >>> demandes = loader.get_dataset("demandes")
    """
    
    def __init__(self, data_path: Union[str, Path]):
        """
        Initialise le DataLoader.
        
        Args:
            data_path: Chemin vers le dossier des donnees CSV
        """
        self.data_path = Path(data_path)
        self.datasets: Dict[str, pd.DataFrame] = {}
        self._validate_path()
    
    def _validate_path(self) -> None:
        """Verifie que le chemin des donnees existe."""
        if not self.data_path.exists():
            raise FileNotFoundError(
                f"Le dossier de donnees n'existe pas: {self.data_path}"
            )
    
    def load_all(self, verbose: bool = True) -> Dict[str, pd.DataFrame]:
        """
        Charge tous les fichiers de donnees.
        
        Args:
            verbose: Afficher les messages de progression
        
        Returns:
            Dictionnaire de tous les DataFrames charges
        """
        if verbose:
            logger.info("=" * 60)
            logger.info("CHARGEMENT DES DONNEES")
            logger.info("=" * 60)
        
        for name, filename in DATA_FILES.items():
            self.load_dataset(name, filename, verbose)
        
        if verbose:
            logger.info("-" * 60)
            logger.info(f"[OK] {len(self.datasets)} fichiers charges avec succes")
            total_rows = sum(len(df) for df in self.datasets.values())
            logger.info(f"[INFO] Total: {total_rows:,} enregistrements")
        
        return self.datasets
    
    def load_dataset(self, 
                     name: str, 
                     filename: str,
                     verbose: bool = True) -> Optional[pd.DataFrame]:
        """
        Charge un fichier de donnees specifique.
        
        Args:
            name: Nom du dataset (cle dans le dictionnaire)
            filename: Nom du fichier CSV
            verbose: Afficher les messages
        
        Returns:
            DataFrame charge ou None si erreur
        """
        filepath = self.data_path / filename
        
        if not filepath.exists():
            logger.warning(f"[WARN] Fichier non trouve: {filename}")
            return None
        
        try:
            # Chargement avec gestion des encodages
            df = self._load_csv_safe(filepath)
            
            # Nettoyage basique des noms de colonnes
            df.columns = df.columns.str.strip()
            
            # Stockage
            self.datasets[name] = df
            
            if verbose:
                logger.info(
                    f"[LOAD] {name}: {len(df):,} lignes x {len(df.columns)} colonnes"
                )
            
            return df
            
        except Exception as e:
            logger.error(f"[ERROR] Erreur lors du chargement de {filename}: {e}")
            return None
    
    def _load_csv_safe(self, 
                       filepath: Path,
                       encodings: List[str] = None) -> pd.DataFrame:
        """
        Charge un CSV en testant plusieurs encodages.
        
        Args:
            filepath: Chemin du fichier
            encodings: Liste d'encodages a tester
        
        Returns:
            DataFrame charge
        """
        if encodings is None:
            encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
        
        for encoding in encodings:
            try:
                return pd.read_csv(
                    filepath,
                    encoding=encoding,
                    sep=',',
                    low_memory=False
                )
            except UnicodeDecodeError:
                continue
            except Exception as e:
                # Essayer avec point-virgule comme separateur
                try:
                    return pd.read_csv(
                        filepath,
                        encoding=encoding,
                        sep=';',
                        low_memory=False
                    )
                except:
                    continue
        
        raise ValueError(f"Impossible de lire le fichier avec les encodages testes")
    
    def get_dataset(self, name: str) -> pd.DataFrame:
        """
        Recupere un dataset charge.
        
        Args:
            name: Nom du dataset
        
        Returns:
            DataFrame demande
            
        Raises:
            KeyError: Si le dataset n'est pas charge
        """
        if name not in self.datasets:
            raise KeyError(
                f"Dataset '{name}' non trouve. "
                f"Datasets disponibles: {list(self.datasets.keys())}"
            )
        return self.datasets[name]
    
    def get_info(self) -> pd.DataFrame:
        """
        Retourne un resume de tous les datasets charges.
        
        Returns:
            DataFrame avec les informations sur chaque dataset
        """
        info = []
        for name, df in self.datasets.items():
            memory_mb = df.memory_usage(deep=True).sum() / 1024**2
            info.append({
                "Dataset": name,
                "Lignes": len(df),
                "Colonnes": len(df.columns),
                "Memoire (MB)": round(memory_mb, 2),
                "Valeurs manquantes (%)": round(
                    df.isna().sum().sum() / df.size * 100, 2
                )
            })
        
        return pd.DataFrame(info)
    
    def describe_dataset(self, name: str) -> Dict:
        """
        Fournit une description detaillee d'un dataset.
        
        Args:
            name: Nom du dataset
        
        Returns:
            Dictionnaire avec description complete
        """
        df = self.get_dataset(name)
        
        return {
            "name": name,
            "shape": df.shape,
            "columns": list(df.columns),
            "dtypes": df.dtypes.to_dict(),
            "memory_mb": df.memory_usage(deep=True).sum() / 1024**2,
            "missing_values": df.isna().sum().to_dict(),
            "missing_pct": (df.isna().sum() / len(df) * 100).to_dict(),
            "duplicates": df.duplicated().sum(),
            "sample": df.head(3).to_dict("records")
        }
    
    def get_column_types(self, name: str) -> Dict[str, List[str]]:
        """
        Categorise les colonnes par type.
        
        Args:
            name: Nom du dataset
        
        Returns:
            Dictionnaire avec colonnes par categorie
        """
        df = self.get_dataset(name)
        
        return {
            "numeriques": df.select_dtypes(include=[np.number]).columns.tolist(),
            "textuelles": df.select_dtypes(include=['object', 'string']).columns.tolist(),
            "temporelles": df.select_dtypes(include=['datetime64']).columns.tolist(),
            "booleennes": df.select_dtypes(include=['bool']).columns.tolist()
        }
    
    def merge_datasets(self,
                       left_name: str,
                       right_name: str,
                       on: Union[str, List[str]],
                       how: str = "left",
                       suffix: tuple = ("_x", "_y")) -> pd.DataFrame:
        """
        Fusionne deux datasets.
        
        Args:
            left_name: Nom du dataset de gauche
            right_name: Nom du dataset de droite
            on: Colonne(s) de jointure
            how: Type de jointure
            suffix: Suffixes pour les colonnes dupliquees
        
        Returns:
            DataFrame fusionne
        """
        left_df = self.get_dataset(left_name)
        right_df = self.get_dataset(right_name)
        
        return pd.merge(left_df, right_df, on=on, how=how, suffixes=suffix)
    
    def export_dataset(self,
                       name: str,
                       output_path: Union[str, Path],
                       format: str = "csv") -> None:
        """
        Exporte un dataset vers un fichier.
        
        Args:
            name: Nom du dataset
            output_path: Chemin de sortie
            format: Format d'export ("csv", "excel", "parquet")
        """
        df = self.get_dataset(name)
        output_path = Path(output_path)
        
        if format == "csv":
            df.to_csv(output_path, index=False, encoding='utf-8')
        elif format == "excel":
            df.to_excel(output_path, index=False)
        elif format == "parquet":
            df.to_parquet(output_path, index=False)
        else:
            raise ValueError(f"Format non supporte: {format}")
        
        logger.info(f"[OK] Dataset '{name}' exporte vers {output_path}")
