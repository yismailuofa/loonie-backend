import os
from concurrent.futures import ThreadPoolExecutor
from typing import Annotated

from dotenv import load_dotenv
from fastapi import APIRouter, File, Form, UploadFile
from PIL import Image, ImageOps
from pillow_heif import register_heif_opener

from api.integrations.kijiji import KijijiIntegration
from api.integrations.marketplace import MarketplaceIntegration
from api.interfaces import Condition, ListingRequest, ListingResults
from api.logger import logger

register_heif_opener()

load_dotenv()

router = APIRouter()


@router.post("", name="Create a listing")
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

        img = Image.open(image.file)
        img = ImageOps.exif_transpose(img)
        img.save(f"temp/{image.filename}")  # type: ignore
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
        if os.getenv("IN_DOCKER_CONTAINER", False):
            logger.debug("Multithreading in Docker container")

            with ThreadPoolExecutor(max_workers=2) as executor:
                m = executor.submit(MarketplaceIntegration().listWithRetries, lr)
                k = executor.submit(KijijiIntegration().listWithRetries, lr)

                m = m.result()
                k = k.result()
        else:
            k = KijijiIntegration().list(lr)
            m = MarketplaceIntegration().list(lr)

        return ListingResults(
            kijiji=k,
            marketplace=m,
        )

    finally:
        # remove temp images
        for image in imagePaths:
            os.remove(image)
