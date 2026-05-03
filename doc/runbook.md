# Runbook technique — ELK Movies Platform

## Responsable : Audrey
## Feature : F7 - Documentation finale

---

## 1. Prérequis

| Outil | Version minimum | Vérification |
|---|---|---|
| Git | 2.x | `git --version` |
| Docker Desktop | 4.x | `docker --version` |
| Docker Compose | 2.x | `docker compose version` |
| Python | 3.8+ | `python --version` |

---

## 2. Installation et démarrage rapide

### 2.1 Cloner le repo

```bash
git clone https://github.com/DataFin/Project-Big-Data-ELK-MOVIES-.git
cd Project-Big-Data-ELK-MOVIES-
```

### 2.2 Placer le dataset

Télécharger `movies.csv` depuis Kaggle :
```
https://www.kaggle.com/datasets/akshaypawar7/millions-of-movies
```

Placer le fichier dans :
```
Project-Big-Data-ELK-MOVIES-/data/movies.csv
```

> Note : movies.csv fait 373 Mo et est ignoré par .gitignore.
> Chaque membre doit le télécharger individuellement.

### 2.3 Démarrer la stack ELK

```bash
docker compose up -d
```

Vérifier que les 3 services sont démarrés :
```bash
docker compose ps
```

Résultat attendu :
```
NAME            STATUS
elasticsearch   Up (healthy)
kibana          Running
logstash        Started
```

### 2.4 Créer l'index movies_clean

```bash
docker stop logstash
```

```bash
Invoke-RestMethod -Method PUT -Uri "http://localhost:9200/movies_clean" -ContentType "application/json" -InFile "elasticsearch/movies_clean_mapping.json"
```

```bash
docker start logstash
```

### 2.5 Vérifier l'ingestion

Attendre 3 à 5 minutes puis :

```bash
# Vérifier movies_raw
Invoke-RestMethod -Method GET -Uri "http://localhost:9200/movies_raw/_count"
# Résultat attendu : 662 083

# Vérifier movies_clean
Invoke-RestMethod -Method GET -Uri "http://localhost:9200/movies_clean/_count"
# Résultat attendu : 662 077
```

### 2.6 Accéder aux services

| Service | URL | Description |
|---|---|---|
| Elasticsearch | http://localhost:9200 | API REST |
| Kibana | http://localhost:5601 | Interface de visualisation |
| Logstash | http://localhost:9600 | API de monitoring |

---

## 3. Arrêter la stack

```bash
# Arrêter sans supprimer les données
docker compose stop

# Arrêter et supprimer les conteneurs (données conservées dans les volumes)
docker compose down

# Arrêter et supprimer TOUT (données perdues)
docker compose down -v
```

> Attention : `docker compose down -v` supprime les volumes et donc
> toutes les données indexées. Il faudra réindexer depuis le début.

---

## 4. Réindexer les données

Si vous devez réindexer depuis zéro :

```bash
# Supprimer les index existants
Invoke-RestMethod -Method DELETE -Uri "http://localhost:9200/movies_raw"
Invoke-RestMethod -Method DELETE -Uri "http://localhost:9200/movies_clean"

# Recréer movies_clean avec le mapping
docker stop logstash
Invoke-RestMethod -Method PUT -Uri "http://localhost:9200/movies_clean" -ContentType "application/json" -InFile "elasticsearch/movies_clean_mapping.json"
docker start logstash

# Attendre 3-5 minutes et vérifier
Invoke-RestMethod -Method GET -Uri "http://localhost:9200/movies_raw/_count"
Invoke-RestMethod -Method GET -Uri "http://localhost:9200/movies_clean/_count"
```

---

## 5. Résolution des problèmes courants

### 5.1 Erreur "container name already in use"

```bash
docker rm -f elasticsearch kibana logstash
docker compose up -d
```

### 5.2 Kibana ne démarre pas

Elasticsearch met parfois 30-60 secondes à démarrer. Attendez et vérifiez :

```bash
docker compose logs elasticsearch --tail 20
```

### 5.3 Logstash plante au démarrage

Vérifiez que le fichier `logstash/pipeline/logstash.conf` existe :

```bash
dir logstash\pipeline
```

### 5.4 movies_clean reste à 0 documents

Vérifiez que l'index a bien été créé avec le mapping avant de démarrer Logstash :

```bash
Invoke-RestMethod -Method GET -Uri "http://localhost:9200/movies_clean/_mapping"
```

### 5.5 Erreur "version is obsolete"

Supprimer la ligne `version: "3.8"` du `docker-compose.yml`.

---

## 6. Structure du projet

```
Project-Big-Data-ELK-MOVIES-
├── data/
│   └── movies.csv              (non versionné - à télécharger)
├── docs/
│   ├── runbook.md              (ce fichier)
│   ├── data_dictionary.md      (dictionnaire des données)
│   ├── data_cleaning.md        (documentation nettoyage)
│   ├── planning_poker.md       (gestion de projet)
│   ├── project_management.md   (organisation équipe)
│   ├── demo_script.md          (script de démonstration)
│   └── demo.gif                (GIF de démonstration)
├── elasticsearch/
│   ├── movies_clean_mapping.json
│   ├── create_index_raw.json
│   ├── queries.md
│   ├── proof_ingestion.md
│   └── quality_check.md
├── kibana/
│   └── dashboard.ndjson        (export dashboard)
├── logstash/
│   ├── pipeline/
│   │   ├── logstash.conf       (ingestion brute)
│   │   └── logstash-clean.conf (nettoyage)
│   └── config/
│       └── logstash.yml
├── logs/
├── search-api/
│   ├── app.py                  (moteur de recherche Flask)
│   ├── requirements.txt
│   └── README.md
├── docker-compose.yml
├── start.bat
├── stop.bat
├── health-check.bat
└── README.md
```

---

## 7. Commandes utiles

```bash
# Voir les logs en temps réel
docker compose logs -f logstash

# Voir l'état du cluster Elasticsearch
Invoke-RestMethod -Method GET -Uri "http://localhost:9200/_cluster/health"

# Lister tous les index
Invoke-RestMethod -Method GET -Uri "http://localhost:9200/_cat/indices?v"

# Voir le mapping de movies_clean
Invoke-RestMethod -Method GET -Uri "http://localhost:9200/movies_clean/_mapping" | ConvertTo-Json -Depth 10

# Tester un document
Invoke-RestMethod -Method GET -Uri "http://localhost:9200/movies_clean/_doc/19995" | ConvertTo-Json -Depth 5

# Redémarrer un service
docker restart logstash
docker restart kibana
docker restart elasticsearch
```

---

## 8. Importer le dashboard Kibana

### 8.1 Créer le Data View

Avant d'importer le dashboard, il faut créer un Data View pointant vers `movies_clean` :

1. Ouvrir `http://localhost:5601`
2. Menu hamburger → **Stack Management** → **Data Views**
3. Cliquer sur **"Create data view"**
4. Remplir les champs :
   - **Name** : `movies_clean`
   - **Index pattern** : `movies_clean`
   - **Timestamp field** : `release_date`
5. Cliquer sur **"Save data view to Kibana"**

### 8.2 Importer le dashboard

1. Menu hamburger → **Stack Management** → **Saved Objects**
2. Cliquer sur **"Import"**
3. Sélectionner le fichier : `kibana/dashboard.ndjson`
4. Cocher **"Automatically overwrite all saved objects"**
5. Cliquer sur **"Import"**

Résultat attendu : confirmation d'import des 8 visualisations et du dashboard.

### 8.3 Accéder au dashboard

1. Menu hamburger → **Analytics** → **Dashboard**
2. Cliquer sur **"ELK Movies Analytics Dashboard"**
3. Sélectionner la période : `Jan 1, 1888` → `Dec 31, 2026`
4. Cliquer sur **Apply**

Résultat attendu : **602 562 films** affichés avec les 8 visualisations.

> Note : La différence entre 662 077 (movies_clean) et 602 562 (dashboard)
> correspond aux 59 515 films sans release_date qui ne peuvent pas être
> filtrés par date. C'est une limite normale du dataset.

### 8.4 Sauvegarder la période dans le dashboard

Pour que tout le monde voie automatiquement la bonne période :

1. Cliquer sur **"Edit"** en haut à droite
2. Cocher **"Store time with dashboard"**
3. Cliquer sur **"Save"**

### 8.5 Visualisations disponibles

| Visualisation | Type | Insight métier |
|---|---|---|
| Nombre total de films | Metric | 602 562 films avec date de sortie |
| Répartition par genre | Pie chart | Drama 30%, Documentary 20%, Comedy 19% |
| Distribution par année | Area chart | Croissance exponentielle depuis 2000 |
| Budget moyen par genre | Heatmap | Evolution du budget depuis 1887 |
| Top 10 films populaires | Datatable | The Northman en tête (score 3 669) |
| Top 5 genres par nombre | Bar chart | Drama domine la production mondiale |
| Note moyenne par genre | Horizontal bar | Comparaison qualitative entre genres |
| Top 10 films rentables | Stacked bar | Revenue vs Budget des blockbusters |

---

## 9. Lancer le moteur de recherche Flask

### 9.1 Installation des dépendances

```bash
cd search-api
pip install -r requirements.txt
```

### 9.2 Lancer l'API Flask

```bash
python app.py
```

Résultat attendu :
```
=======================================================
  ELK Movies Search API v2.0
  Elasticsearch : http://localhost:9200
  Index         : movies_clean
=======================================================
  Interface HTML : http://localhost:5000
  GET /health
  GET /search?q=avatar&genre=Action&min_rating=7
  GET /movie/19995
  GET /genres
  GET /stats
 * Running on http://127.0.0.1:5000
```

### 9.3 Accéder aux interfaces

| Endpoint | URL | Description |
|---|---|---|
| Interface HTML | http://localhost:5000 | Formulaire de recherche visuel |
| Health check | http://localhost:5000/health | État de l'API et connexion ES |
| Recherche API | http://localhost:5000/search?q=avatar | Recherche JSON |
| Détails film | http://localhost:5000/movie/19995 | Film Avatar |
| Liste genres | http://localhost:5000/genres | 19 genres disponibles |
| Statistiques | http://localhost:5000/stats | Stats globales du dataset |

### 9.4 Tester le moteur de recherche

**Test 1 — Health check :**
```
http://localhost:5000/health
```
Résultat attendu :
```json
{
  "status": "ok",
  "elasticsearch": "connected",
  "index": "movies_clean",
  "total_movies": 662077
}
```

**Test 2 — Recherche simple :**
```
http://localhost:5000/search?q=avatar&min_votes=1000
```
Résultat attendu : 2 films dont Avatar (note 7.5)

**Test 3 — Recherche avec filtres :**
```
http://localhost:5000/search?q=batman&language=en&year=2008
```
Résultat attendu : 13 films dont The Dark Knight (note 8.5)

**Test 4 — Filtres avancés dans l'interface HTML :**

1. Ouvrir `http://localhost:5000`
2. Taper **"space"** dans la recherche
3. Sélectionner genre **"Science Fiction"**
4. Note minimale **"7+"**
5. Votes minimum **"1000+"**
6. Cliquer sur **Rechercher**

### 9.5 Filtres disponibles dans l'interface HTML

| Filtre | Options | Description |
|---|---|---|
| Recherche textuelle | Texte libre | Cherche dans titre, synopsis et slogan |
| Genre | 19 genres | Filtre exact par genre |
| Langue originale | en, fr, ja, ko, es, de, it | Filtre par langue |
| Année de sortie | Nombre (ex: 2022) | Filtre par année exacte |
| Note minimale | 5+, 6+, 7+, 8+ | Filtre sur vote_average |
| Votes minimum | 100+, 500+, 1000+, 5000+ | Filtre sur vote_count |
| Tri | Pertinence, Popularité, Note, Date | Ordre des résultats |

### 9.6 Arrêter le moteur de recherche

Dans le terminal Flask, appuyer sur `Ctrl+C`.
