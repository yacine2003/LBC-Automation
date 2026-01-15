
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import sys
from utils import BASE_PATH

# -------------------- CONFIG --------------------
SCOPE = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]
CREDENTIALS_FILE = str(BASE_PATH / "service_account.json")
# ------------------------------------------------

def connect_to_sheets(sheet_url_or_name):
    """
    Connecte au Google Sheet via le fichier JSON de service account.
    """
    print(f"   [GSheet] Connexion au Sheet '{sheet_url_or_name}'...")
    try:
        creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, SCOPE)
        client = gspread.authorize(creds)
        
        # Ouvre le sheet soit par URL soit par nom
        if "http" in sheet_url_or_name:
            sheet = client.open_by_url(sheet_url_or_name).sheet1
        else:
            sheet = client.open(sheet_url_or_name).sheet1
            
        print("   [GSheet] Connexion réussie.")
        return sheet
    except FileNotFoundError:
        print(f"ERROR: Le fichier '{CREDENTIALS_FILE}' est introuvable.")
        print("Veuillez placer votre clé JSON Google Cloud à la racine du projet.")
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"ERROR: Impossible de se connecter au Sheet : {e}")
        raise

def get_next_ad_to_publish(sheet):
    """
    Récupère la première ligne où le statut est 'A_FAIRE'.
    Retourne un dict avec les données et le numéro de ligne (index 1-based).
    """
    print("   [GSheet] Recherche d'une annonce 'A_FAIRE'...")
    try:
        # Récupère toutes les données (c'est plus rapide que de scanner ligne par ligne)
        all_records = sheet.get_all_records()
        
        # On parcourt pour trouver le premier 'A_FAIRE'
        # Note : get_all_records retourne une liste de dicts
        # L'index dans la liste commence à 0, ce qui correspond à la ligne 2 du Sheet (la ligne 1 est les headers)
        for i, record in enumerate(all_records):
            if record.get("Statut") == "A_FAIRE":
                row_number = i + 2 # +1 car 0-indexed, +1 car header en ligne 1
                print(f"   [GSheet] Annonce trouvée ligne {row_number}: {record.get('Titre')}")
                return record, row_number
        
        print("   [GSheet] Aucune annonce 'A_FAIRE' trouvée.")
        return None, None
        
    except Exception as e:
        print(f"ERROR Lecture Sheet: {e}")
        return None, None

def mark_ad_as_published(sheet, row_number):
    """
    Met à jour la colonne Statut à 'FAIT' pour la ligne donnée.
    Suppose que la colonne Statut est la colonne G (7ème colonne) comme dans le plan.
    Pour être plus robuste, on cherche la col 'Statut'.
    """
    try:
        # Trouver l'index de la colonne 'Statut'
        headers = sheet.row_values(1)
        # Normalisation pour éviter les erreurs d'espaces "Prix " ou de casse
        normalized_headers = [h.strip().lower() for h in headers]
        
        if "statut" not in normalized_headers:
            print("ERROR: Colonne 'Statut' introuvable (Vérifiez l'orthographe).")
            return

        col_index = normalized_headers.index("statut") + 1
        
        print(f"   [GSheet] Mise à jour ligne {row_number}, col {col_index} -> 'FAIT'")
        sheet.update_cell(row_number, col_index, "FAIT")
        print("   [GSheet] Mise à jour effectuée.")
    except Exception as e:
        print(f"ERROR Update Sheet: {e}")

if __name__ == "__main__":
    # Test rapide si lancé directement
    pass
