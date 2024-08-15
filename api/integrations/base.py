import os
from abc import ABC, abstractmethod

from dotenv import load_dotenv
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from api.interfaces import ListingRequest, ListingResult
from selenium import webdriver

load_dotenv()


class Integration(ABC):
    def __init__(self):
        self.DEFAULT_TIMEOUT = 10

    @abstractmethod
    def list(self, request: ListingRequest) -> ListingResult:
        raise NotImplementedError

    def getDriver(self) -> webdriver.Chrome | webdriver.Remote:
        options = webdriver.ChromeOptions()
        options.add_argument("--disable-notifications")
        # options.add_argument("--headless")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920,1080")

        if os.getenv("IN_DOCKER_CONTAINER", False):
            options.add_argument("--user-data-dir=/home/seluser/selenium")
            driver = webdriver.Remote(
                options=options, command_executor="http://selenium:4444/wd/hub"
            )
        else:
            service = Service(ChromeDriverManager().install())
            options.add_argument("--user-data-dir=selenium")
            driver = webdriver.Chrome(options=options, service=service)

        return driver
