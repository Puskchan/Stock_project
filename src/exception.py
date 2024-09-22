import sys
from src.logger import logging

def error_message_detail(error: Exception, error_detail: sys) -> str:
    """
    Generates a detailed error message.

    Args:
        error (Exception): The exception that was raised.
        error_detail (sys): The sys module to extract traceback information.

    Returns:
        str: A formatted error message containing the file name, line number, and error message.
    """
    _, _, exc_tb = error_detail.exc_info()
    file_name = exc_tb.tb_frame.f_code.co_filename
    error_message = "Error occurred in python script name [{0}] line number [{1}] error message[{2}]".format(
        file_name, exc_tb.tb_lineno, str(error)
    )

    return error_message

class CustomException(Exception):
    def __init__(self, error_message: str, error_detail: sys) -> None:
        """
        Custom exception class to handle application-specific exceptions.

        Args:
            error_message (str): The error message to be displayed.
            error_detail (sys): The sys module to extract traceback information.
        """
        super().__init__(error_message)
        self.error_message = error_message_detail(error_message, error_detail=error_detail)

    def __str__(self) -> str:
        """
        Returns the string representation of the error message.

        Returns:
            str: The formatted error message.
        """
        return self.error_message