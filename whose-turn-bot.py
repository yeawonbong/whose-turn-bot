from datetime import timedelta as td
from datetime import datetime as dt
from pytimekr import pytimekr
import telegram
import asyncio
import tracemalloc
import schedule
import requests

# Telegram bot token
TOKEN = 'TELEGRAM_TOKEN'

# Teams Webhook URL
TEAMS_WEBHOOK_URL = "TEAMS_URL"

# Initialize the bot
bot = telegram.Bot(token=TOKEN)

def get_dates(start_date, end_date):
    delta = td(days=1)
    result = []
    while start_date <= end_date:
        result.append(start_date)
        start_date += delta
    return result

def count_turn(기준일자) -> int:
    """Count the number of business days after the given date"""

    # 공휴일 리스트 초기화
    holidays = []

    today = dt.date(dt.now())

    # 기준일 년부터 익년까지의 공휴일 가져오기
    for year in range(기준일자.year, today.year+1):
        for holiday in pytimekr.holidays(year):
            if holiday not in holidays:  # 중복 방지
                holidays.append(holiday)

    # Add custom holidays
    holidays.append(dt.date(dt(2024, 5, 1))) #노동절
    holidays.append(dt.date(dt(2024, 5, 6))) #어린이날 대체휴일
    holidays.append(dt.date(dt(2024,10, 1))) #국군의날 휴일

    # 정렬
    holidays.sort()

    print(holidays)
    if(today in holidays or today.weekday() > 4):
        return -1

    turnCnt = -1
    date_range = get_dates(기준일자, today)
    for date in date_range:
        if(date not in holidays and date.weekday() <= 4):
            turnCnt += 1  # Count if it's a business day

    return turnCnt

async def send_turn():
    # List of names
    names = ['아이유', '박보검', '공효진', '현빈', '손예진'\
            , '김수현', '이민호', '박신혜', '송중기', '수지'\
            , '이준기', '전지현', '송혜교', '지창욱', '한지민'\
            , '김우빈', '박서준', '윤아', '정해인', '유아인'\
            , '신민아', '고아라', '이동욱', '박보영']
    mbrCnt = len(names)
    print("mbrCnt:" + str(mbrCnt))
    turn = count_turn(dt.date(dt(2025, 1, 2))) # 순번 시작 기준일
    if 0 <= turn :
        turn %= mbrCnt

        # Create a dictionary mapping numbers to random names
        mapping = {i: names[i] for i in range(0, mbrCnt)}
        
        # 로그
        msg = mapping[turn]+"님의 차례입니다.\n다음 모니터링은 " + (mapping[turn+1] if turn < (mbrCnt - 1) else mapping[0]) + "님입니다."
        print(str(turn) + "번째, " + str(dt.date(dt.now())) + " " + msg)
        
        # 텔레그램 메시지 전송
        # await bot.send_message(chat_id='-4177045035', text=msg) #배치모니터링
        
        # Teams 메시지 전송
        teams_message = {
            "summary": msg,
            "text": msg
        }
        try:
            response = requests.post(TEAMS_WEBHOOK_URL, json=teams_message)
            response.raise_for_status()
            # print("Teams 메시지가 성공적으로 전송되었습니다.")
        except requests.exceptions.RequestException as e:
            print(f"Teams 메시지 전송 실패: {e}")

        # 알림 전송 후 23시간 대기
        await asyncio.sleep(23 * 3600)

async def main():
    while True:
        schedule.run_pending()
        await asyncio.sleep(60)  # 1분 사이클

def schedule_send_turn():
    asyncio.create_task(send_turn())

if __name__ == "__main__":
    tracemalloc.start()
    # Schedule the task to send message at 7:55 AM every day
    schedule.every().day.at("07:55").do(schedule_send_turn)

    # Run the main loop without asyncio.run()
    asyncio.get_event_loop().run_until_complete(main())
