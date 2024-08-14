import os
from typing import Annotated

from fastapi import APIRouter, File, Form, UploadFile

from api.integrations.marketplace import MarketplaceIntegration
from api.interfaces import Condition, ListingRequest, ListingResult, ListingResults

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

    if not os.path.exists("temp"):
        os.makedirs("temp")
    imagePaths = []

    for image in images:
        if not image.size:
            continue

        with open(f"temp/{image.filename}", "wb") as f:
            f.write(image.file.read())

        imagePaths.append(os.path.abspath(f"temp/{image.filename}"))

    lr = ListingRequest(
        title=title,
        description=description,
        size=size,
        price=price,
        condition=condition,
        tags=tags,
        images=imagePaths,
    )

    try:
        # k = KijijiIntegration().list(lr)
        k = ListingResult(
            url="https://www.kijiji.ca/p-select-category.html", success=True
        )
        m = ListingResult(url="https://www.facebook.com/marketplace", success=True)
        m = MarketplaceIntegration().list(lr)

        return ListingResults(
            kijiji=k,
            marketplace=m,
        )

    finally:
        # remove temp images
        for image in imagePaths:
            os.remove(image)
