import yfinance as yf
import pandas as pd

# 테슬라 티커 지정
ticker = 'TSLA'

# 데이터 가져오기: 기간은 1개월
data = yf.download(ticker, period='1mo')

# 종가(Close)만 추출
closing_prices = data['Close']

# 결과 출력
print(closing_prices)
