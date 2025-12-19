import inspect
import traceback

from typing import Callable

from BO.base.exception import ValidationError
from django.conf import settings


class Response:
    def __init__(
            self,
            desc_error: str,
            desc_success: str = '',
            return_list: list = None,
    ):
        self.desc_success = desc_success
        self.desc_error = desc_error
        self.return_list = return_list or []

    def __call__(self, function) -> Callable[..., dict]:
        def wrapper(*args, **kwargs):
            dict_response = {
                'status': True,
                'status_code': 200,
                'description': self.desc_success,
            }
            response = None
            try:
                response = function(*args, **kwargs)

            except ValidationError as e:
                dict_response['status'] = False
                dict_response['status_code'] = e.status_code
                dict_response['description'] = e.message
                response = e.response

            except Exception as e:
                if settings.DEBUG:
                    print(traceback.format_exc())
                    dict_response['error'] = traceback.format_exc()

                dict_response['status'] = False
                dict_response['status_code'] = 500
                dict_response['description'] = self.desc_error

            if response is not None:
                try:
                    if not self.return_list:
                        dict_response['response'] = response

                    elif isinstance(response, dict):
                        dict_response[self.return_list[0]] = response

                    elif isinstance(response, tuple):
                        for key, value in zip(self.return_list, response):
                            dict_response[key] = value

                    elif len(self.return_list) == 1:
                        dict_response[self.return_list[0]] = response

                except:
                    dict_response['status'] = False
                    dict_response['status_code'] = 500
                    dict_response['description'] = 'Error on decorator'
            else:
                if self.return_list:
                    for response in self.return_list:
                        dict_response[response] = None

            return dict_response

        # Add the decorator parameters to the wrapper function's signature
        wrapper.__signature__ = inspect.signature(function)

        return wrapper
