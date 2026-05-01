# Moteur de recherche — ELK Movies Platform

## Responsable : Alexandre
## Feature : F8 - Moteur de recherche

---

## Installation

```bash
cd search-api
pip install -r requirements.txt
python app.py
```

---

## Endpoints

### GET /health
Vérifie que l'API est connectée à Elasticsearch.

```bash
curl http://localhost:5000/health
```

Réponse :
```json
{
  "status": "ok",
  "elasticsearch": "connected",
  "index": "movies_clean",
  "total_movies": 662077
}
```

---

### GET /search
Recherche des films avec filtres optionnels.

**Paramètres :**
- `q` : terme de recherche (titre, synopsis)
- `genre` : filtrer par genre
- `language` : filtrer par langue
- `year` : filtrer par année
- `size` : nombre de résultats (défaut: 10, max: 50)
- `from` : pagination

**Exemples :**

```bash
# Recherche simple
curl "http://localhost:5000/search?q=avatar"

# Recherche + filtre genre
curl "http://localhost:5000/search?q=space&genre=Science+Fiction"

# Recherche + filtre langue
curl "http://localhost:5000/search?q=batman&language=en"

# Recherche + filtre année
curl "http://localhost:5000/search?q=titanic&year=1997"

# Tous les filtres combinés
curl "http://localhost:5000/search?q=hero&genre=Action&language=en&year=2022"

# Pagination
curl "http://localhost:5000/search?q=action&size=5&from=10"
```

---

### GET /movie/<id>
Récupérer un film par son identifiant TMDB.

```bash
curl http://localhost:5000/movie/19995
```

---

### GET /genres
Lister tous les genres avec le nombre de films.

```bash
curl http://localhost:5000/genres
```

---

## Variables d'environnement

| Variable | Défaut | Description |
|---|---|---|
| `ES_HOST` | `http://localhost:9200` | URL d'Elasticsearch |

---

## Lancer avec Docker Compose

Pour intégrer l'API dans la stack Docker, ajouter ce service dans `docker-compose.yml` :

```yaml
search-api:
  build: ./search-api
  container_name: search-api
  ports:
    - "5000:5000"
  environment:
    - ES_HOST=http://elasticsearch:9200
  depends_on:
    elasticsearch:
      condition: service_healthy
  networks:
    - elk_network
```
