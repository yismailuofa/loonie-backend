from typing import Annotated

from fastapi import APIRouter, File, Form, UploadFile

from api.interfaces import Condition, ListingResult, ListingResults

router = APIRouter()


@router.post("/", name="Create a listing")
async def createListing(
    title: Annotated[str, Form()],
    description: Annotated[str, Form()],
    size: Annotated[str, Form()],
    price: Annotated[str, Form()],
    condition: Annotated[Condition, Form()],
    tags: Annotated[str, Form()],
    images: Annotated[list[UploadFile], File()],
) -> ListingResults:
    print(
        {
            "message": "Listing created successfully",
            "title": title,
            "description": description,
            "size": size,
            "price": price,
            "condition": condition,
            "tags": tags,
            "images": [image.filename for image in images],
        }
    )

    return ListingResults(
        kijiji=ListingResult(url="https://www.kijiji.ca", success=True),
        marketplace=ListingResult(url="https://www.marketplace.com", success=True),
    )
