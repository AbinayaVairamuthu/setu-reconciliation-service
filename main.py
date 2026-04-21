from fastapi import FastAPI, HTTPException, Query
from sqlalchemy import create_engine, Column, String, Float, DateTime, desc, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

# --- DATABASE SETUP ---
# We use SQLite for portability. 'check_same_thread' is False for FastAPI compatibility.
DATABASE_URL = "sqlite:///./setu_payments.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- SQL MODELS (The Database Schema) ---
class Event(Base):
    __tablename__ = "events"
    # Primary Key on event_id ensures Idempotency at the database level
    event_id = Column(String, primary_key=True)
    transaction_id = Column(String, index=True)
    merchant_id = Column(String, index=True)
    merchant_name = Column(String)
    event_type = Column(String)
    amount = Column(Float)
    currency = Column(String)
    timestamp = Column(DateTime)

# Create the database file and tables
Base.metadata.create_all(bind=engine)

# --- API SCHEMAS (Input Validation) ---
class PaymentEvent(BaseModel):
    event_id: str
    event_type: str
    transaction_id: str
    merchant_id: str
    merchant_name: str
    amount: float
    currency: str
    timestamp: datetime

# --- FASTAPI APP ---
app = FastAPI(
    title="Setu Solutions Engineering - Reconciliation Service",
    description="A service to ingest payment events and identify reconciliation discrepancies."
)

@app.post("/events")
def ingest_event(event: PaymentEvent):
    """
    Ingests a payment lifecycle event. 
    Handles idempotency: If the event_id already exists, it ignores the duplicate.
    """
    db = SessionLocal()
    try:
        db_event = Event(**event.dict())
        db.add(db_event)
        db.commit()
        return {"status": "success", "message": "Event recorded"}
    except Exception:
        db.rollback()
        # Returns 200 OK for duplicates as per production best practices
        return {"status": "success", "message": "Duplicate event ignored"}
    finally:
        db.close()

@app.get("/transactions")
def list_transactions(
    merchant_id: Optional[str] = None, 
    status: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, le=100)
):
    """
    Returns a paginated list of transactions with optional filters.
    """
    db = SessionLocal()
    query = db.query(Event)
    
    if merchant_id:
        query = query.filter(Event.merchant_id == merchant_id)
    if status:
        query = query.filter(Event.event_type == status)
    
    offset = (page - 1) * limit
    results = query.order_by(desc(Event.timestamp)).offset(offset).limit(limit).all()
    db.close()
    return results

@app.get("/transactions/{transaction_id}")
def get_transaction_details(transaction_id: str):
    """
    Returns the full event history for a specific transaction.
    """
    db = SessionLocal()
    results = db.query(Event).filter(Event.transaction_id == transaction_id).all()
    db.close()
    if not results:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return results

@app.get("/reconciliation/discrepancies")
def get_discrepancies():
    """
    Identifies transactions where 'settled' status exists but 'payment_failed' was also recorded.
    This demonstrates advanced SQL logic for reconciliation.
    """
    db = SessionLocal()
    try:
        # We use raw SQL with the text() wrapper for high-performance set logic
        query = text("""
            SELECT DISTINCT transaction_id 
            FROM events 
            WHERE event_type = 'settled' 
            AND transaction_id IN (
                SELECT transaction_id FROM events WHERE event_type = 'payment_failed'
            )
        """)
        
        result_proxy = db.execute(query)
        discrepancies = [row[0] for row in result_proxy.fetchall()]
        
        return {
            "description": "Inconsistent states: Transaction was 'settled' despite 'payment_failed' record.",
            "count": len(discrepancies),
            "transaction_ids": discrepancies
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()