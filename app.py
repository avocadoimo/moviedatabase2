from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_, desc, asc
from flask_paginate import get_page_parameter
from datetime import datetime
from datetime import datetime 
import os

app = Flask(__name__)

def parse_date(s):
    try:
        return datetime.strptime(s, "%Y/%m/%d")
    except:
        return datetime.min 

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///movie_new.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    movie_id = db.Column(db.String)
    title = db.Column(db.String)
    revenue = db.Column(db.Float)
    year = db.Column(db.Integer)
    release_date = db.Column(db.String)
    category = db.Column(db.String)
    distributor = db.Column(db.String)
    description = db.Column(db.Text)
    director = db.Column(db.String)
    author = db.Column(db.String)
    actor = db.Column(db.String)
    scriptwriter = db.Column(db.String)
    producer = db.Column(db.String)
    copyright = db.Column(db.String)

@app.route("/")
@app.route("/search")
def search():
    query = Movie.query

    year = request.args.get('year')
    title = request.args.get('title')
    distributor = request.args.get('distributor')
    min_revenue = request.args.get('min_revenue')
    max_revenue = request.args.get('max_revenue')
    director = request.args.get('director')
    actor = request.args.get('actor')
    scriptwriter = request.args.get('scriptwriter')
    producer = request.args.get('producer')
    category = request.args.get('category')
    order_by = request.args.get('order_by', 'revenue')
    sort = request.args.get('sort', 'desc')

    if year:
        query = query.filter(Movie.year == year)
    if title:
        query = query.filter(Movie.title.contains(title))
# 略称・正式名すべてを相互に参照できるマップを事前に構築
    groups = [
        ['WB', 'ワーナー', 'ワーナー・ブラザース映画'],
        ['SPE', 'ソニー・ピクチャーズエンタテインメント'],
        ['BV', 'WDS', 'ウォルト・ディズニー・ジャパン', 'ブエナビスタ', 'ディズニー']
    ]

    distributor_aliases = {}
    for group in groups:
        for term in group:
            distributor_aliases[term.upper()] = group

# distributor のフィルタ条件を展開
    if distributor:
        patterns = distributor_aliases.get(distributor.upper(), [distributor])
        conditions = []
        for pattern in patterns:
            conditions.extend([
                Movie.distributor == pattern,
                Movie.distributor.like(f"%、{pattern}、%"),
                Movie.distributor.like(f"{pattern}、%"),
                Movie.distributor.like(f"%、{pattern}"),
                Movie.distributor.like(f"%{pattern}%")
            ])
        query = query.filter(or_(*conditions))

    if category:
        query = query.filter(Movie.category == category)
    if min_revenue:
        query = query.filter(Movie.revenue >= float(min_revenue))
    if max_revenue:
        query = query.filter(Movie.revenue <= float(max_revenue))
    if director:
        query = query.filter(Movie.director.contains(director))
    if actor:
        query = query.filter(Movie.actor.contains(actor))
    if scriptwriter:
        query = query.filter(Movie.scriptwriter.contains(scriptwriter))
    if producer:
        query = query.filter(Movie.producer.contains(producer))

    movies = query.all()

    def parse_date(s):
        try:
            return datetime.strptime(s, "%Y/%m/%d")
        except:
            return datetime.min

    if movies:
        if order_by == 'release_date':
            movies.sort(key=lambda m: parse_date(m.release_date), reverse=(sort == 'desc'))
        elif hasattr(Movie, order_by):
            sample = getattr(movies[0], order_by, '')
            if isinstance(sample, (float, int)):
                movies.sort(key=lambda m: getattr(m, order_by) if getattr(m, order_by) is not None else 0, reverse=(sort == 'desc'))
            else:
                movies.sort(key=lambda m: getattr(m, order_by) or '', reverse=(sort == 'desc'))

    page = request.args.get(get_page_parameter(), type=int, default=1)
    per_page = 50
    start = (page - 1) * per_page
    end = start + per_page
    pagination_items = movies[start:end]

    total_pages = (len(movies) + per_page - 1) // per_page
    has_prev = page > 1
    has_next = page < total_pages

    args_no_page = request.args.to_dict()
    args_no_page.pop("page", None)

    return render_template('search.html',
        movies=pagination_items,
        pagination={
            'page': page,
            'pages': total_pages,
            'has_prev': has_prev,
            'has_next': has_next,
            'prev_num': page - 1,
            'next_num': page + 1
        },
        order_by=order_by,
        sort=sort,
        args_no_page=args_no_page
    )


@app.route("/movie/<int:movie_id>")
def movie_detail(movie_id):
    movie = Movie.query.filter_by(id=movie_id).first_or_404()
    return render_template("movie_detail.html", movie=movie)

@app.route("/table")
def table_view():
    query = Movie.query

    year = request.args.get('year')
    title = request.args.get('title')
    distributor = request.args.get('distributor')
    min_revenue = request.args.get('min_revenue')
    max_revenue = request.args.get('max_revenue')
    director = request.args.get('director')
    actor = request.args.get('actor')
    scriptwriter = request.args.get('scriptwriter')
    producer = request.args.get('producer')
    order_by = request.args.get('order_by', 'release_date')
    sort = request.args.get('sort', 'desc')

    if year:
        query = query.filter(Movie.year == year)
    if title:
        query = query.filter(Movie.title.contains(title))
    if distributor:
        query = query.filter(
            or_(
                Movie.distributor == distributor,
                Movie.distributor.like(f"%、{distributor}、%"),
                Movie.distributor.like(f"{distributor}、%"),
                Movie.distributor.like(f"%、{distributor}"),
                Movie.distributor.like(f"%{distributor}%")
            )
        )
    if min_revenue:
        query = query.filter(Movie.revenue >= float(min_revenue))
    if max_revenue:
        query = query.filter(Movie.revenue <= float(max_revenue))
    if director:
        query = query.filter(Movie.director.contains(director))
    if actor:
        query = query.filter(Movie.actor.contains(actor))
    if scriptwriter:
        query = query.filter(Movie.scriptwriter.contains(scriptwriter))
    if producer:
        query = query.filter(Movie.producer.contains(producer))

    # release_date も正しく並び替え（ここはそのままでもOK）
    if order_by == 'release_date':
        movies = query.all()
        movies.sort(key=lambda m: parse_date(m.release_date), reverse=(sort == 'desc'))
    elif hasattr(Movie, order_by):
        column = getattr(Movie, order_by)
        if sort == 'asc':
            query = query.order_by(asc(column))
        else:
            query = query.order_by(desc(column))
        movies = query.all()
    else:
        movies = query.all()

    return render_template("table_view.html", movies=movies, order_by=order_by, sort=sort)

if __name__ == "__main__":
    app.run(debug=True)
