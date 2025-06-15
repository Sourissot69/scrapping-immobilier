-- =============================================
-- SCHÉMA SUPABASE POUR SCRAPING IMMOBILIER
-- =============================================

-- 1. Table des sources de données (platforms)
CREATE TABLE IF NOT EXISTS sources (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL, -- 'leboncoin', 'seloger'
    base_url TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 2. Table des recherches/campagnes de scraping
CREATE TABLE IF NOT EXISTS search_campaigns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_id INTEGER REFERENCES sources(id),
    search_config JSONB NOT NULL, -- Configuration JSON de la recherche
    search_url TEXT NOT NULL,
    status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'running', 'completed', 'failed'
    total_pages INTEGER DEFAULT 0,
    total_listings_found INTEGER DEFAULT 0,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 3. Table des annonces (niveau liste de recherche)
CREATE TABLE IF NOT EXISTS listings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_id UUID REFERENCES search_campaigns(id),
    source_id INTEGER REFERENCES sources(id),
    
    -- Identifiants
    listing_id VARCHAR(50), -- ID de l'annonce sur le site source
    url TEXT UNIQUE NOT NULL,
    
    -- Données de base (niveau recherche)
    title TEXT,
    price_text TEXT, -- Prix tel qu'affiché (ex: "855000 €", "Prix non spécifié")
    price_numeric INTEGER, -- Prix converti en nombre
    location TEXT,
    
    -- Métadonnées
    page_number INTEGER,
    position_in_page INTEGER,
    scraped_at TIMESTAMP DEFAULT NOW(),
    needs_detail_scraping BOOLEAN DEFAULT TRUE,
    detail_scraped_at TIMESTAMP,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    -- Index unique par source + listing_id
    UNIQUE(source_id, listing_id)
);

-- 4. Table des détails d'annonces (niveau scraping individuel)
CREATE TABLE IF NOT EXISTS listing_details (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    listing_id UUID REFERENCES listings(id) UNIQUE,
    
    -- Informations détaillées
    description TEXT,
    
    -- Propriété
    property_type VARCHAR(50), -- 'maison', 'appartement', 'terrain', etc.
    transaction_type VARCHAR(20), -- 'achat', 'location'
    surface_text TEXT, -- Surface telle qu'affichée (ex: "370 m²")
    surface_numeric REAL, -- Surface en m²
    rooms_total INTEGER, -- Nombre total de pièces
    bedrooms INTEGER, -- Nombre de chambres
    floor_number INTEGER, -- Étage
    
    -- Prix détaillé
    price_per_m2_text TEXT,
    price_per_m2_numeric REAL,
    
    -- Localisation détaillée
    city VARCHAR(100),
    district VARCHAR(100),
    postal_code VARCHAR(10),
    full_address TEXT,
    
    -- Caractéristiques
    has_elevator BOOLEAN,
    has_balcony BOOLEAN,
    has_terrace BOOLEAN,
    has_parking BOOLEAN,
    has_cellar BOOLEAN,
    
    -- Agence
    agency_name TEXT,
    agency_phone VARCHAR(20),
    
    -- Métadonnées de scraping
    scraped_at TIMESTAMP DEFAULT NOW(),
    scraping_success BOOLEAN DEFAULT TRUE,
    scraping_errors TEXT,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 5. Table des images
CREATE TABLE IF NOT EXISTS listing_images (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    listing_id UUID REFERENCES listings(id),
    
    image_url TEXT NOT NULL,
    image_order INTEGER DEFAULT 0,
    is_main_image BOOLEAN DEFAULT FALSE,
    
    -- Métadonnées image
    downloaded BOOLEAN DEFAULT FALSE,
    local_path TEXT,
    file_size INTEGER,
    width INTEGER,
    height INTEGER,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 6. Table des logs de scraping
CREATE TABLE IF NOT EXISTS scraping_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_id UUID REFERENCES search_campaigns(id),
    listing_id UUID REFERENCES listings(id), -- Optionnel, pour logs spécifiques à une annonce
    
    log_level VARCHAR(10) NOT NULL, -- 'INFO', 'WARNING', 'ERROR'
    message TEXT NOT NULL,
    details JSONB, -- Détails supplémentaires en JSON
    
    created_at TIMESTAMP DEFAULT NOW()
);

-- 7. Table des erreurs de scraping
CREATE TABLE IF NOT EXISTS scraping_errors (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_id UUID REFERENCES search_campaigns(id),
    listing_id UUID REFERENCES listings(id), -- Optionnel
    
    error_type VARCHAR(50) NOT NULL, -- 'timeout', 'not_found', 'parsing_error', etc.
    error_message TEXT NOT NULL,
    error_details JSONB,
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,
    
    created_at TIMESTAMP DEFAULT NOW(),
    resolved_at TIMESTAMP
);

-- =============================================
-- INDEX POUR OPTIMISER LES PERFORMANCES
-- =============================================

-- Index pour les recherches fréquentes
CREATE INDEX IF NOT EXISTS idx_listings_source_campaign ON listings(source_id, campaign_id);
CREATE INDEX IF NOT EXISTS idx_listings_scraped_at ON listings(scraped_at);
CREATE INDEX IF NOT EXISTS idx_listings_needs_detail ON listings(needs_detail_scraping);
CREATE INDEX IF NOT EXISTS idx_listings_url ON listings(url);
CREATE INDEX IF NOT EXISTS idx_listings_listing_id ON listings(listing_id);

-- Index pour les détails
CREATE INDEX IF NOT EXISTS idx_listing_details_scraped_at ON listing_details(scraped_at);
CREATE INDEX IF NOT EXISTS idx_listing_details_property_type ON listing_details(property_type);
CREATE INDEX IF NOT EXISTS idx_listing_details_city ON listing_details(city);
CREATE INDEX IF NOT EXISTS idx_listing_details_price_numeric ON listing_details(price_per_m2_numeric);

-- Index pour les images
CREATE INDEX IF NOT EXISTS idx_listing_images_listing_id ON listing_images(listing_id);
CREATE INDEX IF NOT EXISTS idx_listing_images_order ON listing_images(image_order);

-- Index pour les logs
CREATE INDEX IF NOT EXISTS idx_scraping_logs_campaign ON scraping_logs(campaign_id);
CREATE INDEX IF NOT EXISTS idx_scraping_logs_created_at ON scraping_logs(created_at);
CREATE INDEX IF NOT EXISTS idx_scraping_logs_level ON scraping_logs(log_level);

-- =============================================
-- FONCTIONS ET TRIGGERS
-- =============================================

-- Fonction pour mettre à jour updated_at automatiquement
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers pour updated_at
CREATE TRIGGER update_search_campaigns_updated_at BEFORE UPDATE ON search_campaigns FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_listings_updated_at BEFORE UPDATE ON listings FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_listing_details_updated_at BEFORE UPDATE ON listing_details FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_listing_images_updated_at BEFORE UPDATE ON listing_images FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =============================================
-- VUES UTILES
-- =============================================

-- Vue complète des annonces avec détails
CREATE OR REPLACE VIEW listings_complete AS
SELECT 
    l.id,
    l.url,
    l.title,
    l.price_text,
    l.price_numeric,
    l.location,
    s.name as source_name,
    sc.search_config,
    
    -- Détails
    ld.description,
    ld.property_type,
    ld.transaction_type,
    ld.surface_text,
    ld.surface_numeric,
    ld.rooms_total,
    ld.bedrooms,
    ld.floor_number,
    ld.price_per_m2_text,
    ld.price_per_m2_numeric,
    ld.city,
    ld.district,
    ld.postal_code,
    ld.full_address,
    ld.has_elevator,
    ld.has_balcony,
    ld.has_terrace,
    ld.has_parking,
    ld.has_cellar,
    ld.agency_name,
    ld.agency_phone,
    
    -- Comptage des images
    (SELECT COUNT(*) FROM listing_images li WHERE li.listing_id = l.id) as image_count,
    
    -- Dates
    l.scraped_at,
    ld.scraped_at as detail_scraped_at,
    l.created_at
    
FROM listings l
LEFT JOIN listing_details ld ON ld.listing_id = l.id
LEFT JOIN sources s ON s.id = l.source_id
LEFT JOIN search_campaigns sc ON sc.id = l.campaign_id;

-- Vue des statistiques par campagne
CREATE OR REPLACE VIEW campaign_stats AS
SELECT 
    sc.id,
    sc.search_config,
    sc.search_url,
    sc.status,
    sc.total_pages,
    sc.total_listings_found,
    s.name as source_name,
    
    -- Statistiques calculées
    COUNT(l.id) as listings_scraped,
    COUNT(ld.id) as listings_with_details,
    COUNT(CASE WHEN l.needs_detail_scraping = false THEN 1 END) as listings_completed,
    
    -- Durée
    sc.started_at,
    sc.completed_at,
    CASE 
        WHEN sc.completed_at IS NOT NULL THEN sc.completed_at - sc.started_at
        WHEN sc.started_at IS NOT NULL THEN NOW() - sc.started_at
        ELSE NULL
    END as duration,
    
    sc.created_at
    
FROM search_campaigns sc
LEFT JOIN sources s ON s.id = sc.source_id
LEFT JOIN listings l ON l.campaign_id = sc.id
LEFT JOIN listing_details ld ON ld.listing_id = l.id
GROUP BY sc.id, s.name;

-- =============================================
-- DONNÉES INITIALES
-- =============================================

-- Insérer les sources
INSERT INTO sources (name, base_url) VALUES 
    ('leboncoin', 'https://www.leboncoin.fr'),
    ('seloger', 'https://www.seloger.com')
ON CONFLICT (name) DO NOTHING;

-- =============================================
-- POLITIQUES RLS (Row Level Security) - Optionnel
-- =============================================

-- Activer RLS sur les tables sensibles si nécessaire
-- ALTER TABLE listings ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE listing_details ENABLE ROW LEVEL SECURITY;

-- Politique d'exemple (à adapter selon vos besoins)
-- CREATE POLICY "Users can view all listings" ON listings FOR SELECT USING (true);
-- CREATE POLICY "Users can insert listings" ON listings FOR INSERT WITH CHECK (true); 