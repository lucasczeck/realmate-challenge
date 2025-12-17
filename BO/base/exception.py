class ValidationError(Exception):

    def __init__(
        self, 
        message: str = None,
        status_code: int = 400, 
        response=None,
    ):

        self.__message = message
        self.__response = response
        self.__status_code = status_code
        super().__init__(self.__message)

    @property
    def response(self):
        return self.__response

    @property
    def message(self):
        return self.__message

    @property
    def status_code(self):
        return self.__status_code

