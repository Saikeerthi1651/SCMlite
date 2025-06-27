from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class User(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: str = "user"
    created_at: Optional[datetime] = None

class Login(BaseModel):
    email: EmailStr
    password: str

class Shipment(BaseModel):
    shipment_number: str
    route_details: str
    device: str
    po_number: str
    ndc_number: str
    serial_number: str
    container_number: str
    goods_type: str
    delivery_date: str
    delivery_number: str
    batch_id: str
    description: str
    created_by: str
    created_at: Optional[datetime] = None
    status: str = "pending"