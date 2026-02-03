"""
LLM Agent Module
Handles natural language to ADQL conversion and result synthesis
Supports: OpenAI API, Local LLM (LM Studio, Ollama, etc.)
"""
from openai import OpenAI
from typing import Optional, Dict, Any, List
import json
import re
import config


SYSTEM_PROMPT_ADQL = """Tu es un expert en astronomie et en ADQL (Astronomical Data Query Language).
Tu generes des requetes ADQL valides pour l'archive Gaia.

## Tables disponibles

### Gaia DR3
- gaiadr3.gaia_source : Table principale
  - source_id, ra, dec, parallax, parallax_error
  - pmra, pmdec (mouvement propre)
  - phot_g_mean_mag, phot_bp_mean_mag, phot_rp_mean_mag
  - bp_rp (couleur)
  - radial_velocity, teff_gspphot, logg_gspphot

### Cross-match tables
- gaiadr3.tmass_psc_xsc_best_neighbour (Gaia -> 2MASS)
- gaiadr3.sdssdr13_best_neighbour (Gaia -> SDSS)
- gaiadr3.allwise_best_neighbour (Gaia -> WISE)

### External catalogs (via Gaia archive)
- gaiadr1.tmass_original_valid : 2MASS photometry (j_m, h_m, ks_m)
- external.sdssdr13_photoprimary : SDSS photometry (u, g, r, i, z)

## Regles ADQL

1. Utilise CONTAINS(POINT, CIRCLE) pour les recherches spatiales :
   `WHERE CONTAINS(POINT('ICRS', ra, dec), CIRCLE('ICRS', ra_center, dec_center, radius_deg)) = 1`

2. Limite toujours les resultats avec TOP (max 10000)

3. Pour les cross-matches, utilise JOIN :
   ```sql
   SELECT g.*, t.j_m, t.h_m
   FROM gaiadr3.gaia_source AS g
   JOIN gaiadr3.tmass_psc_xsc_best_neighbour AS xmatch ON g.source_id = xmatch.source_id
   JOIN gaiadr1.tmass_original_valid AS t ON xmatch.tmass_oid = t.tmass_oid
   ```

4. Utilise LEFT JOIN si tu veux inclure les sources sans match

## Format de reponse

Reponds UNIQUEMENT avec la requete ADQL, sans explication. La requete doit etre directement executable.
"""


SYSTEM_PROMPT_SYNTHESIS = """Tu es un assistant expert en astrophysique.
Tu analyses des donnees astronomiques et produis des syntheses claires et utiles pour les chercheurs.

Tes reponses doivent etre :
- Concises mais completes
- Scientifiquement rigoureuses
- Orientees vers l'action (que devrait faire le chercheur ensuite ?)

Quand tu analyses des anomalies, suggere des causes possibles et des verifications a faire.
"""


def get_client() -> Optional[OpenAI]:
    """
    Get LLM client - supports OpenAI API or local LLM (LM Studio, Ollama, etc.)

    Configuration via environment variables:
    - USE_LOCAL_LLM=true : Use local LLM server
    - LOCAL_LLM_URL : URL of local server (default: http://localhost:1235/v1)
    - OPENAI_API_KEY : OpenAI API key (if not using local)
    """
    # Priority: Local LLM > OpenAI
    if config.USE_LOCAL_LLM:
        return OpenAI(
            base_url=config.LOCAL_LLM_URL,
            api_key="not-needed"  # LM Studio doesn't require a key
        )

    if config.OPENAI_API_KEY:
        return OpenAI(api_key=config.OPENAI_API_KEY)

    return None


def get_model_name() -> str:
    """Get the model name to use."""
    if config.USE_LOCAL_LLM:
        return config.LOCAL_LLM_MODEL
    return "gpt-4o"


def is_llm_available() -> bool:
    """Check if any LLM is configured."""
    return config.USE_LOCAL_LLM or bool(config.OPENAI_API_KEY)


def get_llm_status() -> str:
    """Get human-readable LLM status."""
    if config.USE_LOCAL_LLM:
        return f"LLM Local ({config.LOCAL_LLM_URL})"
    if config.OPENAI_API_KEY:
        return "OpenAI API"
    return "Non configure"


def natural_language_to_adql(query: str, context: Optional[Dict] = None) -> Optional[str]:
    """
    Convert natural language query to ADQL.

    Args:
        query: User's question in natural language
        context: Optional context (e.g., coordinates already parsed)

    Returns:
        ADQL query string or None if failed
    """
    client = get_client()
    if not client:
        return None

    user_message = query
    if context:
        if 'ra' in context and 'dec' in context:
            user_message += f"\n\nCoordonnees de reference : RA={context['ra']}, Dec={context['dec']}"
        if 'radius' in context:
            user_message += f", rayon={context['radius']} degres"

    try:
        response = client.chat.completions.create(
            model=get_model_name(),
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT_ADQL},
                {"role": "user", "content": user_message}
            ],
            temperature=0,
            max_tokens=4000
        )
        # Extract final answer after </think> tag if present (for thinking models)
        content = response.choices[0].message.content
        if content is None:
            return None
        content = content.strip()
        if "</think>" in content:
            content = content.split("</think>")[-1].strip()
        # Remove markdown code blocks if present
        if content.startswith("```"):
            lines = content.split("\n")
            content = "\n".join(lines[1:-1]) if lines[-1] == "```" else "\n".join(lines[1:])
        return content
    except Exception as e:
        print(f"LLM Error: {e}")
        return None


def synthesize_results(
    query: str,
    data_summary: Dict[str, Any],
    anomalies: Optional[Dict[str, Any]] = None
) -> str:
    """
    Generate a natural language synthesis of query results.

    Args:
        query: Original user query
        data_summary: Summary statistics of the data
        anomalies: Anomaly detection results if available

    Returns:
        Natural language synthesis
    """
    client = get_client()
    if not client:
        return "LLM non configure. Voir les donnees brutes ci-dessus."

    # Build context for LLM
    context_parts = [
        f"Question originale : {query}",
        f"\nResume des donnees :",
        f"- Nombre de sources : {data_summary.get('total_sources', 'N/A')}",
    ]

    if 'magnitude_range' in data_summary:
        context_parts.append(f"- Plage de magnitude G : {data_summary['magnitude_range']}")

    if 'parallax_range' in data_summary:
        context_parts.append(f"- Plage de parallaxe : {data_summary['parallax_range']}")

    if anomalies:
        context_parts.extend([
            f"\nAnalyse des anomalies :",
            f"- Sources avec anomalies : {anomalies.get('sources_with_anomalies', 0)} ({anomalies.get('anomaly_rate', 0):.1f}%)",
            f"- Par type : {anomalies.get('by_type', {})}",
            f"- Par severite : {anomalies.get('by_severity', {})}"
        ])

        if anomalies.get('top_anomalies'):
            context_parts.append("\nTop 3 anomalies :")
            for i, anom in enumerate(anomalies['top_anomalies'][:3], 1):
                context_parts.append(f"  {i}. Source {anom['source_id']} (score: {anom['score']:.0f})")
                for a in anom['anomalies'][:2]:
                    context_parts.append(f"     - {a['description']}")

    context = "\n".join(context_parts)

    try:
        response = client.chat.completions.create(
            model=get_model_name(),
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT_SYNTHESIS},
                {"role": "user", "content": f"Analyse ces resultats et produis une synthese utile :\n\n{context}"}
            ],
            temperature=0.3,
            max_tokens=4000
        )
        content = response.choices[0].message.content
        if content is None:
            return "Pas de reponse du LLM"
        content = content.strip()
        if "</think>" in content:
            content = content.split("</think>")[-1].strip()
        return content
    except Exception as e:
        return f"Erreur lors de la synthese : {e}"


def interpret_anomaly(anomaly: Dict[str, Any]) -> str:
    """
    Get LLM interpretation of a specific anomaly.
    """
    client = get_client()
    if not client:
        return "LLM non configure."

    prompt = f"""Analyse cette anomalie astronomique et donne :
1. Les causes possibles (avec probabilites estimees)
2. Les verifications recommandees
3. L'interet scientifique potentiel

Anomalie :
- Type : {anomaly.get('type')}
- Description : {anomaly.get('description')}
- Severite : {anomaly.get('severity')} ({anomaly.get('sigma', 0):.1f} sigma)
- Details : {json.dumps({k: v for k, v in anomaly.items() if k not in ['type', 'description', 'severity', 'sigma', 'source_id']}, indent=2)}
"""

    try:
        response = client.chat.completions.create(
            model=get_model_name(),
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT_SYNTHESIS},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=4000
        )
        content = response.choices[0].message.content
        if content is None:
            return "Pas de reponse du LLM"
        content = content.strip()
        if "</think>" in content:
            content = content.split("</think>")[-1].strip()
        return content
    except Exception as e:
        return f"Erreur : {e}"


def parse_user_intent(query: str) -> Dict[str, Any]:
    """
    Parse user's natural language query to extract intent and parameters.

    Returns dict with:
    - intent: 'search_region', 'search_object', 'custom_query', 'help'
    - parameters: extracted values (coordinates, object name, etc.)
    """
    client = get_client()
    if not client:
        # Fallback: basic keyword parsing
        return _basic_intent_parsing(query)

    prompt = f"""Analyse cette requete utilisateur et extrais l'intention et les parametres.

Requete : "{query}"

Reponds en JSON avec ce format :
{{
    "intent": "search_region" | "search_object" | "crossmatch" | "anomaly_search" | "custom",
    "object_name": "nom de l'objet si mentionne" | null,
    "ra": nombre ou null,
    "dec": nombre ou null,
    "radius_deg": nombre ou null,
    "catalogs": ["gaia", "2mass", "sdss"] (liste des catalogues demandes),
    "filters": {{}} (filtres additionnels comme magnitude, parallaxe, etc.)
}}

Exemples :
- "etoiles autour de M31" -> {{"intent": "search_object", "object_name": "M31", "catalogs": ["gaia"]}}
- "region RA=180, Dec=45, rayon 0.5 deg" -> {{"intent": "search_region", "ra": 180, "dec": 45, "radius_deg": 0.5}}
- "cross-match Gaia et 2MASS pour NGC 1234" -> {{"intent": "crossmatch", "object_name": "NGC 1234", "catalogs": ["gaia", "2mass"]}}
"""

    try:
        response = client.chat.completions.create(
            model=get_model_name(),
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0,
            max_tokens=4000
        )
        # Try to parse JSON from response
        content = response.choices[0].message.content
        if content is None:
            return _basic_intent_parsing(query)
        content = content.strip()
        # Extract final answer after </think> tag if present
        if "</think>" in content:
            content = content.split("</think>")[-1].strip()
        # Handle potential markdown code blocks
        if content.startswith("```"):
            parts = content.split("```")
            if len(parts) > 1:
                content = parts[1]
                if content.startswith("json"):
                    content = content[4:]
        return json.loads(content.strip())
    except (json.JSONDecodeError, Exception):
        return _basic_intent_parsing(query)


def _basic_intent_parsing(query: str) -> Dict[str, Any]:
    """Fallback basic parsing without LLM."""
    query_lower = query.lower()

    result = {
        "intent": "custom",
        "object_name": None,
        "ra": None,
        "dec": None,
        "radius_deg": None,
        "catalogs": ["gaia"]
    }

    # Check for object names (M##, NGC####, etc.)
    obj_match = re.search(r'\b(M\s?\d+|NGC\s?\d+|IC\s?\d+)\b', query, re.IGNORECASE)
    if obj_match:
        result["intent"] = "search_object"
        result["object_name"] = obj_match.group(1).replace(" ", "")

    # Check for coordinates
    ra_match = re.search(r'ra\s*[=:]\s*([\d.]+)', query_lower)
    dec_match = re.search(r'dec\s*[=:]\s*([+-]?[\d.]+)', query_lower)
    if ra_match and dec_match:
        result["intent"] = "search_region"
        result["ra"] = float(ra_match.group(1))
        result["dec"] = float(dec_match.group(1))

    # Check for radius
    radius_match = re.search(r'rayon?\s*[=:]\s*([\d.]+)', query_lower)
    if radius_match:
        result["radius_deg"] = float(radius_match.group(1))

    # Check for catalogs
    if '2mass' in query_lower:
        result["catalogs"].append("2mass")
    if 'sdss' in query_lower:
        result["catalogs"].append("sdss")
    if 'crossmatch' in query_lower or 'cross-match' in query_lower:
        result["intent"] = "crossmatch"

    return result
