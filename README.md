# test_task_for_StarNAVI

This is a web application developed using FastAPI. It includes various endpoints for authentication, user management, post management, and comment management. The project is designed to be run in a Docker container and uses PostgreSQL as the database.

## Getting Started

These instructions will help you set up and run the project on your local machine for development and testing purposes.

### Prerequisites

- Python 3.11
- Docker

### Installation

```bash
1. Clone the repository:

git clone https://github.com/your-repo/test_task_for_StarNAVI.git
cd test_task_for_StarNAVI

2. Set up the environment:

Change the file example.env to .env in the root directory and enter your environment variables.

3. Build containers:

docker-compose build

4. Run Alembic migrations:

docker-compose run web poetry run alembic upgrade head

5. Start tests:

docker-compose run web poetry run pytest

6. Run project:

docker-compose up -d