
def getMonthRange(year, month):
    this_month = datetime.datetime(year=year, month=month, day=1).date()
    next_month = this_month + relativedelta.relativedelta(months=1)
    last_day = next_month - timedelta(days=1)
    return (last_day.day)


def splitTimes():
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
