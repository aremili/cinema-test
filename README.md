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


## API Docs

- Swagger UI: http://localhost:8000/api/docs/
- ReDoc: http://localhost:8000/api/redoc/
- Admin: http://localhost:8000/admin/
