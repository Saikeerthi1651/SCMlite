import os
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, Depends, Form, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from pymongo import MongoClient
from datetime import datetime
from typing import Optional
import logging
import requests
from auth.models import hash_password, verify_password
from auth.auth_handler import sign_jwt, decode_jwt
from functools import wraps

load_dotenv()
logger = logging.getLogger(__name__)

# Database setup
MONGODB_URI = os.getenv("MONGODB_URI")
DB_NAME = os.getenv("DB_NAME", "scm_db")
client = MongoClient(MONGODB_URI)
db = client[DB_NAME]

# Collections
USERS_COLLECTION = os.getenv("USERS_COLLECTION", "users")
SHIPMENTS_COLLECTION = os.getenv("SHIPMENTS_COLLECTION", "shipments")
SENSOR_READINGS_COLLECTION = os.getenv("SENSOR_READINGS_COLLECTION", "sensor_readings")

# Indexes
db[USERS_COLLECTION].create_index("email", unique=True)
db[SHIPMENTS_COLLECTION].create_index("shipment_number")
db[SENSOR_READINGS_COLLECTION].create_index("timestamp")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

def verify_recaptcha(token: str) -> bool:
    try:
        secret = os.getenv("RECAPTCHA_SECRET")
        if not secret:
            logger.error("RECAPTCHA_SECRET not found")
            return False
            
        response = requests.post(
            "https://www.google.com/recaptcha/api/siteverify",
            data={"secret": secret, "response": token},
            timeout=5
        )
        response.raise_for_status()
        return response.json().get("success", False)
    except Exception as e:
        logger.error(f"reCAPTCHA error: {str(e)}")
        return False

def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = decode_jwt(token)
    if "error" in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=payload["error"],
            headers={"WWW-Authenticate": "Bearer"},
        )
    return payload

def admin_required(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        current_user = kwargs.get("current_user")
        if not current_user or current_user.get("role") != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admins only"
            )
        return await func(*args, **kwargs)
    return wrapper

def auth_router():
    router = APIRouter()
    
    @router.post("/signup")
    async def signup(
        name: str = Form(...),
        email: str = Form(...),
        password: str = Form(...),
        recaptcha_token: Optional[str] = Form(None)
    ):
        try:
            # Validate inputs
            if not all([name, email, password]):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="All fields are required"
                )

            if "@" not in email or "." not in email.split("@")[1]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid email format"
                )

            if len(password) < 8:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Password must be at least 8 characters"
                )

            if os.getenv("RECAPTCHA_ENABLED", "false").lower() == "true":
                if not recaptcha_token or not verify_recaptcha(recaptcha_token):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="reCAPTCHA verification failed"
                    )

            if db[USERS_COLLECTION].find_one({"email": email}):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
            
            role = "admin" if email.endswith("@admin.com") else "user"
            user_data = {
                "name": name, 
                "email": email,
                "password": hash_password(password),
                "role": role,
                "created_at": datetime.utcnow()
            }
            
            result = db[USERS_COLLECTION].insert_one(user_data)
            if not result.inserted_id:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to create user"
                )

            return JSONResponse(
                status_code=status.HTTP_201_CREATED,
                content={"message": "User created successfully"}
            )
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Signup error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Registration failed"
            )

    @router.post("/login")
    async def login(
        form_data: OAuth2PasswordRequestForm = Depends(),
        recaptcha_token: Optional[str] = Form(None)
    ):
        try:
            if os.getenv("RECAPTCHA_ENABLED", "false").lower() == "true":
                if not recaptcha_token or not verify_recaptcha(recaptcha_token):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="reCAPTCHA verification failed"
                    )

            user = db[USERS_COLLECTION].find_one({"email": form_data.username})
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid credentials"
                )

            if not verify_password(form_data.password, user["password"]):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid credentials"
                )

            token = sign_jwt(user["email"], user["role"], user["name"])
            response = JSONResponse({
                "access_token": token["access_token"],
                "token_type": "bearer",
                "user": {
                    "name": user["name"],
                    "email": user["email"],
                    "role": user["role"]
                }
            })
            response.set_cookie(
                key="access_token",
                value=token["access_token"],
                httponly=True,
                secure=os.getenv("ENVIRONMENT") == "production",
                samesite="lax"
            )
            return response
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Login failed"
            )

    @router.post("/token")
    async def login_for_token(form_data: OAuth2PasswordRequestForm = Depends()):
        user = db[USERS_COLLECTION].find_one({"email": form_data.username})
        if not user or not verify_password(form_data.password, user["password"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return sign_jwt(user["email"], user["role"], user["name"])

    @router.get("/me")
    async def read_users_me(current_user: dict = Depends(get_current_user)):
        return current_user

    @router.get("/logout")
    async def logout():
        response = JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "Logged out successfully"}
        )
        response.delete_cookie("access_token")
        return response

    return router

def shipment_router():
    router = APIRouter()

    @router.get("/all")
    async def get_all_shipments():
        try:
            shipments = list(db[SHIPMENTS_COLLECTION].find({}))
            for shipment in shipments:
                shipment["_id"] = str(shipment["_id"])
            return {"shipments": shipments}
        except Exception as e:
            logger.error(f"Error getting shipments: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve shipments"
            )

    @router.post("/create_shipment")
    async def create_shipment(
        current_user: dict = Depends(get_current_user),
        shipment_number: str = Form(...),
        route_details: str = Form(...),
        device: str = Form(...),
        goods_type: str = Form(...),
        delivery_date: str = Form(...),
        batch_id: str = Form(...),
        po_number: Optional[str] = Form(None),
        ndc_number: Optional[str] = Form(None),
        serial_number: Optional[str] = Form(None),
        container_number: Optional[str] = Form(None),
        delivery_number: Optional[str] = Form(None),
        description: Optional[str] = Form(None)
    ):
        try:
            # Validate required fields
            if not all([shipment_number, route_details, device, goods_type, delivery_date, batch_id]):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Missing required fields"
                )

            shipment_data = {
                "shipment_number": shipment_number,
                "route_details": route_details,
                "device": device,
                "goods_type": goods_type,
                "delivery_date": delivery_date,
                "batch_id": batch_id,
                "created_by": current_user["email"],
                "created_at": datetime.utcnow(),
                "status": "pending"
            }

            # Add optional fields if provided
            optional_fields = {
                "po_number": po_number,
                "ndc_number": ndc_number,
                "serial_number": serial_number,
                "container_number": container_number,
                "delivery_number": delivery_number,
                "description": description
            }
            
            for field, value in optional_fields.items():
                if value is not None:
                    shipment_data[field] = value

            result = db[SHIPMENTS_COLLECTION].insert_one(shipment_data)
            if not result.inserted_id:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to create shipment"
                )

            return JSONResponse(
                status_code=status.HTTP_201_CREATED,
                content={"message": "Shipment created successfully"}
            )
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Create shipment error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create shipment"
            )

    @router.get('/search_shipments')
    async def search_shipments(current_user: dict = Depends(get_current_user)):
        try:
            user_email = current_user["email"]
            shipments = list(db[SHIPMENTS_COLLECTION].find({"created_by": user_email}))
            
            for shipment in shipments:
                shipment["_id"] = str(shipment["_id"])
                # Convert datetime fields to string
                for key, value in shipment.items():
                    if isinstance(value, datetime):
                        shipment[key] = value.isoformat()
            
            return {"shipments": shipments}
        except Exception as e:
            logger.error(f"Error fetching user shipments: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error"
            )

    return router

def device_router():
    router = APIRouter()

    @router.get("/data")
    async def get_device_data(
        current_user: dict = Depends(get_current_user),
        limit: int = 20
    ):
        try:
            if current_user.get("role") != "admin":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Admins only"
                )
            
            data = list(db[SENSOR_READINGS_COLLECTION].find()
                       .sort("timestamp", -1)
                       .limit(limit))
            
            for item in data:
                item["_id"] = str(item["_id"])
            
            return {"data": data}
        except Exception as e:
            logger.error(f"Error getting device data: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve device data"
            )

    return router

def admin_router():
    router = APIRouter(dependencies=[Depends(get_current_user)])

    @router.get("/tools")
    async def admin_tools(current_user: dict = Depends(get_current_user)):
        if current_user.get("role") != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admins only"
            )
        return {"message": "Admin tools available"}

    @router.get("/users")
    async def get_users(
        current_user: dict = Depends(get_current_user),
        email: Optional[str] = None
    ):
        try:
            if current_user.get("role") != "admin":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Admins only"
                )
            
            query = {}
            if email:
                query["email"] = {"$regex": email, "$options": "i"}
            
            users = list(db[USERS_COLLECTION].find(query))
            for user in users:
                user["_id"] = str(user["_id"])
            
            return {"users": users}
        except Exception as e:
            logger.error(f"Error getting users: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve users"
            )

    @router.post("/users/{email}/role")
    async def change_user_role(
        email: str,
        role_data: dict,
        current_user: dict = Depends(get_current_user)
    ):
        try:
            if current_user.get("role") != "admin":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Admins only"
                )
            
            if role_data.get("role") not in ["admin", "user"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid role specified"
                )
            
            result = db[USERS_COLLECTION].update_one(
                {"email": email},
                {"$set": {"role": role_data["role"]}}
            )
            
            if result.modified_count == 0:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            
            return {"message": "Role updated successfully"}
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error updating role: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update role"
            )

    @router.delete("/users/{email}")
    async def delete_user(
        email: str,
        current_user: dict = Depends(get_current_user)
    ):
        try:
            if current_user.get("role") != "admin":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Admins only"
                )
            
            result = db[USERS_COLLECTION].delete_one({"email": email})
            
            if result.deleted_count == 0:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            
            return {"message": "User deleted successfully"}
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error deleting user: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete user"
            )

    return router
     
     