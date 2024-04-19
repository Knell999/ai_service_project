import time
from selenium import webdriver
from selenium.webdriver.common.by import By

def youtube(keyword):
    keyword = keyword
    url = f'https://www.youtube.com/results?search_query={keyword}'

    option = webdriver.ChromeOptions().add_argument('--headless') # 크롬창 숨기기 옵션

    driver = webdriver.Chrome(options=option) # 웹 드라이버 생성
    driver.get(url) # 드라이버에 url 요청

    time.sleep(1) # 1초 기다리기

    a_elements = driver.find_elements(By.CSS_SELECTOR,'a#video-title') # id가 video-title인 a태그의 요소들을 가져옴
    img_elements = driver.find_elements(By.CSS_SELECTOR,'#thumbnail > yt-image > img') # 썸네일 가져오기

    # 상위 2개의 영상의 링크를 가져와서 저장
    
    link = []
    title = []
    thumnail = []

    for i in range(0, 2):
        link.append(a_elements[i].get_attribute('href')) # 요소의 href 값을 youtube 리스트에 추가
        thumnail.append(img_elements[i+1].get_attribute('src')) # 요소의 href 값을 youtube 리스트에 추가
        title.append(a_elements[i].get_attribute('title'))
    driver.quit() # 크롬 드라이버 종료

    return {'link':link, 'title':title, 'thumnail':thumnail}