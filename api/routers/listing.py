from fastapi import APIRouter

from api.interfaces import ListingRequest

router = APIRouter()

@router.post("/", name="Create a listing")
async def createListing(request: ListingRequest):
    return {"message": "Listing created successfully!"}