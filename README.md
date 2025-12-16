# Convergent

***Note: this repository is now archived. Please find this project in active development at https://github.com/choruslabs/chorus***

This is an open-source web application implementing a polis-like algorithm for mapping high-dimensional opinion spaces.

## Installation

### Web API

#### Local (without Docker)

The web API is written in [FastAPI](https://fastapi.tiangolo.com/), a web framework for Python. You need to install Python before running the API.

Installation for Windows (instructions are minimally changed for Linux):

```bash
cd server
python -m venv venv
venv/Scripts/activate # (in Linux, use source venv/bin/activate)
pip install -r requirements.txt
```

Add an environment file `.env` in the `server` directory in the same format as `sample.env`, but
replace:

- `DATABASE_URL` with the URL of your **Postgres** database (e.g., `postgresql://user:password@localhost/dbname`)
- `SECRET_KEY` with a random string (you can use `openssl rand -hex 32` to generate one)
- `ALLOWED_ORIGINS` with a comma-separated list of allowed origins (e.g., `http://localhost:5173` if you use the default Vite port)

To run the API (in auto-reload mode):

```bash
uvicorn convergent.main:app --reload
```

Go to `http://localhost:8000/docs` to check if it works: you should see a Swagger page.

#### Using Docker

To build & run locally via docker compose:

```bash
docker-compose build engine
docker-compose up --build
```

Or, to build the server image using Docker:

```bash
cd server
docker build -t convergent.server .
```

To run it on port 8000:

```bash
docker run -p 8000:8000 convergent.server
```

Go to `http://localhost:8000/docs` to check if it works: you should see a Swagger page.

### Frontend

The frontend requires [https://nodejs.org/en](https://nodejs.org/en) to run and is written in [Vite](https://vite.dev/).

Installation using Node:

```bash
cd client
npm install
```

To run the frontend (in development mode):

```bash
npm run dev
```

To run in storybook mode:

```bash
npm run storybook
```

