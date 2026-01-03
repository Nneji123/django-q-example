# Django Q2 Task Queue API

A Django application demonstrating django-q2 task queue integration with REST API endpoints and Swagger documentation.

## Features

- **Django Q2 Integration**: Asynchronous task processing with worker cluster
- **REST API**: Clean class-based views with serializers using Django REST Framework
- **Swagger Documentation**: Interactive API documentation with drf-spectacular
- **Scheduled Tasks**: Support for recurring tasks (e.g., every 5 seconds)
- **Colorful Logging**: Beautiful colored logs using loguru
- **Docker Support**: Ready for containerized deployment

## Architecture

```
┌─────────────────┐
│  Django Server  │  ← Handles HTTP requests (API endpoints)
│  (runserver)    │     Returns immediately after enqueueing tasks
└────────┬────────┘
         │
         │ Enqueues tasks
         ▼
┌─────────────────┐
│   Task Queue    │  ← Database (stores pending tasks)
└────────┬────────┘
         │
         │ Workers pull tasks
         ▼
┌─────────────────┐
│  Q Cluster      │  ← Separate worker processes
│  (qcluster)     │     Execute tasks asynchronously
│  - Worker 1-4   │     Do NOT block the server
└─────────────────┘
```

## Quick Start

### Local Development

1. **Install dependencies:**
   ```bash
   uv sync
   ```

2. **Set up environment variables:**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and configure your settings (especially `SECRET_KEY` for production).

3. **Run migrations:**
   ```bash
   uv run python manage.py migrate
   ```

4. **Start server and cluster:**
   ```bash
   uv run python run.py
   ```

   This starts both the Django server and django-q2 cluster in a single process.

4. **Access the API:**
   - API Base: http://127.0.0.1:8000/api/
   - Swagger UI: http://127.0.0.1:8000/api/docs/
   - ReDoc: http://127.0.0.1:8000/api/redoc/
   - Admin: http://127.0.0.1:8000/admin/

### Docker

1. **Build and run:**
   ```bash
   docker-compose up --build
   ```

2. **Access the API:**
   - API Base: http://localhost:8000/api/
   - Swagger UI: http://localhost:8000/api/docs/

## API Endpoints

### Task Management

- `POST /api/task/` - Enqueue a task
  ```json
  {
    "message": "Hello from API!",
    "delay": 2
  }
  ```

- `GET /api/task/result/?task_id=<id>` - Get task result

### Scheduled Tasks

- `POST /api/scheduled-task/` - Create/update scheduled task (runs every 5 seconds)
- `GET /api/scheduled-task/` - Get scheduled task status
- `DELETE /api/scheduled-task/` - Delete scheduled task

## Configuration

### Django Q2 Settings

Configured in `backend/settings.py`:

```python
Q_CLUSTER = {
    'name': 'django-q',
    'workers': 4,
    'recycle': 500,
    'timeout': 60,
    'retry': 120,
    'queue_limit': 50,
    'bulk': 10,
    'orm': 'default',
}
```

### Auto-create Scheduled Task

Set in `backend/settings.py`:

```python
AUTO_CREATE_SCHEDULED_TASK = True  # Auto-create on startup
```

## How Tasks Work

### Asynchronous Execution

Tasks **do NOT block** the Django server:

1. When you call `async_task()`, the task is stored in the database queue
2. The API endpoint returns immediately with a task ID
3. Worker processes (qcluster) pull tasks from the queue
4. Tasks execute in separate processes, independent of the server

### Example

```python
# This returns immediately, doesn't wait for task completion
task_id = async_task(sample_task, "Hello", delay=10)

# Your API can continue handling other requests
# while the task runs in the background
```

## Development

### Running Tests

```bash
uv run python manage.py test
```

### Code Structure

```
.
├── backend/          # Django project settings
├── tasks/            # Tasks app
│   ├── tasks.py     # Task functions
│   ├── views.py     # API views
│   └── urls.py      # URL routing
├── run.py           # Main entry point (runs server + cluster)
├── Dockerfile       # Docker configuration
└── compose.yml      # Docker Compose configuration
```

## Deployment

### Render.com

1. Connect your repository
2. Set build command: `docker build -t django-q .`
3. Set start command: `docker run -p 8000:8000 django-q`
4. Or use Docker Compose: `docker-compose up`

### Environment Variables

The application uses `.env` file for configuration (via python-dotenv). Key variables:

- `SECRET_KEY` - Django secret key (required, change in production!)
- `DEBUG` - Enable/disable debug mode (True/False)
- `ALLOWED_HOSTS` - Comma-separated list of allowed hosts
- `AUTO_CREATE_SCHEDULED_TASK` - Auto-create scheduled task on startup (True/False)

Copy `.env.example` to `.env` and configure your settings:

```bash
cp .env.example .env
```

**Important**: Never commit `.env` to version control! It's already in `.gitignore`.

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

