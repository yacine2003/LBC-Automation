"""
Module de gestion des captchas
Détecte et permet la résolution manuelle ou automatique
"""

import time
from playwright.sync_api import Page

class CaptchaHandler:
    def __init__(self, ws_callback=None):
        self.captcha_detected = False
        self.manual_mode = True  # Par défaut, résolution manuelle
        self.ws_callback = ws_callback  # Callback pour notifications WebSocket
    
    def notify_captcha_detected(self):
        """Notifie via WebSocket qu'un captcha a été détecté"""
        if self.ws_callback:
            try:
                self.ws_callback({"type": "captcha_detected"})
            except:
                pass
    
    def notify_captcha_resolved(self):
        """Notifie via WebSocket qu'un captcha a été résolu"""
        if self.ws_callback:
            try:
                self.ws_callback({"type": "captcha_resolved"})
            except:
                pass
    
    def detect_captcha(self, page: Page) -> bool:
        """
        Détecte la présence d'un captcha sur la page
        
        Returns:
            True si un captcha est détecté, False sinon
        """
        print("   [Captcha] Vérification présence captcha...")
        
        # Liste des indicateurs de captcha
        captcha_indicators = [
            # Google reCAPTCHA
            "iframe[src*='recaptcha']",
            "div[class*='recaptcha']",
            ".g-recaptcha",
            
            # hCaptcha
            "iframe[src*='hcaptcha']",
            "div[class*='hcaptcha']",
            ".h-captcha",
            
            # DataDome
            "iframe[src*='datadome']",
            "div[id*='datadome']",
            
            # Cloudflare
            "iframe[src*='challenges.cloudflare']",
            "div[class*='cf-challenge']",
            
            # FunCaptcha
            "iframe[src*='funcaptcha']",
            
            # Indicateurs génériques
            "div[id*='captcha']",
            "div[class*='captcha']",
        ]
        
        for selector in captcha_indicators:
            try:
                element = page.locator(selector).first
                if element.is_visible(timeout=1000):
                    captcha_type = selector.split('[')[0]
                    print(f"   [Captcha] ⚠️ CAPTCHA DÉTECTÉ : {captcha_type}")
                    self.captcha_detected = True
                    return True
            except:
                continue
        
        # Vérifier le titre de la page
        try:
            title = page.title().lower()
            if "captcha" in title or "vérification" in title or "verification" in title:
                print(f"   [Captcha] ⚠️ CAPTCHA DÉTECTÉ (titre page) : {page.title()}")
                self.captcha_detected = True
                return True
        except:
            pass
        
        print("   [Captcha] ✅ Aucun captcha détecté")
        return False
    
    def wait_for_manual_resolution(self, page: Page, timeout: int = 300):
        """
        Attend que l'utilisateur résolve manuellement le captcha
        
        Args:
            page: Page Playwright
            timeout: Temps maximum d'attente en secondes (5 min par défaut)
        """
        # Notifier via WebSocket
        self.notify_captcha_detected()
        
        print()
        print("=" * 80)
        print("⏸️  PAUSE CAPTCHA - RÉSOLUTION MANUELLE REQUISE")
        print("=" * 80)
        print()
        print("🔍 Un captcha a été détecté sur la page.")
        print("👉 Veuillez résoudre le captcha manuellement dans le navigateur.")
        print()
        print(f"⏱️  Temps maximum : {timeout} secondes ({timeout//60} minutes)")
        print()
        print("Le bot attendra que vous ayez terminé...")
        print("=" * 80)
        print()
        
        start_time = time.time()
        check_interval = 3  # Vérifier toutes les 3 secondes
        
        while time.time() - start_time < timeout:
            # Vérifier si le captcha a disparu
            if not self.detect_captcha(page):
                print()
                print("=" * 80)
                print("✅ CAPTCHA RÉSOLU - Le bot continue...")
                print("=" * 80)
                print()
                self.captcha_detected = False
                
                # Notifier via WebSocket
                self.notify_captcha_resolved()
                
                return True
            
            # Afficher le temps écoulé
            elapsed = int(time.time() - start_time)
            remaining = timeout - elapsed
            print(f"   ⏳ Attente résolution... ({elapsed}s écoulées, {remaining}s restantes)", end="\r")
            
            time.sleep(check_interval)
        
        # Timeout atteint
        print()
        print("=" * 80)
        print("⚠️  TIMEOUT - Le captcha n'a pas été résolu dans le temps imparti")
        print("=" * 80)
        print()
        return False
    
    def handle_captcha(self, page: Page, max_wait: int = 300) -> bool:
        """
        Gère la présence d'un captcha (détection + résolution)
        
        Args:
            page: Page Playwright
            max_wait: Temps maximum d'attente pour résolution manuelle
        
        Returns:
            True si le captcha a été résolu ou n'existe pas, False sinon
        """
        # Détecter le captcha
        if not self.detect_captcha(page):
            return True  # Pas de captcha, on continue
        
        # Captcha détecté
        if self.manual_mode:
            # Mode manuel : attendre la résolution par l'utilisateur
            return self.wait_for_manual_resolution(page, timeout=max_wait)
        else:
            # Mode automatique : intégration future avec service de résolution
            print("   [Captcha] Mode automatique non implémenté. Passage en mode manuel.")
            return self.wait_for_manual_resolution(page, timeout=max_wait)
    
    def check_at_key_moments(self, page: Page, moment: str):
        """
        Vérifie la présence de captcha aux moments clés du processus
        
        Args:
            page: Page Playwright
            moment: Description du moment (ex: "après connexion", "avant dépôt")
        """
        print(f"   [Captcha] Vérification {moment}...")
        if self.detect_captcha(page):
            print(f"   [Captcha] Captcha détecté {moment}. Résolution requise.")
            return self.handle_captcha(page)
        return True


# Fonction utilitaire pour intégration rapide
def check_and_handle_captcha(page: Page, moment: str = "") -> bool:
    """
    Fonction utilitaire pour vérifier et gérer un captcha
    
    Usage:
        if not check_and_handle_captcha(page, "après connexion"):
            return "CAPTCHA_FAILED"
    """
    handler = CaptchaHandler()
    if moment:
        return handler.check_at_key_moments(page, moment)
    else:
        return handler.handle_captcha(page)

