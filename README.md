# ETL
This repository contains data pipelines for rescuing my data from various web services.

These are implemented in Python and Airflow.

Goals:

- I have a backup of my data in case the service goes away or I stop using it
- I can easily query my data without writing code
- I can join and aggregate data from different sources
- I can filter data by the date it was generated

## Local development

### Python setup
Install Python 3.8.

```
python -m venv env
. env/bin/activate
pip install -r requirements.txt
```

### Airflow setup
(Optional) [configure airflow](https://airflow.apache.org/docs/apache-airflow/stable/howto/set-config.html). By default, `~/airflow/airflow.cfg` will be generated when you install airflow.

By default this will use the SequentialExecutor with SQLite, which is not recommended for production usage. For a more production-like setup using Postgres, change the following settings:

```
sql_alchemy_conn = postgres://etl:etl@localhost/airflow
executor = LocalExecutor
```

Run `airflow initdb`

### Database setup
Create a postgres database for all the data to go into. E.g. on ubuntu:

`sudo -u postgres createdb <dbname>`

Create a database user as well:

```
sudo -u postgres psql
> create user <dbusername> with password '<dbpassword>';
> grant all privileges on database dbname to <dbusername>;
```

### Generate API keys
Generate an Airtable API key on the [account page](https://airtable.com/account).

### Configure the local environment
Create a `.env` file in the root of the project. Set the following environment variables:

```
AIRTABLE_API_KEY=####
AIRFLOW_CONN_POSTGRES_MOVIES=postgresql://<dbusername>:<dbpassword>@localhost/<dbname>
```

### Testing commands
```
# Run a task in isolation
airflow test syncing_movie_and_tv_data create_my_ratings 2015-06-01

# Backfill
airflow backfill syncing_movie_and_tv_data -s 2020-12-06
```

## Pipelines

### TV and Movies
This builds a database of TV shows and movies I've watched.

How this should work:

- Identify shows and movies by IMDB ID and/or https://www.themoviedb.org/
- Get my ratings from Airtable and/or Letterboxd
- Store images in S3
- Copy movie metadata to Airtable

## Licence

All code is licenced under MIT.
