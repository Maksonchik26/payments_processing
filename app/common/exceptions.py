from fastapi import HTTPException, status


class APIError(HTTPException):
    def __init__(
        self,
        status_code: int,
        message: str,
    ):
        self.message = message

        detail = {
            "message": message,
        }

        super().__init__(status_code=status_code, detail=detail)


### Общие ошибки ###
class InvalidAuthData(APIError):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            message="Неверный или отсутствующий API ключ",
        )
