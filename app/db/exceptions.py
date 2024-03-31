class DatabaseIntegrityError(Exception):
    """Exception raised for database integrity-related errors."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)
