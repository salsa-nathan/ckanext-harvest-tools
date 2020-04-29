from ckan.common import config

log = __import__('logging').getLogger(__name__)


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
        'body': body,
        'headers': {'reply-to': config.get('smtp.mail_from')}
    }

    try:
        mailer.mail_recipient(**mail_dict)
    except mailer.MailerException:
        log.error(u'Cannot send email notification to %s.', to, exc_info=1)


def send_notification_email(template, to=None, extra_vars=[]):
    """
    Compile a notification email to be sent via the job worker queue

    :param template: string
    :param to: string
    :param extra_vars: list
    :return:
    """
    from ckan.lib.base import render_jinja2
    from ckan.plugins import toolkit

    if not to:
        to = config.get('email_to')

    subject = config.get('ckan.site_title') + ' - ' + render_jinja2('emails/subject/{0}.txt'.format(template), extra_vars)
    body = render_jinja2('emails/body/{0}.txt'.format(template), extra_vars)

    toolkit.enqueue_job(send_email, [to, subject, body], title=u'Long running harvest job alert')
