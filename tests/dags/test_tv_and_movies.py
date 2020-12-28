import airflow
from airflow.models import DagBag
from airflow.configuration import conf

conf.load_test_config()


def test_dagbag_imports():
    '''
    Ensure the DAG is importable
    '''
    dagbag = DagBag()

    assert not dagbag.import_errors


def test_dag_does_something():
    '''
    Ensure end tasks are present in the DAG
    '''
    dagbag = DagBag()
    dag = dagbag.get_dag('syncing_movie_and_tv_data')

    assert dag.get_task('extract_airtable_shows')
