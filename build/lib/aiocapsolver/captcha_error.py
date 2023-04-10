class CaptchaError(Exception):
    def __init__(self, error_id, description):
        message = f'{error_id}: {description}'
        super().__init__(message)