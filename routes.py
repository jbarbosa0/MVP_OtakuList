from flask import render_template, jsonify
from main import app
from anilist_api import (
    get_popular_animes,
    get_trending_animes,
    get_seasonal_animes,
    get_all_animes
)

@app.route('/')
def homepage():
    populares = get_popular_animes()
    print("Populares:", populares)  # 👈 Teste
    trends = get_trending_animes()
    temporada = get_seasonal_animes()
    return render_template(
        'homepage.html',
        populares=populares,
        trends=trends,
        temporada=temporada
    )

@app.route('/animes')
def all_animes():
    animes = get_all_animes()
    return render_template('animes.html', animes=animes)