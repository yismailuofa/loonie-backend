from fastapi import APIRouter

from .listing import router as listingRouter

router = APIRouter()

router.include_router(listingRouter, prefix="/listing", tags=["Listings"])
