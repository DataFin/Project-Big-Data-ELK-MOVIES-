# Requêtes Elasticsearch DSL — movies_clean

## Responsable : Destiné
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
      // must = conditions obligatoires, le film DOIT être du genre Action
      "must": [
        { "term": { "genres": "Action" } }
      ],
      // filter = on affine les résultats sans affecter le score
      // ici on veut les films sortis après 2015, bien notés et avec assez de votes
      "filter": [
        { "range": { "release_date": { "gte": "2015-01-01" } } },
        { "range": { "vote_average": { "gte": 7.0 } } },
        // on met un minimum de 1000 votes pour éviter les films peu connus
        { "range": { "vote_count": { "gte": 1000 } } }
      ]
    }
  },
  // on trie par popularité pour avoir les plus connus en premier
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
      // must = le film doit avoir un gros budget entre 100M et 500M
      "must": [
        { "range": { "budget": { "gte": 100000000, "lte": 500000000 } } }
      ],
      // must_not = on exclut les films qui ont bien marché (revenue > 50M)
      // et ceux qui sont encore en production (données pas fiables)
      "must_not": [
        { "range": { "revenue": { "gte": 50000000 } } },
        { "term": { "status": "Post Production" } },
        { "term": { "status": "In Production" } },
        { "term": { "status": "Planned" } }
      ],
      // filter = on garde seulement les films en anglais avec assez de votes
      "filter": [
        { "term": { "original_language": "en" } },
        { "range": { "vote_count": { "gte": 100 } } }
      ]
    }
  },
  // on trie par budget décroissant pour voir les plus gros flops en premier
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
      // should = au moins une de ces conditions doit être vraie
      // c'est comme un "OU" — pas besoin que tout soit vrai en même temps
      "should": [
        // boost: 2 veut dire que si le mot est dans le titre c'est plus important
        { "match": { "title": { "query": "space galaxy universe", "boost": 2 } } },
        // on cherche aussi dans le synopsis
        { "match": { "overview": { "query": "space galaxy universe alien planet" } } },
        // ou si le film est dans ces genres
        { "terms": { "genres": ["Science Fiction", "Adventure"] } }
      ],
      // au moins 1 condition should doit être vraie
      "minimum_should_match": 1,
      // en plus on filtre sur la note pour avoir des films de qualité
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
      // must = l'acteur doit obligatoirement être dans le champ credits
      "must": [
        { "term": { "credits": "Leonardo DiCaprio" } }
      ],
      // filter = on affine avec la note et le nombre de votes minimum
      // un film avec 3 votes et une note de 10 c'est pas fiable
      "filter": [
        { "range": { "vote_average": { "gte": 7.0 } } },
        { "range": { "vote_count": { "gte": 500 } } }
      ]
    }
  },
  // on trie par note décroissante pour voir ses meilleurs films en premier
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
      // must = budget et revenue doivent être supérieurs à 1M
      // ça évite les films avec des données à 0 ou incorrectes
      "must": [
        { "range": { "budget": { "gt": 1000000 } } },
        { "range": { "revenue": { "gt": 1000000 } } }
      ],
      // must_not = on exclut les films d'animation et ceux encore en production
      "must_not": [
        { "term": { "genres": "Animation" } },
        { "term": { "status": "Post Production" } },
        { "term": { "status": "In Production" } }
      ],
      // filter = films en anglais avec assez de votes pour être fiables
      "filter": [
        { "range": { "vote_count": { "gte": 500 } } },
        { "term": { "original_language": "en" } }
      ]
    }
  },
  // on trie par revenue décroissant pour voir les plus rentables en premier
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
  // match_all = on prend tous les films sans filtre
  "query": { "match_all": {} },
  // on trie par popularité décroissante
  "sort": [{ "popularity": { "order": "desc" } }],
  "size": 10,
  // _source = on affiche seulement ces champs pour pas surcharger le résultat
  "_source": ["title", "popularity", "vote_average", "release_date", "genres"]
}
```

---

### R07 — Agrégation par genre

**Cas métier : Combien de films par genre dans le dataset ?**

```json
GET /movies_clean/_search
{
  // size: 0 = on veut pas les documents, juste les stats
  "size": 0,
  "aggs": {
    "genres_count": {
      // terms = on groupe par valeur du champ genres
      // et on compte combien de films pour chaque genre
      "terms": {
        "field": "genres",
        "size": 20  // on affiche les 20 genres les plus représentés
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
      // on groupe d'abord par langue
      "terms": {
        "field": "original_language",
        "size": 15,
        // min_doc_count: 100 = on ignore les langues avec moins de 100 films
        // sinon une langue avec 2 films à 10/10 fausserait les résultats
        "min_doc_count": 100
      },
      "aggs": {
        // pour chaque langue on calcule la note moyenne
        "note_moyenne": {
          "avg": { "field": "vote_average" }
        },
        // et aussi la popularité moyenne
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
      // date_histogram = on groupe automatiquement par période
      "date_histogram": {
        "field": "release_date",
        "calendar_interval": "year",  // on regroupe par année
        "format": "yyyy"
      },
      "aggs": {
        // pour chaque année on calcule aussi la note moyenne
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
  // on filtre sur vote_count >= 10000 pour avoir des notes fiables
  // un film avec 10 votes à 9.5 c'est pas pareil qu'un film avec 50000 votes à 9.5
  "query": {
    "range": {
      "vote_count": { "gte": 10000 }
    }
  },
  // on trie d'abord par note puis par nombre de votes pour départager les ex-aequo
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
    // multi_match = on cherche dans plusieurs champs en même temps
    "multi_match": {
      "query": "dark knight batman",
      // title^3 = le titre a 3 fois plus de poids que les autres champs
      "fields": ["title^3", "overview", "tagline"],
      "type": "best_fields",
      // fuzziness AUTO = tolère les fautes de frappe
      // genre "batamn" trouvera quand même "batman"
      "fuzziness": "AUTO"
    }
  },
  // highlight = met en surbrillance les mots trouvés dans les résultats
  "highlight": {
    "fields": {
      "title": {},
      "overview": { "fragment_size": 150 }  // extrait de 150 caractères autour du mot trouvé
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
    // stats = donne min, max, moyenne, somme et count en une seule requête
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
    // en bonus on récupère aussi les genres et langues les plus fréquents
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
| R03 | bool (should) | Recherche full-text espace/SF |
| R04 | bool (must + filter) | Films par acteur bien notés | 
| R05 | bool (must + must_not + filter) | Films rentables hors animation |
| R06 | match_all + sort | Top 10 popularité |
| R07 | aggs terms | Nombre de films par genre |
| R08 | aggs terms + avg | Note moyenne par langue | 
| R09 | aggs date_histogram | Films par année | 
| R10 | range + sort | Meilleurs films très votés |
| R11 | multi_match + highlight | Recherche full-text avec highlight |
| R12 | aggs stats | Statistiques globales |