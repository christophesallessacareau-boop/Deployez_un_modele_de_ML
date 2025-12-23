"""
Script de fusion des données RH avec renommage automatique des clés
Fichier: merge_data.py
Fusion sur la clé commune 'id_employee' avec stratégie INNER
"""

import sys
from pathlib import Path

# Ajoute le dossier src au path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from database import DatabaseManager
import pandas as pd


def harmonize_and_merge(merge_type='inner'):
    """
    Harmonise les noms de colonnes et fusionne les 3 tables
    
    Args:
        merge_type: Type de fusion ('inner', seulement les employés présents partout)
    """
    
    print("=" * 70)
    print("FUSION DES DONNÉES RH SUR LA CLÉ 'id_employee'")
    print("=" * 70)
    
    db_manager = DatabaseManager()
    
    # ==========================================
    # ÉTAPE 1 : Chargement des données
    # ==========================================
    print("\n Étape 1 : Chargement des tables...")
    
    try:
        df_sirh = pd.read_sql_table('extrait_sirh', db_manager.engine)
        print(f"  ✓ SIRH chargée: {len(df_sirh)} lignes")
        print(f"    Colonnes: {list(df_sirh.columns)}")
        
        df_eval = pd.read_sql_table('extrait_evaluation', db_manager.engine)
        print(f"  ✓ Evaluation chargée: {len(df_eval)} lignes")
        print(f"    Colonnes: {list(df_eval.columns)}")
        
        df_sondage = pd.read_sql_table('extrait_sondage', db_manager.engine)
        print(f"  ✓ Sondage chargé: {len(df_sondage)} lignes")
        print(f"    Colonnes: {list(df_sondage.columns)}")
        
    except Exception as e:
        print(f"\n Erreur lors du chargement: {e}")
        print("\n Vérifiez que les tables existent dans PostgreSQL")
        print("   Lancez d'abord: python setup_database.py")
        return False
    
    # ==========================================
    # ÉTAPE 2 : Renommage des clés vers 'id_employee'
    # ==========================================
    print("\n Étape 2 : Harmonisation des clés → 'id_employee'...")
    
    # Clé commune standardisée
    COMMON_KEY = 'id_employee'
    
    # Mapping de renommage pour chaque table
    rename_sirh = {'id_employee': COMMON_KEY} if 'id_employee' in df_sirh.columns else {}
    rename_eval = {'eval_number': COMMON_KEY} if 'eval_number' in df_eval.columns else {}
    rename_sondage = {'code_sondage': COMMON_KEY} if 'code_sondage' in df_sondage.columns else {}
    
    # Application des renommages
    df_sirh_renamed = df_sirh.rename(columns=rename_sirh)
    df_eval_renamed = df_eval.rename(columns=rename_eval)
    df_sondage_renamed = df_sondage.rename(columns=rename_sondage)
    
    print(f"   Clé standardisée: '{COMMON_KEY}'")
    if rename_sirh:
        print(f"    - SIRH: '{list(rename_sirh.keys())[0]}' → '{COMMON_KEY}'")
    if rename_eval:
        print(f"    - Evaluation: '{list(rename_eval.keys())[0]}' → '{COMMON_KEY}'")
    if rename_sondage:
        print(f"    - Sondage: '{list(rename_sondage.keys())[0]}' → '{COMMON_KEY}'")
    
    # Vérification que la clé existe maintenant
    if COMMON_KEY not in df_sirh_renamed.columns:
        print(f"\n Erreur: La colonne '{COMMON_KEY}' n'existe pas dans SIRH")
        return False
    if COMMON_KEY not in df_eval_renamed.columns:
        print(f"\n Erreur: La colonne '{COMMON_KEY}' n'existe pas dans Evaluation")
        return False
    if COMMON_KEY not in df_sondage_renamed.columns:
        print(f"\n Erreur: La colonne '{COMMON_KEY}' n'existe pas dans Sondage")
        return False
    
    # ==========================================
    # ÉTAPE 3 : Analyse des données
    # ==========================================
    print("\n Étape 3 : Analyse des données...")
    
    ids_sirh = set(df_sirh_renamed[COMMON_KEY].dropna().unique())
    ids_eval = set(df_eval_renamed[COMMON_KEY].dropna().unique())
    ids_sondage = set(df_sondage_renamed[COMMON_KEY].dropna().unique())
    
    print(f"\n  Employés uniques par table:")
    print(f"    - SIRH:       {len(ids_sirh)} employés")
    print(f"    - Evaluation: {len(ids_eval)} employés")
    print(f"    - Sondage:    {len(ids_sondage)} employés")
    
    # Intersection
    common_all = ids_sirh & ids_eval & ids_sondage
    print(f"\n   Présents dans les 3 tables: {len(common_all)} employés")
    
    # Total union
    all_ids = ids_sirh | ids_eval | ids_sondage
    print(f"   Total unique (union):        {len(all_ids)} employés")
    
    # ==========================================
    # ÉTAPE 4 : Fusion sur 'id_employee'
    # ==========================================
    print(f"\n Étape 4 : Fusion sur '{COMMON_KEY}' (stratégie: {merge_type.upper()})...")
    
    # Fusion progressive : SIRH + Evaluation
    merged_df = pd.merge(
        df_sirh_renamed,
        df_eval_renamed,
        on=COMMON_KEY,
        how=merge_type,
        suffixes=('_sirh', '_eval')
    )
    print(f"   SIRH + Evaluation: {len(merged_df)} lignes")
    
    # Fusion avec Sondage
    merged_df = pd.merge(
        merged_df,
        df_sondage_renamed,
        on=COMMON_KEY,
        how=merge_type,
        suffixes=('', '_sondage')
    )
    print(f"   + Sondage: {len(merged_df)} lignes")
    
    # ==========================================
    # ÉTAPE 5 : Nettoyage
    # ==========================================
    print("\n Étape 5 : Nettoyage des colonnes dupliquées...")
    
    # Supprime les colonnes avec suffixe '_sondage' (doublons)
    cols_to_drop = [col for col in merged_df.columns if col.endswith('_sondage')]
    if cols_to_drop:
        merged_df = merged_df.drop(columns=cols_to_drop)
        print(f"   {len(cols_to_drop)} colonnes dupliquées supprimées")
    
    # Statistiques sur les valeurs manquantes
    missing_stats = merged_df.isnull().sum()
    total_missing = missing_stats.sum()
    
    if total_missing > 0:
        print(f"\n   Valeurs manquantes détectées:")
        for col, count in missing_stats[missing_stats > 0].items():
            pct = (count / len(merged_df)) * 100
            print(f"    - {col}: {count} ({pct:.1f}%)")
    else:
        print(f"  Aucune valeur manquante!")
    
    # ==========================================
    # ÉTAPE 6 : Sauvegarde dans PostgreSQL
    # ==========================================
    print("\n Étape 6 : Sauvegarde dans PostgreSQL...")
    
    output_table = 'donnees_fusionnees'
    merged_df.to_sql(output_table, db_manager.engine, if_exists='replace', index=False)
    
    # Log de l'opération
    db_manager.log_operation(
        operation_type='MERGE',
        table_name=output_table,
        rows_affected=len(merged_df),
        status='SUCCESS',
        metadata={
            'source_tables': ['extrait_sirh', 'extrait_evaluation', 'extrait_sondage'],
            'join_key': COMMON_KEY,
            'join_type': merge_type,
            'final_columns': list(merged_df.columns),
            'original_keys': ['id_employee', 'eval_number', 'code_sondage']
        }
    )
    
    print(f"   Table '{output_table}' créée avec succès!")
    
    # ==========================================
    # RÉSUMÉ FINAL
    # ==========================================
    print("\n" + "=" * 70)
    print(" FUSION TERMINÉE AVEC SUCCÈS!")
    print("=" * 70)
    
    print(f"\n Résumé de la fusion:")
    print(f"  • Table de destination: '{output_table}'")
    print(f"  • Clé de jointure: '{COMMON_KEY}'")
    print(f"  • Stratégie de fusion: {merge_type.upper()}")
    print(f"  • Nombre de lignes: {len(merged_df)}")
    print(f"  • Nombre de colonnes: {len(merged_df.columns)}")
    
    print(f"\n Colonnes finales ({len(merged_df.columns)}):")
    for i, col in enumerate(merged_df.columns, 1):
        print(f"  {i:2d}. {col}")
    
    print(f"\n Aperçu des 3 premières lignes:")
    print(merged_df.head(3).to_string(index=False))
    
    print(f"\n Pour interroger cette table en SQL:")
    print(f"   SELECT * FROM {output_table} LIMIT 10;")
    
    print(f"\n Pour charger en Python:")
    print(f"   df = db_manager.execute_query('SELECT * FROM {output_table}')")
    
    return True


def main():
    """Fonction principale"""
    
    print("\n Script de fusion des données RH\n")
    
    # fusion INNER (seulement les employés présents partout)
    
    MERGE_TYPE = 'inner'
    
    print(f"Configuration: Fusion {MERGE_TYPE.upper()} sur 'id_employee'\n")
    
    # Exécution de la fusion
    success = harmonize_and_merge(merge_type=MERGE_TYPE)
    
    if success:
        print("\n" + "=" * 70)
        print(" UTILISATION DES DONNÉES FUSIONNÉES")
        print("=" * 70)
        print("""
Les données sont maintenant disponibles dans la table 'donnees_fusionnees' """)
    else:
        print("\n La fusion a échoué. Vérifiez les messages d'erreur ci-dessus.")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())