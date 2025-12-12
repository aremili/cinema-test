import random
import string

import httpx
from datetime import datetime
from django.conf import settings
from django.core.management.base import BaseCommand
from decouple import config

from movies.models import Author, Movie, Source


class Command(BaseCommand):
    help = "Import movies and directors from TMDB"

    TMDB_BASE_URL = "https://api.themoviedb.org/3"

    def __init__(self):
        super().__init__()
        self.api_key = config("TMDB_API_KEY")

    def add_arguments(self, parser):
        parser.add_argument(
            "--count",
            type=int,
            default=50,
            help="Number of movies to import (default: 50)",
        )

    def handle(self, *args, **options):
        count = options["count"]
        self.stdout.write(f"Importing {count} movies from TMDB...")

        movies_imported = 0
        authors_imported = 0
        page = 1

        with httpx.Client(timeout=30) as client:
            while movies_imported < count:
                response = client.get(
                    f"{self.TMDB_BASE_URL}/trending/movie/week",
                    params={"api_key": self.api_key, "page": page},
                )
                response.raise_for_status()
                data = response.json()

                for movie_data in data["results"]:
                    if movies_imported >= count:
                        break

                    # skip if movie already exists
                    tmdb_id = movie_data["id"]
                    if Movie.objects.filter(tmdb_id=tmdb_id).exists():
                        self.stdout.write(f"  -> Skipping movie: {movie_data['title']} (already exists)")
                        continue

                    # Create movie
                    movie = self._create_movie(movie_data)
                    movies_imported += 1
                    self.stdout.write(self.style.SUCCESS(f"  -> Imported movie: {movie.title}"))

                    # Fetch and create directors
                    directors = self._fetch_directors(client, tmdb_id)
                    for director_data in directors:
                        author, created = self._get_or_create_author(client, director_data)
                        movie.authors.add(author)
                        if created:
                            authors_imported += 1
                            self.stdout.write(self.style.SUCCESS(f"  -> Imported director: {author.username}"))

                page += 1
                if page > data["total_pages"]:
                    self.stdout.write(self.style.WARNING(f"\nNo more pages to import. Imported {movies_imported} movies and {authors_imported} new directors."))
                    break

        self.stdout.write(self.style.SUCCESS(
            f"\nDone! Imported {movies_imported} movies and {authors_imported} new directors."
        ))

    def _create_movie(self, data):
        release_date = None
        if data.get("release_date"):
            try:
                release_date = datetime.strptime(data["release_date"], "%Y-%m-%d").date()
            except ValueError:
                pass

        return Movie.objects.create(
            tmdb_id=data["id"],
            title=data["title"],
            overview=data.get("overview", ""),
            release_date=release_date,
            original_language=data.get("original_language", "en"),
            adult=data.get("adult", False),
            popularity=data.get("popularity"),
            vote_average=data.get("vote_average"),
            vote_count=data.get("vote_count"),
            source=Source.TMDB,
        )

    def _fetch_directors(self, client, movie_id):
        response = client.get(
            f"{self.TMDB_BASE_URL}/movie/{movie_id}/credits",
            params={"api_key": self.api_key},
        )
        response.raise_for_status()
        data = response.json()

        directors = [
            person for person in data.get("crew", [])
            if person.get("job") == "Director"
        ]
        return directors

    def _get_or_create_author(self, client, director_data):
        tmdb_id = director_data["id"]

        # check if author already exist
        if existing := Author.objects.filter(tmdb_id=tmdb_id).first():
            return existing, False

        # get full person details
        response = client.get(
            f"{self.TMDB_BASE_URL}/person/{tmdb_id}",
            params={"api_key": self.api_key},
        )
        response.raise_for_status()
        person = response.json()

        birthdate = None
        if person.get("birthday"):
            try:
                birthdate = datetime.strptime(person["birthday"], "%Y-%m-%d").date()
            except ValueError:
                pass

        # Create author
        name = person.get("name", "Unknown")
        username = self._generate_username(name)

        author = Author.objects.create(
            tmdb_id=tmdb_id,
            username=username,
            first_name=name.split()[0] if name else "",
            last_name=" ".join(name.split()[1:]) if len(name.split()) > 1 else "",
            biography=person.get("biography", ""),
            birthdate=birthdate,
            source=Source.TMDB,
        )
        return author, True

    def _generate_username(self, name):
        """Generate username"""
        base = name.lower().replace(" ", "_").replace("-", "_")
        random_suffix = "".join(random.choices(string.ascii_lowercase + string.digits, k=5))
        return f"{base}_{random_suffix}"
