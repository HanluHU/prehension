class Error(Exception):
    """Base class for exceptions in the module"""

    pass


class InputFormatError(Error):
    """Exception raised for errors in the input format"""

    def __str__(self):
        """Print a wrong format message"""

        return "Wrong Format!"
