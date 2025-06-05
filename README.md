# Event Management System

A modern event management system built with FastAPI, async SQLAlchemy, and PostgreSQL. This system allows you to create events, manage attendees, and handle timezone-aware scheduling.

## Features

- Create and manage events with timezone support
- Register attendees with duplicate prevention
- Paginated attendee lists
- Timezone-aware scheduling (IST by default)
- Input validation and error handling
- Async API endpoints
- OpenAPI documentation (Swagger UI)
- Comprehensive test suite

## Prerequisites

- Python 3.8 or higher
- PostgreSQL 12 or higher
- pip (Python package manager)

## Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/anujdarji2001/EventManagement.git
```

### 2. Create and Activate Virtual Environment
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a `.env` file in the root directory with the following content:
```env
DATABASE_URL=postgresql+asyncpg://<username>:<password>@localhost:5432/eventdb
```

### 5. Database Setup
```bash
# Initialize database migrations
alembic init alembic

# Edit alembic.ini and env.py to use app.models.Base and your DATABASE_URL
# Then run migrations
alembic revision --autogenerate -m "init"
alembic upgrade head
```

### 6. Start the Server
```bash
uvicorn app.main:app --reload
```

The server will start at `http://localhost:8000`

## Running Tests

The project includes a comprehensive test suite. To run the tests:

1. Make sure your virtual environment is activated
2. Ensure the server is running (tests connect to `http://localhost:8000`)
3. Run the tests:
```bash
pytest
```

For more detailed test output:
```bash
pytest -v
```

## API Documentation

Once the server is running, you can access:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## API Endpoints

### Events
- `POST /events` - Create a new event
- `GET /events` - List all events (with pagination)

### Attendees
- `POST /events/{event_id}/register` - Register an attendee
- `GET /events/{event_id}/attendees` - List attendees (paginated)

## Example Usage

### Create an Event
```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/events/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "name": "Friday Evening",
  "location": "Ahmedabad",
  "start_time": "2025-06-05T11:35:26.318+05:30",
  "end_time": "2025-06-05T14:35:26.318+05:30",
  "max_capacity": 2
}'
```

### Register an Attendee
```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/events/74/register' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "name": "User",
  "email": "user@example.com"
}'
```
