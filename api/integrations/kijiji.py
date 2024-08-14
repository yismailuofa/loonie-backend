from api.integrations.base import Integration
from api.interfaces import ListingResult


class KijijiIntegration(Integration):
    def list(self, request) -> ListingResult:
        return ListingResult(url="https://kijiji.ca/listing", success=True)
