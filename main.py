# python 3.10, pip, pandas, selenium, openpyxl 다운로드 및 업그레이드 필수
# [userdata.py] 라는 이름으로 main과 같은 폴더에 py 파일 생성
# 그리고 파일 내에 아래 같은 형태로 siteURL, siteID, sitePW 변수 추가
#siteURL = '파워플래너 intro 주소'
#siteID = '사이트 아이디'
#sitePW = '사이트 비밀번호'
#프로그램이 제어하는 크로미움 브라우저에 손을 대는 것을 비권장합니다.

import os
import shutil
import sys
import gc
import time
import random
import pandas as pd
import datetime

from multiprocessing import Pool
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from pandas.io.html import read_html
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

from core.chromewebdriver import generate_chrome
from core.dataUser import siteURL, siteID, sitePW
from core.settingFunction import *

from datetime import timedelta
from dateutil import relativedelta

def getMonthRange(year, month):
    this_month = datetime.datetime(year=year, month=month, day=1).date()
    next_month = this_month + relativedelta.relativedelta(months=1)
    last_day = next_month - timedelta(days=1)
    return (last_day.day)


def splitTimes(browser):
    elm = browser.find_element(
        "xpath", '//*[@id="SELECT_DT"]')  # 현재 년도와 월 그리고 일 함께 가져오기
    now_year_month = elm.get_attribute('value')  # elm에서 value만 빼내기
    # value를 - 기준으로 나누고 정수로 변환
    split_year_month = list(map(int, now_year_month.split('-')))
    return (split_year_month)

def web_head_n_body(value, head_n, body_n):
    temp_head = value.find_elements(By.TAG_NAME, "th")[head_n]
    temp_body = value.find_elements(By.TAG_NAME, "td")[body_n]
    return temp_head, temp_body

def main():
    print('크롤러 시작')
    SELECTYEAR, SELECTMONTH, RANGEMONTH, STARTDAY, BROWERNOTVIEW = setConfig()
    PROJECT_DIR, DOWNLOAD_DIR, DATABASE_DIR, DRIVER_DIR, CORE_DIR = setDirectory()

    delete_file_path = "database/__electDataTEMP.xlsx" #시작 전 임시 엑셀 파일 삭제
    if os.path.exists(delete_file_path):
        os.remove(delete_file_path)

    total_start_runtime = time.time()

    electricity_time_columns_15 = []
    current_time = datetime.datetime(2020, 1, 1)
    for i in range(15, 24*60, 15):
        current_time = current_time + datetime.timedelta(minutes=15)
        electricity_time_columns_15.append(current_time.strftime('%H:%M'))
    electricity_time_columns_15.append('24:00')
    electricity_time_columns_15.append('')
    electricity_time_columns_15.append('SUM')
    electricity_time_columns_15.append('AVERAGE')
    electricity_time_columns_15.append('MAX')
    electricity_time_columns_15.append('MAX x 4')

    electricity_time_columns_60 = []
    current_time = datetime.datetime(2020, 1, 1)
    for i in range(0, 24*60-60, 60):
        current_time = current_time + datetime.timedelta(minutes=60)
        electricity_time_columns_60.append(current_time.strftime('%H'))
    electricity_time_columns_60.append('24')
    electricity_time_columns_60.append('')
    electricity_time_columns_60.append('SUM')
    electricity_time_columns_60.append('AVERAGE')
    electricity_time_columns_60.append('MAX')
    electricity_time_columns_60.append('MAX x 4')

    platform = sys.platform
    if platform == 'linux':
        print('시스템 플랫폼: 리눅스')
        DRIVER_DIR += 'chromedriver_Lin64'
    elif platform == 'darwin':
        print('시스템 플랫폼: 맥')
        DRIVER_DIR += 'chromedriver_Mac64'
    elif platform == 'win32':
        print('시스템 플랫폼: 윈도우')
        DRIVER_DIR += 'chromedriver_Win32'
    else:
        print(f'[{sys.platform}] 시스템 플랫폼 확인 바람. 지원되지 않음.')
        raise Exception()

    browser = generate_chrome(
        driver_path=DRIVER_DIR,
        headless=BROWERNOTVIEW,
        download_path=DOWNLOAD_DIR)

    url = siteURL
    browser.get(url)  # url 주소로 접속
    time.sleep((random.uniform(5, 10)))

    elm = browser.find_element("xpath", '//*[@id="RSA_USER_ID"]')  # 아이디 입력
    elm.send_keys(siteID)
    elm = browser.find_element("xpath", '//*[@id="RSA_USER_PWD"]')  # 비밀번호 입력
    elm.send_keys(sitePW)
    elm = browser.find_element(
        "xpath", '//*[@id="intro_form"]/form/fieldset/input[1]').click()  # 로그인 버튼 클릭
    print("사이트 로그인")
    time.sleep((random.uniform(5, 10)))

    elm = browser.find_element(
        "xpath", '//*[@id="smart2"]/a').click()  # 실시간사용량-시간대별 상단 버튼 누르기
    time.sleep((random.uniform(7, 14)))
    print("해당 메뉴로 이동")

    elm = browser.find_element(
        "xpath", '//*[@id="txt"]/div[2]/div/p[1]/img').click()  # 날짜 선택 펼치기
    time.sleep((random.uniform(0.25, 0.5)))
    print("초기화 작업 진행 중...")

    date_today = datetime.date.today()
    year_today = date_today.strftime("%Y")
    day_today = date_today.strftime("%D")

    if str(SELECTYEAR) != str(year_today):
        elm = browser.find_element(
            "xpath", '//option[@value="{0}"]'.format(str(SELECTYEAR))).click()  # 년도 찾아 누르기
    elm = browser.find_element(
        "xpath", '//*[@id="ui-datepicker-div"]/div/div/select[2]/option[{0}]'.format(str(SELECTMONTH))).click()  # 월 찾아 누르기
    if str(16) != str(day_today):
        elm = browser.find_element(
            "xpath", '//a[@class="ui-state-default" and text()="16"]').click()  # 날짜 찾아 누르기
    else:
        elm = browser.find_element(
            "xpath", '//a[@class="ui-state-default" and text()="21"]').click()  # 날짜 찾아 누르기
    time.sleep((random.uniform(1, 2)))

    first_days = []
    end_days = []
    split_year_month = splitTimes(browser)
    elm = browser.find_element(
        "xpath", '//*[@id="txt"]/div[2]/div/p[1]/img').click()  # 날짜 선택 펼치기

    continue_check = False
    first_check = False

    sum_60 = 0.0
    max_60 = 0.0
    electricity_list_60 = []

    sum_15 = 0.0
    max_15 = 0.0
    electricity_list_15 = []
    # electricity_list_sum_15 = []
    # electricity_list_max_15 = []

    print("초기화 작업 완료")

    for i in range(1, RANGEMONTH+1):  # 탐색이 이루어지는 개월 범위
        month_start_runtime = time.time()
        electricity_df_60 = pd.DataFrame(index=electricity_time_columns_60)
        electricity_df_15 = pd.DataFrame(index=electricity_time_columns_15)
        electricity_df_60_transpose = pd.DataFrame(
            index=electricity_time_columns_60).transpose()
        electricity_df_15_transpose = pd.DataFrame(
            index=electricity_time_columns_15).transpose()
        number_day = getMonthRange(split_year_month[0], split_year_month[1])
        for j in range(STARTDAY, number_day+1):  # 탐색이 이루어지는 요일 범위
            day_start_runtime = time.time()
            time.sleep((random.uniform(3, 4.5)))
            try:
                elm = browser.find_element(
                    "xpath", '//a[@class="ui-state-default" and text()="{0}"]'.format(str(j)))
                ActionChains(browser).move_to_element(elm).perform()
                elm = browser.find_element(
                    "xpath", '//a[@class="ui-state-default ui-state-hover" and text()="{0}"]'.format(str(j))).click()  # 날짜 찾아서 집어넣기
                elm = browser.find_element(
                    "xpath", '//*[@id="txt"]/div[2]/div/p[2]/span[1]/a').click()  # 조회 버튼 누르기
            except:
                print('선택 구간에서 예외가 발생했습니다.')
                elm = browser.find_element(
                    "xpath", '//a[@class="ui-state-default ui-state-highlight" and text()="{0}"]'.format(str(j)))
                ActionChains(browser).move_to_element(elm).perform()
                elm = browser.find_element(
                    "xpath", '//a[@class="ui-state-default ui-state-highlight ui-state-hover" and text()="{0}"]'.format(str(j))).click()  # 날짜 찾아서 집어넣기
                elm = browser.find_element(
                    "xpath", '//*[@id="txt"]/div[2]/div/p[2]/span[1]/a').click()  # 조회 버튼 누르기
                
            print("다음 날로 이동")
            try:
                time.sleep((random.uniform(3, 4.5)))
                pass_text = browser.find_element("xpath", '//td[@id="F_AP_QT"]').text
                if pass_text == "0.00 kWh":
                    elm = browser.find_element(
                        "xpath", '//*[@id="txt"]/div[2]/div/p[1]/img').click()  # 날짜 선택 펼치기
                    time.sleep((random.uniform(1, 2)))
                    print("해당 날짜 데이터 없음")
                    continue

                if first_check == False:
                    first_days = splitTimes(browser)
                    first_check = True

                elm_day = browser.find_element(
                    "xpath", '//*[@id="SELECT_DT"]')  # 현재 년도와 월 그리고 일 함께 가져오기
                now_year_month_day = elm_day.get_attribute('value')  # elm에서 value만 빼내기
                print("==========[ {0} ]==========".format(str(now_year_month_day)))
                print("일일, 작업 시작")

                # 표 제작 시작
                # 1시간 단위 테이블
                print("1시간 단위 테이블, 작업 시작")
                start_runtime = time.time()
                table_60 = browser.find_element(By.ID, 'tableListHour')  # 60분짜리 테이블 경로
                tbody_60 = table_60.find_element(By.TAG_NAME, "tbody")
                rows_60 = tbody_60.find_elements(By.TAG_NAME, "tr")

                max_temp = []
                total_max = 0.0
                print("1시간 단위 테이블, 전반부 연산")
                for index, value in enumerate(rows_60):
                    head, body = web_head_n_body(value, 0, 0)
                    cells = float(body.text.replace(",", ""))
                    electricity_list_60.append(cells)
                    max_temp.append(cells)
                    sum_60 += cells
                print("1시간 단위 테이블, 후반부 연산")
                for index, value in enumerate(rows_60):
                    head, body = web_head_n_body(value, 1, 7)
                    cells = float(body.text.replace(",", ""))
                    electricity_list_60.append(cells)
                    max_temp.append(cells)
                    sum_60 += cells
                print("1시간 단위 테이블, 추가 연산")
                total_max = max(max_temp)
                electricity_list_60.append("")
                electricity_list_60.append(sum_60)  # 하루 합계
                electricity_list_60.append(sum_60/24)  # 하루 평균
                electricity_list_60.append(total_max)  # 하루 최대값
                electricity_list_60.append(total_max*4)  # 하루 최대값 * 4
                electricity_df_60[now_year_month_day] = electricity_list_60
                electricity_list_60.clear()
                max_temp.clear()
                sum_60 = 0.0
                print("1시간 단위 테이블, 작업 완료")
                print("소요 시간: {0}".format(time.time() - start_runtime))

                time.sleep((random.uniform(0.01, 0.1)))
                # 15분 단위 테이블
                print("15분 단위 테이블, 작업 시작")
                start_runtime = time.time()
                table_15 = browser.find_element(
                    By.ID, 'tableListChart')  # 15분짜리 테이블 경로
                tbody_15 = table_15.find_element(By.TAG_NAME, "tbody")
                rows_15 = tbody_15.find_elements(By.TAG_NAME, "tr")

                f = 1
                four_sum = 0.0
                four_max = 0.0
                max_temp = []
                total_max = 0.0
                print("15분 단위 테이블, 전반부 연산")
                for index, value in enumerate(rows_15):
                    head, body = web_head_n_body(value, 0, 0)
                    
                    cells = float(body.text.replace(",", ""))
                    electricity_list_15.append(cells)
                    max_temp.append(cells)
                    sum_15 += cells
                    
                    four_sum += cells
                    f += 1
                    if f > 4:
                        four_max = max(max_temp)
                        total_max = max(four_max, total_max)
                        # electricity_list_sum_15.append(round(four_sum, 2))
                        # electricity_list_max_15.append(four_max*4)
                        # for p in range(3):
                        #     electricity_list_sum_15.append("")
                        #     electricity_list_max_15.append("")
                        f = 1
                        four_sum = 0.0
                        four_max = 0.0
                        max_temp.clear()

                print("15분 단위 테이블, 후반부 연산")
                for index, value in enumerate(rows_15):
                    head, body = web_head_n_body(value, 1, 7)
                    
                    cells = float(body.text.replace(",", ""))
                    electricity_list_15.append(cells)
                    max_temp.append(cells)
                    sum_15 += cells
                    
                    four_sum += cells
                    f += 1
                    if f > 4:
                        four_max = max(max_temp)
                        total_max = max(four_max, total_max)
                        # electricity_list_sum_15.append(round(four_sum, 2))
                        # electricity_list_max_15.append(four_max*4)
                        # for p in range(3):
                            # electricity_list_sum_15.append("")
                            # electricity_list_max_15.append("")
                        f = 1
                        four_sum = 0.0
                        four_max = 0.0
                        max_temp.clear()
                print("15분 단위 테이블, 추가 연산")
                electricity_list_15.append("")
                electricity_list_15.append(sum_15)  # 하루 합계
                electricity_list_15.append(sum_15/((24*60)/15))  # 하루 평균
                electricity_list_15.append(total_max)  # 하루 최대값
                electricity_list_15.append(total_max*4)  # 하루 최대값 * 4
                # for p in range(5):
                #     electricity_list_sum_15.append("")
                #     electricity_list_max_15.append("")
                # print(now_year_month_day)
                electricity_df_15[now_year_month_day] = electricity_list_15
                # electricity_df_15['{0} | SUM'.format(
                #     now_year_month_day)] = electricity_list_sum_15  # 4개당 계산값 날릴일 있으면 여기 날릴 것
                # electricity_df_15['{0} | MAX'.format(
                #     now_year_month_day)] = electricity_list_max_15  # 4개당 계산값 날릴일 있으면 여기 날릴 것
                # print(electricity_df_15)
                electricity_list_15.clear()
                # electricity_list_sum_15.clear()
                # electricity_list_max_15.clear()
                total_max = 0.0
                sum_15 = 0.0
                print("15분 단위 테이블, 작업 완료")
                print("소요 시간: {0}".format(time.time() - start_runtime))
                # 표 제작 종료
                elm = browser.find_element(
                    "xpath", '//*[@id="txt"]/div[2]/div/p[1]/img').click()  # 날짜 선택 펼치기
                print("일일, 작업 완료")
                day_runtime_second = str(datetime.timedelta(seconds=(time.time() - day_start_runtime))).split(".")
                print("일일 작업 시간: {0}".format(day_runtime_second[0]))
            except:
                print('추출 구간에서 예외가 발생했습니다.')
        end_days = splitTimes(browser)
        print("====================")
        print("다음 달로 이동")
        print("====================")
        elm = browser.find_element(
            "xpath", '//*[@id="ui-datepicker-div"]/div/a[2]/span').click()  # 다음 달 버튼 누르기
        elm = browser.find_element(
            "xpath", '//a[@class="ui-state-default" and text()="16"]').click()  # 날짜 찾아 누르기

        time.sleep((random.uniform(1, 1.5)))
        print("월간, 연산 작업")
        split_year_month = splitTimes(browser)
        elm = browser.find_element(
            "xpath", '//*[@id="txt"]/div[2]/div/p[1]/img').click()  # 날짜 선택 펼치기
        time.sleep((random.uniform(1, 1.5)))

        electricity_df_60_transpose = pd.concat(
            [electricity_df_60_transpose, electricity_df_60.transpose()])
        electricity_df_15_transpose = pd.concat(
            [electricity_df_15_transpose, electricity_df_15.transpose()])

        del [[electricity_df_60, electricity_df_15]]
        gc.collect()

        print("월간, 임시 데이터 저장 중...")
        if not os.path.exists('database/__electDataTEMP.xlsx'):
            print("파일을 생성...")
            with pd.ExcelWriter('database/__electDataTEMP.xlsx', mode='w', engine='openpyxl') as writer:
                electricity_df_60_transpose.to_excel(
                    writer, index=True, sheet_name='hour_1')
                electricity_df_15_transpose.to_excel(
                    writer, index=True, sheet_name='minute_15')
        else:
            print("파일에 추가...")
            with pd.ExcelWriter('database/__electDataTEMP.xlsx', mode='a', engine='openpyxl', if_sheet_exists='overlay') as writer:
                electricity_df_60_transpose.to_excel(
                    writer, index=True, sheet_name='hour_1', startrow=writer.sheets['hour_1'].max_row, header=None)
                electricity_df_15_transpose.to_excel(
                    writer, index=True, sheet_name='minute_15', startrow=writer.sheets['minute_15'].max_row, header=None)
        del [[electricity_df_60_transpose, electricity_df_15_transpose]]
        gc.collect()
        print("월간, 임시 데이터 저장 완료")
        month_runtime_second = str(datetime.timedelta(seconds=(time.time() - month_start_runtime))).split(".")
        print("월간 작업 시간: {0}".format(month_runtime_second[0]))   
        time.sleep((random.uniform(1, 1.5)))
    first_days_str = "".join(map(str, first_days))
    end_days_str = "".join(map(str, end_days))

    print("최종 데이터 저장 중...")
    
    shutil.copy2("database/__electDataTEMP.xlsx", 'database/electData__{0}_{1}.xlsx'.format(
            first_days_str, end_days_str))
    # with pd.ExcelWriter('database/electData__{0}_{1}.xlsx'.format(
    #         first_days_str, end_days_str), mode='w', engine='openpyxl') as writer:
    #     electricity_df_60_transpose.to_excel(
    #         writer, index=True, sheet_name='hour_1')
    #     electricity_df_15_transpose.to_excel(
    #         writer, index=True, sheet_name='minute_15')
    print("최종 데이터 저장 완료")
    total_runtime_second = str(datetime.timedelta(seconds=(time.time() - total_start_runtime))).split(".")
    print("전체 작업 시간: {0}".format(total_runtime_second[0]))
    print("작업 종료, 10초 후 완전 종료")
    time.sleep(10.00)

if __name__ == '__main__':
    main()