class AppError(Exception):
    """
    Base class for all application-specific exceptions.
    """
    def __init__(self, message: str = None):
        super().__init__(message or self.__class__.__name__)
        self.message = message or self.__class__.__name__


class NotFoundError(AppError):
    """
    Raised when a requested resource (e.g., database record) cannot be found.
    """
    pass


class ValidationError(AppError):
    """
    Raised when input validation fails (e.g., missing or malformed parameters).
    """
    def __init__(self, field: str, message: str):
        super().__init__(f"Validation failed for '{field}': {message}")
        self.field = field


class DatabaseError(AppError):
    """
    Raised for database operation failures (e.g., connection issues, SQL errors).
    """
    pass


class ServiceError(AppError):
    """
    Raised for general errors in the service layer (e.g., business logic failures).
    """
    pass


class GraphQLError(AppError):
    """
    Raised when a GraphQL-specific error occurs (e.g., resolver failure).
    """
    pass 