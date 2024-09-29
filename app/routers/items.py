from fastapi import APIRouter, Depends, HTTPException, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from app import crud, schemas
from app.database import get_db
from app.redis_cache import get_redis
import json

router = APIRouter()

templates = Jinja2Templates(directory="templates")

@router.get("/items/new", response_class=HTMLResponse)
async def get_form(request: Request):
    return templates.TemplateResponse("item_form.html", {"request": request})

@router.post("/items/", response_model=schemas.Item)
def create_item(title: str = Form(...), description: str = Form(...), db: Session = Depends(get_db)):
    item_data = schemas.ItemCreate(title=title, description=description)
    return crud.create_item(db=db, item=item_data)

@router.get("/items/{item_id}", response_model=schemas.Item)
def read_item(item_id: int, db: Session = Depends(get_db), r = Depends(get_redis)):
    cached_item = r.get(f"item:{item_id}")
    
    if cached_item:
        return json.loads(cached_item)
    
    db_item = crud.get_item(db, item_id=item_id)
    
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    
    r.set(f"item:{item_id}", json.dumps(schemas.Item.from_orm(db_item).dict()), ex=60)

    return db_item

@router.get("/items/", response_model=list[schemas.Item])
def read_items(db: Session = Depends(get_db)):
    items = crud.get_all_items(db)
    return items
