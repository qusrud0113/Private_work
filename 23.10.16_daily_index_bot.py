from datetime import datetime, timedelta
from functools import reduce
from pandas_datareader import data as pdr
from telegram.ext import Updater
import asyncio
import nest_asyncio 
import pandas as pd
import telegram
import yfinance as yf

yesterday = datetime.now() - timedelta(10)
today = datetime.now()

def strtime(time):
    return datetime.strftime(time, '%Y-%m-%d')
yesterday = strtime(yesterday)
today = strtime(today)

yf.pdr_override()

# DiDi Global Inc
didi = pdr.get_data_yahoo("DIDIY", yesterday, today)
# S&P500
SP500 = pdr.get_data_yahoo("^GSPC", yesterday, today)
# KSP
ksp = pdr.get_data_yahoo("^KS11", yesterday, today)
# KSP200
ksp200 = pdr.get_data_yahoo("^KS200", yesterday, today)

didi['Close'] = round(didi['Close'],2)
SP500['Close'] = round(SP500['Close'],2)
ksp['Close'] = round(ksp['Close'],2)
ksp200['Close'] = round(ksp200['Close'],2)

df1 = ksp[['Close']]
df2 = ksp200[['Close']]
df3 = SP500[['Close']]
df4 = didi[['Close']]

df1 = df1.rename(columns={'Close': 'ksp_close'})
df2 = df2.rename(columns={'Close': 'ksp200_close'})
df3 = df3.rename(columns={'Close': 'SP500_close'})
df4 = df4.rename(columns={'Close': 'didi_close'})


# merge
df = reduce(lambda x,y: pd.concat([x,y], axis = 1), [df1, df2, df3, df4])

# reset index
df = df.reset_index()
# df = df.sort_values(by = 'Date', ascending= False)

# using telegram bot
nest_asyncio.apply()
    
async def main():
    TOKEN = '5910133179:AAGdi-StHGo9Vvy-T_VLtZkHxOEWvv243c0'
    # chat_id는 https://api.telegram.org/bot5910133179:AAGdi-StHGo9Vvy-T_VLtZkHxOEWvv243c0/getUpdates 에서 채팅을 보낸 후 F5를 눌러 id 값을 가져옴
    chat_id = '6600639417'
    bot = telegram.Bot(token = TOKEN)
    text_all = '- 일일수익률용 데이터 -\n'
    for i in range(len(df[:3])):
            text = '\n일자: {}\n코스피: {}\n코스피200: {} \nS&P500: {}\nDIDI: {}\n\n'.format(strtime(df.iloc[3+i].Date), df.iloc[3+i].ksp_close, df.iloc[3+i].ksp200_close, df.iloc[3+i].SP500_close, df.iloc[3+i].didi_close )
            text_all = text_all + text
    text_notice = '- 일자별 해야할 일 -\n\n'
    # 만약 오늘이 주의 첫 영업일이면 주간 업무도 추가하고,
    # 월 첫영업일이면 월간보고서 기본 자료 제작 및 코멘트 요청 추가하기 !
    text_notice_list = ['오전) \n 1. 수익률 산출', \
                                '2. * 9시 이전) 국민연금관리 종목',\
                                '               주식유니버스 ',\
                                '               고유자산 확인', \
                                '3. 리스크 관리(손절매)', \
                                '4. 금투협, 금감원 공시', \
                                '5. MDD 자료 만들기', \
                                '오후) \n 6. 이해상충보고서']
    await bot.send_message(chat_id, text_notice)
    for i in text_notice_list:         
        await bot.send_message(chat_id, i)
    await bot.send_message(chat_id, text_all)
    
asyncio.run(main())