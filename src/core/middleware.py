try:
    from django.utils.deprecation import MiddlewareMixin
except ImportError:
    MiddlewareMixin = object

import logging
import time

from django.db import connection, reset_queries


class RemoteAddrMiddleware(object):
    """
    Sets 'REMOTE_ADDR' based on 'HTTP_X_FORWARDED_FOR', if the latter is
    set.
    Based on http://djangosnippets.org/snippets/1706/
    """

    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        response = self.get_response(request)

        if "HTTP_X_FORWARDED_FOR" in request.META:
            ip = request.META["HTTP_X_FORWARDED_FOR"].split(",")[0].strip()
            request.META["REMOTE_ADDR"] = ip

        # Code to be executed for each request/response after
        # the view is called.

        return response


def metric_middleware(get_response):
    """
    Finds nr of queries on every request.
    https://testdriven.io/blog/django-performance-testing/
    """

    def middleware(request):
        reset_queries()

        # Get beginning stats
        start_queries = len(connection.queries)
        start_time = time.perf_counter()

        # Process the request
        response = get_response(request)

        # Get ending stats
        end_time = time.perf_counter()
        end_queries = len(connection.queries)

        # Calculate stats
        total_time = end_time - start_time
        total_queries = end_queries - start_queries

        # Log the results
        logger = logging.getLogger("debug")
        logger.debug(f"Request: {request.method} {request.path}")
        logger.debug(f"Number of Queries: {total_queries}")
        logger.debug(f"Total time: {(total_time):.2f}s")

        return response

    return middleware


# class RemoteAddrMiddleware(MiddlewareMixin):
#     """
#     Middleware for showing real ip address in django-admin-honeypot.
#     Sets 'REMOTE_ADDR' based on 'HTTP_X_FORWARDED_FOR', if the latter is
#     set.
#     Based on http://djangosnippets.org/snippets/1706/
#     Old style middleware, prior to django 1.11
#     """
#
#     def process_request(self, request):
#         if "HTTP_X_FORWARDED_FOR" in request.META:
#             ip = request.META["HTTP_X_FORWARDED_FOR"].split(",")[0].strip()
#             request.META["REMOTE_ADDR"] = ip
