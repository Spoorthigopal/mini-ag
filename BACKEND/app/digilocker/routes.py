from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.shared.dependencies import get_current_user
from app.auth.models import User
from app.auth.utils import decode_access_token
from app.digilocker.schemas import (
    DocumentResponse,
    DocumentListResponse,
    DocumentDeleteRequest
)
from app.digilocker.models import Document
from app.digilocker import service
from typing import Optional, List
import io
import logging
import time

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/digilocker", tags=["digilocker"])

security_scheme = HTTPBearer(auto_error=False)


async def get_current_user_from_header_or_query(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme),
    token: Optional[str] = Query(None, description="Direct download access token"),
    db: Session = Depends(get_db)
) -> User:
    """
    Authenticate user using either the HTTP Bearer Authorization header 
    or the 'token' query parameter.
    """
    token_str = None
    if credentials:
        token_str = credentials.credentials
    elif token:
        token_str = token

    if not token_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token is missing. Provide bearer header or token query parameter."
        )

    try:
        user_id = decode_access_token(token_str)
    except Exception as e:
        logger.error(f"Token decryption/validation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token is invalid or expired"
        )

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User associated with this token not found"
        )
    return user


# ENDPOINT 1: POST /api/digilocker/upload
@router.post(
    "/upload",
    response_model=DocumentResponse,
    status_code=status.HTTP_200_OK
)
async def upload_file(
    file: UploadFile = File(..., description="The document file to upload"),
    category: str = Form(..., description="Category: certificates, transcripts, documents, certificates_backup"),
    document_name: Optional[str] = Form(None, description="Optional custom document display name"),
    description: Optional[str] = Form(None, description="Optional description details"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload a document. Encrypts the payload before database storage.
    Allowed extensions: pdf, docx, png, jpg, jpeg, zip. Max size: 50MB.
    """
    logger.info(f"User {current_user.id} requested file upload: {file.filename}")

    # Read binary bytes of the file
    try:
        file_bytes = await file.read()
    except Exception as e:
        logger.error(f"Error reading uploaded file: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not read uploaded file content"
        )

    filename = document_name if document_name else file.filename
    if not filename:
        filename = "unnamed_document"

    try:
        doc_response = service.upload_document(
            user_id=current_user.id,
            file_bytes=file_bytes,
            filename=filename,
            category=category,
            description=description,
            db=db
        )
        return doc_response
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Upload logic failure: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error occurred during encryption and storage."
        )


# ENDPOINT 2: GET /api/digilocker/documents
@router.get(
    "/documents",
    response_model=DocumentListResponse,
    status_code=status.HTTP_200_OK
)
async def list_user_documents(
    category: Optional[str] = Query(None, description="Filter by category"),
    page: int = Query(1, ge=1, description="Page index"),
    limit: int = Query(10, ge=1, le=50, description="Page size limit (max 50)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Fetch user's secure documents list (paginated). Includes overall storage usage.
    """
    logger.info(f"User {current_user.id} listing documents page={page} limit={limit}")
    return service.list_documents(
        user_id=current_user.id,
        db=db,
        category_filter=category,
        page=page,
        limit=limit
    )


# ENDPOINT 3: GET /api/digilocker/download/{doc_id}
@router.get(
    "/download/{doc_id}",
    status_code=status.HTTP_200_OK
)
async def download_file_by_id(
    doc_id: str,
    current_user: User = Depends(get_current_user_from_header_or_query),
    db: Session = Depends(get_db)
):
    """
    Retrieve and decrypt document. Checks file integrity before returning.
    Supports query parameter 'token' for direct downloads from <a> tags.
    """
    logger.info(f"User {current_user.id} requested download of {doc_id}")

    # Fetch filename and extensions to configure response headers
    doc = db.query(Document).filter(Document.document_id == doc_id).first()
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID {doc_id} not found"
        )
    if doc.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access Denied: You do not own this document"
        )

    # Call decryption service
    file_bytes = service.download_document(
        user_id=current_user.id,
        doc_id=doc_id,
        db=db
    )

    # Determine Content-Type
    filename = doc.filename
    content_type = "application/octet-stream"
    if filename.endswith(".pdf"):
        content_type = "application/pdf"
    elif filename.endswith(".docx"):
        content_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    elif filename.endswith(".png"):
        content_type = "image/png"
    elif filename.endswith((".jpg", ".jpeg")):
        content_type = "image/jpeg"
    elif filename.endswith(".zip"):
        content_type = "application/zip"

    # StreamingResponse is ideal for file retrieval
    return StreamingResponse(
        io.BytesIO(file_bytes),
        media_type=content_type,
        headers={
            "Content-Disposition": f"attachment; filename=\"{filename}\"",
            "Access-Control-Expose-Headers": "Content-Disposition"
        }
    )


# ENDPOINT 4: GET /api/digilocker/view/{doc_id}
@router.get(
    "/view/{doc_id}",
    status_code=status.HTTP_200_OK
)
async def view_file_by_id(
    doc_id: str,
    current_user: User = Depends(get_current_user_from_header_or_query),
    db: Session = Depends(get_db)
):
    """
    Retrieve and decrypt document for inline browser viewing.
    Sets Content-Disposition: inline so the browser renders it in a new tab.
    Supports query parameter 'token' for direct access from <a> tags.
    """
    logger.info(f"User {current_user.id} requested inline view of {doc_id}")

    doc = db.query(Document).filter(Document.document_id == doc_id).first()
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID {doc_id} not found"
        )
    if doc.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access Denied: You do not own this document"
        )

    # Decrypt
    file_bytes = service.download_document(
        user_id=current_user.id,
        doc_id=doc_id,
        db=db
    )

    filename = doc.filename
    content_type = "application/octet-stream"
    if filename.endswith(".pdf"):
        content_type = "application/pdf"
    elif filename.endswith(".docx"):
        content_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    elif filename.endswith(".png"):
        content_type = "image/png"
    elif filename.endswith((".jpg", ".jpeg")):
        content_type = "image/jpeg"
    elif filename.endswith(".zip"):
        content_type = "application/zip"
    elif filename.endswith(".svg"):
        content_type = "image/svg+xml"

    # Content-Disposition: inline causes browser to render instead of download
    return StreamingResponse(
        io.BytesIO(file_bytes),
        media_type=content_type,
        headers={
            "Content-Disposition": f"inline; filename=\"{filename}\"",
            "Access-Control-Expose-Headers": "Content-Disposition"
        }
    )


# ENDPOINT 5: DELETE /api/digilocker/{doc_id}
@router.delete(
    "/{doc_id}",
    status_code=status.HTTP_200_OK
)
async def delete_file_by_id(
    doc_id: str,
    request: Optional[DocumentDeleteRequest] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Securely delete document records from the database. Owner verification checked.
    """
    logger.info(f"User {current_user.id} requested deletion of {doc_id}")
    
    # Optional double check confirmation on request payload
    if request and request.document_id != doc_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mismatch between payload document_id and URL path parameter doc_id"
        )

    success = service.delete_document(
        user_id=current_user.id,
        doc_id=doc_id,
        db=db
    )
    
    if success:
        return {"status": "success", "message": "Document securely deleted"}
        
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Could not delete document"
    )


# ENDPOINT 6: PATCH /api/digilocker/{doc_id}/rename
@router.patch(
    "/{doc_id}/rename",
    response_model=DocumentResponse,
    status_code=status.HTTP_200_OK
)
async def rename_document(
    doc_id: str,
    new_name: str = Form(..., description="New filename for the document"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Rename a document (updates filename metadata only, encrypted data untouched).
    The file extension must be preserved to ensure valid downloads.
    """
    logger.info(f"User {current_user.id} requested rename of {doc_id} to '{new_name}'")

    doc = db.query(Document).filter(Document.document_id == doc_id).first()
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID {doc_id} not found"
        )
    if doc.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access Denied: You do not own this document"
        )

    new_name = new_name.strip()
    if not new_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New name cannot be empty"
        )

    # Preserve the original extension if new_name has no extension
    orig_ext = doc.filename.rsplit(".", 1)[-1].lower() if "." in doc.filename else ""
    if orig_ext and "." not in new_name:
        new_name = f"{new_name}.{orig_ext}"

    doc.filename = new_name
    db.commit()
    db.refresh(doc)

    logger.info(f"Document {doc_id} renamed to '{new_name}' by user {current_user.id}")

    return DocumentResponse(
        document_id=doc.document_id,
        document_name=doc.filename,
        category=doc.category,
        file_size=doc.file_size,
        upload_date=doc.upload_date,
        last_accessed=doc.last_accessed,
        encrypted=True,
        checksum=doc.checksum
    )


# ENDPOINT 7: PUT /api/digilocker/{doc_id}/replace
@router.put(
    "/{doc_id}/replace",
    response_model=DocumentResponse,
    status_code=status.HTTP_200_OK
)
async def replace_document(
    doc_id: str,
    file: UploadFile = File(..., description="New file to replace the existing document"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Replace the encrypted content of an existing document with a new file.
    Re-encrypts with AES-256-GCM and updates all encryption fields in-place.
    The document_id and metadata (category, name) are preserved.
    """
    logger.info(f"User {current_user.id} requested replace of {doc_id} with '{file.filename}'")

    doc = db.query(Document).filter(Document.document_id == doc_id).first()
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID {doc_id} not found"
        )
    if doc.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access Denied: You do not own this document"
        )

    # Read new file bytes
    try:
        file_bytes = await file.read()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not read uploaded file content"
        )

    # Validate size
    if len(file_bytes) > 50 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Replacement file exceeds the 50 MB limit"
        )

    # Validate extension
    from app.digilocker.service import ALLOWED_EXTENSIONS
    new_filename = file.filename or doc.filename
    ext = new_filename.rsplit(".", 1)[-1].lower() if "." in new_filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type '.{ext}' is not supported. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    try:
        from app.digilocker import encryption
        enc_result = encryption.encrypt_file(file_bytes, current_user.id)

        # Update all encryption fields in-place
        doc.encrypted_data = enc_result["ciphertext"]
        doc.salt = enc_result["salt"]
        doc.nonce = enc_result["nonce"]
        doc.tag = enc_result["tag"]
        doc.checksum = enc_result["checksum"]
        doc.file_size = len(file_bytes)
        doc.filename = new_filename

        db.commit()
        db.refresh(doc)

        logger.info(f"Document {doc_id} replaced and re-encrypted by user {current_user.id}")

        return DocumentResponse(
            document_id=doc.document_id,
            document_name=doc.filename,
            category=doc.category,
            file_size=doc.file_size,
            upload_date=doc.upload_date,
            last_accessed=doc.last_accessed,
            encrypted=True,
            checksum=doc.checksum
        )
    except HTTPException as he:
        raise he
    except Exception as e:
        db.rollback()
        logger.error(f"Replace/re-encrypt failed for {doc_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Document replacement failed: {e}"
        )
