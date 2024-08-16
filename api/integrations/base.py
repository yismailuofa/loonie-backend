import os
from abc import ABC, abstractmethod

from dotenv import load_dotenv

from api.interfaces import ListingRequest, ListingResult
from selenium import webdriver

load_dotenv()


class Integration(ABC):
    def __init__(self):
        self.DEFAULT_TIMEOUT = 25

    @abstractmethod
    def list(self, request: ListingRequest) -> ListingResult:
        raise NotImplementedError

    def getDriver(
        self, exec_name="selenium:4444"
    ) -> webdriver.Chrome | webdriver.Remote:
        options = webdriver.ChromeOptions()
        options.add_argument("--disable-notifications")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-extensions")
        options.add_argument("--window-size=1920,1080")
        # options.add_argument("--headless")

        if os.getenv("IN_DOCKER_CONTAINER", False):
            options.add_argument("--user-data-dir=/home/seluser/selenium")
            driver = webdriver.Remote(
                options=options, command_executor=f"http://{exec_name}/wd/hub"
            )
        else:
            options.add_argument("--user-data-dir=selenium")
            driver = webdriver.Chrome(options=options)

        return driver
