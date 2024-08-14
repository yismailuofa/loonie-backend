from enum import Enum

from pydantic import BaseModel


class Condition(str, Enum):
    New = "New"
    UsedLikeNew = "Used - Like New"
    UsedGood = "Used - Good"
    UsedFair = "Used - Fair"

    def __str__(self):
        return self.value


class ListingResult(BaseModel):
    url: str
    success: bool


class ListingResults(BaseModel):
    kijiji: ListingResult
    marketplace: ListingResult


class ListingRequest(BaseModel):
    title: str
    description: str
    size: str
    price: str
    condition: Condition
    tags: str
    images: list[str]
