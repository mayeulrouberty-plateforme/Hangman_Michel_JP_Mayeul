# Cosmic Query Agent - MVP

> Agent conversationnel pour l'exploration multi-catalogues avec détection d'anomalies

## Installation rapide

```bash
# 1. Créer l'environnement virtuel
python -m venv venv

# 2. Activer (Windows)
.\venv\Scripts\activate
# Ou Linux/Mac
source venv/bin/activate

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Configurer l'API OpenAI (optionnel mais recommandé)
copy .env.example .env
# Éditer .env et ajouter votre clé OPENAI_API_KEY
```

## Lancement

```bash
streamlit run app.py
```

L'application s'ouvre sur http://localhost:8501

## Fonctionnalités MVP

### ✅ Implémenté

- [x] Recherche par coordonnées (RA/Dec)
- [x] Résolution de noms d'objets (M31, NGC, etc.)
- [x] Requêtes Gaia DR3
- [x] Cross-match Gaia + 2MASS
- [x] Cross-match Gaia + SDSS
- [x] Détection d'anomalies photométriques
- [x] Détection d'anomalies astrométriques
- [x] Détection de couleurs anormales
- [x] Dashboard des anomalies
- [x] Visualisation carte du ciel
- [x] Diagramme HR
- [x] Export CSV
- [x] Synthèse LLM (si clé API configurée)

### 🔜 À venir

- [ ] Génération ADQL via langage naturel
- [ ] Plus de catalogues (WISE, Pan-STARRS)
- [ ] Historique des requêtes
- [ ] Rapport PDF

## Structure

```
src/
├── app.py              # Application Streamlit principale
├── config.py           # Configuration
├── astro_queries.py    # Requêtes Gaia/SDSS/2MASS
├── anomaly_detector.py # Détection d'incohérences
├── llm_agent.py        # Intégration LLM
├── requirements.txt    # Dépendances
└── .env.example        # Template variables d'environnement
```

## Sans clé OpenAI

L'application fonctionne sans clé API, mais :
- Pas de synthèse automatique
- Pas d'interprétation des anomalies
- Parsing langage naturel basique

## Exemples de recherche

1. **Par coordonnées** : RA=83.82, Dec=-5.39 (Nébuleuse d'Orion)
2. **Par nom** : M45 (Pléiades), NGC 6121 (M4), Sirius
3. **Avec anomalies** : Chercher dans des régions denses, augmenter le rayon
