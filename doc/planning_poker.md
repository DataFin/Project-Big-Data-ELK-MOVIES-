# Planning Poker — ELK Movies Platform

## Participants
- **Sandrine** (lead technique)
- **Audrey**
- **Destiné**
- **Alexandre**

---

## 1. Échelle utilisée

Fibonacci : 1, 2, 3, 5, 8, 13

---

## 2. Stories estimées

| ID | User Story | Votes initiaux | Estimation finale | Hypothèses | Owner |
|---|---|---|---|---|---|
| US-01 | En tant que développeur, je veux une stack ELK opérationnelle pour pouvoir travailler localement | 2, 3, 3, 2 | 3 | Docker Desktop installé sur chaque PC | Audrey |
| US-02 | En tant qu'analyste, je veux ingérer movies.csv dans movies_raw pour avoir les données brutes disponibles | 3, 3, 5, 3 | 3 | Le fichier movies.csv est disponible sur Kaggle | Sandrine |
| US-03 | En tant qu'analyste, je veux des données nettoyées dans movies_clean pour produire des visualisations fiables | 5, 8, 8, 5 | 8 | Le pipeline de nettoyage couvre tous les champs du dataset | Destiné + Sandrine + Audrey |
| US-04 | En tant que développeur, je veux un mapping explicite pour movies_clean pour garantir le bon typage des données | 3, 5, 5, 3 | 5 | Les types sont bien définis dans le dictionnaire de données | Alexandre |
| US-05 | En tant qu'analyste, je veux 12 requêtes DSL commentées pour explorer les données films | 5, 5, 8, 5 | 5 | Les requêtes couvrent des cas métier réels | Destiné |
| US-06 | En tant que manager, je veux un dashboard Kibana pour visualiser les tendances du cinéma | 5, 8, 8, 8 | 8 | Kibana est opérationnel et movies_clean est indexé | Destiné + Audrey + Sandrine |
| US-07 | En tant que développeur, je veux une documentation complète pour que le projet soit reproductible | 3, 3, 5, 3 | 3 | La documentation couvre tous les aspects techniques | Audrey + Sandrine |
| US-08 | En tant qu'utilisateur, je veux un moteur de recherche pour trouver des films par titre ou genre | 5, 8, 8, 5 | 8 | Flask est disponible, Elasticsearch est opérationnel | Alexandre |

---

## 3. Décisions de découpage

**Story US-03 (Nettoyage) :**
- Découpage : 3 sous-tâches (types, listes, anomalies)
- Risque : données aberrantes dans le dataset (budgets erronés)
- Action : ajouter des filtres de validation dans le pipeline

**Story US-06 (Dashboard Kibana) :**
- Découpage : 6 à 8 visualisations indépendantes
- Risque : certaines visualisations nécessitent des agrégations complexes
- Action : tester chaque visualisation individuellement avant le dashboard

**Story US-08 (Moteur de recherche) :**
- Découpage : API Flask + recherche full-text + filtres
- Risque : latence Elasticsearch selon la complexité des requêtes
- Action : limiter à 3 filtres maximum pour la v1

---

## 4. Répartition finale des features

| Membre | Features | Points total |
|---|---|---|
| **Sandrine** (lead) | F2 Ingestion brute + F7 Documentation + normalisation F3 + F6 Dashboard Kibana| 3 + 3 + 3 + 8 = 17 |
| **Audrey** | F1 Bootstrap stack + F7 Documentation + anomalies F3 + F6 Dashboard Kibana | 3 + 3 + 2 + 8 = 16 |
| **Destiné** | F3 Nettoyage (types + date) + F6 Dashboard Kibana +F5 Requêtes DSL | 3 + 8 + 5  = 16 |
| **Alexandre** | F4 Mapping qualité + F8 Moteur de recherche | 5 + 8 = 13 |

---

## 5. Ordre de réalisation

```
F1 Bootstrap stack (Audrey)
        ↓
F2 Ingestion brute (Sandrine)
        ↓
F3 Nettoyage (Destiné + Sandrine + Audrey)
        ↓
F4 Mapping & qualité (Alexandre)
        ↓
F5 Requêtes analytiques (Destiné)
        ↓
F6 Dashboard Kibana (Destiné + Sandrine + Audrey)
        ↓
F7 Documentation (Audrey + Sandrine)
        ↓
F8 Moteur de recherche (Alexandre)
```
