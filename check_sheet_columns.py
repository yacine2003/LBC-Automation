"""
Script de diagnostic pour vérifier les colonnes du Google Sheet
Détecte les problèmes de nommage (espaces, casse, etc.)
"""

import gsheet_manager
from config import SHEET_NAME

def main():
    print("=" * 80)
    print("🔍 DIAGNOSTIC DES COLONNES GOOGLE SHEET")
    print("=" * 80)
    print()
    
    try:
        sheet = gsheet_manager.connect_to_sheets(SHEET_NAME)
        print(f"✅ Connexion réussie au Sheet '{SHEET_NAME}'")
        print()
        
        # Lire les en-têtes
        headers = sheet.row_values(1)
        print(f"📋 Nombre de colonnes : {len(headers)}")
        print()
        
        # Colonnes attendues
        expected = ['ID', 'Titre', 'Description', 'Prix', 'Categorie', 'Photos', 'Statut', 'Type', 'Ville']
        
        print("📊 ANALYSE DES COLONNES :")
        print("-" * 80)
        
        for i, header in enumerate(headers, 1):
            # Vérifier les espaces invisibles
            stripped = header.strip()
            has_leading = header != header.lstrip()
            has_trailing = header != header.rstrip()
            
            status = "✅"
            warning = ""
            
            if has_leading or has_trailing:
                status = "⚠️"
                warning = f" (Espaces détectés: début={has_leading}, fin={has_trailing})"
            
            print(f"  {status} Col {i:2d}: '{header}' (stripped: '{stripped}'){warning}")
            
            # Vérifier si c'est une colonne attendue
            if stripped in expected:
                if header != stripped:
                    print(f"           → ATTENTION : Devrait être '{stripped}' sans espaces")
        
        print("-" * 80)
        print()
        
        # Vérifier les colonnes manquantes
        missing = []
        for exp in expected:
            found = False
            for h in headers:
                if h.strip() == exp:
                    found = True
                    break
            if not found:
                missing.append(exp)
        
        if missing:
            print("❌ COLONNES MANQUANTES :")
            for m in missing:
                print(f"   - {m}")
            print()
        else:
            print("✅ Toutes les colonnes attendues sont présentes")
            print()
        
        # Lire une ligne exemple
        print("📝 EXEMPLE DE DONNÉES (ligne 2) :")
        print("-" * 80)
        try:
            records = sheet.get_all_records()
            if records:
                first_record = records[0]
                for key, value in first_record.items():
                    val_preview = str(value)[:50] if value else "(vide)"
                    print(f"  '{key}' = {val_preview}")
            else:
                print("  (Aucune donnée)")
        except Exception as e:
            print(f"  Erreur lecture données : {e}")
        
        print("-" * 80)
        print()
        
        # Recommandations
        print("💡 RECOMMANDATIONS :")
        print("-" * 80)
        has_issues = any(h != h.strip() for h in headers)
        
        if has_issues:
            print("⚠️  Vous avez des colonnes avec des espaces inutiles.")
            print("    → Renommez-les dans Google Sheets pour enlever les espaces")
            print()
            print("    Colonnes à corriger :")
            for h in headers:
                if h != h.strip():
                    print(f"      - '{h}' → '{h.strip()}'")
        else:
            print("✅ Aucun problème détecté dans les noms de colonnes")
        
        print("=" * 80)
        
    except Exception as e:
        print(f"❌ ERREUR : {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

