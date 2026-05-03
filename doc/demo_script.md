# Script de démonstration — ELK Movies Platform

## Responsable : Toute l'équipe
## Feature : F7 - Documentation finale

---

## 1. Objectif de la démonstration

Montrer que la plateforme ELK Movies est entièrement fonctionnelle :
- Stack ELK démarrée et opérationnelle
- 662 083 films ingérés dans movies_raw
- 662 077 films nettoyés dans movies_clean
- Requêtes DSL fonctionnelles
- Dashboard Kibana exploitable
- Moteur de recherche Flask opérationnel

---

## 2. Prérequis avant la démo

- Docker Desktop démarré
- Projet cloné sur le PC
- movies.csv placé dans data/
- Terminal PowerShell ouvert dans le dossier du projet

---

## 3. Déroulement de la démonstration

### Étape 1 — Démarrer la stack (30 secondes)

```bash
docker compose up -d
docker compose ps
```

**Ce qu'on doit voir :** Les 3 services (elasticsearch, kibana, logstash) démarrent
correctement avec le statut Healthy/Running.

---

### Étape 2 — Vérifier l'ingestion brute (30 secondes)

```bash
Invoke-RestMethod -Method GET -Uri "http://localhost:9200/movies_raw/_count"
```

**Ce qu'on doit voir :** 662 083 films ingérés dans movies_raw.

---

### Étape 3 — Vérifier les données nettoyées (1 minute)

```bash
Invoke-RestMethod -Method GET -Uri "http://localhost:9200/movies_clean/_count"
```

Puis afficher le film Avatar nettoyé :

```bash
Invoke-RestMethod -Method GET -Uri "http://localhost:9200/movies_clean/_doc/19995" | ConvertTo-Json -Depth 5
```

**Ce qu'on doit voir :**
- 662 077 films dans movies_clean
- genres est un tableau ["Action", "Adventure", "Fantasy", "Science Fiction"]
- budget est un entier 237000000 (pas une chaîne)
- release_date est une vraie date ISO 8601

---

### Étape 4 — Démontrer une requête DSL (1 minute)

Dans Kibana Dev Tools (http://localhost:5601) :

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
  "size": 5
}
```

**Ce qu'on montre :** Une requête bool complexe qui retourne les films d'action
populaires récents avec une bonne note.

---

### Étape 5 — Montrer le dashboard Kibana (2 minutes)

Ouvrir http://localhost:5601, importer le fichier json du dashbord pris sur github et naviguer vers le dashboard Movies Analytics.

**Ce qu'on montre :**
- Répartition des films par genre
- Evolution de la production par année
- Top films par popularité
- Distribution des notes
- Films par langue

---

### Étape 6 — Démontrer le moteur de recherche (1 minute)

```bash
# Rechercher des films par titre
curl http://localhost:5000/search?q=avatar

# Filtrer par genre
curl http://localhost:5000/search?q=space&genre=Science+Fiction

# Filtrer par langue
curl http://localhost:5000/search?q=batman&language=en&year=2008
```

**Ce qu'on montre :** Le moteur de recherche Flask retourne des résultats
pertinents avec la recherche full-text et les filtres.

---

## 4. Points clés à mettre en avant

- **Reproductibilité** : le projet démarre en 3 commandes sur n'importe quelle machine
- **Qualité des données** : 6 documents supprimés sur 662 083 (99.99% de données valides)
- **Typage explicite** : budget, revenue, dates sont correctement typés
- **Recherche avancée** : l'analyzer french_english_analyzer améliore la qualité de la recherche
- **Organisation** : Gitflow respecté avec PR et reviews tracées

---

## 5. Durée totale estimée

| Étape | Durée |
|---|---|
| Démarrage stack | 30 sec |
| Vérification ingestion | 30 sec |
| Données nettoyées | 1 min |
| Requête DSL | 1 min |
| Dashboard Kibana | 2 min |
| Moteur de recherche | 1 min |
| **Total** | **~6 minutes** |
