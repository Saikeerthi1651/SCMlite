import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import logging
from auth.routes import auth_router, shipment_router, device_router,admin_router

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

app = FastAPI(
    title="SCM API",
    description="Supply Chain Management System",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")

# Import and include routers after app is created

app.include_router(auth_router(), prefix="/auth", tags=["Authentication"])
app.include_router(shipment_router(), prefix="/shipment", tags=["Shipments"])
app.include_router(device_router(), prefix="/device", tags=["Device Data"])
app.include_router(admin_router(), prefix="/admin",tags=["Admin"])

@app.get("/", include_in_schema=False)
async def redirect_to_frontend():
    return RedirectResponse(url="/frontend/index.html", status_code=302)

@app.get("/health", tags=["System"])
async def health_check():
    return {"status": "healthy"}