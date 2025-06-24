# Share Code

Share Code is a collaborative code-sharing platform built with FastAPI, supporting real-time project collaboration, user authentication, and granular access control. It allows users to create projects, manage files, and collaborate with others in real time via websockets.

## Features

- **User Authentication**: Register, login, and manage user profiles securely.
- **Project Management**: Create, update, and delete projects. Assign access rights to collaborators.
- **File Management**: Add, edit, rename, and delete files within projects.
- **Access Control**: Grant "view" or "full access" permissions to users on a per-project basis.
- **Real-Time Collaboration**: Work together on projects using websockets for instant updates.
- **RESTful API**: Well-structured API endpoints for all major operations.
- **Admin Panel**: (Optional, commented in code) SQLAdmin integration for managing data models.
- **Static File Serving**: Serve CSS, JS, and other static assets.

## Tech Stack

- **Backend**: FastAPI, SQLModel, SQLAlchemy, Alembic
- **Database**: PostgreSQL (via asyncpg)
- **Authentication**: JWT-based
- **Real-Time**: Websockets (FastAPI + custom ConnectionManager)
- **Frontend**: Jinja2 templates, static assets (CSS/JS)
- **Admin**: SQLAdmin (optional)
- **Other**: Docker support (if you add Dockerfile), dotenv for config

## Getting Started

### Prerequisites

- Python 3.9+
- PostgreSQL database

### Installation

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd sharecode
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   - Create a `.env` file in the root directory.
   - Add your database URL and secret key:
     ```
     DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/sharecode
     SECRET_KEY=your_secret_key
     ```

4. **Run database migrations:**
   ```bash
   alembic upgrade head
   ```

5. **Start the server:**
   ```bash
   uvicorn main:app --reload
   ```

6. **Access the app:**
   - API: [http://localhost:8000/docs](http://localhost:8000/docs)
   - Web: [http://localhost:8000/](http://localhost:8000/)

## Usage

- **Register/Login**: Use `/api/register` and `/api/token` endpoints.
- **Projects**: Create and manage projects via `/api/project`.
- **Files**: Manage files within projects.
- **Websockets**: Connect to `/ws/join-project/{project_id}?token=...` for real-time collaboration.
- **Admin Panel**: (Optional) Uncomment the SQLAdmin code in `main.py` to enable.

## Project Structure

```
sharecode/
  apps/
    auth_app/         # Authentication logic and routes
    file_app/         # File management logic and routes
    project_app/      # Project management logic and routes
    _websocket_app/   # Websocket endpoints and utilities
  models/             # SQLModel data models
  static/             # Static assets (CSS, JS)
  templates/          # Jinja2 HTML templates
  main.py             # FastAPI entrypoint
  db.py               # Database session and engine
  utils/              # Utility modules (e.g., ConnectionManager)
  requirements.txt    # Python dependencies
  alembic.ini         # Alembic config for migrations
```

## API Overview

- **Authentication**
  - `POST /api/register` — Register a new user
  - `POST /api/token` — Obtain JWT token
  - `GET /api/users/me` — Get current user info

- **Projects**
  - `POST /api/project` — Create a project
  - `GET /api/project` — List projects
  - `GET /api/project/{project_id}` — Project details
  - `PUT /api/project/{project_id}` — Update project
  - `DELETE /api/project/{project_id}` — Delete project

- **Project Access**
  - `POST /api/project/{project_id}/access` — Grant access
  - `PUT /api/project/{project_id}/access` — Update access
  - `DELETE /api/project/{project_id}/access/{access_id}` — Remove access

- **Websockets**
  - `GET /ws/join-project/{project_id}?token=...` — Real-time collaboration

## Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.

## License

[MIT](LICENSE)