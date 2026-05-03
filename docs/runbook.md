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
│   └── demo_script.md          (script de démonstration)
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
│   └── requirements.txt
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
