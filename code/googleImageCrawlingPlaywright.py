# 필요한 라이브러리들을 임포트합니다.
import asyncio
import logging
import pathlib
import ssl
import datetime

# import random
from urllib.parse import urlparse, parse_qs

from playwright.async_api import async_playwright
import aiofiles
import aiohttp

# 로깅을 설정합니다.
logging.basicConfig(
    format="%(asctime)s - %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S",
    filename=datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S.log"),
    encoding="utf-8",
)

# SSL 컨텍스트를 생성하고 설정합니다.
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE
ssl_context.options |= 0x4  # OP_LEGACY_SERVER_CONNECT

# 다운로드 시 허용되는 컨텐츠 타입을 설정합니다.
accepted_content_types = ["image/jpeg", "image/png", "image/jpg", "image/webp"]


class AsyncImageDownloader:
    """
    AsyncImageDownloader 클래스는 Playwright를 사용하여 이미지를 다운로드하는 클래스입니다.
    """

    def __init__(self, search_for):
        """
        클래스를 초기화합니다.

        :param search_for: 검색어
        """

        self.search_for = search_for
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        }
        self.scroll_amount = 5

        self.found_images = 0
        self.failed_gathers = 0

        self.successful_downloads = 0
        self.failed_downloads = 0

    async def fetch_image_url(self, page, image):
        """
        구글 이미지 검색 같이 클릭이 필요한 경우에 쓰입니다.
        이미지 URL을 가져옵니다.

        :param page: 페이지
        :param image: 이미지
        :return: 이미지 URL
        """

        try:
            logging.info("Clicking on images...")
            await image.click()
            image_url_element = await page.wait_for_selector(
                '//img[@class="sFlh5c pT0Scc iPVvYb"]', timeout=16000
            )  # Add a wait
            if image_url_element:
                image_url = await image_url_element.get_attribute("src")
                logging.info(f"Fetched image URL: {image_url}")
                return image_url
        except TimeoutError:
            logging.error(f"Timed out while fetching image URL for {image}")
            return

    async def fetch_image_urls(self, page):
        """
        이미지 URL들을 가져옵니다.
        현재 Naver 이미지 검색에 맞춰져 있습니다.

        :param page: 페이지
        :return: 이미지 URL들
        """

        image_urls = []
        logging.info(f"Searching for {self.search_for}")
        await page.goto(
            # f"https://www.google.com/search?as_st=y&as_q={self.search_for}&as_epq=&as_oq=&as_eq=&imgsz=l&imgar=&imgcolor=&imgtype=face&cr=&as_sitesearch=&as_filetype=&tbs=&udm=2"
            f"https://search.naver.com/search.naver?where=image&mode=column&section=image&query={self.search_for}&res_fr=786432&res_to=100000000&sm=tab_opt&color=&ccl=0&recent=0&datetype=0&startdate=0&enddate=0&gif=0&optStr=&nq=&dq=&rq=&tq=&nso_open=1&pq="
        )  # Update URL as needed

        images = set()
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight);")
        for i in range(self.scroll_amount):
            # '//div[@class="czzyk XOEbc"]'
            image_elements = await page.query_selector_all(
                ".image_tile_bx._fe_image_viewer_focus_target .thumb img"
            )
            for image_element in image_elements:
                image_src = await image_element.get_attribute("src")
                if not image_src.startswith("data:image"):
                    if image_src in images:
                        logging.info(f"Found image: {image_src} (duplicate)")
                    else:
                        logging.info(f"Found image: {image_src}")
                    images.add(image_src)
                else:
                    logging.info(f"Skipping image: {image_src} (base64)")
                    self.failed_gathers += 1

            logging.info(f"Scrolling {i + 1}/{self.scroll_amount}")
            scroll_height_before = await page.evaluate("document.body.scrollHeight")
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight);")
            await page.wait_for_timeout(
                1500
            )  # Wait for potential dynamic content to load
            scroll_height_after = await page.evaluate("document.body.scrollHeight")
            if scroll_height_before == scroll_height_after:
                break

        logging.info(f"Found {len(images)} images")
        self.found_images = len(images)

        # tasks = [self.fetch_image_url(page, image) for image in images]
        # asyncio.gather(*tasks)
        # may lead to duplicate downloads
        # instead, we will await each task individually
        #
        # if clicking is needed, uncomment the following line
        # for image in random.shuffle(images):
        #     image_url = await self.fetch_image_url(page, image)
        #     if image_url:
        #         self.successful_gathers += 1
        #         image_urls.append(image_url)
        #     else:
        #         self.failed_gathers += 1

        for src in images:
            parsed_url = urlparse(src)
            query = parse_qs(parsed_url.query)
            inner_url = query["src"][0]
            image_urls.append(inner_url)

        await page.close()

        return image_urls

    async def download_image(self, i, session, url, path):
        """
        이미지를 다운로드합니다.

        :param i: 인덱스(파일명에 사용됩니다.)
        :param session: 세션
        :param url: URL
        :param path: 경로
        """

        async with session.get(url) as response:
            pathlib.Path(path).mkdir(parents=True, exist_ok=True)
            if response.status // 100 == 2:
                content_type = response.content_type
                if content_type not in accepted_content_types:
                    logging.error(f"Skipping {url} due to content type {content_type}")
                    self.failed_downloads += 1
                    return
                async with aiofiles.open(
                    f"{path}/{self.search_for}_{i}.{content_type.split('/')[1]}", "wb"
                ) as f:
                    await f.write(await response.read())
                    logging.info(f"Downloaded {url}")
                    self.successful_downloads += 1
            else:
                logging.error(f"Failed to download {url}")
                self.failed_downloads += 1

    async def task(self):
        """
        메인 함수입니다.
        """

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            urls = await self.fetch_image_urls(page)

            async with aiohttp.ClientSession(
                headers=self.headers, connector=aiohttp.TCPConnector(ssl=ssl_context)
            ) as session:
                tasks = [
                    self.download_image(
                        i,
                        session,
                        url,
                        f"imgs/{self.search_for}_images",  # adjust path as needed
                    )
                    for i, url in enumerate(urls)
                ]

                logging.info("Starting download...")
                await asyncio.gather(*tasks)

            await browser.close()


if __name__ == "__main__":
    search_keywords = ["이승기", "남주혁", "박보영", "서강준"]
    downloader = AsyncImageDownloader(search_keywords[3])
    asyncio.run(downloader.task())
    logging.info(f"Failed gathers: {downloader.failed_gathers}")
    logging.info(
        f"Successful downloads: {downloader.successful_downloads}, Failed downloads: {downloader.failed_downloads}"
    )
