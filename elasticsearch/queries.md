# Requêtes Elasticsearch DSL — movies_clean

## Responsable : Sandrine
## Feature : F5 - Requêtes analytiques
## Index : movies_clean (662 077 documents)

---

## Requêtes BOOL (5 obligatoires)

### R01 — Films d'action populaires récents (bool - must + filter)

**Cas métier : Trouver les films d'action sortis après 2015 avec une note > 7**

**Résultat obtenu : 110 films**

```json
GET /movies_clean/_search
{
  "query": {
    "bool": {
      "must": [
        { "term": { "genres": "Action" } }
      ],
      "filter": [
        { "range": { "release_date": { "gte": "2015-01-01" } } },
        { "range": { "vote_average": { "gte": 7.0 } } },
        { "range": { "vote_count": { "gte": 1000 } } }
      ]
    }
  },
  "sort": [{ "popularity": { "order": "desc" } }],
  "size": 10
}
```

**Top 3 résultats :**
- The Northman (popularité: 3669, note: 7.3)
- Sonic the Hedgehog 2 (popularité: 2984, note: 7.8)
- Uncharted (popularité: 2735, note: 7.2)

---

### R02 — Films avec gros budget mais faibles recettes (bool - must + must_not)

**Cas métier : Identifier les flops commerciaux (budget entre 100M et 500M, recettes < 50M)**

**Note : filtre sur vote_count >= 100 pour exclure les données aberrantes du dataset**

**Résultat obtenu : 18 films**

```json
GET /movies_clean/_search
{
  "query": {
    "bool": {
      "must": [
        { "range": { "budget": { "gte": 100000000, "lte": 500000000 } } }
      ],
      "must_not": [
        { "range": { "revenue": { "gte": 50000000 } } },
        { "term": { "status": "Post Production" } },
        { "term": { "status": "In Production" } },
        { "term": { "status": "Planned" } }
      ],
      "filter": [
        { "term": { "original_language": "en" } },
        { "range": { "vote_count": { "gte": 100 } } }
      ]
    }
  },
  "sort": [{ "budget": { "order": "desc" } }],
  "size": 10
}
```

**Top 3 résultats :**
- Luca (Pixar) - budget: 200M, recettes: 49M, note: 7.9
- Turning Red (Pixar) - budget: 190M, recettes: 19M, note: 7.5
- The Irishman - budget: 159M, recettes: 968K, note: 7.6

---

### R03 — Recherche full-text sur titre et synopsis (bool - should)

**Cas métier : Trouver les films liés à l'espace ou à la science-fiction**

```json
GET /movies_clean/_search
{
  "query": {
    "bool": {
      "should": [
        { "match": { "title": { "query": "space galaxy universe", "boost": 2 } } },
        { "match": { "overview": { "query": "space galaxy universe alien planet" } } },
        { "terms": { "genres": ["Science Fiction", "Adventure"] } }
      ],
      "minimum_should_match": 1,
      "filter": [
        { "range": { "vote_average": { "gte": 6.5 } } }
      ]
    }
  },
  "size": 10
}
```

---

### R04 — Films par acteur avec bonne note (bool - must + filter)

**Cas métier : Tous les films avec Leonardo DiCaprio notés > 7**

```json
GET /movies_clean/_search
{
  "query": {
    "bool": {
      "must": [
        { "term": { "credits": "Leonardo DiCaprio" } }
      ],
      "filter": [
        { "range": { "vote_average": { "gte": 7.0 } } },
        { "range": { "vote_count": { "gte": 500 } } }
      ]
    }
  },
  "sort": [{ "vote_average": { "order": "desc" } }],
  "size": 10
}
```

---

### R05 — Films rentables par genre (bool - must + must_not + filter)

**Cas métier : Films rentables (recettes > budget) hors animation et données manquantes**

```json
GET /movies_clean/_search
{
  "query": {
    "bool": {
      "must": [
        { "range": { "budget": { "gt": 1000000 } } },
        { "range": { "revenue": { "gt": 1000000 } } }
      ],
      "must_not": [
        { "term": { "genres": "Animation" } },
        { "term": { "status": "Post Production" } },
        { "term": { "status": "In Production" } }
      ],
      "filter": [
        { "range": { "vote_count": { "gte": 500 } } },
        { "term": { "original_language": "en" } }
      ]
    }
  },
  "sort": [{ "revenue": { "order": "desc" } }],
  "size": 10
}
```

---

## Requêtes ANALYTIQUES (7 supplémentaires)

### R06 — Top 10 films par popularité

**Cas métier : Quels sont les films les plus populaires du dataset ?**

```json
GET /movies_clean/_search
{
  "query": { "match_all": {} },
  "sort": [{ "popularity": { "order": "desc" } }],
  "size": 10,
  "_source": ["title", "popularity", "vote_average", "release_date", "genres"]
}
```

---

### R07 — Agrégation par genre

**Cas métier : Combien de films par genre dans le dataset ?**

```json
GET /movies_clean/_search
{
  "size": 0,
  "aggs": {
    "genres_count": {
      "terms": {
        "field": "genres",
        "size": 20
      }
    }
  }
}
```

---

### R08 — Note moyenne par langue originale

**Cas métier : Quelle langue produit les films les mieux notés en moyenne ?**

```json
GET /movies_clean/_search
{
  "size": 0,
  "aggs": {
    "par_langue": {
      "terms": {
        "field": "original_language",
        "size": 15,
        "min_doc_count": 100
      },
      "aggs": {
        "note_moyenne": {
          "avg": { "field": "vote_average" }
        },
        "popularite_moyenne": {
          "avg": { "field": "popularity" }
        }
      }
    }
  }
}
```

---

### R09 — Distribution des films par année

**Cas métier : Evolution du nombre de films produits par année**

```json
GET /movies_clean/_search
{
  "size": 0,
  "aggs": {
    "films_par_annee": {
      "date_histogram": {
        "field": "release_date",
        "calendar_interval": "year",
        "format": "yyyy"
      },
      "aggs": {
        "note_moyenne": {
          "avg": { "field": "vote_average" }
        }
      }
    }
  }
}
```

---

### R10 — Films les mieux notés avec beaucoup de votes

**Cas métier : Quels films ont la meilleure note avec au moins 10 000 votes ?**

```json
GET /movies_clean/_search
{
  "query": {
    "range": {
      "vote_count": { "gte": 10000 }
    }
  },
  "sort": [
    { "vote_average": { "order": "desc" } },
    { "vote_count": { "order": "desc" } }
  ],
  "size": 10,
  "_source": ["title", "vote_average", "vote_count", "genres", "release_date"]
}
```

---

### R11 — Recherche full-text avec highlight

**Cas métier : Rechercher un film par mot-clé dans le titre ou synopsis**

```json
GET /movies_clean/_search
{
  "query": {
    "multi_match": {
      "query": "dark knight batman",
      "fields": ["title^3", "overview", "tagline"],
      "type": "best_fields",
      "fuzziness": "AUTO"
    }
  },
  "highlight": {
    "fields": {
      "title": {},
      "overview": { "fragment_size": 150 }
    }
  },
  "size": 5
}
```

---

### R12 — Statistiques globales du dataset

**Cas métier : Vue d'ensemble des statistiques du dataset films**

```json
GET /movies_clean/_search
{
  "size": 0,
  "aggs": {
    "budget_stats": {
      "stats": { "field": "budget" }
    },
    "revenue_stats": {
      "stats": { "field": "revenue" }
    },
    "note_stats": {
      "stats": { "field": "vote_average" }
    },
    "runtime_stats": {
      "stats": { "field": "runtime" }
    },
    "top_genres": {
      "terms": {
        "field": "genres",
        "size": 5
      }
    },
    "top_langues": {
      "terms": {
        "field": "original_language",
        "size": 5
      }
    }
  }
}
```

---

## Récapitulatif des requêtes

| ID | Type | Cas métier | Résultat |
|---|---|---|---|
| R01 | bool (must + filter) | Films d'action populaires récents | 110 films |
| R02 | bool (must + must_not + filter) | Flops commerciaux | 18 films |
| R03 | bool (should) | Recherche full-text espace/SF | A tester |
| R04 | bool (must + filter) | Films par acteur bien notés | A tester |
| R05 | bool (must + must_not + filter) | Films rentables hors animation | A tester |
| R06 | match_all + sort | Top 10 popularité | A tester |
| R07 | aggs terms | Nombre de films par genre | A tester |
| R08 | aggs terms + avg | Note moyenne par langue | A tester |
| R09 | aggs date_histogram | Films par année | A tester |
| R10 | range + sort | Meilleurs films très votés | A tester |
| R11 | multi_match + highlight | Recherche full-text avec highlight | A tester |
| R12 | aggs stats | Statistiques globales | A tester |

