# Cinema API

Cinema API for managing movies, authors, and ratings.

## Requirements

- Docker & Docker Compose
- [just](https://github.com/casey/just) - to simplify commands

## Environment Variables

Create a `.env` file from env.example:

```bash
SECRET_KEY='your-secret-key'
DEBUG=True
TMDB_API_KEY=your-tmdb-api-key
```

## To run the API

```bash
# Start containers
just up

# Run migrations
just migrate

# Create admin user
just createsuperuser

# to import movies from TMDB (50 by default )
just import-tmdb
```

## Commands

Run `just` to see all available commands:
(Without `just`, see the `justfile` for alternative docker commands.)

| Command | Description |
|---------|-------------|
| `just up` | Start containers |
| `just build` | Rebuild and start |
| `just down` | Stop containers |
| `just logs` | View API logs |
| `just migrate` | Run migrations |
| `just makemigrations` | Create migrations |
| `just test` | Run tests |
| `just schemathesis` | API schema tests for edge cases|
| `just shell` | Django shell |
| `just import-tmdb` | Import TMDB movies |
| `just lint` | Lint code |
| `just format` | Format code |


## Authentication 

To use protected endpoints:

```bash
# 1. Register a new user
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"username": "user", "email": "user@example.com", "password": "password123"}'

# 2. Get access token
curl -X POST http://localhost:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "user", "password": "password123"}'

# 3. Use token in requests
curl http://localhost:8000/api/movies/favorites/ \
  -H "Authorization: Bearer <access_token>"
```

### Protected Endpoints

All write endpoints require authentication:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/authors/` | POST | Create author |
| `/api/authors/{id}/` | PUT/PATCH | Update author |
| `/api/authors/{id}/` | DELETE | Delete author |
| `/api/authors/{id}/rate/` | POST | Rate an author by spectator only |
| `/api/movies/{id}/` | PUT/PATCH | Update movie |
| `/api/movies/{id}/rate/` | POST | Rate a movie by spectator only |
| `/api/movies/{id}/favorite/` | POST | Add to favorites by spectator only |
| `/api/movies/{id}/favorite/` | DELETE | Remove from favorites by spectator only |
| `/api/movies/favorites/` | GET | List favorites by spectator only |


## API Docs

- Swagger UI: http://localhost:8000/api/docs/
- ReDoc: http://localhost:8000/api/redoc/
- Admin: http://localhost:8000/admin/