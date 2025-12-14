# main.py
from fastapi import FastAPI, HTTPException, Depends
from sqlmodel import Field, Session, SQLModel, create_engine, select

from typing import Optional, List
from uuid import uuid4
import os

app = FastAPI(
    title="Majd's AI Engineer Sprint API",
    description="Week 1 Day 4 – FastAPI + PostgreSQL (Docker Compose)",
    version="1.0"
)

# SQLModel table definition
class Item(SQLModel, table=True):
    id: Optional[str] = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    name: str
    description: Optional[str] = None
    price: float
    category: str

# Database URL – will be overridden by Docker Compose env
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://postgres:password@localhost:5432/postgres")

# Sync engine for simplicity (async later if needed)
engine = create_engine(DATABASE_URL, echo=True)

# Create tables on startup
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

# Dependency to get DB session
def get_session():
    with Session(engine) as session:
        yield session

# CREATE
@app.post("/items/", response_model=Item)
def create_item(item: Item, session: Session = Depends(get_session)):
    session.add(item)
    session.commit()
    session.refresh(item)
    return item

# READ ALL
@app.get("/items/", response_model=List[Item])
def read_items(session: Session = Depends(get_session)):
    items = session.exec(select(Item)).all()
    return items

# READ ONE
@app.get("/items/{item_id}", response_model=Item)
def read_item(item_id: str, session: Session = Depends(get_session)):
    item = session.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

# UPDATE
@app.put("/items/{item_id}", response_model=Item)
def update_item(item_id: str, item_update: Item, session: Session = Depends(get_session)):
    item = session.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    update_data = item_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(item, key, value)
    session.add(item)
    session.commit()
    session.refresh(item)
    return item

# DELETE
@app.delete("/items/{item_id}")
def delete_item(item_id: str, session: Session = Depends(get_session)):
    item = session.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    session.delete(item)
    session.commit()
    return {"detail": "Item deleted"}

@app.get("/")
def read_root():
    return {"message": "FastAPI + PostgreSQL running! Go to /docs"}