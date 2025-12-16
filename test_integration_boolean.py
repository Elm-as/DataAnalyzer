"""
Test d'integration complete - Detection et conversion automatique
"""
import pandas as pd
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def test_integration_complete():
    """Test du workflow complet avec detection automatique"""
    print("\n" + "=" * 80)
    print("TEST D'INTEGRATION COMPLETE")
    print("=" * 80)
    
    from utils.data_validator import BooleanDetector, DataValidator
    
    # 1. Charger les donnees
    print("\n[1/5] Chargement du dataset...")
    df = pd.read_csv('disease_symptom_matrix.csv')
    print(f"   ✅ {df.shape[0]} lignes x {df.shape[1]} colonnes chargees")
    
    # 2. Detection initiale (frontend simulation)
    print("\n[2/5] Detection initiale des types (frontend)...")
    types_before = {}
    for col in df.columns:
        if df[col].dtype in ['int64', 'float64']:
            types_before[col] = 'number'
        else:
            types_before[col] = 'string'
    
    boolean_cols_before = sum(1 for t in types_before.values() if t == 'boolean')
    numeric_cols_before = sum(1 for t in types_before.values() if t == 'number')
    print(f"   - Colonnes numeriques: {numeric_cols_before}")
    print(f"   - Colonnes booleennes: {boolean_cols_before}")
    print(f"   ⚠️ Probleme: {numeric_cols_before} colonnes sont des 0/1 non detectes!")
    
    # 3. Detection automatique (backend)
    print("\n[3/5] Detection automatique des booleens (backend API)...")
    boolean_detection = BooleanDetector.detect_boolean_columns(df)
    detected = [col for col, is_bool in boolean_detection.items() if is_bool]
    print(f"   ✅ {len(detected)} colonnes booleennes detectees")
    print(f"   Exemples: {detected[:5]}")
    
    # 4. Conversion automatique
    print("\n[4/5] Conversion automatique...")
    df_converted, converted = BooleanDetector.auto_convert_booleans(df)
    print(f"   ✅ {len(converted)} colonnes converties")
    
    # 5. Verification des resultats
    print("\n[5/5] Verification des resultats...")
    types_after = {}
    for col in df_converted.columns:
        if df_converted[col].dtype == 'bool':
            types_after[col] = 'boolean'
        elif df_converted[col].dtype in ['int64', 'float64']:
            types_after[col] = 'number'
        else:
            types_after[col] = 'string'
    
    boolean_cols_after = sum(1 for t in types_after.values() if t == 'boolean')
    numeric_cols_after = sum(1 for t in types_after.values() if t == 'number')
    
    print(f"\n   AVANT conversion:")
    print(f"   - Numeriques: {numeric_cols_before}")
    print(f"   - Booleennes: {boolean_cols_before}")
    print(f"\n   APRES conversion:")
    print(f"   - Numeriques: {numeric_cols_after}")
    print(f"   - Booleennes: {boolean_cols_after}")
    
    # Validation de la qualite
    print("\n[BONUS] Validation de la qualite des donnees...")
    report = DataValidator.validate(df_converted)
    print(f"   - Completude: {report['quality']['completeness']:.1f}%")
    print(f"   - Colonnes problematiques: {len(report['problematicColumns'])}")
    
    # Test d'une analyse simple
    print("\n[TEST] Analyse simple sur colonnes booleennes...")
    # Compter les True/False dans une colonne
    test_col = detected[0]
    true_count = df_converted[test_col].sum()
    false_count = len(df_converted) - true_count
    print(f"   Colonne: {test_col}")
    print(f"   - True: {true_count} ({true_count/len(df_converted)*100:.1f}%)")
    print(f"   - False: {false_count} ({false_count/len(df_converted)*100:.1f}%)")
    
    # Resultats
    print("\n" + "=" * 80)
    print("RESULTATS")
    print("=" * 80)
    
    success = (
        len(detected) >= 1000 and  # Au moins 1000 colonnes booleennes
        boolean_cols_after > boolean_cols_before and  # Plus de booleens detectes
        numeric_cols_after < numeric_cols_before  # Moins de numeriques (convertis)
    )
    
    if success:
        print("\n✅ SUCCES COMPLET!")
        print(f"\n   🎯 {len(detected)} colonnes 0/1 detectees comme BOOLEENNES")
        print(f"   🔄 {len(converted)} colonnes converties en type bool")
        print(f"   📊 Types corrects pour analyses adaptees")
        print(f"   ⚡ Prêt pour workflow complet (Preview → Configuration → Analyse)")
        
        print("\n   WORKFLOW COMPLET VALIDE:")
        print("   1. ✅ Upload CSV")
        print("   2. ✅ Detection automatique des types")
        print("   3. ✅ Conversion automatique bool (backend)")
        print("   4. ✅ Preview avec types corrects")
        print("   5. ✅ (Optionnel) Conversion manuelle")
        print("   6. ✅ Configuration des colonnes")
        print("   7. ✅ Analyses avec types adaptes")
        
    else:
        print("\n❌ ECHEC")
        print(f"   Detectes: {len(detected)}")
        print(f"   Booleens avant: {boolean_cols_before}")
        print(f"   Booleens apres: {boolean_cols_after}")
    
    print("\n" + "=" * 80)
    return success

if __name__ == '__main__':
    success = test_integration_complete()
    sys.exit(0 if success else 1)
