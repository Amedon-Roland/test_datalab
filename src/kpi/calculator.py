"""
Module de calcul des KPI.
==========================

Classe KPICalculator pour calculer tous les indicateurs de performance
a partir des donnees nettoyees.

Auteur: Data Analyst - Togo Datalab
Date: Janvier 2026
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import logging

from .definitions import KPI_DEFINITIONS, KPIDefinition
from ..utils.helpers import safe_divide, format_number, format_percentage
from ..utils.constants import SEUILS_PERFORMANCE, REGIONS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class KPIResult:
    """Resultat du calcul d'un KPI."""
    kpi_id: str
    nom: str
    valeur: float
    unite: str
    statut: str  # "vert", "orange", "rouge"
    tendance: str  # "hausse", "baisse", "stable"
    variation: float = None
    details: Dict = None
    timestamp: str = None


class KPICalculator:
    """
    Calculateur de KPI.
    
    Cette classe centralise le calcul de tous les indicateurs de performance
    definis pour le pilotage du service public.
    
    Attributes:
        datasets: Dictionnaire des DataFrames sources
        results: Dictionnaire des resultats de calcul
        
    Example:
        >>> calculator = KPICalculator(cleaned_datasets)
        >>> calculator.calculate_all()
        >>> results = calculator.get_summary()
    """
    
    def __init__(self, datasets: Dict[str, pd.DataFrame]):
        """
        Initialise le calculateur avec les datasets.
        
        Args:
            datasets: Dictionnaire des DataFrames nettoyes
        """
        self.datasets = datasets
        self.results: Dict[str, KPIResult] = {}
        self._timestamp = datetime.now().isoformat()
    
    def _get_status(self, 
                    value: float, 
                    kpi_def: KPIDefinition) -> str:
        """
        Determine le statut (couleur) d'un KPI selon sa valeur.
        
        Args:
            value: Valeur calculee
            kpi_def: Definition du KPI
        
        Returns:
            Statut ("vert", "orange", "rouge")
        """
        if kpi_def.seuil_vert is None:
            return "vert"
        
        if kpi_def.tendance_positive == "hausse":
            # Plus c'est haut, mieux c'est
            if value >= kpi_def.seuil_vert:
                return "vert"
            elif value >= kpi_def.seuil_orange:
                return "orange"
            else:
                return "rouge"
        else:
            # Plus c'est bas, mieux c'est
            if value <= kpi_def.seuil_vert:
                return "vert"
            elif value <= kpi_def.seuil_orange:
                return "orange"
            else:
                return "rouge"
    

    # KPI DE PERFORMANCE OPERATIONNELLE
    
    
    def calculate_delai_moyen_traitement(self) -> KPIResult:
        """
        Calcule le delai moyen de traitement des demandes.
        
        Returns:
            Resultat du KPI
        """
        kpi_def = KPI_DEFINITIONS["delai_moyen_traitement"]
        
        if 'demandes' not in self.datasets:
            return self._empty_result("delai_moyen_traitement", kpi_def)
        
        df = self.datasets['demandes']
        
        # Calcul global
        delai_moyen = df['delai_traitement_jours'].mean()
        delai_median = df['delai_traitement_jours'].median()
        
        # Par region
        delai_par_region = df.groupby('region')['delai_traitement_jours'].agg(['mean', 'median', 'count'])
        
        # Par type de document
        delai_par_type = df.groupby('type_document')['delai_traitement_jours'].mean()
        
        result = KPIResult(
            kpi_id="delai_moyen_traitement",
            nom=kpi_def.nom,
            valeur=round(delai_moyen, 2),
            unite=kpi_def.unite,
            statut=self._get_status(delai_moyen, kpi_def),
            tendance="stable",
            details={
                "delai_median": round(delai_median, 2),
                "par_region": delai_par_region.to_dict(),
                "par_type_document": delai_par_type.to_dict(),
                "nombre_demandes": len(df)
            },
            timestamp=self._timestamp
        )
        
        self.results["delai_moyen_traitement"] = result
        return result
    
    def calculate_taux_utilisation_capacite(self) -> KPIResult:
        """
        Calcule le taux d'utilisation de la capacite des centres.
        
        Returns:
            Resultat du KPI
        """
        kpi_def = KPI_DEFINITIONS["taux_utilisation_capacite"]
        
        if 'centres' not in self.datasets or 'logs' not in self.datasets:
            return self._empty_result("taux_utilisation_capacite", kpi_def)
        
        centres = self.datasets['centres']
        logs = self.datasets['logs']
        
        # Filtrer les logs de traitement
        logs_traitement = logs[logs['type_operation'] == 'Traitement']
        
        # Calculer le volume moyen par centre
        volume_par_centre = logs_traitement.groupby('centre_id')['nombre_traite'].mean()
        
        # Joindre avec capacites
        centres_capacite = centres.set_index('centre_id')['personnel_capacite_jour']
        
        # Calculer le taux pour chaque centre
        taux_utilisation = {}
        for centre_id in volume_par_centre.index:
            if centre_id in centres_capacite.index:
                capacite = centres_capacite[centre_id]
                if capacite > 0:
                    taux = (volume_par_centre[centre_id] / capacite) * 100
                    taux_utilisation[centre_id] = round(taux, 2)
        
        # Taux moyen global
        taux_moyen = np.mean(list(taux_utilisation.values())) if taux_utilisation else 0
        
        result = KPIResult(
            kpi_id="taux_utilisation_capacite",
            nom=kpi_def.nom,
            valeur=round(taux_moyen, 2),
            unite=kpi_def.unite,
            statut=self._get_status(taux_moyen, kpi_def),
            tendance="stable",
            details={
                "par_centre": taux_utilisation,
                "centres_analyses": len(taux_utilisation),
                "centres_surcharges": sum(1 for t in taux_utilisation.values() if t > 100),
                "centres_sous_utilises": sum(1 for t in taux_utilisation.values() if t < 50)
            },
            timestamp=self._timestamp
        )
        
        self.results["taux_utilisation_capacite"] = result
        return result
    
    # =========================================================================
    # KPI D'ACCESSIBILITE ET COUVERTURE
    # =========================================================================
    
    def calculate_ratio_population_centre(self) -> KPIResult:
        """
        Calcule le ratio population par centre.
        
        Returns:
            Resultat du KPI
        """
        kpi_def = KPI_DEFINITIONS["ratio_population_centre"]
        
        if 'centres' not in self.datasets or 'socioeco' not in self.datasets:
            return self._empty_result("ratio_population_centre", kpi_def)
        
        centres = self.datasets['centres']
        socioeco = self.datasets['socioeco']
        
        # Population par region
        pop_par_region = socioeco.groupby('region')['population'].sum()
        
        # Centres actifs par region
        centres_actifs = centres[centres['statut_centre'] == 'Actif']
        centres_par_region = centres_actifs.groupby('region').size()
        
        # Ratio par region
        ratio_par_region = {}
        for region in pop_par_region.index:
            pop = pop_par_region[region]
            nb_centres = centres_par_region.get(region, 1)
            ratio_par_region[region] = int(pop / nb_centres)
        
        # Ratio national
        pop_totale = pop_par_region.sum()
        nb_centres_total = len(centres_actifs)
        ratio_national = int(pop_totale / nb_centres_total) if nb_centres_total > 0 else 0
        
        result = KPIResult(
            kpi_id="ratio_population_centre",
            nom=kpi_def.nom,
            valeur=ratio_national,
            unite=kpi_def.unite,
            statut=self._get_status(ratio_national, kpi_def),
            tendance="stable",
            details={
                "par_region": ratio_par_region,
                "population_totale": int(pop_totale),
                "nombre_centres_actifs": nb_centres_total,
                "regions_sous_dotees": [r for r, ratio in ratio_par_region.items() 
                                        if ratio > kpi_def.seuil_rouge]
            },
            timestamp=self._timestamp
        )
        
        self.results["ratio_population_centre"] = result
        return result
    
    def calculate_couverture_communale(self) -> KPIResult:
        """
        Calcule le taux de couverture communale.
        
        Returns:
            Resultat du KPI
        """
        kpi_def = KPI_DEFINITIONS["couverture_communale"]
        
        if 'centres' not in self.datasets or 'communes' not in self.datasets:
            return self._empty_result("couverture_communale", kpi_def)
        
        centres = self.datasets['centres']
        communes = self.datasets['communes']
        
        # Communes uniques
        toutes_communes = set(communes['commune'].unique())
        
        # Communes avec au moins un centre actif
        centres_actifs = centres[centres['statut_centre'] == 'Actif']
        communes_couvertes = set(centres_actifs['commune'].unique())
        
        # Taux de couverture
        taux_couverture = (len(communes_couvertes) / len(toutes_communes)) * 100 if toutes_communes else 0
        
        # Par region
        couverture_par_region = {}
        for region in REGIONS:
            communes_region = set(communes[communes['region'] == region]['commune'].unique())
            centres_region = set(centres_actifs[centres_actifs['region'] == region]['commune'].unique())
            if communes_region:
                couverture_par_region[region] = round(
                    len(centres_region & communes_region) / len(communes_region) * 100, 2
                )
        
        # Communes non couvertes
        communes_non_couvertes = list(toutes_communes - communes_couvertes)
        
        result = KPIResult(
            kpi_id="couverture_communale",
            nom=kpi_def.nom,
            valeur=round(taux_couverture, 2),
            unite=kpi_def.unite,
            statut=self._get_status(taux_couverture, kpi_def),
            tendance="stable",
            details={
                "par_region": couverture_par_region,
                "total_communes": len(toutes_communes),
                "communes_couvertes": len(communes_couvertes),
                "communes_non_couvertes": communes_non_couvertes[:20]  # Limiter
            },
            timestamp=self._timestamp
        )
        
        self.results["couverture_communale"] = result
        return result
    
    # =========================================================================
    # KPI DE QUALITE DE SERVICE
    # =========================================================================
    
    def calculate_taux_rejet(self) -> KPIResult:
        """
        Calcule le taux de rejet des demandes.
        
        Returns:
            Resultat du KPI
        """
        kpi_def = KPI_DEFINITIONS["taux_rejet"]
        
        if 'demandes' not in self.datasets:
            return self._empty_result("taux_rejet", kpi_def)
        
        df = self.datasets['demandes']
        
        # Taux moyen pondere
        total_demandes = df['nombre_demandes'].sum()
        total_rejets = (df['nombre_demandes'] * df['taux_rejet']).sum()
        taux_rejet_pondere = (total_rejets / total_demandes) * 100 if total_demandes > 0 else 0
        
        # Par type de document
        taux_par_type = df.groupby('type_document').apply(
            lambda x: (x['nombre_demandes'] * x['taux_rejet']).sum() / x['nombre_demandes'].sum() * 100
        ).round(2).to_dict()
        
        # Par region
        taux_par_region = df.groupby('region').apply(
            lambda x: (x['nombre_demandes'] * x['taux_rejet']).sum() / x['nombre_demandes'].sum() * 100
        ).round(2).to_dict()
        
        # Raisons de rejet (depuis logs si disponible)
        raisons_rejet = {}
        if 'logs' in self.datasets:
            logs = self.datasets['logs']
            raisons = logs[logs['raison_rejet'] != 'N/A']['raison_rejet'].value_counts()
            raisons_rejet = raisons.to_dict()
        
        result = KPIResult(
            kpi_id="taux_rejet",
            nom=kpi_def.nom,
            valeur=round(taux_rejet_pondere, 2),
            unite=kpi_def.unite,
            statut=self._get_status(taux_rejet_pondere, kpi_def),
            tendance="stable",
            details={
                "par_type_document": taux_par_type,
                "par_region": taux_par_region,
                "raisons_rejet": raisons_rejet,
                "total_demandes": int(total_demandes)
            },
            timestamp=self._timestamp
        )
        
        self.results["taux_rejet"] = result
        return result
    
    def calculate_temps_attente_moyen(self) -> KPIResult:
        """
        Calcule le temps d'attente moyen en centre.
        
        Returns:
            Resultat du KPI
        """
        kpi_def = KPI_DEFINITIONS["temps_attente_moyen"]
        
        if 'logs' not in self.datasets:
            return self._empty_result("temps_attente_moyen", kpi_def)
        
        logs = self.datasets['logs']
        logs_traitement = logs[logs['type_operation'] == 'Traitement']
        
        # Temps d'attente moyen global
        temps_moyen = logs_traitement['temps_attente_moyen_minutes'].mean()
        
        # Par centre
        temps_par_centre = logs_traitement.groupby('centre_id')['temps_attente_moyen_minutes'].mean()
        
        # Statistiques
        temps_min = logs_traitement['temps_attente_moyen_minutes'].min()
        temps_max = logs_traitement['temps_attente_moyen_minutes'].max()
        temps_median = logs_traitement['temps_attente_moyen_minutes'].median()
        
        result = KPIResult(
            kpi_id="temps_attente_moyen",
            nom=kpi_def.nom,
            valeur=round(temps_moyen, 2),
            unite=kpi_def.unite,
            statut=self._get_status(temps_moyen, kpi_def),
            tendance="stable",
            details={
                "temps_median": round(temps_median, 2),
                "temps_min": round(temps_min, 2),
                "temps_max": round(temps_max, 2),
                "par_centre": temps_par_centre.round(2).to_dict(),
                "centres_critiques": temps_par_centre[temps_par_centre > 90].index.tolist()
            },
            timestamp=self._timestamp
        )
        
        self.results["temps_attente_moyen"] = result
        return result
    
    # =========================================================================
    # KPI D'EFFICIENCE
    # =========================================================================
    
    def calculate_productivite_agent(self) -> KPIResult:
        """
        Calcule la productivite moyenne par agent.
        
        Returns:
            Resultat du KPI
        """
        kpi_def = KPI_DEFINITIONS["productivite_agent"]
        
        if 'logs' not in self.datasets:
            return self._empty_result("productivite_agent", kpi_def)
        
        logs = self.datasets['logs']
        logs_traitement = logs[(logs['type_operation'] == 'Traitement') & (logs['personnel_present'] > 0)]
        
        # Productivite par ligne
        logs_traitement = logs_traitement.copy()
        logs_traitement['productivite'] = logs_traitement['nombre_traite'] / logs_traitement['personnel_present']
        
        # Productivite moyenne
        productivite_moyenne = logs_traitement['productivite'].mean()
        
        # Par centre
        productivite_par_centre = logs_traitement.groupby('centre_id')['productivite'].mean()
        
        result = KPIResult(
            kpi_id="productivite_agent",
            nom=kpi_def.nom,
            valeur=round(productivite_moyenne, 2),
            unite=kpi_def.unite,
            statut=self._get_status(productivite_moyenne, kpi_def),
            tendance="stable",
            details={
                "par_centre": productivite_par_centre.round(2).to_dict(),
                "meilleurs_centres": productivite_par_centre.nlargest(5).to_dict(),
                "centres_faibles": productivite_par_centre.nsmallest(5).to_dict()
            },
            timestamp=self._timestamp
        )
        
        self.results["productivite_agent"] = result
        return result
    
    def calculate_indice_charge(self) -> KPIResult:
        """
        Calcule l'indice de charge par region.
        
        Returns:
            Resultat du KPI
        """
        kpi_def = KPI_DEFINITIONS["indice_charge"]
        
        if 'demandes' not in self.datasets or 'centres' not in self.datasets:
            return self._empty_result("indice_charge", kpi_def)
        
        demandes = self.datasets['demandes']
        centres = self.datasets['centres']
        
        # Volume de demandes par region
        volume_par_region = demandes.groupby('region')['nombre_demandes'].sum()
        
        # Capacite par region
        centres_actifs = centres[centres['statut_centre'] == 'Actif']
        capacite_par_region = centres_actifs.groupby('region')['personnel_capacite_jour'].sum()
        
        # Indice de charge par region
        indice_par_region = {}
        for region in volume_par_region.index:
            volume = volume_par_region[region]
            capacite = capacite_par_region.get(region, 1)
            # Normaliser par le nombre de jours (environ 250 jours ouvres)
            indice = volume / (capacite * 250) if capacite > 0 else float('inf')
            indice_par_region[region] = round(indice, 3)
        
        # Indice global
        volume_total = volume_par_region.sum()
        capacite_totale = capacite_par_region.sum()
        indice_global = volume_total / (capacite_totale * 250) if capacite_totale > 0 else 0
        
        result = KPIResult(
            kpi_id="indice_charge",
            nom=kpi_def.nom,
            valeur=round(indice_global, 3),
            unite=kpi_def.unite,
            statut=self._get_status(indice_global, kpi_def),
            tendance="stable",
            details={
                "par_region": indice_par_region,
                "volume_total": int(volume_total),
                "capacite_totale_jour": int(capacite_totale),
                "regions_surchargees": [r for r, i in indice_par_region.items() if i > 1.0]
            },
            timestamp=self._timestamp
        )
        
        self.results["indice_charge"] = result
        return result
    
    # =========================================================================
    # METHODES UTILITAIRES
    # =========================================================================
    
    def _empty_result(self, kpi_id: str, kpi_def: KPIDefinition) -> KPIResult:
        """Cree un resultat vide pour un KPI non calculable."""
        return KPIResult(
            kpi_id=kpi_id,
            nom=kpi_def.nom,
            valeur=None,
            unite=kpi_def.unite,
            statut="indisponible",
            tendance="indisponible",
            details={"erreur": "Donnees insuffisantes"},
            timestamp=self._timestamp
        )
    
    def calculate_all(self) -> Dict[str, KPIResult]:
        """
        Calcule tous les KPI definis.
        
        Returns:
            Dictionnaire des resultats
        """
        logger.info("\n" + "=" * 60)
        logger.info("CALCUL DES INDICATEURS DE PERFORMANCE (KPI)")
        logger.info("=" * 60 + "\n")
        
        # Performance operationnelle
        logger.info("[CALC] KPI Performance operationnelle...")
        self.calculate_delai_moyen_traitement()
        self.calculate_taux_utilisation_capacite()
        
        # Accessibilite
        logger.info("[CALC] KPI Accessibilite / Couverture...")
        self.calculate_ratio_population_centre()
        self.calculate_couverture_communale()
        
        # Qualite de service
        logger.info("[CALC] KPI Qualite de service...")
        self.calculate_taux_rejet()
        self.calculate_temps_attente_moyen()
        
        # Efficience
        logger.info("[CALC] KPI Efficience / Charge...")
        self.calculate_productivite_agent()
        self.calculate_indice_charge()
        
        logger.info("\n" + "-" * 60)
        logger.info(f"[OK] {len(self.results)} KPI calcules")
        
        return self.results
    
    def get_summary(self) -> pd.DataFrame:
        """
        Retourne un resume de tous les KPI calcules.
        
        Returns:
            DataFrame recapitulatif
        """
        if not self.results:
            return pd.DataFrame()
        
        summary_data = []
        for kpi_id, result in self.results.items():
            kpi_def = KPI_DEFINITIONS.get(kpi_id)
            
            summary_data.append({
                "KPI": result.nom,
                "Categorie": kpi_def.categorie if kpi_def else "N/A",
                "Valeur": f"{result.valeur} {result.unite}" if result.valeur is not None else "N/A",
                "Statut": result.statut.capitalize(),
                "Tendance": result.tendance
            })
        
        return pd.DataFrame(summary_data)
    
    def get_kpi_details(self, kpi_id: str) -> Dict[str, Any]:
        """
        Retourne les details complets d'un KPI.
        
        Args:
            kpi_id: Identifiant du KPI
        
        Returns:
            Dictionnaire avec tous les details
        """
        if kpi_id not in self.results:
            return {"erreur": f"KPI '{kpi_id}' non trouve"}
        
        result = self.results[kpi_id]
        kpi_def = KPI_DEFINITIONS.get(kpi_id)
        
        return {
            "id": kpi_id,
            "nom": result.nom,
            "valeur": result.valeur,
            "unite": result.unite,
            "statut": result.statut,
            "tendance": result.tendance,
            "details": result.details,
            "definition": {
                "objectif_metier": kpi_def.objectif_metier if kpi_def else None,
                "description": kpi_def.description if kpi_def else None,
                "seuils": {
                    "vert": kpi_def.seuil_vert if kpi_def else None,
                    "orange": kpi_def.seuil_orange if kpi_def else None,
                    "rouge": kpi_def.seuil_rouge if kpi_def else None
                } if kpi_def else None
            }
        }
    
    def export_to_excel(self, output_path: str) -> None:
        """
        Exporte les KPI vers un fichier Excel.
        
        Args:
            output_path: Chemin du fichier de sortie
        """
        import openpyxl
        
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            # Feuille resume
            summary = self.get_summary()
            summary.to_excel(writer, sheet_name='Resume KPI', index=False)
            
            # Feuille definitions
            from .definitions import export_kpi_definitions_to_excel_format
            definitions_df = pd.DataFrame(export_kpi_definitions_to_excel_format())
            definitions_df.to_excel(writer, sheet_name='Definitions KPI', index=False)
            
            # Feuilles details par KPI
            for kpi_id, result in self.results.items():
                if result.details:
                    for key, value in result.details.items():
                        if isinstance(value, dict) and len(value) > 0:
                            try:
                                df = pd.DataFrame([
                                    {"Cle": k, "Valeur": v} 
                                    for k, v in value.items()
                                ])
                                sheet_name = f"{kpi_id[:20]}_{key[:10]}"[:31]
                                df.to_excel(writer, sheet_name=sheet_name, index=False)
                            except:
                                pass
        
        logger.info(f"[OK] KPI exportes vers: {output_path}")
    
    def print_dashboard(self) -> None:
        """Affiche un dashboard console des KPI."""
        print("\n" + "=" * 70)
        print("                    TABLEAU DE BORD KPI")
        print("=" * 70 + "\n")
        
        # Grouper par categorie
        categories = {}
        for kpi_id, result in self.results.items():
            kpi_def = KPI_DEFINITIONS.get(kpi_id)
            if kpi_def:
                cat = kpi_def.categorie
                if cat not in categories:
                    categories[cat] = []
                categories[cat].append(result)
        
        for category, results in categories.items():
            print(f"\n[CATEGORIE] {category.upper()}")
            print("-" * 50)
            
            for result in results:
                statut_indicator = {
                    "vert": "[VERT]",
                    "orange": "[ORANGE]",
                    "rouge": "[ROUGE]"
                }.get(result.statut, "[?]")
                
                value_str = f"{result.valeur} {result.unite}" if result.valeur is not None else "N/A"
                print(f"  {statut_indicator} {result.nom}: {value_str}")
        
        print("\n" + "=" * 70)
