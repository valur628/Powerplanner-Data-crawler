import configparser
import os

def setDirectory():
    PROJECT_DIR = str(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
    DOWNLOAD_DIR = f'{PROJECT_DIR}/download'
    DATABASE_DIR = f'{PROJECT_DIR}/database'
    DRIVER_DIR = f'{PROJECT_DIR}/lib/webDriver/'
    CORE_DIR = f'{PROJECT_DIR}/core/'
    return PROJECT_DIR, DOWNLOAD_DIR, DATABASE_DIR, DRIVER_DIR, CORE_DIR

def setConfig():
    # 설정파일 읽기
    config = configparser.ConfigParser()    
    config.read('core/config.ini', encoding='utf-8') 
    # 설장파일 색션 확인
    config.sections()
    # 섹션값 읽기
    c_selectYear = int(config['Crawler']['Select_Year'])
    c_selectMonth = int(config['Crawler']['Select_Month'])
    c_rangeMonth = int(config['Crawler']['Range_Month'])
    c_startDay = int(config['Crawler']['Start_Day'])
    c_browerNotView = config['Driver']['Brower_NotShow']
    return c_selectYear, c_selectMonth, c_rangeMonth, c_startDay, c_browerNotView
