from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from app.digilocker.models import Document
from app.digilocker import encryption
from app.digilocker.schemas import DocumentResponse, DocumentListResponse
from datetime import datetime
import logging
import uuid
from fastapi import HTTPException, status

logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS = {"pdf", "docx", "png", "jpg", "jpeg", "zip"}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
STORAGE_LIMIT = 500 * 1024 * 1024  # 500MB


def upload_document(
    user_id: str,
    file_bytes: bytes,
    filename: str,
    category: str,
    description: str = None,
    db: Session = None
) -> DocumentResponse:
    """
    Validates, encrypts, and uploads a document to the database.
    Verifies file size, file extensions, and storage limits for the user.
    """
    file_size = len(file_bytes)

    # 1. Validate File Size
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds maximum allowed size of 50MB. Received: {file_size / (1024 * 1024):.2f}MB"
        )

    # 2. Validate File Extension
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type '.{ext}' is not supported. Allowed formats: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    # 3. Check Storage Capacity Limit
    current_storage = db.query(func.sum(Document.file_size)).filter(Document.user_id == user_id).scalar() or 0
    if current_storage + file_size > STORAGE_LIMIT:
        remaining_space = STORAGE_LIMIT - current_storage
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Storage limit of 500MB exceeded. Remaining: {remaining_space / (1024 * 1024):.2f}MB. New file size: {file_size / (1024 * 1024):.2f}MB"
        )

    try:
        # 4. Encrypt File Bytes via AES-256-GCM
        enc_result = encryption.encrypt_file(file_bytes, user_id)
        
        # 5. Create Document Record
        document_uuid = str(uuid.uuid4())
        doc = Document(
            user_id=user_id,
            document_id=document_uuid,
            filename=filename,
            category=category,
            file_size=file_size,
            encrypted_data=enc_result["ciphertext"],
            salt=enc_result["salt"],
            nonce=enc_result["nonce"],
            tag=enc_result["tag"],
            checksum=enc_result["checksum"],
            description=description,
            upload_date=datetime.utcnow(),
            last_accessed=datetime.utcnow()
        )
        db.add(doc)
        db.commit()
        db.refresh(doc)
        
        logger.info(f"Document {document_uuid} successfully uploaded and encrypted for user {user_id}")
        
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
        logger.error(f"Error encrypting or saving document: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Document upload failed due to encryption/database failure: {e}"
        )


def download_document(user_id: str, doc_id: str, db: Session) -> bytes:
    """
    Decrypts and returns file bytes for a document. Verifies user ownership and checksum integrity.
    """
    doc = db.query(Document).filter(Document.document_id == doc_id).first()
    
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID {doc_id} not found"
        )
        
    if doc.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access Denied: You do not own this document."
        )

    try:
        # Decrypt ciphertext
        plaintext = encryption.decrypt_file(
            ciphertext=doc.encrypted_data,
            salt=doc.salt,
            nonce=doc.nonce,
            tag=doc.tag,
            user_id=user_id
        )

        # Verify checksum integrity
        integrity_ok = encryption.verify_file_integrity(plaintext, doc.checksum)
        if not integrity_ok:
            logger.warning(f"Integrity check failed for document {doc_id}. Checksums do not match.")
            # We raise an HTTP error to protect from serving tampered files
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Security validation failed: Stored file checksum does not match decrypted content."
            )

        # Update last_accessed metadata
        doc.last_accessed = datetime.utcnow()
        db.commit()

        # Audit log trail
        logger.info(f"Audit log: User {user_id} downloaded document {doc_id} at {datetime.utcnow().isoformat()}")
        
        return plaintext

    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Failed to download/decrypt document {doc_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Document decryption or verification failed: {e}"
        )


def list_documents(
    user_id: str,
    db: Session,
    category_filter: str = None,
    page: int = 1,
    limit: int = 10
) -> DocumentListResponse:
    """
    Lists paginated metadata logs of uploaded documents with usage calculations.
    """
    try:
        query = db.query(Document).filter(Document.user_id == user_id)
        
        if category_filter:
            allowed = ["certificates", "transcripts", "documents", "certificates_backup"]
            if category_filter not in allowed:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid category filter. Must be one of: {', '.join(allowed)}"
                )
            query = query.filter(Document.category == category_filter)

        total_docs = query.count()
        
        # Paginated fetch
        offset = (page - 1) * limit
        docs = query.order_by(Document.upload_date.desc()).offset(offset).limit(limit).all()

        # Storage totals for user
        total_used = db.query(func.sum(Document.file_size)).filter(Document.user_id == user_id).scalar() or 0

        # Build response objects list
        document_responses = []
        for doc in docs:
            document_responses.append(DocumentResponse(
                document_id=doc.document_id,
                document_name=doc.filename,
                category=doc.category,
                file_size=doc.file_size,
                upload_date=doc.upload_date,
                last_accessed=doc.last_accessed,
                encrypted=True,
                checksum=doc.checksum
            ))

        return DocumentListResponse(
            total_documents=total_docs,
            category_filter=category_filter,
            documents=document_responses,
            storage_used=total_used,
            storage_limit=STORAGE_LIMIT
        )
        
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error listing documents: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error compiling document lists"
        )


def delete_document(user_id: str, doc_id: str, db: Session) -> bool:
    """
    Removes document record securely. Owner-only deletion checked.
    """
    try:
        doc = db.query(Document).filter(Document.document_id == doc_id).first()
        
        if not doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document with ID {doc_id} not found"
            )
            
        if doc.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access Denied: You do not own this document."
            )

        db.delete(doc)
        db.commit()
        
        logger.info(f"Audit log: User {user_id} deleted document {doc_id} at {datetime.utcnow().isoformat()}")
        return True
        
    except HTTPException as he:
        raise he
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to delete document {doc_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to execute document deletion"
        )


def get_storage_usage(user_id: str, db: Session) -> dict:
    """
    Retrieves database storage statistics.
    """
    used = db.query(func.sum(Document.file_size)).filter(Document.user_id == user_id).scalar() or 0
    percentage = (used / STORAGE_LIMIT) * 100.0 if STORAGE_LIMIT > 0 else 0
    return {
        "used_bytes": used,
        "limit_bytes": STORAGE_LIMIT,
        "percentage": round(percentage, 2)
    }
