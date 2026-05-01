# =============================================================
# app.py — Moteur de recherche Flask AMELIORE
# Equipe : Sandrine (lead), Audrey, Destine, Alexandre
# Feature : F8 - Moteur de recherche
# Responsable : Alexandre
# Version 2.0 - Interface HTML + filtres ameliores + stats
# =============================================================

from flask import Flask, request, jsonify, render_template_string
from elasticsearch import Elasticsearch
import os

app = Flask(__name__)

ES_HOST = os.getenv("ES_HOST", "http://localhost:9200")
ES_INDEX = "movies_clean"
es = Elasticsearch(ES_HOST)

# -----------------------------------------------------------
# INTERFACE HTML — Formulaire de recherche visuel
# -----------------------------------------------------------
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ELK Movies Search</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: Arial, sans-serif; background: #f0f4f8; color: #333; }
        header { background: #1F4E79; color: white; padding: 20px 40px; }
        header h1 { font-size: 28px; }
        header p { font-size: 14px; opacity: 0.8; margin-top: 4px; }
        .container { max-width: 1100px; margin: 30px auto; padding: 0 20px; }
        .search-box { background: white; border-radius: 10px; padding: 25px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); margin-bottom: 20px; }
        .search-box h2 { color: #1F4E79; margin-bottom: 15px; font-size: 18px; }
        .form-grid { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 15px; margin-bottom: 15px; }
        .form-group { display: flex; flex-direction: column; }
        .form-group label { font-size: 13px; color: #666; margin-bottom: 5px; font-weight: bold; }
        .form-group input, .form-group select { padding: 10px; border: 1px solid #ddd; border-radius: 6px; font-size: 14px; }
        .form-row { display: flex; gap: 15px; align-items: flex-end; }
        .form-row .form-group { flex: 1; }
        .btn { padding: 10px 25px; border: none; border-radius: 6px; font-size: 14px; cursor: pointer; font-weight: bold; }
        .btn-primary { background: #1F4E79; color: white; }
        .btn-primary:hover { background: #2E75B6; }
        .btn-secondary { background: #eee; color: #333; }
        .stats-bar { display: flex; gap: 15px; margin-bottom: 20px; }
        .stat-card { background: white; border-radius: 8px; padding: 15px 20px; flex: 1; box-shadow: 0 2px 6px rgba(0,0,0,0.08); border-left: 4px solid #1F4E79; }
        .stat-card .number { font-size: 24px; font-weight: bold; color: #1F4E79; }
        .stat-card .label { font-size: 12px; color: #888; margin-top: 3px; }
        .results-info { color: #666; font-size: 14px; margin-bottom: 15px; }
        .results-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; }
        .movie-card { background: white; border-radius: 10px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.1); transition: transform 0.2s; }
        .movie-card:hover { transform: translateY(-3px); box-shadow: 0 6px 16px rgba(0,0,0,0.15); }
        .movie-poster { width: 100%; height: 180px; object-fit: cover; background: #eee; }
        .movie-poster-placeholder { width: 100%; height: 180px; background: linear-gradient(135deg, #1F4E79, #2E75B6); display: flex; align-items: center; justify-content: center; color: white; font-size: 40px; }
        .movie-info { padding: 15px; }
        .movie-title { font-size: 16px; font-weight: bold; color: #1F4E79; margin-bottom: 6px; }
        .movie-meta { display: flex; gap: 10px; margin-bottom: 8px; flex-wrap: wrap; }
        .badge { background: #EEF4FF; color: #1F4E79; padding: 2px 8px; border-radius: 12px; font-size: 11px; }
        .badge-year { background: #FFF3CD; color: #856404; }
        .badge-lang { background: #D4EDDA; color: #155724; }
        .rating { display: flex; align-items: center; gap: 5px; }
        .rating .star { color: #FFC107; font-size: 14px; }
        .rating .score { font-weight: bold; font-size: 15px; }
        .rating .votes { color: #999; font-size: 11px; }
        .movie-overview { font-size: 12px; color: #666; line-height: 1.5; margin-top: 8px; max-height: 60px; overflow: hidden; }
        .movie-budget { font-size: 11px; color: #888; margin-top: 6px; }
        .pagination { display: flex; justify-content: center; gap: 10px; margin-top: 30px; }
        .page-btn { padding: 8px 16px; border: 1px solid #ddd; background: white; border-radius: 6px; cursor: pointer; font-size: 14px; }
        .page-btn.active { background: #1F4E79; color: white; border-color: #1F4E79; }
        .page-btn:hover { background: #EEF4FF; }
        .no-results { text-align: center; padding: 60px; color: #999; }
        .no-results .icon { font-size: 60px; margin-bottom: 15px; }
        .loading { text-align: center; padding: 40px; color: #666; }
    </style>
</head>
<body>
    <header>
        <h1>🎬 ELK Movies Search</h1>
        <p>Moteur de recherche connecté à Elasticsearch — {{ total_movies }} films disponibles</p>
    </header>

    <div class="container">
        <!-- Formulaire de recherche -->
        <div class="search-box">
            <h2>Rechercher un film</h2>
            <form method="GET" action="/">
                <div class="form-grid">
                    <div class="form-group" style="grid-column: span 3;">
                        <label>Recherche (titre, synopsis, slogan)</label>
                        <input type="text" name="q" value="{{ query.q }}" placeholder="Ex: avatar, dark knight, space..." />
                    </div>
                    <div class="form-group">
                        <label>Genre</label>
                        <select name="genre">
                            <option value="">Tous les genres</option>
                            {% for g in genres %}
                            <option value="{{ g }}" {% if query.genre == g %}selected{% endif %}>{{ g }}</option>
                            {% endfor %}
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Langue originale</label>
                        <select name="language">
                            <option value="">Toutes les langues</option>
                            <option value="en" {% if query.language == 'en' %}selected{% endif %}>Anglais (en)</option>
                            <option value="fr" {% if query.language == 'fr' %}selected{% endif %}>Francais (fr)</option>
                            <option value="ja" {% if query.language == 'ja' %}selected{% endif %}>Japonais (ja)</option>
                            <option value="ko" {% if query.language == 'ko' %}selected{% endif %}>Coreen (ko)</option>
                            <option value="es" {% if query.language == 'es' %}selected{% endif %}>Espagnol (es)</option>
                            <option value="de" {% if query.language == 'de' %}selected{% endif %}>Allemand (de)</option>
                            <option value="it" {% if query.language == 'it' %}selected{% endif %}>Italien (it)</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Annee de sortie</label>
                        <input type="number" name="year" value="{{ query.year }}" placeholder="Ex: 2022" min="1888" max="2026" />
                    </div>
                </div>
                <div class="form-row">
                    <div class="form-group">
                        <label>Trier par</label>
                        <select name="sort">
                            <option value="score" {% if query.sort == 'score' %}selected{% endif %}>Pertinence</option>
                            <option value="popularity" {% if query.sort == 'popularity' %}selected{% endif %}>Popularite</option>
                            <option value="vote_average" {% if query.sort == 'vote_average' %}selected{% endif %}>Note</option>
                            <option value="release_date" {% if query.sort == 'release_date' %}selected{% endif %}>Date de sortie</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Note minimale</label>
                        <select name="min_rating">
                            <option value="">Toutes les notes</option>
                            <option value="5" {% if query.min_rating == '5' %}selected{% endif %}>5+</option>
                            <option value="6" {% if query.min_rating == '6' %}selected{% endif %}>6+</option>
                            <option value="7" {% if query.min_rating == '7' %}selected{% endif %}>7+</option>
                            <option value="8" {% if query.min_rating == '8' %}selected{% endif %}>8+</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Votes minimum</label>
                        <select name="min_votes">
                            <option value="">Tous</option>
                            <option value="100" {% if query.min_votes == '100' %}selected{% endif %}>100+</option>
                            <option value="500" {% if query.min_votes == '500' %}selected{% endif %}>500+</option>
                            <option value="1000" {% if query.min_votes == '1000' %}selected{% endif %}>1 000+</option>
                            <option value="5000" {% if query.min_votes == '5000' %}selected{% endif %}>5 000+</option>
                        </select>
                    </div>
                    <button type="submit" class="btn btn-primary">🔍 Rechercher</button>
                    <a href="/" class="btn btn-secondary">Reinitialiser</a>
                </div>
            </form>
        </div>

        <!-- Resultats -->
        {% if results is not none %}
            <div class="results-info">
                {% if total > 0 %}
                    <strong>{{ total }}</strong> film(s) trouve(s)
                    {% if query.q %} pour "<strong>{{ query.q }}</strong>"{% endif %}
                    {% if query.genre %} dans le genre <strong>{{ query.genre }}</strong>{% endif %}
                    {% if query.year %} en <strong>{{ query.year }}</strong>{% endif %}
                {% endif %}
            </div>

            {% if results %}
                <div class="results-grid">
                    {% for film in results %}
                    <div class="movie-card">
                        {% if film.poster_url %}
                        <img src="{{ film.poster_url }}" alt="{{ film.title }}" class="movie-poster" onerror="this.style.display='none';this.nextElementSibling.style.display='flex';">
                        <div class="movie-poster-placeholder" style="display:none;">🎬</div>
                        {% else %}
                        <div class="movie-poster-placeholder">🎬</div>
                        {% endif %}
                        <div class="movie-info">
                            <div class="movie-title">{{ film.title }}</div>
                            <div class="movie-meta">
                                {% if film.release_date %}
                                <span class="badge badge-year">{{ film.release_date[:4] }}</span>
                                {% endif %}
                                {% if film.language %}
                                <span class="badge badge-lang">{{ film.language }}</span>
                                {% endif %}
                                {% for genre in (film.genres or [])[:2] %}
                                <span class="badge">{{ genre }}</span>
                                {% endfor %}
                            </div>
                            {% if film.vote_average %}
                            <div class="rating">
                                <span class="star">★</span>
                                <span class="score">{{ "%.1f"|format(film.vote_average) }}</span>
                                <span class="votes">({{ film.vote_count }} votes)</span>
                            </div>
                            {% endif %}
                            {% if film.overview and film.overview != 'N/A' %}
                            <div class="movie-overview">{{ film.overview }}</div>
                            {% endif %}
                            {% if film.budget and film.budget > 0 %}
                            <div class="movie-budget">Budget : {{ "${:,.0f}".format(film.budget) }}</div>
                            {% endif %}
                        </div>
                    </div>
                    {% endfor %}
                </div>

                <!-- Pagination -->
                {% if total_pages > 1 %}
                <div class="pagination">
                    {% if current_page > 1 %}
                    <a href="?{{ pagination_params }}&page={{ current_page - 1 }}" class="page-btn">← Precedent</a>
                    {% endif %}
                    <span class="page-btn active">Page {{ current_page }} / {{ total_pages }}</span>
                    {% if current_page < total_pages %}
                    <a href="?{{ pagination_params }}&page={{ current_page + 1 }}" class="page-btn">Suivant →</a>
                    {% endif %}
                </div>
                {% endif %}
            {% else %}
                <div class="no-results">
                    <div class="icon">🎬</div>
                    <p>Aucun film trouve pour ces criteres.</p>
                    <p style="margin-top:10px; font-size:13px;">Essayez d'elargir votre recherche.</p>
                </div>
            {% endif %}
        {% endif %}
    </div>
</body>
</html>
"""

def format_pagination_params(query):
    params = []
    for k, v in query.items():
        if v and k != 'page':
            params.append(f"{k}={v}")
    return "&".join(params)

def do_search(query, genre, language, year, sort_by, min_rating, min_votes, page, size=12):
    must_clauses = []
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
            filter_clauses.append({"range": {"release_date": {"gte": f"{y}-01-01", "lte": f"{y}-12-31"}}})
        except ValueError:
            pass
    if min_rating:
        try:
            filter_clauses.append({"range": {"vote_average": {"gte": float(min_rating)}}})
        except ValueError:
            pass
    if min_votes:
        try:
            filter_clauses.append({"range": {"vote_count": {"gte": int(min_votes)}}})
        except ValueError:
            pass

    if not must_clauses:
        must_clauses.append({"match_all": {}})

    es_query = {"bool": {"must": must_clauses, "filter": filter_clauses}}

    sort_options = {
        "score": ["_score", {"popularity": {"order": "desc"}}],
        "popularity": [{"popularity": {"order": "desc"}}],
        "vote_average": [{"vote_average": {"order": "desc"}}, {"vote_count": {"order": "desc"}}],
        "release_date": [{"release_date": {"order": "desc"}}]
    }
    sort = sort_options.get(sort_by, ["_score", {"popularity": {"order": "desc"}}])

    from_idx = (page - 1) * size
    response = es.search(
        index=ES_INDEX,
        query=es_query,
        size=size,
        from_=from_idx,
        sort=sort,
        source_includes=["id", "title", "overview", "genres", "original_language",
                         "release_date", "vote_average", "vote_count", "popularity",
                         "budget", "revenue", "runtime", "poster_path"]
    )
    body = response.body
    hits = body["hits"]["hits"]
    total = body["hits"]["total"]["value"]

    films = []
    for hit in hits:
        s = hit["_source"]
        poster = s.get("poster_path")
        budget = s.get("budget")
        films.append({
            "id": s.get("id"),
            "title": s.get("title"),
            "overview": s.get("overview"),
            "genres": s.get("genres") or [],
            "language": s.get("original_language"),
            "release_date": s.get("release_date"),
            "vote_average": s.get("vote_average"),
            "vote_count": s.get("vote_count"),
            "popularity": s.get("popularity"),
            "budget": budget if budget not in [-1, "-1"] else None,
            "poster_url": f"https://image.tmdb.org/t/p/w500{poster}" if poster else None,
            "score": hit["_score"]
        })

    return films, total


# -----------------------------------------------------------
# ENDPOINT : / (Interface HTML)
# -----------------------------------------------------------
@app.route("/", methods=["GET"])
def index():
    query = request.args.get("q", "").strip()
    genre = request.args.get("genre", "").strip()
    language = request.args.get("language", "").strip()
    year = request.args.get("year", "").strip()
    sort_by = request.args.get("sort", "score").strip()
    min_rating = request.args.get("min_rating", "").strip()
    min_votes = request.args.get("min_votes", "").strip()
    page = max(1, int(request.args.get("page", 1)))

    # Recuperer les genres disponibles
    genres_resp = es.search(index=ES_INDEX, size=0, aggs={"genres": {"terms": {"field": "genres", "size": 30}}})
    genres = [b["key"] for b in genres_resp.body["aggregations"]["genres"]["buckets"]]

    # Nombre total de films
    count_resp = es.count(index=ES_INDEX)
    total_movies = count_resp.body.get("count", 0)

    results = None
    total = 0
    total_pages = 0
    current_query = {"q": query, "genre": genre, "language": language, "year": year, "sort": sort_by, "min_rating": min_rating, "min_votes": min_votes}

    if any([query, genre, language, year, min_rating, min_votes]):
        results, total = do_search(query, genre, language, year, sort_by, min_rating, min_votes, page)
        total_pages = (total + 11) // 12

    pagination_params = format_pagination_params(current_query)

    return render_template_string(
        HTML_TEMPLATE,
        results=results,
        total=total,
        total_pages=total_pages,
        current_page=page,
        query=current_query,
        genres=genres,
        total_movies=f"{total_movies:,}",
        pagination_params=pagination_params
    )


# -----------------------------------------------------------
# ENDPOINT : /health
# -----------------------------------------------------------
@app.route("/health", methods=["GET"])
def health():
    try:
        if es.ping():
            count_resp = es.count(index=ES_INDEX)
            return jsonify({
                "status": "ok",
                "elasticsearch": "connected",
                "index": ES_INDEX,
                "total_movies": count_resp.body.get("count", 0)
            }), 200
        return jsonify({"status": "error", "elasticsearch": "unreachable"}), 503
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 503


# -----------------------------------------------------------
# ENDPOINT : /search (API JSON)
# -----------------------------------------------------------
@app.route("/search", methods=["GET"])
def search():
    query = request.args.get("q", "").strip()
    genre = request.args.get("genre", "").strip()
    language = request.args.get("language", "").strip()
    year = request.args.get("year", "").strip()
    sort_by = request.args.get("sort", "score").strip()
    min_rating = request.args.get("min_rating", "").strip()
    min_votes = request.args.get("min_votes", "").strip()
    size = min(int(request.args.get("size", 10)), 50)
    page = max(1, int(request.args.get("page", 1)))

    if not any([query, genre, language, year, min_rating, min_votes]):
        return jsonify({"error": "Au moins un parametre requis"}), 400

    try:
        films, total = do_search(query, genre, language, year, sort_by, min_rating, min_votes, page, size)
        total_pages = (total + size - 1) // size
        return jsonify({
            "query": {"q": query, "genre": genre, "language": language, "year": year, "sort": sort_by, "min_rating": min_rating, "min_votes": min_votes},
            "total": total,
            "results": films,
            "pagination": {"current_page": page, "total_pages": total_pages, "has_next": page < total_pages}
        }), 200
    except Exception as e:
        import traceback; traceback.print_exc()
        return jsonify({"error": "Erreur recherche", "message": str(e)}), 500


# -----------------------------------------------------------
# ENDPOINT : /movie/<id>
# -----------------------------------------------------------
@app.route("/movie/<int:movie_id>", methods=["GET"])
def get_movie(movie_id):
    try:
        response = es.get(index=ES_INDEX, id=movie_id)
        body = response.body
        return jsonify({"id": movie_id, "found": body["found"], "film": body["_source"] if body["found"] else None}), 200
    except Exception as e:
        return jsonify({"error": f"Film {movie_id} non trouve", "message": str(e)}), 404


# -----------------------------------------------------------
# ENDPOINT : /genres
# -----------------------------------------------------------
@app.route("/genres", methods=["GET"])
def get_genres():
    try:
        response = es.search(index=ES_INDEX, size=0, aggs={"genres": {"terms": {"field": "genres", "size": 50}}})
        buckets = response.body["aggregations"]["genres"]["buckets"]
        return jsonify({"total_genres": len(buckets), "genres": [{"genre": b["key"], "count": b["doc_count"]} for b in buckets]}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# -----------------------------------------------------------
# ENDPOINT : /stats
# -----------------------------------------------------------
@app.route("/stats", methods=["GET"])
def stats():
    try:
        response = es.search(
            index=ES_INDEX, size=0,
            aggs={
                "total": {"value_count": {"field": "id"}},
                "note_moyenne": {"avg": {"field": "vote_average"}},
                "top_genres": {"terms": {"field": "genres", "size": 5}},
                "top_langues": {"terms": {"field": "original_language", "size": 5}},
                "films_par_annee": {"date_histogram": {"field": "release_date", "calendar_interval": "year", "format": "yyyy", "min_doc_count": 100}},
                "budget_stats": {"stats": {"field": "budget"}},
                "runtime_stats": {"avg": {"field": "runtime"}}
            }
        )
        aggs = response.body["aggregations"]
        return jsonify({
            "total_films": aggs["total"]["value"],
            "note_moyenne": round(aggs["note_moyenne"]["value"] or 0, 2),
            "runtime_moyen_minutes": round(aggs["runtime_stats"]["value"] or 0),
            "top_5_genres": [{"genre": b["key"], "count": b["doc_count"]} for b in aggs["top_genres"]["buckets"]],
            "top_5_langues": [{"langue": b["key"], "count": b["doc_count"]} for b in aggs["top_langues"]["buckets"]],
            "production_par_annee": [{"annee": b["key_as_string"], "count": b["doc_count"]} for b in aggs["films_par_annee"]["buckets"][-10:]]
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# -----------------------------------------------------------
# LANCEMENT
# -----------------------------------------------------------
if __name__ == "__main__":
    print("=" * 55)
    print("  ELK Movies Search API v2.0")
    print("  Elasticsearch :", ES_HOST)
    print("  Index         :", ES_INDEX)
    print("=" * 55)
    print("  Interface HTML : http://localhost:5000")
    print("  GET /health")
    print("  GET /search?q=avatar&genre=Action&min_rating=7")
    print("  GET /movie/19995")
    print("  GET /genres")
    print("  GET /stats")
    print()
    app.run(host="0.0.0.0", port=5000, debug=True)
