from enum import Enum

from pydantic import BaseModel


class Condition(str, Enum):
    New = "New"
    UsedLikeNew = "Used - Like New"
    UsedGood = "Used - Good"
    UsedFair = "Used - Fair"


class ListingResult(BaseModel):
    url: str
    success: bool


class ListingResults(BaseModel):
    kijiji: ListingResult
    marketplace: ListingResult
