# Concept A : Deep Dive Technique

> **Parent** : [CONCEPT_A_CrossMatch_Agent.md](./CONCEPT_A_CrossMatch_Agent.md)
> **Dernière mise à jour** : 2025-01-26

---

## 1. APIs et Sources de Données

### 1.1 Catalogues accessibles via astroquery

| Catalogue | Module astroquery | Type d'accès | Volume |
|-----------|-------------------|--------------|--------|
| Gaia DR3 | `astroquery.gaia` | TAP/ADQL | 1.8 Md objets |
| SDSS DR17 | `astroquery.sdss` | Cone search | 1+ Md objets |
| 2MASS | `astroquery.vizier` | TAP | 470 M objets |
| WISE | `astroquery.vizier` | TAP | 747 M objets |
| SIMBAD | `astroquery.simbad` | TAP | 16 M objets |
| VizieR | `astroquery.vizier` | TAP | 22000+ catalogues |

### 1.2 Cross-match pré-calculés dans Gaia

L'archive Gaia contient des tables de correspondance :
- `gaiadr3.panstarrs1_best_neighbour`
- `gaiadr3.tmass_psc_xsc_best_neighbour` (2MASS)
- `gaiadr3.allwise_best_neighbour`
- `gaiadr3.sdssdr13_best_neighbour`

**Avantage** : Pas besoin de recalculer le cross-match, juste faire des JOINs.

---

## 2. Exemples de requêtes ADQL

### 2.1 Requête simple Gaia

```sql
SELECT TOP 100
    source_id, ra, dec, parallax, phot_g_mean_mag
FROM gaiadr3.gaia_source
WHERE CONTAINS(
    POINT('ICRS', ra, dec),
    CIRCLE('ICRS', 180.0, 45.0, 0.5)
) = 1
```

### 2.2 Cross-match Gaia + 2MASS

```sql
SELECT
    g.source_id, g.ra, g.dec, g.phot_g_mean_mag,
    t.j_m, t.h_m, t.ks_m
FROM gaiadr3.gaia_source AS g
JOIN gaiadr3.tmass_psc_xsc_best_neighbour AS xmatch
    ON g.source_id = xmatch.source_id
JOIN gaiadr1.tmass_original_valid AS t
    ON xmatch.tmass_oid = t.tmass_oid
WHERE CONTAINS(
    POINT('ICRS', g.ra, g.dec),
    CIRCLE('ICRS', 180.0, 45.0, 0.5)
) = 1
```

### 2.3 Cross-match Gaia + SDSS

```sql
SELECT
    g.source_id, g.ra, g.dec,
    s.u_mag, s.g_mag, s.r_mag, s.i_mag, s.z_mag
FROM gaiadr3.gaia_source AS g
JOIN gaiadr3.sdssdr13_best_neighbour AS xmatch
    ON g.source_id = xmatch.source_id
JOIN external.sdssdr13_photoprimary AS s
    ON xmatch.sdssdr13_oid = s.objid
WHERE CONTAINS(
    POINT('ICRS', g.ra, g.dec),
    CIRCLE('ICRS', 180.0, 45.0, 0.5)
) = 1
```

---

## 3. Prototype Python

### 3.1 Installation

```bash
pip install astroquery astropy pandas openai langchain
```

### 3.2 Code de base - Requête multi-catalogues

```python
from astroquery.gaia import Gaia
from astroquery.sdss import SDSS
from astroquery.vizier import Vizier
from astropy.coordinates import SkyCoord
import astropy.units as u

def query_region(ra: float, dec: float, radius_deg: float = 0.5):
    """
    Interroge plusieurs catalogues pour une région du ciel.

    Args:
        ra: Right Ascension en degrés
        dec: Declination en degrés
        radius_deg: Rayon de recherche en degrés

    Returns:
        dict avec les résultats de chaque catalogue
    """
    results = {}
    coord = SkyCoord(ra=ra*u.degree, dec=dec*u.degree, frame='icrs')

    # 1. Gaia DR3
    gaia_query = f"""
    SELECT source_id, ra, dec, parallax, phot_g_mean_mag, bp_rp
    FROM gaiadr3.gaia_source
    WHERE CONTAINS(
        POINT('ICRS', ra, dec),
        CIRCLE('ICRS', {ra}, {dec}, {radius_deg})
    ) = 1
    """
    gaia_job = Gaia.launch_job_async(gaia_query)
    results['gaia'] = gaia_job.get_results()

    # 2. SDSS
    sdss_results = SDSS.query_region(coord, radius=radius_deg*u.degree)
    results['sdss'] = sdss_results

    # 3. 2MASS via VizieR
    vizier = Vizier(columns=['RAJ2000', 'DEJ2000', 'Jmag', 'Hmag', 'Kmag'])
    tmass = vizier.query_region(coord, radius=radius_deg*u.degree,
                                 catalog='II/246/out')  # 2MASS
    results['2mass'] = tmass[0] if tmass else None

    return results


def cross_match_gaia_2mass(ra: float, dec: float, radius_deg: float = 0.5):
    """
    Utilise le cross-match pré-calculé Gaia-2MASS.
    """
    query = f"""
    SELECT
        g.source_id, g.ra, g.dec, g.phot_g_mean_mag, g.bp_rp,
        t.j_m, t.h_m, t.ks_m,
        xmatch.angular_distance
    FROM gaiadr3.gaia_source AS g
    JOIN gaiadr3.tmass_psc_xsc_best_neighbour AS xmatch
        ON g.source_id = xmatch.source_id
    JOIN gaiadr1.tmass_original_valid AS t
        ON xmatch.tmass_oid = t.tmass_oid
    WHERE CONTAINS(
        POINT('ICRS', g.ra, g.dec),
        CIRCLE('ICRS', {ra}, {dec}, {radius_deg})
    ) = 1
    """
    job = Gaia.launch_job_async(query)
    return job.get_results()
```

### 3.3 Intégration LLM - Génération de requêtes

```python
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

SYSTEM_PROMPT = """Tu es un assistant expert en astronomie et en ADQL.
Tu génères des requêtes ADQL valides pour l'archive Gaia.

Tables disponibles:
- gaiadr3.gaia_source (source_id, ra, dec, parallax, phot_g_mean_mag, bp_rp, ...)
- gaiadr3.tmass_psc_xsc_best_neighbour (cross-match 2MASS)
- gaiadr3.sdssdr13_best_neighbour (cross-match SDSS)
- gaiadr3.allwise_best_neighbour (cross-match WISE)

Règles:
1. Utilise toujours CONTAINS() pour les recherches spatiales
2. Limite les résultats avec TOP si approprié
3. Utilise les tables de cross-match pour joindre les catalogues
"""

def natural_language_to_adql(user_query: str) -> str:
    """
    Convertit une question en langage naturel en requête ADQL.
    """
    llm = ChatOpenAI(model="gpt-4", temperature=0)

    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("human", "Génère une requête ADQL pour: {query}")
    ])

    chain = prompt | llm
    response = chain.invoke({"query": user_query})

    return response.content
```

---

## 4. Architecture détaillée

```
┌────────────────────────────────────────────────────────────────┐
│                      FRONTEND (Streamlit)                       │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Input: Question en langage naturel                      │  │
│  │  "Quelles étoiles autour de M31 ont des données IR ?"    │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────┬───────────────────────────────────┘
                             │
                             ▼
┌────────────────────────────────────────────────────────────────┐
│                    AGENT ORCHESTRATOR                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐ │
│  │ Query Parser │  │ ADQL         │  │ Response             │ │
│  │ (LLM)        │──│ Generator    │──│ Synthesizer          │ │
│  │              │  │ (LLM)        │  │ (LLM)                │ │
│  └──────────────┘  └──────────────┘  └──────────────────────┘ │
└────────────────────────────┬───────────────────────────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        ▼                    ▼                    ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│   GAIA TAP    │   │  SDSS API     │   │   VizieR      │
│   Service     │   │               │   │   (2MASS,     │
│               │   │               │   │    WISE)      │
└───────┬───────┘   └───────┬───────┘   └───────┬───────┘
        │                   │                   │
        └───────────────────┼───────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────────────┐
│                    DATA AGGREGATOR                             │
│  - Consolidation des résultats                                 │
│  - Détection d'incohérences                                    │
│  - Calcul de statistiques                                      │
└────────────────────────────┬───────────────────────────────────┘
                             │
                             ▼
┌────────────────────────────────────────────────────────────────┐
│                    OUTPUT GENERATOR                            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐│
│  │ Tableau     │  │ Graphiques  │  │ Rapport Markdown        ││
│  │ consolidé   │  │ (HR, carte) │  │ synthétique             ││
│  └─────────────┘  └─────────────┘  └─────────────────────────┘│
└────────────────────────────────────────────────────────────────┘
```

---

## 5. MVP pour 24h - Scope réduit

### Must Have (P0)
- [ ] Interface Streamlit basique
- [ ] Requête Gaia simple (coordonnées → résultats)
- [ ] Cross-match Gaia + 2MASS (via table pré-calculée)
- [ ] Génération ADQL via LLM
- [ ] Affichage tableau résultats

### Should Have (P1)
- [ ] Ajout SDSS
- [ ] Graphique HR diagram automatique
- [ ] Carte du ciel interactive (Plotly)
- [ ] Export CSV

### Nice to Have (P2)
- [ ] Détection d'incohérences basique
- [ ] Rapport PDF généré
- [ ] Cache des requêtes

---

## 6. Stack technique recommandée

| Composant | Choix | Justification |
|-----------|-------|---------------|
| **LLM** | GPT-4 via API | Meilleur pour génération ADQL |
| **Framework** | LangChain | Tools/Agents bien intégrés |
| **Données** | astroquery | Standard astronomie Python |
| **UI** | Streamlit | Rapide à prototyper |
| **Graphiques** | Plotly | Interactif |
| **Coordonnées** | astropy | Conversion/manipulation |

---

## 7. Risques techniques identifiés

| Risque | Impact | Mitigation |
|--------|--------|------------|
| Rate limiting APIs | Bloquant | Cache local, requêtes économes |
| ADQL mal généré par LLM | Moyen | Validation syntaxique, fallback templates |
| Timeout requêtes longues | Moyen | Limiter TOP, async jobs |
| Cross-match trop lent | Moyen | Utiliser tables pré-calculées Gaia |

---

## 8. Ressources et documentation

- [astroquery docs](https://astroquery.readthedocs.io/)
- [Gaia TAP+ tutorial](https://astroquery.readthedocs.io/en/latest/gaia/gaia.html)
- [ADQL examples Gaia](https://www.cosmos.esa.int/web/gaia-users/archive/writing-queries)
- [Cross-match tutorial Astropy](https://learn.astropy.org/tutorials/4_Coordinates-Crossmatch.html)
- [CDS XMatch service](https://cds-astro.github.io/tutorials/5_Brown_Dwarf_Search__Cross-matching_Catalogs.html)
- [ADQL specification](https://www.ivoa.net/documents/ADQL/)
