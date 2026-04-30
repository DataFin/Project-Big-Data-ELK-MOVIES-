# =============================================================
# app.py — Moteur de recherche Flask
# Equipe : Sandrine (lead), Audrey, Destine, Alexandre
# Feature : F8 - Moteur de recherche
# Responsable : Alexandre
# Version corrigee pour elasticsearch-py 8.x
# =============================================================

from flask import Flask, request, jsonify
from elasticsearch import Elasticsearch
import os

app = Flask(__name__)

ES_HOST = os.getenv("ES_HOST", "http://localhost:9200")
ES_INDEX = "movies_clean"

es = Elasticsearch(ES_HOST)


# -----------------------------------------------------------
# ENDPOINT : /health
# -----------------------------------------------------------
@app.route("/health", methods=["GET"])
def health():
    try:
        if es.ping():
            count_resp = es.count(index=ES_INDEX)
            total = count_resp.body.get("count", 0)
            return jsonify({
                "status": "ok",
                "elasticsearch": "connected",
                "index": ES_INDEX,
                "total_movies": total
            }), 200
        else:
            return jsonify({
                "status": "error",
                "elasticsearch": "unreachable"
            }), 503
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 503


# -----------------------------------------------------------
# ENDPOINT : /search
# -----------------------------------------------------------
@app.route("/search", methods=["GET"])
def search():
    query    = request.args.get("q", "").strip()
    genre    = request.args.get("genre", "").strip()
    language = request.args.get("language", "").strip()
    year     = request.args.get("year", "").strip()
    size     = min(int(request.args.get("size", 10)), 50)
    from_idx = int(request.args.get("from", 0))

    if not query and not genre and not language and not year:
        return jsonify({
            "error": "Au moins un parametre requis : q, genre, language ou year"
        }), 400

    must_clauses   = []
    filter_clauses = []

    if query:
        must_clauses.append({
            "multi_match": {
                "query": query,
                "fields": ["title^3", "overview", "tagline"],
                "type": "best_fields",
                "fuzziness": "AUTO"
            }
        })

    if genre:
        filter_clauses.append({"term": {"genres": genre}})

    if language:
        filter_clauses.append({"term": {"original_language": language}})

    if year:
        try:
            y = int(year)
            filter_clauses.append({
                "range": {
                    "release_date": {
                        "gte": f"{y}-01-01",
                        "lte": f"{y}-12-31"
                    }
                }
            })
        except ValueError:
            return jsonify({"error": "L'annee doit etre un entier (ex: 2022)"}), 400

    if not must_clauses:
        must_clauses.append({"match_all": {}})

    es_query = {
        "bool": {
            "must": must_clauses,
            "filter": filter_clauses
        }
    }

    try:
        response = es.search(
            index=ES_INDEX,
            query=es_query,
            size=size,
            from_=from_idx,
            sort=["_score", {"popularity": {"order": "desc"}}],
            source_includes=[
                "id", "title", "overview", "genres",
                "original_language", "release_date",
                "vote_average", "vote_count", "popularity",
                "budget", "revenue", "runtime",
                "credits", "keywords", "poster_path"
            ]
        )

        body  = response.body
        hits  = body["hits"]["hits"]
        total = body["hits"]["total"]["value"]

        films = []
        for hit in hits:
            s = hit["_source"]
            poster = s.get("poster_path")
            films.append({
                "id":           s.get("id"),
                "title":        s.get("title"),
                "overview":     s.get("overview"),
                "genres":       s.get("genres", []),
                "language":     s.get("original_language"),
                "release_date": s.get("release_date"),
                "vote_average": s.get("vote_average"),
                "vote_count":   s.get("vote_count"),
                "popularity":   s.get("popularity"),
                "budget":       s.get("budget") if s.get("budget") not in [-1, "-1"] else None,
                "revenue":      s.get("revenue") if s.get("revenue") not in [-1, "-1"] else None,
                "runtime":      s.get("runtime") if s.get("runtime") not in [-1, "-1"] else None,
                "credits":      (s.get("credits") or [])[:5],
                "keywords":     (s.get("keywords") or [])[:10],
                "poster_url":   f"https://image.tmdb.org/t/p/w500{poster}" if poster else None,
                "score":        hit["_score"]})

        return jsonify({
            "query": {
                "q": query, "genre": genre,
                "language": language, "year": year,
                "size": size, "from": from_idx
            },
            "total": total,
            "results": films,
            "pagination": {
                "current_page": from_idx // size + 1,
                "total_pages":  (total + size - 1) // size,
                "has_next":     from_idx + size < total,
                "next_from":    from_idx + size if from_idx + size < total else None
            }
        }), 200

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            "error": "Erreur lors de la recherche",
            "message": str(e)
        }), 500


# -----------------------------------------------------------
# ENDPOINT : /movie/<id>
# -----------------------------------------------------------
@app.route("/movie/<int:movie_id>", methods=["GET"])
def get_movie(movie_id):
    try:
        response = es.get(index=ES_INDEX, id=movie_id)
        body = response.body
        return jsonify({
            "id":    movie_id,
            "found": body["found"],
            "film":  body["_source"] if body["found"] else None
        }), 200
    except Exception as e:
        return jsonify({
            "error":   f"Film {movie_id} non trouve",
            "message": str(e)
        }), 404


# -----------------------------------------------------------
# ENDPOINT : /genres
# -----------------------------------------------------------
@app.route("/genres", methods=["GET"])
def get_genres():
    try:
        response = es.search(
            index=ES_INDEX,
            size=0,
            aggs={"genres": {"terms": {"field": "genres", "size": 50}}}
        )
        buckets = response.body["aggregations"]["genres"]["buckets"]
        genres  = [{"genre": b["key"], "count": b["doc_count"]} for b in buckets]
        return jsonify({"total_genres": len(genres), "genres": genres}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# -----------------------------------------------------------
# LANCEMENT
# -----------------------------------------------------------
if __name__ == "__main__":
    print("=" * 50)
    print("  ELK Movies Search API")
    print("  Elasticsearch :", ES_HOST)
    print("  Index         :", ES_INDEX)
    print("=" * 50)
    print("  GET /health")
    print("  GET /search?q=avatar")
    print("  GET /search?q=space&genre=Science+Fiction")
    print("  GET /search?q=batman&language=en&year=2008")
    print("  GET /movie/19995")
    print("  GET /genres")
    print()
    app.run(host="0.0.0.0", port=5000, debug=True)
