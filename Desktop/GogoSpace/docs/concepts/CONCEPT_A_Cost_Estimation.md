# Concept A : Estimation des Coûts de Déploiement

> **Parent** : [CONCEPT_A_CrossMatch_Agent.md](./CONCEPT_A_CrossMatch_Agent.md)
> **Dernière mise à jour** : 2025-01-26

---

## 1. Scénarios de déploiement

| Scénario | Description | Cible |
|----------|-------------|-------|
| **Demo Hackathon** | Gratuit, limité | Jury ActInSpace |
| **Prototype** | Usage faible, tests | Équipe interne |
| **Production légère** | ~100 utilisateurs/mois | Labo de recherche |
| **Production** | ~1000+ utilisateurs/mois | Agence spatiale |

---

## 2. Coûts par composant

### 2.1 LLM (Génération ADQL + Synthèse)

Source : [OpenAI Pricing](https://openai.com/api/pricing/)

| Modèle | Input (1M tokens) | Output (1M tokens) | Recommandé |
|--------|-------------------|--------------------| -----------|
| GPT-4 | $30.00 | $60.00 | Non (trop cher) |
| **GPT-4o** | **$2.50** | **$10.00** | **Oui** |
| GPT-4o-mini | $0.15 | $0.60 | Oui (budget) |
| Claude 3.5 Sonnet | $3.00 | $15.00 | Alternative |

#### Estimation usage par requête

| Étape | Tokens input | Tokens output |
|-------|--------------|---------------|
| Parsing question | ~200 | ~50 |
| Génération ADQL | ~500 | ~200 |
| Synthèse résultats | ~2000 | ~500 |
| **Total/requête** | **~2700** | **~750** |

#### Coût par requête (GPT-4o)

```
Input:  2700 tokens × $2.50/1M = $0.00675
Output: 750 tokens × $10.00/1M = $0.0075
────────────────────────────────────────
Total par requête: ~$0.014 (~1.4 centimes)
```

#### Projection mensuelle

| Usage | Requêtes/mois | Coût LLM/mois |
|-------|---------------|---------------|
| Demo | 50 | $0.70 |
| Prototype | 500 | $7.00 |
| Production légère | 5,000 | $70.00 |
| Production | 50,000 | $700.00 |

---

### 2.2 Hébergement Application

Source : [Streamlit Cloud](https://streamlit.io/cloud)

| Option | Coût | RAM | Limitations |
|--------|------|-----|-------------|
| **Streamlit Community Cloud** | **Gratuit** | 1 GB | Repo public, domaine streamlit.app |
| Streamlit Teams | $250/mois | Plus | Repos privés, auth |
| Heroku | $7-25/mois | 512MB-1GB | Flexible |
| Railway | $5-20/mois | Flexible | Simple |
| AWS EC2 t3.micro | ~$8/mois | 1 GB | Contrôle total |
| Google Cloud Run | Pay-per-use | Flexible | ~$5-20/mois |

**Recommandation hackathon** : Streamlit Community Cloud (gratuit)

---

### 2.3 APIs Astronomiques

| Service | Coût | Limite |
|---------|------|--------|
| Gaia TAP | **Gratuit** | Fair use |
| SDSS CasJobs | **Gratuit** | Inscription requise |
| VizieR | **Gratuit** | Fair use |
| CDS XMatch | **Gratuit** | Fair use |

**Coût total APIs astro : $0**

---

### 2.4 Base de données (cache optionnel)

| Option | Coût | Usage |
|--------|------|-------|
| SQLite local | Gratuit | Dev/Demo |
| Supabase Free | Gratuit | 500 MB, 50K rows |
| PlanetScale Free | Gratuit | 5 GB |
| PostgreSQL (Railway) | ~$5/mois | Production |

---

## 3. Résumé par scénario

### Scénario A : Demo Hackathon (24h)

| Composant | Solution | Coût |
|-----------|----------|------|
| Hébergement | Streamlit Community | $0 |
| LLM | GPT-4o (50 requêtes) | < $1 |
| APIs astro | Gaia, SDSS, VizieR | $0 |
| Base données | SQLite | $0 |
| **TOTAL** | | **< $1** |

---

### Scénario B : Prototype (3 mois)

| Composant | Solution | Coût/mois |
|-----------|----------|-----------|
| Hébergement | Streamlit Community | $0 |
| LLM | GPT-4o (500 req/mois) | $7 |
| APIs astro | Gratuit | $0 |
| Base données | Supabase Free | $0 |
| **TOTAL** | | **~$7/mois** |

**Coût 3 mois : ~$21**

---

### Scénario C : Production légère (1 an)

| Composant | Solution | Coût/mois |
|-----------|----------|-----------|
| Hébergement | Railway / Heroku | $15 |
| LLM | GPT-4o (5K req/mois) | $70 |
| APIs astro | Gratuit | $0 |
| Base données | PostgreSQL | $5 |
| Monitoring | Sentry Free | $0 |
| Domaine | .org/.io | $1 |
| **TOTAL** | | **~$91/mois** |

**Coût annuel : ~$1,100**

---

### Scénario D : Production (1 an)

| Composant | Solution | Coût/mois |
|-----------|----------|-----------|
| Hébergement | AWS/GCP | $50-100 |
| LLM | GPT-4o (50K req/mois) | $700 |
| APIs astro | Gratuit | $0 |
| Base données | PostgreSQL managed | $25 |
| CDN/Cache | Cloudflare | $0-20 |
| Monitoring | Datadog/Sentry | $0-50 |
| Domaine + SSL | | $2 |
| **TOTAL** | | **~$800-900/mois** |

**Coût annuel : ~$10,000-11,000**

---

## 4. Optimisations possibles

### Réduire les coûts LLM

| Stratégie | Économie | Impact |
|-----------|----------|--------|
| Cache des requêtes similaires | -30-50% | Faible |
| GPT-4o-mini pour parsing | -70% sur parsing | Aucun |
| Templates ADQL pré-générés | -50% génération | Moyen |
| Batch processing | -20% | Latence accrue |

### Réduire les coûts infra

| Stratégie | Économie |
|-----------|----------|
| Streamlit gratuit + domaine custom via CNAME | -100% hosting |
| Serverless (Cloud Run) | Pay-per-use |
| Cache agressif | Moins de requêtes API |

---

## 5. Comparaison avec alternatives

### Si on utilisait un LLM local (Mistral/LLaMA)

| Aspect | Cloud (GPT-4o) | Local |
|--------|----------------|-------|
| Coût récurrent | ~$70/mois | $0 |
| Coût initial | $0 | GPU ~$1000+ |
| Qualité ADQL | Excellente | Moyenne |
| Maintenance | Aucune | Élevée |
| Latence | ~2-3s | ~5-10s |

**Recommandation** : Cloud pour hackathon et prototype, local si budget récurrent problématique.

---

## 6. Tableau récapitulatif

| Scénario | Coût initial | Coût mensuel | Coût annuel |
|----------|--------------|--------------|-------------|
| **Demo Hackathon** | $0 | < $1 | - |
| **Prototype 3 mois** | $0 | $7 | $21 |
| **Production légère** | $0 | $91 | $1,100 |
| **Production** | $0 | $850 | $10,200 |

---

## 7. Sources

- [OpenAI API Pricing](https://openai.com/api/pricing/)
- [Streamlit Cloud](https://streamlit.io/cloud)
- [Railway Pricing](https://railway.app/pricing)
- [Supabase Pricing](https://supabase.com/pricing)
- [Gaia Archive](https://gea.esac.esa.int/archive/) (gratuit)
