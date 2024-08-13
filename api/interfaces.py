from enum import Enum

from fastapi import File, Form, UploadFile
from pydantic import BaseModel


class Condition(str, Enum):
    New = "New"
    UsedLikeNew = "Used - Like New"
    UsedGood = "Used - Good"
    UsedFair = "Used - Fair"


class ListingRequest(BaseModel):
    title: str = Form(...)
    description: str = Form(...)
    size: str = Form(...)
    price: str = Form(...)
    condition: Condition = Form(...)
    tags: str = Form(...)
    images: list[UploadFile] = File(...)
