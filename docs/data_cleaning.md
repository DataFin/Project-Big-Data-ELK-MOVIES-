# Documentation du nettoyage des données — movies_clean

## Équipe
- **Sandrine** (lead) — Normalisation des listes
- **Destiné** — Conversions de types + parsing date + indexation
- **Audrey** — Traitement des anomalies

---

## 1. Description des colonnes

| Colonne | Type brut | Type nettoyé | Description |
|---|---|---|---|
| `id` | string | integer | Identifiant unique du film |
| `title` | string | text | Titre du film |
| `genres` | string (`"Action-Adventure"`) | keyword[] | Liste des genres |
| `original_language` | string | keyword | Langue originale |
| `overview` | string | text | Synopsis |
| `popularity` | string | float | Score de popularité |
| `production_companies` | string | keyword[] | Sociétés de production |
| `release_date` | string (`"2022-04-07"`) | date | Date de sortie |
| `budget` | string (`"70000000.0"`) | integer | Budget en dollars |
| `revenue` | string (`"400000000.0"`) | integer | Recettes en dollars |
| `runtime` | string (`"137.0"`) | integer | Durée en minutes |
| `status` | string | keyword | Statut de sortie |
| `tagline` | string | text | Slogan du film |
| `vote_average` | string | float | Note moyenne (0-10) |
| `vote_count` | string (`"1478.0"`) | integer | Nombre de votes |
| `credits` | string | keyword[] | Liste des acteurs |
| `keywords` | string | keyword[] | Mots-clés |
| `poster_path` | string | keyword (non indexé) | Chemin affiche |
| `backdrop_path` | string | keyword (non indexé) | Chemin image fond |
| `recommendations` | string | keyword[] | IDs films recommandés |

---

## 2. Anomalies détectées

### 2.1 Types incorrects
Tous les champs arrivent comme des **chaînes de caractères** depuis le CSV,
même les valeurs numériques.

```
"budget"     : "70000000.0"  → doit être 70000000 (integer)
"runtime"    : "137.0"       → doit être 137 (integer)
"vote_count" : "1478.0"      → doit être 1478 (integer)
"popularity" : "3669.153"    → doit être 3669.153 (float)
```

### 2.2 Listes encodées comme chaînes
Les champs multi-valeurs sont des chaînes séparées par `-` au lieu de vrais tableaux.

```
"genres"   : "Action-Adventure-Fantasy"
"credits"  : "Alexander Skarsgård-Nicole Kidman-Claes Bang"
"keywords" : "sword-father murder-prince-iceland-viking"
```

### 2.3 Dates non typées
```
"release_date" : "2022-04-07"  → chaîne de caractères, pas une date
```
Elasticsearch ne peut pas faire de requêtes de plage (range) sur une chaîne.

### 2.4 Valeurs manquantes ou nulles
```
"budget"   : 0.0   → budget non renseigné
"revenue"  : 0.0   → recettes non renseignées
"tagline"  : ""    → slogan vide
"overview" : ""    → synopsis vide
```

### 2.5 Encodage UTF-8 cassé
Les caractères spéciaux sont mal encodés dans certains noms d'acteurs.
```
"Alexander SkarsgÃ¥rd"  → "Alexander Skarsgård"
"BjÃ¶rk"               → "Björk"
```

---

## 3. Règles de nettoyage appliquées

### 3.1 Conversion des types numériques (Destiné)

```ruby
# Dans logstash-clean.conf
mutate {
  convert => {
    "id"           => "integer"
    "popularity"   => "float"
    "vote_average" => "float"
    "budget"       => "float"   # float d'abord car "137.0" ne parse pas en integer
    "revenue"      => "float"
    "runtime"      => "float"
    "vote_count"   => "float"
  }
}
mutate {
  convert => {
    "budget"     => "integer"   # ensuite on convertit en integer
    "revenue"    => "integer"
    "runtime"    => "integer"
    "vote_count" => "integer"
  }
}
```

### 3.2 Parsing de la date (Destiné)

```ruby
date {
  match    => ["release_date", "yyyy-MM-dd"]
  target   => "release_date"
  timezone => "UTC"
}
```

### 3.3 Normalisation des listes (Sandrine)

```ruby
mutate {
  split => { "genres"               => "-" }
  split => { "keywords"             => "-" }
  split => { "credits"              => "-" }
  split => { "production_companies" => "-" }
  split => { "recommendations"      => "-" }
}
```

### 3.4 Traitement des anomalies (Audrey)

```ruby
# Valeurs nulles remplacées par -1 (convention : donnée non disponible)
if [budget]  == 0 { mutate { replace => { "budget"  => -1 } } }
if [revenue] == 0 { mutate { replace => { "revenue" => -1 } } }
if [runtime] == 0 { mutate { replace => { "runtime" => -1 } } }

# Champs texte vides remplacés par "N/A"
if ![tagline] or [tagline] == "" { mutate { replace => { "tagline" => "N/A" } } }

# Documents inutilisables supprimés
if ![title] or [title] == "" { drop { } }
if ![id]    or [id]    == "" { drop { } }
```

---

## 4. Mesure d'impact avant/après nettoyage

| Métrique | movies_raw | movies_clean |
|---|---|---|
| Nombre de documents | 662 083 | ~660 000 (estimation) |
| Type de `budget` | string | integer |
| Type de `release_date` | string | date |
| Type de `genres` | string | keyword[] |
| Valeurs nulles `budget` | ~45% | remplacées par -1 |
| Valeurs nulles `tagline` | ~30% | remplacées par "N/A" |
| Documents supprimés | 0 | ~2 000 (sans titre/id) |

> Note : les chiffres exacts seront mis à jour après l'indexation complète
> de movies_clean en comparant les _count des deux index.

---

## 5. Commandes de vérification

```bash
# Comparer le nombre de documents avant/après
curl http://localhost:9200/movies_raw/_count
curl http://localhost:9200/movies_clean/_count

# Vérifier le mapping de movies_clean
curl http://localhost:9200/movies_clean/_mapping?pretty

# Vérifier un document nettoyé
curl http://localhost:9200/movies_clean/_search?size=1&pretty
```
