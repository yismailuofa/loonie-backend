import os

from dotenv import load_dotenv
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

from api.integrations.base import Integration
from api.interfaces import ListingResult
from api.logger import logger

load_dotenv()


class KijijiIntegration(Integration):
    def list(self, request) -> ListingResult:
        driver = self.getDriver("selenium-kj:4444")
        try:
            wait = WebDriverWait(driver, self.DEFAULT_TIMEOUT)

            driver.get("https://www.kijiji.ca/p-select-category.html")

            wait.until(
                EC.any_of(
                    EC.presence_of_element_located((By.ID, "username")),
                    EC.presence_of_element_located((By.NAME, "AdTitleForm")),
                )
            )

            if not driver.find_elements(By.ID, "username"):
                logger.debug("Already logged in to Kijiji")
            else:
                if not (user := os.getenv("KIJIJI_USERNAME")) or not (
                    password := os.getenv("KIJIJI_PASSWORD")
                ):
                    logger.debug("Missing Facebook credentials")
                    raise Exception("Missing Facebook credentials")

                logger.debug("Logging in to Kijiji")
                wait.until(lambda d: d.find_element(By.ID, "username")).send_keys(user)
                wait.until(lambda d: d.find_element(By.ID, "password")).send_keys(
                    password, Keys.RETURN
                )

            logger.debug("Adding title")
            wait.until(lambda d: d.find_element(By.NAME, "AdTitleForm")).send_keys(
                request.title, Keys.RETURN
            )

            logger.debug("Selecting category")
            wait.until(
                lambda d: d.find_element(By.XPATH, '//span[text()="Buy & Sell"]')
            ).click()
            wait.until(
                lambda d: d.find_element(By.XPATH, '//span[text()="Clothing"]')
            ).click()
            wait.until(
                lambda d: d.find_element(By.XPATH, '//span[text()="Men\'s Shoes"]')
            ).click()

            wait.until(
                lambda d: d.current_url.startswith(
                    "https://www.kijiji.ca/p-post-ad.html"
                )
            )

            wait.until(lambda d: d.find_element(By.ID, "OFFER1"))

            logger.debug("Adding rest of form")

            if request.images:
                imageInput = driver.find_element(
                    By.XPATH,
                    "//input[@accept='image/jpeg,.jpg,.jpeg,image/png,.png,image/gif,.gif,image/bmp,.bmp']",
                )
                joinedPaths = "\n".join(request.images)
                imageInput.send_keys(joinedPaths)

                # wait for images to upload
                wait.until(
                    lambda d: len(
                        d.find_elements(
                            By.XPATH,
                            '//ol[@id="MediaUploadedImages"]/li[contains(@class, "thumbnail")]',
                        )
                    )
                    == len(request.images)
                )

            wait.until(
                lambda d: d.find_element(
                    By.XPATH, '//label[text()="Willing to drop-off / deliver"]'
                )
            ).click()
            wait.until(
                lambda d: d.find_element(
                    By.XPATH, '//label[text()="Willing to ship the item"]'
                )
            ).click()
            wait.until(
                lambda d: d.find_element(
                    By.XPATH, '//label[text()="Offer curbside pick up"]'
                )
            ).click()

            wait.until(
                lambda d: d.find_element(
                    By.XPATH, '//label[text()="Offer cashless payment"]'
                )
            ).click()
            wait.until(
                lambda d: d.find_element(By.XPATH, '//label[text()="Cash accepted"]')
            ).click()

            conditionSelect = Select(
                wait.until(lambda d: d.find_element(By.ID, "condition_s"))
            )
            index = list(map(lambda x: x.text.lower(), conditionSelect.options)).index(
                request.condition.value.lower()
            )
            conditionSelect.select_by_index(index)

            sizeSelect = Select(wait.until(lambda d: d.find_element(By.ID, "size_s")))
            if not request.size.replace(".", "").isdigit():
                request.size = "Other"
            index = list(map(lambda x: x.text, sizeSelect.options)).index(request.size)
            sizeSelect.select_by_index(index)

            wait.until(lambda d: d.find_element(By.ID, "pstad-descrptn")).send_keys(
                request.description
            )

            if request.tags:
                joinedTags = ",".join(request.tags.split("\n")) + ","
                driver.find_element(By.ID, "pstad-tagsInput").send_keys(joinedTags)

            wait.until(lambda d: d.find_element(By.ID, "PriceAmount")).send_keys(
                request.price
            )

            logger.debug("Posting ad")
            wait.until(
                lambda d: d.find_element(By.XPATH, '//button[text()="Post Your Ad"]')
            ).click()

            longWait = WebDriverWait(driver, 60)
            longWait.until(EC.title_contains(request.title))

            logger.debug("Successfully listed on Kijiji")

            return ListingResult(
                url="https://www.kijiji.ca/m-my-ads/active/", success=True
            )

        except Exception as e:
            logger.debug("Failed to list on Kijiji: ", exc_info=e)
            return ListingResult(url="", success=False)
        finally:
            driver.quit()
