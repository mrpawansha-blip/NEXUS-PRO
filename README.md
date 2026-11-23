# NEXUS-PRO — Smart Task Management System

NEXUS-PRO is a portfolio-ready task manager built with **Python, FastAPI, SQLAlchemy, SQLite, HTML, and CSS**. It includes a browser dashboard and a documented REST API.

## Features

- Create, view, update task status, and delete tasks
- Priorities: low, medium, high
- Statuses: pending, in progress, completed
- SQLite database storage through SQLAlchemy
- Input validation and clear HTTP error responses
- Application logging to console and `app.log`
- Interactive API documentation at `/docs`
- Basic automated API tests

## Project structure

```text
NEXUS-PRO/
├── app/
│   ├── main.py              # FastAPI routes and dashboard
│   ├── database.py          # SQLAlchemy engine/session
│   ├── models.py            # Task database model
│   ├── templates/index.html # Dashboard HTML
│   └── static/style.css     # Dashboard styling
├── tests/test_api.py        # API tests
├── requirements.txt
├── render.yaml
├── .gitignore
└── README.md
```

## Requirements

- Python 3.10 or newer
- pip
- Git (for GitHub upload)

## Run locally

1. Open a terminal in this project folder.
2. Create and activate a virtual environment:

   **Windows**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```

   **macOS/Linux**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Start the application:

   ```bash
   uvicorn app.main:app --reload
   ```

5. Open:
   - Dashboard: http://127.0.0.1:8000
   - API docs: http://127.0.0.1:8000/docs
   - Health check: http://127.0.0.1:8000/health

The SQLite database file `nexus.db` is created automatically at first startup.

## REST API

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/tasks` | List tasks |
| POST | `/api/tasks` | Create a task |
| PATCH | `/api/tasks/{task_id}` | Update task fields/status |
| DELETE | `/api/tasks/{task_id}` | Delete a task |
| GET | `/health` | Health check |

Example create request:

```json
{
  "title": "Finish capstone project",
  "description": "Test and document the application",
  "priority": "high"
}
```

## Database schema

Table: `tasks`

| Column | Type | Rules |
|---|---|---|
| id | Integer | Primary key |
| title | String(120) | Required |
| description | Text | Optional |
| priority | String(10) | low / medium / high |
| status | String(20) | pending / in_progress / completed |
| created_at | DateTime | UTC timestamp |

## Run tests

```bash
pytest -q
```

## Deployment

A starter Render configuration is included in `render.yaml`.

1. Push the project to a GitHub repository.
2. In Render, create a new **Web Service** and connect the repository.
3. Build command: `pip install -r requirements.txt`
4. Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Deploy, then verify `/health` and `/docs`.

**Persistence note:** the default SQLite database is suitable for local learning and testing. For a production deployment, attach a persistent disk or configure a managed PostgreSQL database using the `DATABASE_URL` environment variable. Do not rely on an ephemeral deployment filesystem for important data.

## Security and limitations

This learning project does not include user accounts or authentication. Do not store private or sensitive data in a public deployment. Add authentication, authorization, migrations, rate limiting, and production database backups before using it for real users.

## License

For educational and portfolio use.
