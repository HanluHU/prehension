class Error(Exception):
    """Base class for exceptions in this module."""
    pass


class InputFormatError(Error):
    """Exception raised for errors in the input.

    Attributes:
        expression -- input expression in which the error occurred
        message -- explanation of the error
    """

    def __str__(self):
        return "Wrong Format!"
