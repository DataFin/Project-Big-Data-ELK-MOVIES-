# Preuve d'ingestion — movies_raw

## Informations générales

| Élément | Valeur |
|---|---|
| Index | `movies_raw` |
| Date d'ingestion | 13/04/2026 |
| Responsable | Sandrine |
| Source | `data/movies.csv` (373 Mo) |
| Pipeline | `logstash/pipeline/logstash.conf` |

---

## 1. Comptage des documents (_count)

**Commande exécutée :**
```bash
curl http://localhost:9200/movies_raw/_count
```

**Résultat obtenu :**
```json
{
  "count": 662083,
  "_shards": {
    "total": 1,
    "successful": 1,
    "skipped": 0,
    "failed": 0
  }
}
```

**Interprétation :**
- 662 083 films ont été ingérés avec succès
- 1 shard actif, 0 erreur
- L'ingestion est complète et fiable

---

## 2. Échantillon de documents

**Commande exécutée :**
```bash
curl http://localhost:9200/movies_raw/_search?size=2&pretty
```

**Résultat obtenu :**
```json
{
  "hits": {
    "total": { "value": 662083 },
    "hits": [
      {
        "_index": "movies_raw",
        "_id": "639933",
        "_source": {
          "id": "639933",
          "title": "The Northman",
          "genres": "Action-Adventure-Fantasy",
          "original_language": "en",
          "overview": "Prince Amleth is on the verge of becoming a man...",
          "popularity": "3669.153",
          "release_date": "2022-04-07",
          "budget": "70000000.0",
          "revenue": "68350700.0",
          "runtime": "137.0",
          "status": "Released",
          "vote_average": "7.3",
          "vote_count": "1478.0"
        }
      },
      {
        "_index": "movies_raw",
        "_id": "338953",
        "_source": {
          "id": "338953",
          "title": "Fantastic Beasts: The Secrets of Dumbledore",
          "genres": "Fantasy-Adventure-Action",
          "original_language": "en",
          "popularity": "3456.961",
          "release_date": "2022-04-06",
          "budget": "200000000.0",
          "revenue": "400000000.0",
          "runtime": "142.0",
          "status": "Released",
          "vote_average": "6.9",
          "vote_count": "1800.0"
        }
      }
    ]
  }
}
```

---

## 3. Anomalies observées dans movies_raw

Ces anomalies seront corrigées dans `movies_clean` (Feature F3/F4) :

| Champ | Problème observé | Correction prévue |
|---|---|---|
| `genres` | Chaîne séparée par `-` | Tableau `["Action","Adventure"]` |
| `budget` | Float `70000000.0` | Integer `70000000` |
| `revenue` | Float `400000000.0` | Integer `400000000` |
| `runtime` | Float `137.0` | Integer `137` |
| `vote_count` | Float `1478.0` | Integer `1478` |
| `release_date` | Chaîne `"2022-04-07"` | Date ISO `2022-04-07` |
| `credits` | Encodage UTF-8 cassé | Noms corrigés |
| `keywords` | Chaîne séparée par `-` | Tableau `["sword","revenge"]` |
| `popularity` | Chaîne `"3669.153"` | Float `3669.153` |

---

## 4. Mapping dynamique détecté par Elasticsearch

Tous les champs sont indexés comme `text` ou `keyword` car le dynamic mapping
devine les types automatiquement. C'est intentionnel pour `movies_raw` —
le typage explicite sera fait dans `movies_clean`.

```bash
curl http://localhost:9200/movies_raw/_mapping?pretty
```
