from datetime import datetime

class AppException(Exception):
    """Base exception for all StudHelper errors."""
    def __init__(self, message: str, status_code: int = 500, error_code: str = "INTERNAL_ERROR"):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        super().__init__(self.message)

    def __str__(self) -> str:
        return f"[{self.error_code}] Status {self.status_code}: {self.message}"


# AUTHENTICATION EXCEPTIONS
class AuthenticationError(AppException):
    """User authentication failed."""
    def __init__(self, message: str = "Authentication failed", error_code: str = "AUTHENTICATION_FAILED"):
        super().__init__(message, status_code=401, error_code=error_code)


class InvalidTokenError(AuthenticationError):
    """JWT token validation failed."""
    def __init__(self, message: str = "Invalid token"):
        super().__init__(message, error_code="INVALID_TOKEN")


class TokenExpiredError(AuthenticationError):
    """JWT token expired."""
    def __init__(self, message: str = "Token has expired"):
        super().__init__(message, error_code="TOKEN_EXPIRED")


class InvalidCredentialsError(AuthenticationError):
    """Invalid credentials provided."""
    def __init__(self, message: str = "Invalid email or password"):
        super().__init__(message, error_code="INVALID_CREDENTIALS")


# AUTHORIZATION EXCEPTIONS
class AuthorizationError(AppException):
    """User lacks permissions for this request."""
    def __init__(self, message: str = "Access Denied: unauthorized operation", error_code: str = "AUTHORIZATION_FAILED"):
        super().__init__(message, status_code=403, error_code=error_code)


class InsufficientPermissionsError(AuthorizationError):
    """User role lacks required permissions."""
    def __init__(self, message: str = "Insufficient role permissions"):
        super().__init__(message, error_code="INSUFFICIENT_PERMISSIONS")


# RESOURCE EXCEPTIONS
class ResourceNotFoundError(AppException):
    """Requested resource (user, session, job) not found."""
    def __init__(self, message: str = "Resource not found", error_code: str = "NOT_FOUND"):
        super().__init__(message, status_code=404, error_code=error_code)


class ResourceAlreadyExistsError(AppException):
    """Resource already exists in database."""
    def __init__(self, message: str = "Resource already exists", error_code: str = "ALREADY_EXISTS"):
        super().__init__(message, status_code=409, error_code=error_code)


# VALIDATION EXCEPTIONS
class ValidationError(AppException):
    """Input validation checks failed."""
    def __init__(self, message: str = "Validation error", error_code: str = "VALIDATION_ERROR"):
        super().__init__(message, status_code=400, error_code=error_code)


class InvalidInputError(ValidationError):
    """Specific parameters fail checks."""
    def __init__(self, message: str = "Invalid parameter input"):
        super().__init__(message, error_code="INVALID_INPUT")


class InvalidFileTypeError(ValidationError):
    """Uploaded file extension/format is incorrect."""
    def __init__(self, message: str = "Invalid file type format"):
        super().__init__(message, error_code="INVALID_FILE_TYPE")


class FileTooLargeError(ValidationError):
    """Uploaded file size exceeds limits."""
    def __init__(self, message: str = "File size exceeds allowed limits"):
        super().__init__(message, error_code="FILE_TOO_LARGE")


# STORAGE EXCEPTIONS
class StorageError(AppException):
    """Database, encryption, or file system error occurred."""
    def __init__(self, message: str = "Storage engine failure", error_code: str = "STORAGE_ERROR"):
        super().__init__(message, status_code=500, error_code=error_code)


class StorageLimitExceededError(ValidationError):
    """Individual storage boundaries exceeded."""
    def __init__(self, message: str = "Storage limit exceeded"):
        super().__init__(message, error_code="STORAGE_LIMIT_EXCEEDED")


class EncryptionError(StorageError):
    """File encryption algorithm failure."""
    def __init__(self, message: str = "Data encryption failed"):
        super().__init__(message, error_code="ENCRYPTION_ERROR")


class DecryptionError(StorageError):
    """Data decryption tag verify failure."""
    def __init__(self, message: str = "Data decryption failed"):
        super().__init__(message, error_code="DECRYPTION_ERROR")


# INTERVIEW EXCEPTIONS
class InterviewSessionError(AppException):
    """Standard session check error."""
    def __init__(self, message: str = "Interview session error", error_code: str = "INTERVIEW_SESSION_ERROR"):
        super().__init__(message, status_code=400, error_code=error_code)


class InterviewSessionNotFoundError(ResourceNotFoundError):
    """Target mock interview session is missing."""
    def __init__(self, message: str = "Interview session not found"):
        super().__init__(message, error_code="INTERVIEW_SESSION_NOT_FOUND")


class InterviewSessionExpiredError(AppException):
    """Active time exceeded 1 hour limit."""
    def __init__(self, message: str = "Interview session expired"):
        super().__init__(message, status_code=410, error_code="INTERVIEW_SESSION_EXPIRED")


# EXTERNAL SERVICE EXCEPTIONS
class ExternalServiceError(AppException):
    """External API network connection issue."""
    def __init__(self, message: str = "External API call failed", error_code: str = "EXTERNAL_SERVICE_ERROR"):
        super().__init__(message, status_code=502, error_code=error_code)


class AIServiceError(ExternalServiceError):
    """AI services (Gemini) down or rate-limited."""
    def __init__(self, message: str = "Gemini LLM call failed"):
        super().__init__(message, error_code="AI_SERVICE_ERROR")


class EmbeddingServiceError(ExternalServiceError):
    """NVIDIA NIM embeddings API call failure."""
    def __init__(self, message: str = "Embeddings API call failed"):
        super().__init__(message, error_code="EMBEDDING_SERVICE_ERROR")


class JobSearchServiceError(ExternalServiceError):
    """JSearch API query failure."""
    def __init__(self, message: str = "JSearch API service failed"):
        super().__init__(message, error_code="JOB_SEARCH_SERVICE_ERROR")


# DATABASE EXCEPTIONS
class DatabaseError(StorageError):
    """SQLAlchemy or database query syntax error."""
    def __init__(self, message: str = "Database operation failed", error_code: str = "DATABASE_ERROR"):
        super().__init__(message, error_code=error_code)


class DatabaseConnectionError(DatabaseError):
    """Database connections timed out."""
    def __init__(self, message: str = "Database connection failed"):
        super().__init__(message, error_code="DATABASE_CONNECTION_ERROR")


# RAG/VECTOR EXCEPTIONS
class RAGError(AppException):
    """RAG pipeline search error."""
    def __init__(self, message: str = "RAG search failed", error_code: str = "RAG_ERROR"):
        super().__init__(message, status_code=500, error_code=error_code)


class VectorSearchError(RAGError):
    """Pinecone vector indexing issues."""
    def __init__(self, message: str = "Pinecone search query failed"):
        super().__init__(message, error_code="VECTOR_SEARCH_ERROR")


def format_error_response(exception: AppException) -> dict:
    """
    Format AppException instance into a dictionary payload for FastAPI JSONResponse.
    """
    return {
        "error": exception.__class__.__name__,
        "message": exception.message,
        "status_code": exception.status_code,
        "error_code": exception.error_code,
        "timestamp": datetime.utcnow().isoformat()
    }
