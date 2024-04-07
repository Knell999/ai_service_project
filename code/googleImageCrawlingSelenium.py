import asyncio
import datetime
import json
import logging
import pathlib
import signal
import ssl
import certifi
import requests
import aiofiles  # pip install aiofiles
import aiohttp  # pip install aiohttp
import urllib3

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import (
    WebDriverException,
    TimeoutException,
    ElementClickInterceptedException,
    NoSuchElementException,
)


def clear_sessions(session_id=None):
    """
    여기서 우리는 고아 세션을 쿼리하고 삭제합니다
    문서: https://www.selenium.dev/documentation/grid/advanced_features/endpoints/
    :param session_id: 삭제할 세션의 ID입니다.
    :return: None
    """
    url = "http://127.0.0.1:4444"

    if not session_id:
        # delete all sessions
        r = requests.get("{}/status".format(url))
        data = json.loads(r.text)
        for node in data["value"]["nodes"]:
            for slot in node["slots"]:
                if slot["session"]:
                    id = slot["session"]["sessionId"]
                    r = requests.delete("{}/session/{}".format(url, id))
    else:
        # delete session from params
        r = requests.delete("{}/session/{}".format(url, session_id))


# Constants
HUB_URL = "http://localhost:4444/wd/hub"
BROWSER_OPTIONS = {
    "chrome": ChromeOptions(),
    # "firefox": FirefoxOptions(),
    # "edge": EdgeOptions(),
}

logging.basicConfig(
    format="%(asctime)s - %(message)s",
    filename=datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S.log"),
    level=logging.INFO,
)


ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE
ssl_context.options |= 0x4  # OP_LEGACY_SERVER_CONNECT

# surpress InsecureRequestWarning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class ImageDownloader:
    """
    이미지 다운로더 클래스입니다. 브라우저 이름과 검색어를 받아 이미지를 다운로드합니다.
    """

    def __init__(self, browser_name, search_for):
        """
        ImageDownloader 클래스의 생성자입니다.
        :param browser_name: 사용할 브라우저의 이름입니다.
        :param search_for: 검색할 키워드입니다.
        """
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate",
            # "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }
        self.browser = self.setup_driver(browser_name)
        self.search_for = search_for
        self.scroll_amount = 2

        self.successful_downloads = 0
        self.skipped_downloads = 0
        self.total_before = 0

    def setup_driver(self, browser_name):
        """
        브라우저 드라이버를 설정합니다.
        :param browser_name: 설정할 브라우저의 이름입니다.
        :return: 설정된 브라우저 드라이버를 반환합니다.
        """
        try:
            options = BROWSER_OPTIONS.get(browser_name)
            # user agent options deprecated???
            options.add_argument("--ignore-certificate-errors")
            options.add_argument("--ignore-ssl-errors")
            options.add_argument("--no-sandbox")
            driver = webdriver.Remote(HUB_URL, options=options)
            return driver
        except Exception as e:  # Catch WebDriverException
            logging.error(f"Error setting up {browser_name} WebDriver: {e}")
            return None

    async def is_website_available(self, url):
        """
        웹 사이트가 사용 가능한지 확인합니다.
        :param url: 확인할 웹 사이트의 URL입니다.
        :return: 웹 사이트의 사용 가능 여부를 반환합니다.
        """
        async with aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(ssl=ssl_context)
        ) as session:
            try:
                async with session.get(url, headers=self.headers) as response:
                    return response.status // 100 == 2
            except Exception as e:
                logging.error(f"Error checking website availability: {e}")
                return False

    async def main_task(self, driver, keyword, path):
        """
        주요 작업을 수행합니다. 이미지 URL을 가져오고 이미지를 다운로드합니다.
        :param driver: 사용할 브라우저 드라이버입니다.
        :param keyword: 검색할 키워드입니다.
        :param path: 이미지를 저장할 경로입니다.
        """
        try:
            url = f"https://www.google.com/search?as_st=y&as_q={keyword}&as_epq=&as_oq=&as_eq=&imgsz=l&imgar=&imgcolor=&imgtype=face&cr=&as_sitesearch=&as_filetype=&tbs=&udm=2"
            driver.get(url)
            logging.info(f"Getting image URLs for {keyword}...")
            last_height = driver.execute_script("return document.body.scrollHeight")
            image_urls = []
            for i in range(self.scroll_amount):  # scroll twice
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                await asyncio.sleep(1)
                logging.info(f"Scrolling {i} out of {self.scroll_amount}...")
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height

            logging.info("Loading image elements...")
            image_elements = WebDriverWait(driver, 30).until(
                EC.presence_of_all_elements_located(
                    # (By.XPATH, '//g-img/img[starts-with(@id, "dimg_")]') # blocked click by another element in front
                    (By.XPATH, '//h3[@class="ob5Hkd"]')
                )
            )
            print("image_elements : ", len(image_elements))
            self.total_before = len(image_elements)
            logging.info("Clicking on images...")

            for image in image_elements:
                try:
                    image.click()
                    await asyncio.sleep(0.75)
                    image_url_element = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located(
                            (By.XPATH, '//div[@class="v6bUne"]//img[@class="sFlh5c pT0Scc iPVvYb"]')
                        )
                    ).get_attribute("src")
                    logging.info(f"Found image URL: {str(image_url_element)}")

                    if not await self.is_website_available(image_url_element):
                        logging.error(f"Website {image_url_element} is not available.")
                        continue

                    image_urls.append(image_url_element)
                except (TimeoutException, NoSuchElementException):
                    logging.error(
                        f"Error getting image URL. original : {image_url_element}"
                    )
            
            tasks = [self.download_image(url, path) for url in image_urls]
            await asyncio.gather(*tasks)  # await all tasks at once
        except WebDriverException as e:  # Catch WebDriverException
            logging.error(f"An error occurred: {type(e).__name__}, {e}")
            return

    async def download_image(self, image_url_element, path):
        """
        이미지를 다운로드합니다.
        :param image_url_element: 다운로드할 이미지의 URL입니다.
        :param path: 이미지를 저장할 경로입니다.
        """

        try:
            async with aiohttp.ClientSession(
                connector=aiohttp.TCPConnector(ssl=ssl_context)
            ) as session:
                async with session.get(
                    image_url_element, headers=self.headers
                ) as response:
                    if response.status == 200:
                        pathlib.Path(path).mkdir(parents=True, exist_ok=True)
                        content_type = response.content_type
                        accepted_content_types = [
                            "image/jpeg",
                            "image/png",
                            "image/webp",
                        ]
                        if content_type not in accepted_content_types:
                            logging.info(
                                f"skipping {self.successful_downloads}: {content_type}"
                            )
                            self.skipped_downloads += 1
                            return
                        extension = f".{content_type.split('/')[-1]}"
                        async with aiofiles.open(
                            f"{path}/{self.successful_downloads}{extension}", "wb"
                        ) as f:
                            await f.write(await response.read())
                        self.successful_downloads += 1
                    else:
                        logging.error(
                            f"Error downloading image No.{self.successful_downloads}: {response.status}"
                        )
        except Exception as e:  # Catch any exception
            logging.error(
                f"Error downloading image No.{self.successful_downloads}: {e}"
            )


if __name__ == "__main__":
    signal.signal(signal.SIGINT, lambda sig, frame: clear_sessions())
    testers = ["이승기", "남주혁", "박보영", "서강준"]

    downloader = ImageDownloader("chrome", testers[0])
    logging.info(f"Starting image download for {downloader.search_for}...")

    try:
        asyncio.run(
            downloader.main_task(
                downloader.browser,
                downloader.search_for,
                f"code/imgs/{downloader.search_for}_images",
            )
        )
    except WebDriverException as e:  # Catch WebDriverException
        logging.error(f"Error: {e}")
        try:
            clear_sessions(downloader.browser.session_id)
        except (
            WebDriverException
        ) as e:  # Catch WebDriverException when clearing sessions
            logging.error(f"Error clearing sessions: {e}")
        try:
            downloader.browser.quit()
        except (
            WebDriverException
        ) as e:  # Catch WebDriverException when quitting the browser
            logging.error(f"Error quitting the browser: {e}")
    print(f"total {downloader.total_before} images found")
    print(f"downloaded {downloader.successful_downloads} images")
    print(f"skipped {downloader.skipped_downloads} images (wrong format only)")
    print(
        f"total {downloader.successful_downloads + downloader.skipped_downloads} images. check logs for more info."
    )
    logging.info("드라이버 종료")

    print("이미지 다운로드 완료")
