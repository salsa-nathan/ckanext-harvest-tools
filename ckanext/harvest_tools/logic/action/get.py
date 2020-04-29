import psycopg2

from ckan.logic import side_effect_free
from ckan.plugins import toolkit
from datetime import datetime

log = __import__('logging').getLogger(__name__)


def get_connection():
    try:
        return psycopg2.connect(
            user="ckan",
            password="ckan",
            host="postgres",
            port="5432",
            database="ckan"
        )
    except (Exception, psycopg2.Error) as error:
        log.error("Error while connecting to PostgreSQL", error)


def get_harvest_table_info():
    sql_query_text = """\
        SELECT *, pg_size_pretty(total_bytes) AS total 
            , pg_size_pretty(index_bytes) AS INDEX 
            , pg_size_pretty(toast_bytes) AS toast 
            , pg_size_pretty(table_bytes) AS TABLE 
        FROM (
            SELECT *, total_bytes-index_bytes-COALESCE(toast_bytes,0) AS table_bytes FROM ( 
                SELECT relname AS TABLE_NAME 
                    , c.reltuples AS row_estimate 
                    , pg_total_relation_size(c.oid) AS total_bytes 
                    , pg_indexes_size(c.oid) AS index_bytes 
                    , pg_total_relation_size(reltoastrelid) AS toast_bytes 
                FROM pg_class c 
                LEFT JOIN pg_namespace n ON n.oid = c.relnamespace 
                WHERE relkind = 'r' 
                    AND nspname = 'public' 
                    AND relname LIKE 'harvest%' 
                ) a 
            ) a;"""

    try:
        connection = get_connection()

        # Ref.: https://stackoverflow.com/a/43634941/9012261
        connection.autocommit = True

        cursor = connection.cursor()
        cursor.execute(sql_query_text)
        return cursor.fetchall()
    except (Exception, psycopg2.Error) as error:
        log.error("Error while connecting to PostgreSQL", error)
    finally:
        # closing database connection.
        if (connection):
            cursor.close()
            connection.close()
            #print("PostgreSQL connection is closed\n------------------------------------------------\n")


def get_alerts_for_table(table_data, row_threshold=5, total_bytes_threshold=((1024 * 1024) * 2), toast_bytes_threshold=((1024 * 1024) * 1)):
    alerts = []
    table_name = table_data[0]
    row_estimate = table_data[1]
    total_bytes = table_data[2]
    toast_bytes = table_data[4]

    # Check `row_estimate`
    if row_estimate > row_threshold:
        alerts.append('Table: `%s` has more than %s rows' % (table_name, row_threshold))
    # Check `total_bytes`
    if total_bytes > total_bytes_threshold:
        alerts.append('Table: `%s` has %s total_bytes' % (table_name, total_bytes))
    # Check `toast_bytes`
    if toast_bytes > toast_bytes_threshold:
        alerts.append('Table: `%s` has %s toast_bytes' % (table_name, toast_bytes))

    return alerts


@side_effect_free
def harvest_object_report(context, data_dict):
    """
    Query the database to find out the size of `harvest_object` table
    :param context:
    :param data_dict:
    :return:
    """
    toolkit.check_access('harvest_object_report', context, {})

    alerts = []
    row_threshold = 5
    # MB
    total_bytes_threshold = (1024 * 1024) * 2
    # MB
    toast_bytes_threshold = (1024 * 1024) * 1

    results = get_harvest_table_info()

    for result in results:
        if result[0] == 'harvest_object':
            alerts = get_alerts_for_table(result)

    return {
        "context": str(context),
        "alerts": alerts or [],
        "tables": results or []
    }


@side_effect_free
def long_running_harvest_jobs(context, data_dict):
    """
    Check for long-running harvest jobs and send an alert notification
    :param context:
    :param data_dict:
    :return:
    """
    toolkit.check_access('long_running_harvest_jobs', context, {})

    alerts = []
    job_details = []

    now = datetime.now()

    job_list = toolkit.get_action('harvest_job_list')(context, {"status": "Running"})

    for job in job_list:
        # e.g. 2020-04-20 02:58:01.670143
        job_created = job['created']
        datetime_job_created = datetime.strptime(job_created, '%Y-%m-%d %H:%M:%S.%f')

        job['days_running'] = abs((now - datetime_job_created).days)

        if job['days_running'] >= 1:
            # if the job has been running for over a day, safe to say it's stalled
            alerts.append("Job ID %s has been running for %s days - please investigate" % (job['id'], job['days_running']))
            job_details.append(job)
        else:
            job['seconds_running'] = abs((now - datetime_job_created).seconds)
            job['hours_running'] = job['seconds_running'] / 3600
            if job['hours_running'] > 2:
                alerts.append("Job ID %s has been running for %s hours - please investigate" % (job['id'], job['hours_running']))
                job_details.append(job)

    return {
        "alerts": alerts or None,
        "job_details": job_details or None,
        "datetime_job_created": str(datetime_job_created),
        "now": str(now)
    }


@side_effect_free
def clean_harvest_object_table(context, data_dict):
    """
    Clean the `harvest_object` table
    :param context:
    :param data_dict:
    :return:
    """
    toolkit.check_access('clean_harvest_object_table', context, {})

    try:
        sql_query_text = """\
            DELETE FROM harvest_object_error 
                WHERE harvest_object_id IN (
                    SELECT id 
                    FROM harvest_object 
                    WHERE current != 't'
        );"""

        connection = get_connection()

        # Ref.: https://stackoverflow.com/a/43634941/9012261
        connection.autocommit = True

        cursor = connection.cursor()
        cursor.execute(sql_query_text)
        log.info('Success: `harvest_object_error` table cleaned')

        cursor.execute("DELETE FROM harvest_object WHERE current != 't';")
        log.info('Success: `harvest_object` table cleaned')

        cursor.execute("VACUUM(FULL, ANALYZE) harvest_object;")
        log.info('Success: `harvest_object` table vacuumed')

        cursor.execute("REINDEX TABLE harvest_object;")
        log.info('Success: `harvest_object` table re-indexed')

    except (Exception, psycopg2.Error) as error:
        log.error("Error while connecting to PostgreSQL", error)
    finally:
        # closing database connection.
        if (connection):
            cursor.close()
            connection.close()

    return True

