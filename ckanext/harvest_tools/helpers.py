import psycopg2
import ckan.plugins.toolkit as tk

log = __import__('logging').getLogger(__name__)
config = tk.config
render = tk.render
enqueue_job = tk.enqueue_job


ROW_THRESHOLD = 100000
TOTAL_BYTES_THRESHOLD = ((1024 * 1024) * 1000)
TOAST_BYTES_THRESHOLD = ((1024 * 1024) * 1000)


def send_email(to, subject, body):
    """
    Use CKAN mailer logic to send an email to an individual email address

    :param to: string
    :param subject: string
    :param body: string
    :return:
    """
    import ckan.lib.mailer as mailer

    # Attempt to send mail.
    mail_dict = {
        'recipient_email': to,
        'recipient_name': to,
        'subject': subject,
        'body': body
    }

    try:
        mailer.mail_recipient(**mail_dict)
    except mailer.MailerException:
        log.error(u'Cannot send email notification to %s.', to, exc_info=1)


def send_notification_email(template, to=None, extra_vars=[]):
    """
    Compile an alert email notification to be sent via the job worker queue

    :param template: string
    :param to: string
    :param extra_vars: list
    :return:
    """

    if not to:
        to = config.get('ckanext.harvest_tools.email_to', config.get('email_to'))

    subject = config.get('ckan.site_title') + ' - ' + render('emails/subject/{0}.txt'.format(template), extra_vars)
    body = render('emails/body/{0}.txt'.format(template), extra_vars)

    enqueue_job(send_email, [to, subject, body], title=u'Harvest tools email alert')


def get_connection():
    db_host = config.get('ckanext.harvest_tools.db_host', "postgres")
    db_port = config.get('ckanext.harvest_tools.db_port', "5432")
    db_name = config.get('ckanext.harvest_tools.db_name', "ckan")
    db_user = config.get('ckanext.harvest_tools.db_user', "ckan")
    db_pass = config.get('ckanext.harvest_tools.db_pass', "ckan")

    try:
        return psycopg2.connect(
            user=db_user,
            password=db_pass,
            host=db_host,
            port=db_port,
            database=db_name
        )
    except (Exception, psycopg2.Error) as error:
        log.error("Error while connecting to PostgreSQL", error)


def get_alerts_for_table(table_data, row_threshold=ROW_THRESHOLD, total_bytes_threshold=TOTAL_BYTES_THRESHOLD,
                         toast_bytes_threshold=TOAST_BYTES_THRESHOLD):
    alerts = []
    table_name = table_data[0]
    row_estimate = table_data[1]
    total_bytes = table_data[2]
    toast_bytes = table_data[4]

    # Check `row_estimate`
    if row_estimate > row_threshold:
        alerts.append('Table: `%s` has more than %s rows - currently %d rows' % (table_name, row_threshold, row_estimate))
    # Check `total_bytes`
    if total_bytes > total_bytes_threshold:
        alerts.append('Table: `%s` has %s total_bytes - currently %s' % (table_name, total_bytes, table_data[6]))
    # Check `toast_bytes`
    if toast_bytes > toast_bytes_threshold:
        alerts.append('Table: `%s` has %s toast_bytes - currently %s' % (table_name, toast_bytes, table_data[8]))

    return alerts
