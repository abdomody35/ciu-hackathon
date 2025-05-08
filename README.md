# ciu-hackathon

## Set up the PostgreSQL database:

- Configure the .env file with your database credentials:
  ```
  DB_NAME=<your-database-name>
  DB_USER=<your-database-username>
  DB_PASSWORD=<your-database-password>
  DB_HOST=<your-database-host>
  DB_PORT=<your-databse-port>
  ```
- Start the database container using Docker Compose:
  ```bash
  docker-compose up -d
  ```
- Apply the schema and seed data:
  ```bash
   psql -U <DB_USER> -d <DB_NAME> -f schema.sql
   psql -U <DB_USER> -d <DB_NAME> -f seed.sql
  ```
  [learn how to run commands on docker containers](https://docs.docker.com/reference/cli/docker/container/exec/)
