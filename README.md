# 🏠 Scraper LeBonCoin Simple - Immobilier

Script Python simple et efficace pour scraper les annonces immobilières de LeBonCoin avec contournement automatique des protections anti-bot.

## ✨ Fonctionnalités

- 🛡️ **Contournement automatique** des protections (Cloudflare, captchas)
- 🎭 **Simulation comportement humain** (scroll, pauses, mouvements souris)
- 🌐 **Support proxy** pour éviter les blocages IP
- 📊 **Export CSV/JSON** des résultats
- 🚀 **Interface en ligne de commande** simple

## 🚀 Installation Rapide

### Prérequis
- Python 3.8+
- Google Chrome installé

### Installation
```bash
# Cloner ou télécharger le script
git clone <repo-url> ou télécharger scraper_leboncoin_simple.py

# Installer les dépendances
pip install -r requirements.txt

# Ou installation manuelle
pip install undetected-chromedriver selenium beautifulsoup4 requests fake-useragent
```

## 🎮 Utilisation

### Exemples d'utilisation

```bash
# Scraper basique - Appartements à Marseille
python scraper_leboncoin_simple.py --ville "Marseille"

# Avec prix maximum et type spécifique
python scraper_leboncoin_simple.py --ville "Paris" --type "appartement" --prix-max 500000

# Scraper plusieurs pages en mode silencieux
python scraper_leboncoin_simple.py --ville "Lyon" --pages 10 --headless

# Export en JSON
python scraper_leboncoin_simple.py --ville "Nice" --format "json"

# Avec proxy (à configurer dans le script)
python scraper_leboncoin_simple.py --ville "Toulouse" --proxy
```

### Options disponibles

| Option | Description | Exemple |
|--------|-------------|---------|
| `--ville` | Ville à scraper (obligatoire) | `--ville "Marseille"` |
| `--type` | Type de bien (appartement/maison) | `--type "maison"` |
| `--prix-max` | Prix maximum en euros | `--prix-max 300000` |
| `--pages` | Nombre de pages à scraper | `--pages 5` |
| `--headless` | Mode sans interface graphique | `--headless` |
| `--proxy` | Utiliser un proxy | `--proxy` |
| `--format` | Format de sortie (csv/json/both) | `--format "json"` |

## 📊 Résultats

Le script génère automatiquement des fichiers avec timestamp :
- `leboncoin_immobilier_YYYYMMDD_HHMMSS.csv`
- `leboncoin_immobilier_YYYYMMDD_HHMMSS.json`

### Structure des données extraites
```json
{
  "titre": "Appartement T3 centre ville",
  "prix": "250 000 €",
  "localisation": "Marseille 13001",
  "url": "https://www.leboncoin.fr/ad/...",
  "date_extraction": "2025-01-XX..."
}
```

## 🛡️ Contournement des Protections

### Protections gérées automatiquement
- ✅ **Cloudflare** - Attente automatique + simulation humaine
- ✅ **Captchas** - Résolution avec CapSolver (API key requise)
- ✅ **Anti-bot générique** - User-Agent aléatoire + comportement humain
- ✅ **Rate limiting** - Pauses aléatoires entre requêtes

### Configuration CapSolver (optionnel)
Pour la résolution automatique des captchas :
1. Créer un compte sur [CapSolver](https://capsolver.com)
2. Obtenir votre API key
3. Modifier dans le script : `capsolver.api_key = "VOTRE_CLE_API"`

## ⚙️ Configuration Proxy (optionnel)

Pour utiliser un proxy, modifiez dans le script :
```python
# Dans la méthode setup_driver()
if self.use_proxy:
    options.add_argument("--proxy-server=http://votre-proxy:port")
```

## 🔧 Personnalisation

### Modifier les sélecteurs CSS
Si LeBonCoin change sa structure, modifiez les sélecteurs dans `extract_listings_from_page()` :
```python
# Sélecteurs actuels
ad_containers = self.driver.find_elements(By.CSS_SELECTOR, "[data-qa-id='aditem_container']")
title_elem = container.find_element(By.CSS_SELECTOR, "[data-qa-id='aditem_title']")
```

### Ajouter d'autres données
Vous pouvez extraire plus d'informations en ajoutant dans `extract_listings_from_page()` :
```python
# Exemple : surface
try:
    surface_elem = container.find_element(By.CSS_SELECTOR, "[data-qa-id='aditem_surface']")
    listing["surface"] = surface_elem.text.strip()
except NoSuchElementException:
    listing["surface"] = "Non spécifiée"
```

## 📈 Performance

### Optimisations intégrées
- **Pauses aléatoires** : 2-6 secondes entre pages
- **Simulation humaine** : Scroll + mouvements souris
- **User-Agent rotation** : Évite la détection
- **Timeout intelligent** : 30s pour Cloudflare, 10s pour chargement

### Recommandations
- **Pages par session** : Max 10-15 pages pour éviter détection
- **Fréquence** : Espacer les sessions de plusieurs heures
- **Proxy rotation** : Changer d'IP régulièrement

## ⚠️ Considérations Légales

- ✅ **Respecter robots.txt** et conditions d'utilisation
- ✅ **Rate limiting** : Ne pas surcharger les serveurs
- ✅ **Usage personnel** : Éviter usage commercial intensif
- ✅ **Données personnelles** : Respecter RGPD

## 🐛 Dépannage

### Erreurs courantes

**Chrome non trouvé**
```bash
# Installer Chrome ou spécifier le chemin
export CHROME_BIN=/path/to/chrome
```

**Timeout Cloudflare**
```bash
# Augmenter le timeout ou utiliser un proxy
python scraper_leboncoin_simple.py --ville "Paris" --proxy
```

**Sélecteurs obsolètes**
- Vérifier la structure HTML de LeBonCoin
- Mettre à jour les sélecteurs CSS dans le script

### Logs et debug
Le script affiche en temps réel :
- 🔍 Détection des protections
- 🌩️ Contournement Cloudflare
- 📄 Progression du scraping
- ✅ Résultats par page

## 📞 Support

Pour des questions ou améliorations :
- Vérifier les sélecteurs CSS si le scraping échoue
- Tester avec `--headless` désactivé pour voir le navigateur
- Utiliser un proxy si blocage IP

---

**🚀 Prêt à scraper ? Lancez : `python scraper_leboncoin_simple.py --ville "VotreVille"`** 