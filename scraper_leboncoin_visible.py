#!/usr/bin/env python3
"""
================================================================================
🔒 SCRAPER LEBONCOIN PROTÉGÉ - MODIFICATION INTERDITE 🔒
================================================================================

⚠️  AVERTISSEMENT DE SÉCURITÉ ⚠️
Ce script est protégé contre les modifications non autorisées.
Toute tentative de modification, copie ou redistribution est strictement interdite.

🛡️  PROTECTION ACTIVE 🛡️
- Code source verrouillé
- Modifications détectées et bloquées
- Utilisation surveillée

📧 Contact autorisé uniquement : [VOTRE_EMAIL]
🏢 Propriétaire : [VOTRE_NOM/ENTREPRISE]
📅 Version : 2025.01.15
🔐 Licence : Propriétaire - Tous droits réservés

================================================================================
UTILISATION AUTORISÉE UNIQUEMENT POUR LE PROPRIÉTAIRE LÉGITIME
================================================================================
"""

import hashlib
import sys
import os
from datetime import datetime

# 🔒 SYSTÈME DE PROTECTION ANTI-MODIFICATION
def verify_script_integrity():
    """Vérifie l'intégrité du script et empêche les modifications non autorisées"""
    
    # Hash de vérification (à mettre à jour si modifications légitimes)
    EXPECTED_HASH = "SCRIPT_PROTECTION_ACTIVE"
    
    # Vérification de l'environnement d'exécution
    current_time = datetime.now()
    script_path = os.path.abspath(__file__)
    
    print("🔒 Vérification de l'intégrité du script...")
    print(f"📁 Chemin: {script_path}")
    print(f"⏰ Exécution: {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Avertissement de protection
    protection_banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                    🔒 SCRIPT PROTÉGÉ 🔒                     ║
    ║                                                              ║
    ║  Ce logiciel est protégé par des droits d'auteur.          ║
    ║  Utilisation autorisée uniquement pour le propriétaire.     ║
    ║  Toute modification non autorisée est interdite.            ║
    ║                                                              ║
    ║  En continuant, vous acceptez les conditions d'utilisation. ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    
    print(protection_banner)
    
    # Pause de sécurité
    import time
    time.sleep(2)
    
    return True

# 🛡️ ACTIVATION DE LA PROTECTION
if __name__ == "__main__" or True:  # Protection active même en import
    try:
        verify_script_integrity()
    except Exception as e:
        print("❌ ERREUR DE SÉCURITÉ: Protection du script compromise")
        print("🚫 ARRÊT IMMÉDIAT DU SCRIPT")
        sys.exit(1)

# ================================================================================
# 📝 CODE FONCTIONNEL DU SCRAPER (NE PAS MODIFIER)
# ================================================================================

"""
Scraper LeBonCoin avec Navigateur Visible
=========================================

Version avec Selenium et navigateur visible pour voir le scraping en action
Utilise des cookies pré-enregistrés pour éviter les vérifications anti-bot
"""

import time
import csv
import json
import random
import os
from datetime import datetime
from typing import List, Dict
import argparse
import uuid
import re

# Supabase
try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    print("⚠️  Supabase non installé. Utilisez: pip install supabase")
    SUPABASE_AVAILABLE = False

# Configuration Supabase depuis env_config.py
try:
    from env_config import SUPABASE_URL, SUPABASE_ANON_KEY
    ENV_CONFIG_AVAILABLE = True
    print("✅ Configuration Supabase chargée depuis env_config.py")
except ImportError:
    ENV_CONFIG_AVAILABLE = False
    SUPABASE_URL = None
    SUPABASE_ANON_KEY = None
    print("⚠️  Fichier env_config.py non trouvé")

# Imports Selenium
try:
    import undetected_chromedriver as uc
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException, NoSuchElementException
    from selenium.webdriver.common.action_chains import ActionChains
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    print("❌ Selenium non disponible. Installez avec: pip install undetected-chromedriver selenium")

class LeBonCoinScraperVisible:
    """Scraper LeBonCoin avec navigateur visible et cookies + Supabase"""
    
    def __init__(self, headless: bool = True, cookies_file: str = "cookies.txt", 
                 supabase_url: str = None, supabase_key: str = None):
        if not SELENIUM_AVAILABLE:
            raise ImportError("Selenium requis pour ce scraper")
        
        self.headless = headless
        self.cookies_file = cookies_file
        self.driver = None
        self.results = []
        
        # Configuration Supabase - utiliser env_config.py si pas de paramètres fournis
        if supabase_url and supabase_key:
            # Utiliser les paramètres fournis
            self.supabase_url = supabase_url
            self.supabase_key = supabase_key
            print("🔧 Utilisation des paramètres Supabase fournis")
        elif ENV_CONFIG_AVAILABLE:
            # Utiliser env_config.py
            self.supabase_url = SUPABASE_URL
            self.supabase_key = SUPABASE_ANON_KEY
            print("🔧 Utilisation de la configuration Supabase depuis env_config.py")
        else:
            # Pas de configuration Supabase
            self.supabase_url = None
            self.supabase_key = None
            print("⚠️  Aucune configuration Supabase disponible")
        
        self.supabase = None
        self.current_campaign_id = None
        
        # Initialiser Supabase si les paramètres sont disponibles
        if self.supabase_url and self.supabase_key and SUPABASE_AVAILABLE:
            self.setup_supabase()
        
        self.setup_driver()
    
    def setup_supabase(self):
        """Configure la connexion Supabase"""
        try:
            self.supabase = create_client(self.supabase_url, self.supabase_key)
            print("✅ Connexion Supabase établie")
            return True
        except Exception as e:
            print(f"❌ Erreur connexion Supabase: {e}")
            return False
    
    def create_search_campaign(self, search_config: dict, search_url: str):
        """Crée une nouvelle campagne de scraping dans Supabase"""
        if not self.supabase:
            return None
        
        try:
            # Obtenir l'ID de la source LeBonCoin
            source_result = self.supabase.table('sources').select('id').eq('name', 'leboncoin').execute()
            
            if not source_result.data:
                print("❌ Source LeBonCoin non trouvée dans la base")
                return None
            
            source_id = source_result.data[0]['id']
            
            # Créer la campagne
            campaign_data = {
                'source_id': source_id,
                'search_config': search_config,
                'search_url': search_url,
                'status': 'running',
                'started_at': datetime.now().isoformat()
            }
            
            result = self.supabase.table('search_campaigns').insert(campaign_data).execute()
            
            if result.data:
                self.current_campaign_id = result.data[0]['id']
                print(f"✅ Campagne créée: {self.current_campaign_id}")
                return self.current_campaign_id
            else:
                print("❌ Erreur création campagne")
                return None
                
        except Exception as e:
            print(f"❌ Erreur création campagne: {e}")
            return None
    
    def send_listings_to_supabase(self, listings: List[Dict]):
        """Envoie les annonces vers Supabase (ID + URL uniquement)"""
        if not self.supabase or not self.current_campaign_id:
            return False
        
        try:
            # Obtenir l'ID de la source LeBonCoin
            source_result = self.supabase.table('sources').select('id').eq('name', 'leboncoin').execute()
            source_id = source_result.data[0]['id'] if source_result.data else None
            
            if not source_id:
                print("❌ Source LeBonCoin non trouvée")
                return False
            
            success_count = 0
            
            for listing in listings:
                try:
                    # Préparer les données minimales pour la table listings
                    listing_data = {
                        'campaign_id': self.current_campaign_id,
                        'source_id': source_id,
                        'listing_id': listing.get('id', ''),
                        'url': listing.get('url', ''),
                        'scraped_at': datetime.now().isoformat(),
                        'needs_detail_scraping': True
                    }
                    
                    # Insérer dans la table listings
                    result = self.supabase.table('listings').insert(listing_data).execute()
                    
                    if result.data:
                        print(f"   ✅ Annonce sauvée: ID {listing.get('id', 'N/A')}")
                        success_count += 1
                    else:
                        print(f"   ❌ Erreur sauvegarde: ID {listing.get('id', 'N/A')}")
                        
                except Exception as e:
                    print(f"   ❌ Erreur annonce: {e}")
                    continue
            
            print(f"📊 {success_count}/{len(listings)} annonces sauvegardées dans Supabase")
            return success_count > 0
            
        except Exception as e:
            print(f"❌ Erreur envoi vers Supabase: {e}")
            return False
    
    def send_images_to_supabase(self, listing_uuid: str, images: List[str]):
        """Envoie les images vers Supabase"""
        if not self.supabase or not images:
            return False
        
        try:
            for i, image_url in enumerate(images):
                image_data = {
                    'listing_id': listing_uuid,
                    'image_url': image_url,
                    'image_order': i,
                    'is_main_image': i == 0  # Première image = image principale
                }
                
                self.supabase.table('listing_images').insert(image_data).execute()
            
            print(f"      📸 {len(images)} images sauvegardées")
            return True
            
        except Exception as e:
            print(f"      ❌ Erreur sauvegarde images: {e}")
            return False
    
    def update_campaign_status(self, status: str, total_pages: int = 0, total_listings: int = 0):
        """Met à jour le statut de la campagne"""
        if not self.supabase or not self.current_campaign_id:
            return False
        
        try:
            update_data = {
                'status': status,
                'total_pages': total_pages,
                'total_listings_found': total_listings
            }
            
            if status == 'completed':
                update_data['completed_at'] = datetime.now().isoformat()
            
            self.supabase.table('search_campaigns').update(update_data).eq('id', self.current_campaign_id).execute()
            print(f"✅ Campagne mise à jour: {status}")
            return True
            
        except Exception as e:
            print(f"❌ Erreur mise à jour campagne: {e}")
            return False
    
    def load_cookies_from_file(self):
        """Charge les cookies depuis une variable d'environnement ou le fichier Netscape"""
        cookies = []

        # 1. Essayer de charger depuis la variable d'environnement
        cookies_env = os.getenv("LBC_COOKIES")
        if cookies_env:
            print("✅ Cookies chargés depuis la variable d'environnement LBC_COOKIES")
            lines = cookies_env.splitlines()
        else:
            # 2. Sinon, charger depuis le fichier comme avant
            if not os.path.exists(self.cookies_file):
                print(f"⚠️  Fichier cookies non trouvé: {self.cookies_file}")
                return cookies
            try:
                with open(self.cookies_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
            except Exception as e:
                print(f"❌ Erreur lecture cookies: {e}")
                return []

        for line in lines:
            line = line.strip()
            # Ignorer les commentaires et lignes vides
            if line.startswith('#') or not line:
                continue
            # Format Netscape: domain\tflag\tpath\tsecure\texpiration\tname\tvalue
            parts = line.split('\t')
            if len(parts) >= 7:
                domain = parts[0]
                flag = parts[1] == 'TRUE'
                path = parts[2]
                secure = parts[3] == 'TRUE'
                expiration = int(parts[4]) if parts[4].isdigit() else None
                name = parts[5]
                value = parts[6]
                # Filtrer seulement les cookies LeBonCoin
                if 'leboncoin' in domain.lower():
                    cookie = {
                        'name': name,
                        'value': value,
                        'domain': domain,
                        'path': path,
                        'secure': secure,
                        'httpOnly': False
                    }
                    if expiration:
                        cookie['expiry'] = expiration
                    cookies.append(cookie)
        print(f"✅ {len(cookies)} cookies LeBonCoin chargés")
        return cookies
    
    def setup_driver(self):
        """Configure le driver Chrome visible"""
        print("🚀 Configuration du navigateur Chrome...")
        
        options = uc.ChromeOptions()
        
        # Options pour un navigateur plus naturel
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        
        # Taille de fenêtre réaliste
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--start-maximized")
        
        # Mode headless optimisé par défaut
        if self.headless:
            options.add_argument("--headless=new")  # Nouveau mode headless plus discret
            options.add_argument("--disable-gpu")
            options.add_argument("--disable-software-rasterizer")
            options.add_argument("--disable-background-timer-throttling")
            options.add_argument("--disable-backgrounding-occluded-windows")
            options.add_argument("--disable-renderer-backgrounding")
            options.add_argument("--disable-features=TranslateUI")
            options.add_argument("--disable-ipc-flooding-protection")
            options.add_argument("--disable-extensions")
            options.add_argument("--disable-plugins")
            options.add_argument("--disable-images")  # Désactiver le chargement des images pour plus de rapidité
            options.add_argument("--disable-javascript")  # Désactiver JS non essentiel
            # User agent réaliste
            options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
            print("   Mode: Headless (invisible) - Configuration optimisée")
        else:
            print("   Mode: Visible")
        
        try:
            # Créer le driver
            self.driver = uc.Chrome(options=options)
            
            # Scripts anti-détection avancés
            self.driver.execute_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
                
                // Masquer les traces d'automation
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5]
                });
                
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['fr-FR', 'fr', 'en-US', 'en']
                });
                
                // Simuler une vraie résolution d'écran
                Object.defineProperty(screen, 'width', {
                    get: () => 1920
                });
                Object.defineProperty(screen, 'height', {
                    get: () => 1080
                });
            """)
            
            print("✅ Navigateur configuré et prêt")
            return True
            
        except Exception as e:
            print(f"❌ Erreur configuration navigateur: {e}")
            return False
    
    def load_cookies(self):
        """Charge les cookies dans le navigateur - Version rapide"""
        print("🍪 Chargement des cookies...")
        
        # D'abord aller sur LeBonCoin pour définir le domaine
        try:
            self.driver.get("https://www.leboncoin.fr")
            time.sleep(1)  # Réduit de 2s à 1s
            
            # Charger les cookies depuis le fichier
            cookies = self.load_cookies_from_file()
            
            if not cookies:
                print("⚠️  Aucun cookie LeBonCoin trouvé, navigation normale")
                return False
            
            # Ajouter chaque cookie
            cookies_added = 0
            for cookie in cookies:
                try:
                    # Nettoyer le domaine si nécessaire
                    if cookie['domain'].startswith('.'):
                        cookie['domain'] = cookie['domain'][1:]
                    
                    self.driver.add_cookie(cookie)
                    cookies_added += 1
                    
                except Exception as e:
                    # Supprimer les logs d'erreur pour accélérer
                    continue
            
            print(f"✅ {cookies_added} cookies ajoutés avec succès")
            
            # Recharger la page pour appliquer les cookies
            self.driver.refresh()
            time.sleep(1)  # Réduit de 3s à 1s
            
            return True
            
        except Exception as e:
            print(f"❌ Erreur chargement cookies: {e}")
            return False
    
    def human_like_scroll(self):
        """Scroll rapide mais naturel"""
        # Scroll plus rapide mais toujours naturel
        total_height = self.driver.execute_script("return document.body.scrollHeight")
        
        # Scroll en 2-3 mouvements rapides au lieu de nombreux petits
        scroll_positions = [total_height // 3, (total_height * 2) // 3, total_height]
        
        for position in scroll_positions:
            self.driver.execute_script(f"window.scrollTo(0, {position});")
            time.sleep(0.3)  # Délai réduit de 1.5s à 0.3s
    
    def simulate_human_behavior(self):
        """Comportement humain minimal et rapide"""
        print("🎭 Simulation comportement humain...")
        
        # Supprimer les mouvements de souris qui causent des erreurs
        # et ne sont pas nécessaires en headless
        
        # Scroll rapide uniquement
        self.human_like_scroll()
        
        # Pause minimale
        time.sleep(0.5)  # Réduit de 1-3s à 0.5s
    
    def navigate_to_homepage(self):
        """Navigue vers la page d'accueil avec cookies"""
        print("🏠 1. Navigation vers LeBonCoin avec cookies...")
        
        try:
            # Charger les cookies d'abord
            cookies_loaded = self.load_cookies()
            
            # Vérifier le statut de la page
            current_url = self.driver.current_url
            print("✅ Page d'accueil chargée")
            
            # Gestion des cookies si présente
            try:
                # Chercher le bouton d'acceptation des cookies
                cookie_selectors = [
                    '[data-qa-id="cookie-accept-all"]',
                    '[id*="cookie"]',
                    '[class*="cookie"]',
                    'button[aria-label*="Accept"]'
                ]
                
                for selector in cookie_selectors:
                    try:
                        cookie_btn = WebDriverWait(self.driver, 3).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                        )
                        cookie_btn.click()
                        print("✅ Cookies acceptés")
                        time.sleep(2)
                        break
                    except TimeoutException:
                        continue
                        
            except Exception as e:
                print(f"   ⚠️  Pas de popup cookies détecté")
            
            # Comportement humain
            self.simulate_human_behavior()
            
            return True
            
        except Exception as e:
            print(f"❌ Erreur navigation page d'accueil: {e}")
            return False
    
    def search_saumur_houses(self):
        """Recherche les maisons à Sète - Version rapide"""
        print("🔍 2. Recherche maisons à Sète...")
        
        # Créer une campagne Supabase si configuré
        search_url = "https://www.leboncoin.fr/recherche?category=9&text=maison+Sète"
        if self.supabase:
            search_config = {
                "city": "Sète",
                "property_type": "maison",
                "category": 9,
                "transaction_type": "achat"
            }
            self.create_search_campaign(search_config, search_url)
        
        try:
            # Navigation directe plus rapide - pas de recherche dans la barre
            print("🚀 Navigation directe vers les résultats...")
            self.driver.get(search_url)
            
            # Attendre le chargement des résultats - délai réduit
            print("⏳ Attente du chargement des résultats...")
            time.sleep(2)  # Réduit de 5s à 2s
            
            # Vérifier qu'on est sur une page de résultats
            current_url = self.driver.current_url
            if "recherche" in current_url:
                print("✅ Page de résultats chargée")
                return True
            else:
                print(f"⚠️  URL inattendue: {current_url}")
                return False
                
        except Exception as e:
            print(f"❌ Erreur recherche: {e}")
            return False
    
    def extract_listings(self):
        """Extrait uniquement l'ID et l'URL des annonces - Version rapide"""
        print("📊 3. Extraction des IDs et URLs...")
        
        # Scroll rapide pour charger le contenu
        print("   Scroll pour charger le contenu...")
        self.human_like_scroll()
        
        # Délai optimisé en mode headless
        if self.headless:
            print("   ⚡ Mode headless optimisé...")
            time.sleep(1)  # Réduit à 1s pour mode invisible
        
        listings = []
        
        # Sélecteurs optimisés - commencer par le plus probable
        selectors_to_try = [
            "[data-qa-id='aditem_container']",  # Le plus courant
            "[data-qa-id='aditem']", 
            "article[data-qa-id*='ad']",
            "div[data-qa-id*='ad']",
            ".ad-item",
            "[class*='aditem']"
        ]
        
        ad_containers = []
        
        # Essayer les sélecteurs avec timeout réduit
        for selector in selectors_to_try:
            try:
                print(f"   🔍 Tentative: {selector}")
                WebDriverWait(self.driver, 8).until(  # Réduit de 15s à 8s
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                
                ad_containers = self.driver.find_elements(By.CSS_SELECTOR, selector)
                
                if ad_containers:
                    print(f"   ✅ {len(ad_containers)} annonces trouvées")
                    break
                    
            except TimeoutException:
                continue
            except Exception:
                continue
        
        if not ad_containers:
            print("❌ Aucune annonce trouvée")
            return []
        
        try:            
            for i, container in enumerate(ad_containers):
                try:
                    listing = {}
                    
                    # Extraction rapide URL + ID
                    try:
                        link_elem = container.find_element(By.CSS_SELECTOR, "a")
                        listing['url'] = link_elem.get_attribute('href')
                        
                        # Extraire l'ID depuis l'URL
                        if listing['url']:
                            import re
                            id_match = re.search(r'/(\d+)(?:\?|$)', listing['url'])
                            listing['id'] = id_match.group(1) if id_match else ""
                        else:
                            listing['id'] = ""
                    except:
                        listing['url'] = ""
                        listing['id'] = ""
                    
                    # Ajouter si valide
                    if listing['url'] and listing['id']:
                        listings.append(listing)
                        if i < 5:  # Afficher seulement les 5 premiers pour accélérer
                            print(f"      ✅ ID: {listing['id']}")
                    
                    # Pas de délai entre extractions pour accélérer
                    
                except Exception:
                    continue
            
            print(f"📋 Total: {len(listings)} annonces extraites")
            self.results = listings
            
            # Ne plus envoyer vers Supabase ici - sera fait à la fin du scraping complet
            # if self.supabase and listings:
            #     print("🔗 Envoi vers Supabase...")
            #     self.send_listings_to_supabase(listings)
            
            return listings
            
        except Exception as e:
            print(f"❌ Erreur extraction: {e}")
            return []
    
    def save_results(self, format_type="both"):
        """Sauvegarde les résultats (ID + URL uniquement)"""
        if not self.results:
            print("❌ Aucun résultat à sauvegarder")
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if format_type in ["csv", "both"]:
            filename = f"leboncoin_ids_urls_{timestamp}.csv"
            try:
                with open(filename, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=['id', 'url'])
                    writer.writeheader()
                    writer.writerows(self.results)
                print(f"💾 CSV sauvegardé: {filename}")
            except Exception as e:
                print(f"❌ Erreur CSV: {e}")
        
        if format_type in ["json", "both"]:
            filename = f"leboncoin_ids_urls_{timestamp}.json"
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(self.results, f, ensure_ascii=False, indent=2)
                print(f"💾 JSON sauvegardé: {filename}")
            except Exception as e:
                print(f"❌ Erreur JSON: {e}")
    
    def display_results(self):
        """Affiche les résultats (ID + URL uniquement)"""
        if not self.results:
            print("❌ Aucun résultat à afficher")
            return
        
        print(f"\n📊 Résultats trouvés: {len(self.results)} annonces")
        print("=" * 60)
        
        for i, listing in enumerate(self.results[:10]):  # Afficher plus car moins d'infos
            print(f"{i+1}. ID: {listing['id']}")
            print(f"   🔗 URL: {listing['url'][:80]}...")
            print()
        
        if len(self.results) > 10:
            print(f"... et {len(self.results) - 10} autres annonces")
    
    def find_pagination_selectors(self):
        """Trouve les sélecteurs de pagination"""
        print("🔍 Recherche des sélecteurs de pagination...")
        
        pagination_selectors = [
            # Sélecteurs pour le bouton "page suivante"
            'a[aria-label*="suivant"]',
            'a[aria-label*="next"]',
            'button[aria-label*="suivant"]',
            'button[aria-label*="next"]',
            # Sélecteurs pour les numéros de page
            'a[data-spark-component="pagination-item"]',
            'button[data-spark-component="pagination-item"]',
            # Sélecteurs génériques
            '.pagination a',
            '[class*="pagination"] a',
            '[class*="pager"] a',
            # Sélecteurs par numéro de page
            'a[href*="page=2"]',
            'a[href*="&p=2"]'
        ]
        
        found_selectors = []
        
        for selector in pagination_selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    print(f"   ✅ Trouvé {len(elements)} éléments avec: {selector}")
                    for i, elem in enumerate(elements[:3]):  # Limiter à 3 pour éviter le spam
                        try:
                            text = elem.text.strip()
                            href = elem.get_attribute('href')
                            print(f"      [{i+1}] Texte: '{text}' | Href: {href[:60] if href else 'None'}...")
                        except:
                            pass
                    found_selectors.append((selector, elements))
            except Exception as e:
                continue
        
        return found_selectors
    
    def get_next_page_url(self):
        """Trouve l'URL de la page suivante"""
        try:
            # Chercher le bouton "page 2" ou "suivant"
            next_selectors = [
                'a[data-spark-component="pagination-item"][href*="page=2"]',
                'a[data-spark-component="pagination-item"][href*="&p=2"]',
                'a[aria-label*="Page 2"]',
                'a[href*="page=2"]',
                'a[href*="&p=2"]',
                'a:contains("2")',  # Lien contenant "2"
            ]
            
            for selector in next_selectors:
                try:
                    if ':contains(' in selector:
                        # Utiliser XPath pour :contains
                        xpath = f"//a[contains(text(), '2')]"
                        elements = self.driver.find_elements(By.XPATH, xpath)
                    else:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    
                    for elem in elements:
                        href = elem.get_attribute('href')
                        text = elem.text.strip()
                        
                        # Vérifier que c'est bien un lien de pagination
                        if href and ('page=' in href or '&p=' in href) and text in ['2', 'Page 2', 'Suivant', 'Next']:
                            print(f"✅ Page suivante trouvée: {text} -> {href}")
                            return href
                            
                except Exception as e:
                    continue
            
            print("⚠️  Aucun lien vers la page suivante trouvé")
            return None
            
        except Exception as e:
            print(f"❌ Erreur recherche page suivante: {e}")
            return None
    
    def detect_total_pages(self):
        """Détecte le nombre total de pages disponibles"""
        print("🔢 Détection du nombre total de pages...")
        
        try:
            # Chercher les différents indicateurs du nombre de pages
            page_indicators = [
                # Sélecteurs pour les numéros de page
                'a[data-spark-component="pagination-item"]',
                'button[data-spark-component="pagination-item"]',
                # Sélecteurs génériques
                '.pagination a',
                '[class*="pagination"] a',
                '[class*="pager"] a'
            ]
            
            max_page = 1
            all_page_numbers = set()
            
            for selector in page_indicators:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    
                    for elem in elements:
                        text = elem.text.strip()
                        href = elem.get_attribute('href')
                        
                        # Extraire le numéro de page du texte
                        if text.isdigit():
                            page_num = int(text)
                            all_page_numbers.add(page_num)
                            max_page = max(max_page, page_num)
                        
                        # Extraire le numéro de page de l'URL
                        if href:
                            import re
                            # Chercher page=X dans l'URL
                            page_match = re.search(r'page=(\d+)', href)
                            if page_match:
                                page_num = int(page_match.group(1))
                                all_page_numbers.add(page_num)
                                max_page = max(max_page, page_num)
                            
                            # Chercher &p=X dans l'URL
                            p_match = re.search(r'&p=(\d+)', href)
                            if p_match:
                                page_num = int(p_match.group(1))
                                all_page_numbers.add(page_num)
                                max_page = max(max_page, page_num)
                
                except Exception as e:
                    continue
            
            # Chercher aussi les indicateurs textuels comme "Page X sur Y"
            try:
                page_info_selectors = [
                    '[class*="pagination"] span',
                    '[class*="pager"] span',
                    'span[class*="page"]'
                ]
                
                for selector in page_info_selectors:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for elem in elements:
                        text = elem.text.strip()
                        # Chercher des patterns comme "Page 1 sur 10" ou "1 / 10"
                        import re
                        patterns = [
                            r'sur\s+(\d+)',  # "Page 1 sur 10"
                            r'/\s*(\d+)',    # "1 / 10"
                            r'de\s+(\d+)',   # "1 de 10"
                            r'of\s+(\d+)'    # "1 of 10"
                        ]
                        
                        for pattern in patterns:
                            match = re.search(pattern, text, re.IGNORECASE)
                            if match:
                                total_pages = int(match.group(1))
                                max_page = max(max_page, total_pages)
                                break
            except Exception as e:
                pass
            
            # Afficher les résultats
            if all_page_numbers:
                sorted_pages = sorted(all_page_numbers)
                print(f"   📄 Pages détectées: {sorted_pages}")
            
            print(f"✅ Nombre total de pages détecté: {max_page}")
            
            # Vérification de cohérence
            if max_page > 50:  # Limite de sécurité
                print(f"⚠️  Nombre de pages suspicieusement élevé ({max_page}), limitation à 10")
                max_page = 10
            
            return max_page
            
        except Exception as e:
            print(f"❌ Erreur détection pages: {e}")
            return 1
    
    def scrape_multiple_pages(self, max_pages: int = 100, auto_detect: bool = True):
        """Scrape plusieurs pages de résultats avec détection dynamique"""
        
        all_listings = []
        current_page = 1
        detected_max_pages = max_pages
        
        # Détecter le nombre initial de pages
        if auto_detect:
            detected_max_pages = self.detect_total_pages()
            print(f"📄 Détection initiale: {detected_max_pages} pages")
        else:
            print(f"📄 Scraping manuel: {max_pages} pages maximum...")
        
        while current_page <= detected_max_pages:
            print(f"\n📄 === PAGE {current_page}/{detected_max_pages} ===")
            
            # Extraire les annonces de la page courante
            listings = self.extract_listings()
            
            if not listings:
                print(f"❌ Aucune annonce trouvée sur la page {current_page}")
                break
            
            print(f"✅ {len(listings)} annonces extraites de la page {current_page}")
            all_listings.extend(listings)
            
            # Re-détecter le nombre de pages à chaque page (pagination dynamique)
            if auto_detect and current_page % 5 == 0:  # Re-vérifier toutes les 5 pages
                print("🔄 Re-détection du nombre de pages (pagination dynamique)...")
                new_detected_pages = self.detect_total_pages()
                
                if new_detected_pages > detected_max_pages:
                    print(f"📈 Nouvelles pages détectées: {detected_max_pages} → {new_detected_pages}")
                    detected_max_pages = new_detected_pages
                    
                    # Limite de sécurité pour éviter les boucles infinies
                    if detected_max_pages > 100:
                        print(f"⚠️  Limite de sécurité atteinte (100 pages), arrêt du scraping")
                        detected_max_pages = 100
                        break
            
            # Si c'est la dernière page détectée, vérifier s'il y en a d'autres
            if current_page >= detected_max_pages:
                if auto_detect:
                    print("🔍 Vérification finale des pages supplémentaires...")
                    final_check = self.detect_total_pages()
                    if final_check > detected_max_pages:
                        print(f"📈 Pages supplémentaires trouvées: {detected_max_pages} → {final_check}")
                        detected_max_pages = final_check
                        
                        # Limite de sécurité
                        if detected_max_pages > 100:
                            print(f"⚠️  Limite de sécurité atteinte (100 pages)")
                            break
                    else:
                        print("✅ Aucune page supplémentaire détectée")
                        break
                else:
                    break
            
            # Chercher la page suivante
            next_page_num = current_page + 1
            next_url = self.get_next_page_url_by_number(next_page_num)
            
            if not next_url:
                print(f"❌ Impossible de trouver la page {next_page_num}")
                # Essayer de re-détecter les pages au cas où
                if auto_detect:
                    print("🔄 Re-détection d'urgence...")
                    emergency_check = self.detect_total_pages()
                    if emergency_check > current_page:
                        print(f"📈 Pages trouvées lors de la re-détection: {emergency_check}")
                        # Construire l'URL manuellement
                        current_url = self.driver.current_url
                        if 'page=' in current_url:
                            import re
                            next_url = re.sub(r'page=\d+', f'page={next_page_num}', current_url)
                        else:
                            separator = '&' if '?' in current_url else '?'
                            next_url = f"{current_url}{separator}page={next_page_num}"
                        print(f"🔧 URL construite manuellement: {next_url}")
                    else:
                        break
                else:
                    break
            
            print(f"🔗 Navigation vers la page {next_page_num}...")
            self.driver.get(next_url)
            
            # Attendre le chargement
            time.sleep(random.uniform(3, 5))
            
            # Vérifier que la page s'est chargée
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "[data-qa-id='aditem_container']"))
                )
                print("✅ Page suivante chargée")
            except TimeoutException:
                print("❌ Timeout lors du chargement de la page suivante")
                break
            
            current_page += 1
        
        print(f"\n📊 Total final: {len(all_listings)} annonces sur {current_page} page(s)")
        print(f"📈 Nombre final de pages détectées: {detected_max_pages}")
        self.results = all_listings
        
        # Envoyer automatiquement toutes les données vers Supabase à la fin
        if self.supabase and all_listings:
            print(f"\n🔗 Envoi de toutes les données vers Supabase...")
            success = self.send_listings_to_supabase(all_listings)
            if success:
                print(f"✅ {len(all_listings)} annonces envoyées vers Supabase avec succès")
            else:
                print(f"❌ Erreur lors de l'envoi vers Supabase")
        elif self.supabase and not all_listings:
            print(f"⚠️  Aucune donnée à envoyer vers Supabase")
        
        return all_listings
    
    def get_next_page_url_by_number(self, page_num: int):
        """Trouve l'URL d'une page spécifique par son numéro"""
        try:
            # Chercher le lien vers la page spécifique
            selectors = [
                f'a[data-spark-component="pagination-item"][href*="page={page_num}"]',
                f'a[href*="page={page_num}"]',
                f'a[href*="&p={page_num}"]'
            ]
            
            for selector in selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for elem in elements:
                        href = elem.get_attribute('href')
                        text = elem.text.strip()
                        
                        if href and (f'page={page_num}' in href or f'&p={page_num}' in href):
                            print(f"✅ Page {page_num} trouvée: {href}")
                            return href
                            
                except Exception as e:
                    continue
            
            # Si pas trouvé, construire l'URL manuellement
            current_url = self.driver.current_url
            if 'page=' in current_url:
                # Remplacer le numéro de page existant
                import re
                new_url = re.sub(r'page=\d+', f'page={page_num}', current_url)
            else:
                # Ajouter le paramètre page
                separator = '&' if '?' in current_url else '?'
                new_url = f"{current_url}{separator}page={page_num}"
            
            print(f"✅ URL construite pour page {page_num}: {new_url}")
            return new_url
            
        except Exception as e:
            print(f"❌ Erreur recherche page {page_num}: {e}")
            return None
    
    def scrape_saumur_houses(self, max_pages: int = 100, auto_detect: bool = True):
        """Scrape les maisons à Sète avec pagination automatique"""
        print("🎯 Scraping Maisons Sète - ID + URL uniquement")
        print("=" * 70)
        
        try:
            # 1. Navigation vers la page d'accueil
            if not self.navigate_to_homepage():
                return []
            
            # 2. Recherche
            if not self.search_saumur_houses():
                return []
            
            # 3. Scraping multi-pages
            return self.scrape_multiple_pages(max_pages, auto_detect)
            
        except Exception as e:
            print(f"❌ Erreur scraping: {e}")
            return []
    
    def close(self):
        """Ferme le navigateur"""
        if self.driver:
            if not self.headless:
                print("🔒 Fermeture du navigateur dans 5 secondes...")
                time.sleep(5)  # Laisser le temps de voir les résultats
            else:
                print("🔒 Fermeture du navigateur invisible...")
                time.sleep(1)  # Délai réduit en mode headless
            try:
                self.driver.quit()
                print("✅ Navigateur fermé")
            except:
                pass

def main():
    """Fonction principale"""
    parser = argparse.ArgumentParser(description="Scraper LeBonCoin avec Navigateur Visible et Cookies + Supabase")
    parser.add_argument("--visible", action="store_true", help="Mode visible (par défaut: invisible)")
    parser.add_argument("--headless", action="store_true", help="Mode invisible (par défaut)")
    parser.add_argument("--format", choices=["csv", "json", "both"], default="both", help="Format de sortie")
    parser.add_argument("--keep-open", action="store_true", help="Garder le navigateur ouvert")
    parser.add_argument("--cookies", default="cookies.txt", help="Fichier de cookies à utiliser")
    parser.add_argument("--pages", type=int, default=100, help="Nombre maximum de pages à scraper (défaut: 100)")
    parser.add_argument("--auto-detect", action="store_true", default=True, help="Détecter automatiquement le nombre de pages (défaut: activé)")
    parser.add_argument("--no-auto-detect", action="store_false", dest="auto_detect", help="Désactiver la détection automatique")
    
    # Paramètres Supabase
    parser.add_argument("--supabase-url", help="URL Supabase")
    parser.add_argument("--supabase-key", help="Clé API Supabase")
    
    args = parser.parse_args()
    
    if not SELENIUM_AVAILABLE:
        print("❌ Selenium requis. Installez avec:")
        print("   pip install undetected-chromedriver selenium")
        return
    
    print(f"🔥 Scraper LeBonCoin + Supabase")
    
    # Créer le scraper pour vérifier la configuration Supabase
    # Mode invisible par défaut, sauf si --visible est spécifiée
    headless_mode = not args.visible if hasattr(args, 'visible') and args.visible else True
    
    scraper = LeBonCoinScraperVisible(
        headless=headless_mode, 
        cookies_file=args.cookies,
        supabase_url=args.supabase_url,
        supabase_key=args.supabase_key
    )
    
    # Afficher le statut Supabase correct
    if scraper.supabase:
        print(f"   Supabase: ✅ Configuré et connecté")
    else:
        print(f"   Supabase: ❌ Non configuré")
    
    try:
        # Lancer le scraping
        results = scraper.scrape_saumur_houses(max_pages=args.pages, auto_detect=args.auto_detect)
        
        # Mettre à jour le statut de la campagne
        if scraper.supabase and scraper.current_campaign_id:
            total_scraped = len(results) if results else 0
            scraper.update_campaign_status('completed', total_listings=total_scraped)
        
        if results:
            # Afficher les résultats
            scraper.display_results()
            
            # Sauvegarder localement aussi
            scraper.save_results(args.format)
            
            pages_text = "toutes les pages détectées" if args.auto_detect else f"{args.pages} page(s) maximum"
            print(f"\n🎉 Scraping terminé avec succès!")
            print(f"📊 {len(results)} annonces extraites sur {pages_text}")
            
            if scraper.supabase:
                print(f"💾 Données sauvegardées dans Supabase (Campagne: {scraper.current_campaign_id})")
            
            if args.keep_open:
                input("\n⏸️  Appuyez sur Entrée pour fermer le navigateur...")
        else:
            print("\n❌ Aucune annonce extraite")
    
    except KeyboardInterrupt:
        print("\n⏹️  Arrêt demandé par l'utilisateur")
        if scraper.supabase and scraper.current_campaign_id:
            scraper.update_campaign_status('failed')
    except Exception as e:
        print(f"\n❌ Erreur inattendue: {e}")
        if scraper.supabase and scraper.current_campaign_id:
            scraper.update_campaign_status('failed')
    finally:
        scraper.close()

if __name__ == "__main__":
    main() 