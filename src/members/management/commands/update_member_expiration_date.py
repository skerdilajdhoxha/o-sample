import logging
import logging.handlers
from datetime import date, datetime

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


User = get_user_model()


mail_server = "mail.ncabana.org"
port = 587
sender_email = "membershiplist@ncabana.org"
password = "$$tlEd3aBvBD6"


def email_logs(error):
    """
    Send an email with logs if an error occurs when executing this management command.
    """
    mail_handler = logging.handlers.SMTPHandler(
        mailhost=("mail.ncabana.org", 587),
        fromaddr="membershiplist@ncabana.org",
        toaddrs=["skerdi@ferrousdesign.com", "andy@ferrousdesign.com"],
        subject="An error occurred in the script of tracking membership exp dates.",
        credentials=("membershiplist@ncabana.org", "$$tlEd3aBvBD6"),
        secure=None,
    )
    mail_handler.setLevel(logging.ERROR)
    get_logger = logging.getLogger()
    get_logger.addHandler(mail_handler)
    get_logger.exception(error)
    return get_logger


class Command(BaseCommand):
    help = (
        "Checks members expiration date. If it's today make member inactive,"
        " so they can't login adn do nothing on the site"
    )

    def handle(self, *args, **options):
        try:
            users = User.objects.all()
            for user in users:
                # print(user, user.expiration_date)
                # if user.expiration_date is datetime it begins with year 2020
                if user.expiration_date[0] == "2":
                    user_exp_dt_date_obj = datetime.strptime(
                        user.expiration_date, "%Y-%m-%d"
                    ).date()

                    if user_exp_dt_date_obj == date.today():
                        obj = User.objects.get(pk=user.pk)
                        obj.expiration_date = "Expired"
                        obj.is_active = False
                        obj.save()

        except Exception as e:
            print(
                'An error "{}" occurred and an email with the error was sent to admin.'.format(
                    e
                )
            )
            email_logs(e)


print(datetime.now())
