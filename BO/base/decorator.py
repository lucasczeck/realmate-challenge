import inspect
import traceback
import sentry_sdk

from typing import Callable

from BO.base.excecao import ValidationError
from django.conf import settings


class Response:
    def __init__(
            self,
            desc_error: str,
            desc_success: str = '',
            lista_retornos: list = None,
            is_manter_retorno: bool = False,
    ):
        self.desc_success = desc_success
        self.desc_error = desc_error
        self.lista_retornos = lista_retornos or []
        self.is_manter_retorno = is_manter_retorno

    def __call__(self, funcao) -> Callable[..., dict]:
        def wrapper(*args, **kwargs):
            response = {
                'status': True,
                'status_code': 200,
                'descricao': self.desc_success,
            }
            retorno = None
            try:
                retorno = funcao(*args, **kwargs)

            except ValidationError as e:
                response['status'] = False
                response['status_code'] = e.status_code
                response['descricao'] = e.mensagem
                response['descricao_desenvolvedor'] = e.mensagem_desenvolvedor if e.mensagem_desenvolvedor else None
                retorno = e.retorno

            except Exception as e:
                if settings.DEBUG:
                    print(traceback.format_exc())
                    response['erro'] = traceback.format_exc()

                response['status'] = False
                response['status_code'] = 500
                response['descricao'] = self.desc_error

            if self.is_manter_retorno:
                return retorno

            if retorno is not None:
                try:
                    if not self.lista_retornos:
                        response['retorno'] = retorno

                    elif isinstance(retorno, dict):
                        response[self.lista_retornos[0]] = retorno

                    elif isinstance(retorno, tuple):
                        for nm_chave, valor in zip(self.lista_retornos, retorno):
                            response[nm_chave] = valor

                    elif len(self.lista_retornos) == 1:
                        response[self.lista_retornos[0]] = retorno

                except:
                    response['status'] = False
                    response['status_code'] = 500
                    response['descricao'] = 'Erro no decorator'
            else:
                if self.lista_retornos:
                    for retorno in self.lista_retornos:
                        response[retorno] = None

            return response

        # Add the decorator parameters to the wrapper function's signature
        wrapper.__signature__ = inspect.signature(funcao)

        return wrapper
