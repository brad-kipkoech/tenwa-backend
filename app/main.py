from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import Base, engine
from app.models import AdminUser, QuoteRequest, Shipment, ShipmentUpdate
from app.routes import admin, quotes, shipments


Base.metadata.create_all(bind=engine)


app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
)


allowed_origins = [
    "https://tenwatradingandlogistics.com",
    "https://www.tenwatradingandlogistics.com",
    "https://tenwa-frontend.vercel.app",
    "https://tenwa-frontend-md2gbto90-brad-klaus-projects.vercel.app",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

if settings.FRONTEND_URL and settings.FRONTEND_URL not in allowed_origins:
    allowed_origins.append(settings.FRONTEND_URL)


app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(quotes.router)
app.include_router(shipments.router)
app.include_router(admin.router)


@app.get("/")
def root():
    return {
        "message": "Tenwa Logistics API is running",
        "environment": settings.APP_ENV,
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
    }