#!/usr/bin/python3

"""
This script is meant to reduce the size of log files if they reach a certain size.
This will be run by a cron job, so all paths must be absolute.
"""

import logging
import logging.handlers
import os
from pathlib import Path


def email_logs(error):
    """
    Send an email with logs if an error occurs when executing this management command.
    """
    mail_handler = logging.handlers.SMTPHandler(
        mailhost=("mail.ferrousdesign.com", 587),
        fromaddr="cryptoBot2000@ferrousdesign.com",
        toaddrs=["skerdi@ferrousdesign.com", "andy@ferrousdesign.com"],
        subject="An error occurred in shortening log files in OHI-SHOP-002.",
        credentials=("cryptoBot2000@ferrousdesign.com", "$$hU8eRsPPk2d"),
        secure=None,
    )
    mail_handler.setLevel(logging.ERROR)
    get_logger = logging.getLogger()
    get_logger.addHandler(mail_handler)
    get_logger.exception(error)
    return get_logger


def shorten_file(file_in, file_out):
    file_size = Path(file_in).stat().st_size
    # get file size in megabytes
    file_size_mb = file_size / (1024 * 1024)
    # if file size is bigger than 100 MB
    if file_size_mb >= 100:
        with open(file_in, "r") as f_in, open(file_out, "w") as f_out:
            lines = f_in.readlines()
            # get half of lines number
            half_of_lines_nr = int(len(lines) / 2)
            # copy to file out last half of lines
            half_of_lines = lines[half_of_lines_nr:]
            for line in half_of_lines:
                f_out.write(line)

        os.remove(file_in)
        os.rename(file_out, file_in)


if __name__ == "__main__":

    try:
        shorten_file(
            "/home/django/django_project/src/members/management/commands/update_member_expiration_date.txt",
            "/home/django/django_project/src/members/management/commands/update_member_expiration_date_temporary.txt",
        )
    except Exception as e:
        print(f'An error "{e}" occurred and an email with the error was sent to admin.')
        # logger.exception(e)
        email_logs(e)
