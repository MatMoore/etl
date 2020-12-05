from dotenv import load_dotenv
from airtable import airtable
from os import environ
from airflow.hooks.postgres_hook import PostgresHook
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.postgres_operator import PostgresOperator
from datetime import datetime, timedelta
from urllib.parse import urlparse
import logging

logger = logging.getLogger(__name__)

load_dotenv()

api_key = environ['AIRTABLE_API_KEY']
base_id = 'appnLPq9OiukOkhGm'
shows_table = 'Shows'


def validate_imdb_url(url):
    '''
    Make sure IMDB url is actually an IMDB url.
    This is not enforced in the airtable.

    TODO: this is a bit flaky since the URL could be formatted in different
    ways. Instead of storing the whole URL, it would be better to extract the
    ID part.
    '''
    try:
        result = urlparse(url)
        return result.netloc in ('imdb.com', 'www.imdb.com')
    except Exception:
        return False


def extract_airtable_shows():
    '''
    Load shows from airtable into a Postgres table
    Airtable shows are identified by their IMDB ID.

    This task stores the IDs and ratings only.
    '''
    hook = PostgresHook(postgres_conn_id='postgres_movies')

    base = airtable.Airtable(base_id, api_key)

    ratings = []
    for record in base.iterate(shows_table):
        fields = record['fields']
        rating = fields.get('Mat Rating')
        imdb_url = fields.get('IMDB')

        if rating is not None and validate_imdb_url(imdb_url):
            ratings.append((imdb_url, rating))

    logger.info('Rated %d movies', len(ratings))

    hook.insert_rows('my_ratings', rows=ratings, target_fields=('imdb_url', 'stars'))


def extract_imdb_data(**kwargs):
    '''
    Add IMDB ratings and metadata to shows
    '''


def promote_staging(**kwargs):
    '''
    Replace the live schema with the staging schema
    '''


default_args = {
    'owner': 'airflow',
    'retries': 0
}


with DAG('syncing_movie_and_tv_data',
         default_args=default_args,
         start_date=datetime.now(),
         schedule_interval=timedelta(minutes=10)
         ) as dag:

    # TODO: use alembic for this?
    create_my_ratings = PostgresOperator(
        task_id='create_my_ratings',
        postgres_conn_id='postgres_movies',
        sql='''
        create table if not exists my_ratings(imdb_url text unique primary key, stars integer not null);
        truncate table my_ratings;
        ''',
        dag=dag
    )
 
    extract_airtable_shows = PythonOperator(
        task_id='extract_airtable_shows',
        python_callable=extract_airtable_shows,
        dag=dag
    )
