
import gsheet_manager
import sys

# Remplacez par le NOM ou l'URL de votre Google Sheet
# Exemple : "Annonces LBC Automation" ou "https://docs.google.com/spreadsheets/d/..."
SHEET_NAME_OR_URL = "Annonces LBC" 

def main():
    print("--- TEST GOOGLE SHEETS ---")
    
    # 1. Connexion
    try:
        sheet = gsheet_manager.connect_to_sheets(SHEET_NAME_OR_URL)
    except Exception as e:
        print("\n[ECHEC] Impossible de se connecter.")
        print("Vérifiez que 'service_account.json' est présent et que le nom du Sheet est correct.")
        return

    # 2. Lecture Header
    print("\n[TEST] Lecture des en-têtes (ligne 1)...")
    headers = sheet.row_values(1)
    print(f"   -> En-têtes trouvés : {headers}")
    
    expected_cols = ["Titre", "Description", "Prix", "Statut"]
    for col in expected_cols:
        if col not in headers:
            print(f"   WARNING: Colonne '{col}' manquante ! Le script risque de planter.")

    # 3. Récupération Annonce A_FAIRE
    print("\n[TEST] Recherche d'une annonce 'A_FAIRE'...")
    record, row_num = gsheet_manager.get_next_ad_to_publish(sheet)
    
    if record:
        print(f"   -> Trouvé Ligne {row_num} :")
        print(f"      Titre: {record.get('Titre')}")
        print(f"      Prix: {record.get('Prix')}")
        print(f"      Statut: {record.get('Statut')}")
        
        # 4. (Optionnel) Test Update
        # print("\n[TEST] Tentative de mise à jour du statut...")
        # gsheet_manager.mark_ad_as_published(sheet, row_num)
        # print("   -> Statut mis à jour (Checkez votre Sheet !)")
    else:
        print("   -> Aucune annonce 'A_FAIRE' trouvée.")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        SHEET_NAME_OR_URL = sys.argv[1]
    msg = f"Nom du Sheet ciblé : '{SHEET_NAME_OR_URL}'"
    print(msg)
    print("-" * len(msg))
    
    main()
