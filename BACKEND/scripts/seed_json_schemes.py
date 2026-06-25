"""
Seed welfare schemes from a JSON file into the database and Pinecone.
Run: python scripts/seed_json_schemes.py
"""
import sys
import os
import json
import logging
import uuid

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from app.database import SessionLocal, init_db
from app.welfare.models import WelfareScheme
from app.welfare.rag import welfare_rag
from app.shared.embeddings import embeddings_client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

JSON_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "schemes.json")

def load_from_json():
    if not os.path.exists(JSON_PATH):
        logger.error(f"❌ Could not find {JSON_PATH}. Please create this file with your data.")
        sys.exit(1)

    with open(JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    schemes_list = data.get("schemes", [])
    if not schemes_list:
        logger.error("❌ No schemes found in the JSON file.")
        sys.exit(1)

    db = SessionLocal()
    added = 0
    try:
        for scheme in schemes_list:
            meta = scheme.get("metadata", {})
            name = meta.get("scheme_name", "Unknown Scheme")
            
            # Check if exists
            existing = db.query(WelfareScheme).filter(WelfareScheme.name == name).first()
            if existing:
                logger.info(f"Skipping {name}, already exists in DB.")
                continue

            text_content = scheme.get("text", "")
            scheme_id = str(uuid.uuid4())
            
            logger.info(f"Embedding and adding: {name}")
            try:
                embedding_vector = embeddings_client.embed_text(text_content)
            except Exception as e:
                logger.warning(f"Could not embed scheme '{name}': {e}")
                embedding_vector = None

            db_scheme = WelfareScheme(
                id=scheme_id,
                name=name,
                description=text_content,  # Storing the full text so the frontend has all details
                scheme_type=meta.get("scheme_type", "Government Scheme"),
                provider=meta.get("provider", "Government of India"),
                application_url=meta.get("website", ""),
                embedding_text=text_content,
                embedding_vector=embedding_vector
            )
            db.add(db_scheme)

            # Upsert into Pinecone
            if embedding_vector:
                try:
                    # We pass the full text as part of metadata so RAG can use it
                    pinecone_metadata = {
                        "name": name,
                        "description": text_content,
                        "scheme_type": db_scheme.scheme_type,
                        "provider": db_scheme.provider,
                        "scheme_status": "active"
                    }
                    welfare_rag.upsert_scheme(
                        scheme_id=scheme_id,
                        embedding=embedding_vector,
                        metadata=pinecone_metadata
                    )
                except Exception as e:
                    logger.warning(f"Pinecone upsert failed for '{name}': {e}")

            added += 1

        db.commit()
        logger.info(f"✅ Loaded {added} new welfare schemes from JSON!")
        
    except Exception as e:
        logger.error(f"❌ Error loading schemes: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    logger.info("Initializing DB and loading JSON data...")
    init_db()
    load_from_json()
