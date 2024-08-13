from abc import ABC, abstractmethod

from api.interfaces import ListingRequest


class Integration(ABC):
    @abstractmethod
    def list(self, request: ListingRequest) -> bool:
        raise NotImplementedError
