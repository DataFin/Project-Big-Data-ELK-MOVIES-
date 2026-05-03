# Documentation projet — ELK Movies Platform

## Responsable : Audrey
## Feature : F7 - Documentation finale

---

## 1. Présentation du projet

**Nom du projet :** ELK Movies Data Platform
**Équipe :** Sandrine (lead), Audrey, Destiné, Alexandre
**Repository :** https://github.com/DataFin/Project-Big-Data-ELK-MOVIES-
**Dataset :** movies.csv — Kaggle (662 083 films, 373 Mo)
**Stack technique :** Elasticsearch 8.13, Kibana 8.13, Logstash 8.13, Python Flask

---

## 2. Organisation Gitflow

### 2.1 Branches

| Branche | Rôle | Protection |
|---|---|---|
| `main` | Code stable final | PR obligatoire, no push direct |
| `dev` | Intégration de toutes les features | PR obligatoire, no push direct |
| `feature/*` | Développement d'une feature | Mergée dans dev via PR |

### 2.2 Règles

- Interdiction de push direct sur `main` et `dev`
- PR obligatoire pour merger
- Minimum 1 reviewer par PR
- Commits explicites avec préfixes (feat, fix, docs, chore, config)

### 2.3 Branches créées

| Branche | Responsable | Statut |
|---|---|---|
| `feature/bootstrap-structure` | Audrey | PR ouverte |
| `feature/ingestion-raw` | Sandrine | PR ouverte |
| `feature/nettoyage-normalisation` | Sandrine + Destiné + Audrey | PR ouverte |
| `feature/mapping-qualite` | Alexandre | A créer |
| `feature/requetes-analytiques` | Sandrine | A créer |
| `feature/dashboard-kibana` | Destiné | A créer |
| `feature/documentation` | Audrey | A créer |
| `feature/search-api` | Alexandre | A créer |

---

## 3. Répartition des features

| Feature | Responsable | Description |
|---|---|---|
| F1 - Bootstrap stack | Audrey | Docker Compose, scripts start/stop/health-check |
| F2 - Ingestion brute | Sandrine | Pipeline Logstash → movies_raw (662 083 docs) |
| F3 - Nettoyage | Destiné + Sandrine + Audrey | Pipeline nettoyage → movies_clean (662 077 docs) |
| F4 - Mapping & qualité | Alexandre | Mapping explicite, analyzer, contrôle qualité |
| F5 - Requêtes analytiques | Sandrine | 12 requêtes DSL dont 5 bool |
| F6 - Dashboard Kibana | Destiné | 6-8 visualisations, 1 dashboard |
| F7 - Documentation | Audrey | Runbook, dictionnaire, planning poker |
| F8 - Moteur de recherche | Alexandre | API Flask connectée à Elasticsearch |

---

## 4. Conventions de commit

| Préfixe | Utilisation | Exemple |
|---|---|---|
| `feat:` | Nouvelle fonctionnalité | `feat: ajout pipeline ingestion brute` |
| `fix:` | Correction d'un bug | `fix: correction mapping revenue en long` |
| `docs:` | Documentation | `docs: ajout runbook.md` |
| `chore:` | Tâche technique | `chore: création structure dossiers` |
| `config:` | Configuration | `config: mise à jour docker-compose.yml` |

---

## 5. Architecture technique

```
movies.csv (373 Mo, non versionné)
        ↓
Logstash (logstash.conf)          Logstash (logstash-clean.conf)
        ↓                                  ↓
movies_raw (662 083 docs)    movies_clean (662 077 docs)
        ↓                                  ↓
        └──────────── Kibana Dashboard ────┘
                              ↓
                    Flask Search API
```

### 5.1 Services Docker

| Service | Image | Port | Rôle |
|---|---|---|---|
| elasticsearch | elasticsearch:8.13.0 | 9200, 9300 | Stockage et indexation |
| kibana | kibana:8.13.0 | 5601 | Visualisation |
| logstash | logstash:8.13.0 | 9600 | Ingestion et nettoyage |

---

## 6. Résultats obtenus

### 6.1 Ingestion

| Index | Documents | Statut |
|---|---|---|
| movies_raw | 662 083 | ✅ Opérationnel |
| movies_clean | 662 077 | ✅ Opérationnel |
| Différence | 6 documents | Supprimés (sans titre ou id) |

### 6.2 Nettoyage

| Transformation | Avant | Après |
|---|---|---|
| Type budget | string "70000000.0" | long 70000000 |
| Type release_date | string "2022-04-07" | date ISO 8601 |
| Type genres | string "Action-Adventure" | keyword[] ["Action", "Adventure"] |
| Valeurs nulles budget | 0 | -1 (convention N/A) |
| Analyzer full-text | Non | french_english_analyzer |

---

## 7. Difficultés rencontrées

| Problème | Cause | Solution |
|---|---|---|
| Erreur "container name in use" | Anciens conteneurs actifs | `docker rm -f elasticsearch kibana logstash` |
| Erreur "out of range of int" | Revenue Avatar > 2 milliards | Changer integer → long dans le mapping |
| Commentaires dans le mapping | Elasticsearch refuse le champ "comment" | Supprimer tous les champs comment du JSON |
| Logstash recrée l'index | Logstash démarre avant la création du mapping | Arrêter Logstash avant de créer l'index |
| LF/CRLF warnings | Différence Windows/Linux | Normal sur Windows, sans impact |
