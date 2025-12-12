# Commands for Cinema API

# show available commands
default:
    @just --list

# Start development server
up:
    docker compose up -d

# Start with rebuild
build:
    docker compose up -d --build

# Stop all containers
down:
    docker compose down

# View logs
logs:
    docker compose logs -f api

# run migrations
migrate:
    docker compose exec api uv run python manage.py migrate

# make migrations
makemigrations:
    docker compose exec api uv run python manage.py makemigrations

# create superuser
createsuperuser:
    docker compose exec api uv run python manage.py createsuperuser

# Run tests
test *args:
    docker compose exec api uv run pytest {{args}}

# Run schemathesis
schemathesis:
    docker compose exec api uv run schemathesis run http://localhost:8000/api/schema/

# Open Django shell
shell:
    docker compose exec api uv run python manage.py shell_plus

# Import TMDB movies
import-tmdb count="50":
    docker compose exec api uv run python manage.py import_tmdb --count {{count}}

# Lint and format
lint:
    uv run ruff check .

format:
    uv run ruff format .
