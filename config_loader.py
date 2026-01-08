"""
Module de chargement de la configuration depuis fichier externe
Permet au client de configurer le bot sans modifier le code
"""

import os
from pathlib import Path

def load_env_file(env_file="config.env"):
    """
    Charge les variables depuis un fichier .env
    
    Args:
        env_file: Nom du fichier de configuration
    
    Returns:
        dict: Dictionnaire des variables de configuration
    """
    config = {}
    env_path = Path(env_file)
    
    if not env_path.exists():
        print(f"⚠️  Fichier {env_file} introuvable.")
        print(f"   Copiez {env_file}.example vers {env_file} et configurez-le.")
        return None
    
    with open(env_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            
            # Ignorer les commentaires et lignes vides
            if not line or line.startswith('#'):
                continue
            
            # Parser les variables KEY=VALUE
            if '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()
                
                # Supprimer les guillemets si présents
                if value.startswith('"') and value.endswith('"'):
                    value = value[1:-1]
                elif value.startswith("'") and value.endswith("'"):
                    value = value[1:-1]
                
                config[key] = value
    
    return config

def get_config_value(key, default=None, config_dict=None):
    """
    Récupère une valeur de configuration
    
    Ordre de priorité :
    1. Variable d'environnement système
    2. Fichier config.env
    3. Valeur par défaut
    
    Args:
        key: Nom de la variable
        default: Valeur par défaut si non trouvée
        config_dict: Dictionnaire de config (si déjà chargé)
    
    Returns:
        Valeur de la configuration
    """
    # 1. Variable d'environnement système (prioritaire)
    env_value = os.getenv(key)
    if env_value is not None:
        return env_value
    
    # 2. Fichier config.env
    if config_dict is None:
        config_dict = load_env_file()
    
    if config_dict and key in config_dict:
        return config_dict[key]
    
    # 3. Valeur par défaut
    return default

def convert_to_bool(value):
    """Convertit une valeur string en booléen"""
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() in ('true', '1', 'yes', 'oui', 'on')
    return bool(value)

def convert_to_int(value, default=0):
    """Convertit une valeur string en entier"""
    try:
        return int(value)
    except (ValueError, TypeError):
        return default

def load_full_config():
    """
    Charge toute la configuration avec conversion de types
    
    Returns:
        dict: Configuration complète avec types corrects
    """
    config_dict = load_env_file()
    
    if config_dict is None:
        return None
    
    # Configuration avec types convertis
    config = {
        # Identifiants
        'EMAIL': get_config_value('LEBONCOIN_EMAIL', config_dict=config_dict),
        'PASSWORD': get_config_value('LEBONCOIN_PASSWORD', config_dict=config_dict),
        
        # Google Sheets
        'SHEET_NAME': get_config_value('GOOGLE_SHEET_NAME', 'LBC-Automation', config_dict),
        
        # Publication
        'MAX_ADS_PER_RUN': convert_to_int(
            get_config_value('MAX_ADS_PER_RUN', '3', config_dict), 3
        ),
        'DELAY_BETWEEN_ADS_MIN': convert_to_int(
            get_config_value('DELAY_BETWEEN_ADS_MIN', '300', config_dict), 300
        ),
        'DELAY_BETWEEN_ADS_MAX': convert_to_int(
            get_config_value('DELAY_BETWEEN_ADS_MAX', '600', config_dict), 600
        ),
        'ENABLE_REAL_POSTING': convert_to_bool(
            get_config_value('ENABLE_REAL_POSTING', 'false', config_dict)
        ),
        
        # Navigateur
        'BROWSER_MODE': get_config_value('BROWSER_MODE', 'minimized', config_dict),
        
        # Captcha
        'CAPTCHA_MAX_WAIT': convert_to_int(
            get_config_value('CAPTCHA_MAX_WAIT', '300', config_dict), 300
        ),
        'CAPTCHA_MODE': get_config_value('CAPTCHA_MODE', 'manual', config_dict),
        
        # URLs (constants)
        'LOGIN_URL': "https://www.leboncoin.fr/se-connecter",
        'POST_AD_URL': "https://www.leboncoin.fr/deposer-une-annonce",
        'COOKIE_FILE': "state.json",
    }
    
    return config

# Export pour utilisation dans d'autres modules
__all__ = ['load_env_file', 'get_config_value', 'load_full_config', 'convert_to_bool', 'convert_to_int']

