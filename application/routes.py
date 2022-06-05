from flask import current_app as app, request
from application import models, schema
from application.models import db
from flask_restx import Api, Resource, Namespace

api: Api = app.config['api']
movies_ns: Namespace = api.namespace('movies')
directors_ns: Namespace = api.namespace('directors')
genres_ns: Namespace = api.namespace('genres')

movie_schema = schema.Movie()
movies_schema = schema.Movie(many=True)

director_schema = schema.Director()
directors_schema = schema.Director(many=True)

genre_schema = schema.Genre()
genres_schema = schema.Genre(many=True)


@movies_ns.route('/')
class MoviesView(Resource):
    def get(self):
        movies = db.session.query(models.Movie)
        args = request.args
        director_id = args.get('director_id')
        if director_id is not None:
            movies = movies.filter(models.Movie.director_id == director_id)

        genre_id = args.get('genre_id')
        if genre_id is not None:
            movies = movies.filter(models.Movie.genre_id == genre_id)

        all_movies = movies.all()
        return movies_schema.dump(all_movies), 200

    def post(self):
        req_json = request.json
        new_movie = models.Movie(**req_json)
        with db.session.begin():
            db.session.add(new_movie)
            db.session.commit()
        return "", 201


@movies_ns.route('/<int:m_id>')
class MovieView(Resource):
    @movies_ns.response(200, description="Возвращает фильм по ID")
    def get(self, m_id: int):
        try:
            movie = models.Movie.query.get(m_id)
            return movie_schema.dump(movie), 200
        except Exception:
            return "Failed to find", 404

    def put(self, m_id):
        movie = models.Movie.get(m_id)
        req_json = request.json
        movie.id = req_json.get("id")
        movie.title = req_json.get("title")
        movie.description = req_json.get("description")
        movie.trailer = req_json.get("trailer")
        movie.year = req_json.get("year")
        movie.rating = req_json.get("rating")
        db.session.add(movie)
        db.session.commit()
        return "", 204

    def delete(self, m_id: int):
        db.session.query(models.Movie).filter(models.Movie.id == m_id).delete()
        db.session.commit()
        return "", 200


@genres_ns.route('/')
class GenresView(Resource):
    def get(self):
        genres = db.session.query(models.Genre).all()
        return genres_schema.dump(genres), 200


@genres_ns.route('/<int:genre_id>')
class GenreView(Resource):
    def get(self, genre_id: int):
        genre = db.session.query(models.Genre).filter(models.Genre.genre_id == genre_id).first()
        return genre_schema.dump(genre), 200


@directors_ns.route('/')
class DirectorsView(Resource):
    def get(self):
        directors = db.session.query(models.Director).all()
        return director_schema.dump(directors), 200


@directors_ns.route('/<int:director_id>')
class DirectorView(Resource):
    def get(self, director_id: int):
        director = db.session.query(models.Director).filter(models.Director.id == director_id).first()
        return director_schema.dump(director), 200
