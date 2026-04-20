# Contrôle qualité — Avant/Après nettoyage

## Responsable : Alexandre
## Feature : F4 - Mapping & qualité data

---

## 1. Comparaison des index

| Métrique | movies_raw | movies_clean | Différence |
|---|---|---|---|
| Nombre de documents | 662 083 | 662 077 | -6 (sans titre/id) |
| Type de `budget` | text | integer/long | Converti |
| Type de `revenue` | text | long | Converti |
| Type de `release_date` | text | date | Converti |
| Type de `genres` | text | keyword[] | Normalisé |
| Type de `credits` | text | keyword[] | Normalisé |
| Type de `vote_count` | text | integer | Converti |
| Analyzer personnalisé | Non | Oui | Ajouté |

---

## 2. Requêtes de vérification

### 2.1 Compter les documents dans chaque index

```json
GET /movies_raw/_count
```
Résultat : 662 083

```json
GET /movies_clean/_count
```
Résultat : 662 077

### 2.2 Vérifier le mapping de movies_clean

```json
GET /movies_clean/_mapping
```

Résultat attendu :
- `budget` → long
- `revenue` → long
- `release_date` → date
- `genres` → keyword
- `title` → text avec french_english_analyzer

### 2.3 Vérifier qu'une requête range fonctionne sur movies_clean

Cette requête ne fonctionne PAS sur movies_raw car budget est une chaîne.
Elle fonctionne sur movies_clean car budget est un entier.

```json
GET /movies_clean/_search
{
  "query": {
    "range": {
      "budget": {
        "gte": 100000000
      }
    }
  },
  "size": 3
}
```

### 2.4 Vérifier que genres est bien un tableau

```json
GET /movies_clean/_search
{
  "query": {
    "term": {
      "genres": "Action"
    }
  },
  "size": 3
}
```

Résultat attendu : films dont genres contient "Action"

### 2.5 Vérifier que release_date est bien une date

Cette requête ne fonctionne PAS sur movies_raw.
Elle fonctionne sur movies_clean car release_date est une vraie date.

```json
GET /movies_clean/_search
{
  "query": {
    "range": {
      "release_date": {
        "gte": "2020-01-01",
        "lte": "2023-12-31"
      }
    }
  },
  "size": 3
}
```

### 2.6 Vérifier l'analyzer personnalisé

```json
GET /movies_clean/_analyze
{
  "analyzer": "french_english_analyzer",
  "text": "Les films d'action et d'aventure"
}
```

Résultat attendu : les mots vides (les, d) sont supprimés,
les mots sont réduits à leur racine (films → film, action → action).

### 2.7 Vérifier un document nettoyé (Avatar)

```json
GET /movies_clean/_doc/19995
```

Résultat attendu :
- genres : ["Action", "Adventure", "Fantasy", "Science Fiction"]
- budget : 237000000 (integer, pas "237000000.0")
- revenue : 2847246203 (long)
- runtime : 162 (integer, pas "162.0")
- release_date : "2009-12-10T00:00:00.000Z" (date ISO)

---

## 3. Anomalies détectées et corrigées

| Anomalie | Nombre de documents affectés | Correction appliquée |
|---|---|---|
| budget = 0 | ~297 000 (45%) | Remplacé par -1 |
| revenue = 0 | ~400 000 (60%) | Remplacé par -1 |
| tagline vide | ~200 000 (30%) | Remplacé par "N/A" |
| overview vide | ~50 000 (8%) | Remplacé par "N/A" |
| Documents sans titre | ~6 | Supprimés |

---

## 4. Vérification de l'analyzer personnalisé

L'analyzer `french_english_analyzer` est défini dans les settings de movies_clean.
Il est appliqué aux champs : title, overview, tagline.

Vérification que l'analyzer est bien présent :

```json
GET /movies_clean/_settings
```

Résultat attendu : présence de `french_english_analyzer` dans la section `analysis`.

---

## 5. Commandes PowerShell pour exécuter les vérifications

```powershell
# Comparer les counts
Invoke-RestMethod -Method GET -Uri "http://localhost:9200/movies_raw/_count"
Invoke-RestMethod -Method GET -Uri "http://localhost:9200/movies_clean/_count"

# Vérifier le mapping
Invoke-RestMethod -Method GET -Uri "http://localhost:9200/movies_clean/_mapping" | ConvertTo-Json -Depth 10

# Vérifier Avatar
Invoke-RestMethod -Method GET -Uri "http://localhost:9200/movies_clean/_doc/19995" | ConvertTo-Json -Depth 5

# Vérifier les settings
Invoke-RestMethod -Method GET -Uri "http://localhost:9200/movies_clean/_settings" | ConvertTo-Json -Depth 10
```
