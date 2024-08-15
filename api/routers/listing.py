import os
from typing import Annotated

from fastapi import APIRouter, File, Form, UploadFile
from PIL import Image
from pillow_heif import register_heif_opener

from api.integrations.kijiji import KijijiIntegration
from api.integrations.marketplace import MarketplaceIntegration
from api.interfaces import Condition, ListingRequest, ListingResults

register_heif_opener()

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
            img = Image.open(image.file)
            img = img.convert("RGB")
            img.save(f"temp/{image.filename}", "JPEG")

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
        m = MarketplaceIntegration().list(lr)
        k = KijijiIntegration().list(lr)

        return ListingResults(
            kijiji=k,
            marketplace=m,
        )

    finally:
        # remove temp images
        for image in imagePaths:
            os.remove(image)
