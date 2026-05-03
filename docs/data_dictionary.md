# Dictionnaire de données — movies_clean

## Responsable : Audrey
## Feature : F7 - Documentation finale

---

## 1. Source des données

| Élément | Valeur |
|---|---|
| Source | Kaggle - Millions of Movies |
| URL | https://www.kaggle.com/datasets/akshaypawar7/millions-of-movies |
| Format | CSV |
| Taille | 373 Mo |
| Nombre de films (brut) | 662 083 |
| Nombre de films (nettoyé) | 662 077 |

---

## 2. Index Elasticsearch

| Index | Description | Documents |
|---|---|---|
| `movies_raw` | Données brutes sans transformation | 662 083 |
| `movies_clean` | Données nettoyées et typées | 662 077 |

---

## 3. Dictionnaire des champs

### 3.1 Identifiant

| Champ | Type ES | Type source | Description | Exemple |
|---|---|---|---|---|
| `id` | integer | string | Identifiant unique TMDB du film | 19995 |

---

### 3.2 Informations générales

| Champ | Type ES | Type source | Description | Exemple |
|---|---|---|---|---|
| `title` | text + keyword | string | Titre du film. Indexé en full-text avec french_english_analyzer pour la recherche. Le sous-champ keyword permet le tri et les agrégations. | "Avatar" |
| `original_language` | keyword | string | Code ISO 639-1 de la langue originale du film | "en", "fr", "ja" |
| `status` | keyword | string | Statut de sortie du film | "Released", "Post Production", "In Production", "Planned" |
| `overview` | text | string | Synopsis du film. Indexé en full-text avec french_english_analyzer. | "In the 22nd century..." |
| `tagline` | text | string | Slogan du film. "N/A" si absent. | "Enter the world of Pandora." |

---

### 3.3 Dates

| Champ | Type ES | Type source | Description | Exemple | Valeurs spéciales |
|---|---|---|---|---|---|
| `release_date` | date | string | Date de sortie au format ISO 8601 | "2009-12-10T00:00:00.000Z" | null si absente |

---

### 3.4 Métriques financières

| Champ | Type ES | Type source | Description | Exemple | Valeurs spéciales |
|---|---|---|---|---|---|
| `budget` | long | float | Budget du film en dollars américains | 237000000 | -1 si non disponible |
| `revenue` | long | float | Recettes mondiales en dollars américains | 2847246203 | -1 si non disponible |

> Note : budget et revenue utilisent le type `long` (et non `integer`) car
> certains films comme Avatar (2.8 milliards) dépassent la limite de l'integer.

---

### 3.5 Métriques techniques

| Champ | Type ES | Type source | Description | Exemple | Valeurs spéciales |
|---|---|---|---|---|---|
| `runtime` | integer | float | Durée du film en minutes | 162 | -1 si non disponible |
| `popularity` | float | float | Score de popularité TMDB | 373.462 | Calculé par TMDB |

---

### 3.6 Métriques d'évaluation

| Champ | Type ES | Type source | Description | Exemple |
|---|---|---|---|---|
| `vote_average` | float | float | Note moyenne des utilisateurs sur 10 | 7.5 |
| `vote_count` | integer | float | Nombre total de votes | 25481 |

---

### 3.7 Listes (champs multi-valeurs)

Ces champs étaient des chaînes séparées par "-" dans le CSV original.
Ils ont été normalisés en tableaux par le pipeline Logstash.

| Champ | Type ES | Description | Exemple |
|---|---|---|---|
| `genres` | keyword[] | Liste des genres du film | ["Action", "Adventure", "Fantasy"] |
| `keywords` | keyword[] | Liste des mots-clés associés | ["space travel", "alien", "marine"] |
| `credits` | keyword[] | Liste des acteurs principaux | ["Sam Worthington", "Zoe Saldana"] |
| `production_companies` | keyword[] | Sociétés de production | ["Lightstorm Entertainment", "20th Century Fox"] |
| `recommendations` | keyword[] | IDs des films recommandés | ["24428", "49026", "70160"] |

---

### 3.8 Chemins d'images

Ces champs ne sont pas indexés (index: false) car ils ne sont pas
utilisés pour les recherches — ils servent uniquement à afficher les images.

| Champ | Type ES | Description | Exemple |
|---|---|---|---|
| `poster_path` | keyword (non indexé) | Chemin vers l'affiche du film | "/jRXYjXNq0Cs2TcJjLkki24MLp7u.jpg" |
| `backdrop_path` | keyword (non indexé) | Chemin vers l'image de fond | "/cqnVuxXe6vA7wfNWubak3x36DKJ.jpg" |

Pour afficher une image, construire l'URL :
```
https://image.tmdb.org/t/p/w500{poster_path}
```

---

## 4. Valeurs spéciales

| Valeur | Signification | Champs concernés |
|---|---|---|
| `-1` | Donnée non disponible dans le dataset | budget, revenue, runtime |
| `"N/A"` | Champ texte vide dans le dataset | tagline, overview |
| `null` | Valeur absente | release_date, poster_path, backdrop_path |
| `[]` | Liste vide | genres, keywords, credits, production_companies, recommendations |

---

## 5. Analyzer personnalisé

L'analyzer `french_english_analyzer` est appliqué aux champs `title`, `overview` et `tagline`.

| Composant | Type | Rôle |
|---|---|---|
| `standard tokenizer` | tokenizer | Découpe le texte en mots |
| `lowercase` | filter | Met tout en minuscules |
| `asciifolding` | filter | Supprime les accents (café → cafe) |
| `french_english_stop` | filter | Supprime les mots vides (le, la, the, a...) |
| `french_english_stemmer` | filter | Réduit les mots à leur racine (films → film) |

---

## 6. Statistiques globales du dataset

| Métrique | Valeur |
|---|---|
| Total films | 662 077 |
| Films avec budget renseigné (> 0) | ~365 000 (55%) |
| Films avec recettes renseignées (> 0) | ~262 000 (40%) |
| Films avec tagline | ~462 000 (70%) |
| Langue la plus représentée | Anglais (en) |
| Genre le plus représenté | Drama |
| Période couverte | 1888 - 2026 |
