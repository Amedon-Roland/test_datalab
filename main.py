#!/usr/bin/env python3
"""
Script Principal - Analyse des Services Publics Togo
======================================================

Ce script execute l'ensemble du pipeline d'analyse:
1. Chargement des donnees
2. Nettoyage et validation
3. Analyse exploratoire (EDA)
4. Calcul des KPI
5. Export des resultats

Usage:
    python main.py

Auteur: Data Analyst - Togo Datalab
Date: Janvier 2026
"""

import sys
import os
from pathlib import Path

# Ajouter le repertoire src au path
sys.path.insert(0, str(Path(__file__).parent))

import pandas as pd
import warnings
warnings.filterwarnings('ignore')

# Imports des modules du projet
from src.data.loader import DataLoader
from src.data.cleaner import DataCleaner
from src.data.validator import DataValidator
from src.analysis.eda import ExploratoryAnalysis
from src.kpi.calculator import KPICalculator
from src.kpi.definitions import export_kpi_definitions_to_excel_format


def main():
    """Point d'entree principal du script."""
    
    print("\n" + "=" * 70)
    print("   OPTIMISATION DU RESEAU DE SERVICES PUBLICS - TOGO DATALAB")
    print("   Analyse pour la delivrance de documents officiels")
    print("=" * 70 + "\n")
    
    # Configuration des chemins
    BASE_PATH = Path(__file__).parent
    DATA_PATH = BASE_PATH
    OUTPUT_PATH = BASE_PATH / "outputs"
    REPORTS_PATH = BASE_PATH / "reports"
    
    # Creer les dossiers de sortie
    OUTPUT_PATH.mkdir(exist_ok=True)
    (OUTPUT_PATH / "visualizations").mkdir(exist_ok=True)
    (OUTPUT_PATH / "exports").mkdir(exist_ok=True)
    REPORTS_PATH.mkdir(exist_ok=True)
    
    # =========================================================================
    # ETAPE 1: CHARGEMENT DES DONNEES
    # =========================================================================
    print("\n[ETAPE 1] CHARGEMENT DES DONNEES")
    print("-" * 50)
    
    loader = DataLoader(DATA_PATH)
    raw_datasets = loader.load_all(verbose=True)
    
    # Afficher les informations
    print("\nApercu des donnees chargees:")
    info_df = loader.get_info()
    print(info_df.to_string(index=False))
    
    # =========================================================================
    # ETAPE 2: VALIDATION INITIALE
    # =========================================================================
    print("\n\n[ETAPE 2] VALIDATION INITIALE DES DONNEES")
    print("-" * 50)
    
    validator = DataValidator()
    validation_results = validator.validate_all(raw_datasets)
    validator.print_summary()
    
    # =========================================================================
    # ETAPE 3: NETTOYAGE DES DONNEES
    # =========================================================================
    print("\n\n[ETAPE 3] NETTOYAGE DES DONNEES")
    print("-" * 50)
    
    cleaner = DataCleaner()
    cleaned_datasets = cleaner.clean_all(raw_datasets)
    
    # Sauvegarder le rapport de nettoyage
    cleaning_report = cleaner.get_cleaning_report()
    if len(cleaning_report) > 0:
        cleaning_report.to_csv(
            REPORTS_PATH / "rapport_nettoyage.csv", 
            index=False, 
            encoding='utf-8'
        )
        print(f"\nRapport de nettoyage sauvegarde: {REPORTS_PATH / 'rapport_nettoyage.csv'}")
    
    # =========================================================================
    # ETAPE 4: VALIDATION APRES NETTOYAGE
    # =========================================================================
    print("\n\n[ETAPE 4] VALIDATION APRES NETTOYAGE")
    print("-" * 50)
    
    validator.clear_results()
    post_validation = validator.validate_all(cleaned_datasets)
    validator.print_summary()
    
    # =========================================================================
    # ETAPE 5: ANALYSE EXPLORATOIRE (EDA)
    # =========================================================================
    print("\n\n[ETAPE 5] ANALYSE EXPLORATOIRE DES DONNEES")
    print("-" * 50)
    
    eda = ExploratoryAnalysis(
        cleaned_datasets, 
        output_path=str(OUTPUT_PATH / "visualizations")
    )
    
    eda_results = eda.run_full_analysis()
    
    # Generer le rapport EDA
    eda_report = eda.generate_eda_report(
        output_path=str(REPORTS_PATH / "rapport_eda.md")
    )
    
    # =========================================================================
    # ETAPE 6: CALCUL DES KPI
    # =========================================================================
    print("\n\n[ETAPE 6] CALCUL DES INDICATEURS DE PERFORMANCE (KPI)")
    print("-" * 50)
    
    calculator = KPICalculator(cleaned_datasets)
    kpi_results = calculator.calculate_all()
    
    # Afficher le dashboard
    calculator.print_dashboard()
    
    # Exporter les KPI
    calculator.export_to_excel(str(OUTPUT_PATH / "exports" / "kpi_resultats.xlsx"))
    
    # Exporter le resume en CSV
    kpi_summary = calculator.get_summary()
    kpi_summary.to_csv(
        OUTPUT_PATH / "exports" / "kpi_resume.csv", 
        index=False, 
        encoding='utf-8'
    )
    
    # =========================================================================
    # ETAPE 7: EXPORT DES DONNEES NETTOYEES
    # =========================================================================
    print("\n\n[ETAPE 7] EXPORT DES DONNEES NETTOYEES")
    print("-" * 50)
    
    for name, df in cleaned_datasets.items():
        output_file = OUTPUT_PATH / "exports" / f"{name}_clean.csv"
        df.to_csv(output_file, index=False, encoding='utf-8')
        print(f"  [OK] {name}: {output_file}")
    
    # Copier egalement dans data/processed
    processed_path = BASE_PATH / "data" / "processed"
    processed_path.mkdir(parents=True, exist_ok=True)
    for name, df in cleaned_datasets.items():
        df.to_csv(processed_path / f"{name}_clean.csv", index=False, encoding='utf-8')
    
    # =========================================================================
    # ETAPE 8: GENERATION DU TABLEAU DES KPI
    # =========================================================================
    print("\n\n[ETAPE 8] GENERATION DU TABLEAU KPI (FORMAT MARKDOWN)")
    print("-" * 50)
    
    # Creer le tableau des KPI pour le livrable
    kpi_table = generate_kpi_table(calculator)
    
    with open(REPORTS_PATH / "tableau_kpi.md", 'w', encoding='utf-8') as f:
        f.write(kpi_table)
    
    print(f"  [OK] Tableau KPI sauvegarde: {REPORTS_PATH / 'tableau_kpi.md'}")
    
    # Export Excel du tableau KPI
    kpi_definitions_df = pd.DataFrame(export_kpi_definitions_to_excel_format())
    kpi_definitions_df.to_excel(
        OUTPUT_PATH / "exports" / "definitions_kpi.xlsx",
        index=False
    )
    print(f"  [OK] Definitions KPI Excel: {OUTPUT_PATH / 'exports' / 'definitions_kpi.xlsx'}")
    
    # =========================================================================
    # RESUME FINAL
    # =========================================================================
    print("\n\n" + "=" * 70)
    print("                         RESUME FINAL")
    print("=" * 70)
    
    print(f"""
Fichiers generes:
   - Donnees nettoyees: {OUTPUT_PATH / 'exports'}
   - Visualisations: {OUTPUT_PATH / 'visualizations'}
   - Rapport EDA: {REPORTS_PATH / 'rapport_eda.md'}
   - Rapport de nettoyage: {REPORTS_PATH / 'rapport_nettoyage.csv'}
   - Tableau KPI: {REPORTS_PATH / 'tableau_kpi.md'}
   - KPI Excel: {OUTPUT_PATH / 'exports' / 'kpi_resultats.xlsx'}

Statistiques cles:
""")
    
    # Afficher quelques metriques cles
    if 'demandes' in cleaned_datasets:
        df = cleaned_datasets['demandes']
        print(f"   * Total demandes analysees: {len(df)} enregistrements")
        if 'nombre_demandes' in df.columns:
            print(f"   * Volume total de demandes: {df['nombre_demandes'].sum():,.0f}")
    
    if 'centres' in cleaned_datasets:
        print(f"   * Centres de service: {len(cleaned_datasets['centres'])}")
    
    print(f"\n   * KPI calcules: {len(kpi_results)}")
    
    # Compter les statuts
    statuts = {"vert": 0, "orange": 0, "rouge": 0}
    for result in kpi_results.values():
        if result.statut in statuts:
            statuts[result.statut] += 1
    
    print(f"   * KPI en zone verte: {statuts['vert']}")
    print(f"   * KPI en zone orange: {statuts['orange']}")
    print(f"   * KPI en zone rouge: {statuts['rouge']}")
    
    print("\n" + "=" * 70)
    print("[OK] ANALYSE TERMINEE AVEC SUCCES")
    print("=" * 70 + "\n")
    
    return cleaned_datasets, kpi_results


def generate_kpi_table(calculator: KPICalculator) -> str:
    """
    Genere le tableau des KPI au format Markdown.
    
    Args:
        calculator: Instance de KPICalculator avec resultats
    
    Returns:
        Contenu Markdown du tableau
    """
    from src.kpi.definitions import KPI_DEFINITIONS
    
    md = []
    md.append("# Tableau des Indicateurs Cles de Performance (KPI)\n\n")
    md.append("*Optimisation du reseau de services publics - Togo Datalab*\n\n")
    md.append("---\n\n")
    
    # Tableau principal
    md.append("## Resume des KPI\n\n")
    md.append("| Nom du KPI | Categorie | Valeur | Statut | Objectif metier |\n")
    md.append("|:-----------|:----------|:-------|:-------|:----------------|\n")
    
    for kpi_id, result in calculator.results.items():
        kpi_def = KPI_DEFINITIONS.get(kpi_id)
        if kpi_def:
            statut_indicator = {"vert": "VERT", "orange": "ORANGE", "rouge": "ROUGE"}.get(result.statut, "?")
            value = f"{result.valeur} {result.unite}" if result.valeur else "N/A"
            objectif = kpi_def.objectif_metier[:80] + "..." if len(kpi_def.objectif_metier) > 80 else kpi_def.objectif_metier
            md.append(f"| **{kpi_def.nom}** | {kpi_def.categorie} | {value} | {statut_indicator} | {objectif} |\n")
    
    md.append("\n---\n\n")
    
    # Details par KPI
    md.append("## Details des KPI\n\n")
    
    for kpi_id, kpi_def in KPI_DEFINITIONS.items():
        md.append(f"### {kpi_def.nom}\n\n")
        md.append(f"**Categorie:** {kpi_def.categorie}\n\n")
        md.append(f"**Objectif metier:** {kpi_def.objectif_metier}\n\n")
        md.append(f"**Description:** {kpi_def.description}\n\n")
        md.append(f"**Regle de calcul:** `{kpi_def.regle_calcul}`\n\n")
        
        # Valeur calculee
        if kpi_id in calculator.results:
            result = calculator.results[kpi_id]
            statut_indicator = {"vert": "VERT", "orange": "ORANGE", "rouge": "ROUGE"}.get(result.statut, "?")
            md.append(f"**Valeur actuelle:** {result.valeur} {result.unite} [{statut_indicator}]\n\n")
        
        md.append(f"**Seuils:**\n")
        md.append(f"- VERT: {'<=' if kpi_def.tendance_positive == 'baisse' else '>='} {kpi_def.seuil_vert} {kpi_def.unite}\n")
        md.append(f"- ORANGE: {'<=' if kpi_def.tendance_positive == 'baisse' else '>='} {kpi_def.seuil_orange} {kpi_def.unite}\n")
        md.append(f"- ROUGE: {'>' if kpi_def.tendance_positive == 'baisse' else '<'} {kpi_def.seuil_rouge} {kpi_def.unite}\n\n")
        
        # Requete SQL
        md.append("<details>\n<summary>Requete SQL</summary>\n\n")
        md.append("```sql\n")
        md.append(kpi_def.requete_sql.strip())
        md.append("\n```\n\n")
        md.append("</details>\n\n")
        md.append("---\n\n")
    
    return "".join(md)


if __name__ == "__main__":
    cleaned_data, kpis = main()
