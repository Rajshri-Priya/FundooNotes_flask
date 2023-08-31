import smtplib
import ssl
from email.message import EmailMessage
from celery import Celery
from celery.schedules import crontab
from settings import settings

celery = Celery(__name__,
                broker=settings.REDIS_URL,
                backend=settings.REDIS_URL,
                broker_connection_retry_on_startup=True,
                redbeat_redis_url=settings.REDIS_URL, beat_max_loop_interval=5,
                beat_scheduler="redbeat.schedulers.RedBeatScheduler", redbeat_lock_key=None, enable_utc=False)


def create_crontab_schedule(minute, hour, day_of_month, month_of_year):
    schedule = crontab(
        minute=minute,
        hour=hour,
        day_of_month=day_of_month,
        month_of_year=month_of_year,
    )
    return schedule


@celery.task()
def send_mail(payload):
    msg = EmailMessage()
    msg['From'] = settings.MAIL_USERNAME
    msg['To'] = payload.get('recipient_email')
    msg['Subject'] = 'Notes Reminder BY Flask Microservices'
    msg.set_content(payload.get('message'))
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(settings.MAIL_SERVER, settings.MAIL_PORT, context=context) as smtp:
        smtp.login(user=settings.MAIL_USERNAME, password=settings.MAIL_PASSWORD)
        smtp.sendmail(settings.MAIL_USERNAME, payload.get('recipient_email'), msg.as_string())
        smtp.quit()
    return f"Mail sent to {payload.get('recipient_email')}"
