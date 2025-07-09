import yfinance as yf
from bokeh.plotting import figure, show
from bokeh.io import output_file
from datetime import datetime, timedelta

# HTML 파일로 출력 설정
output_file("tsla_plot.html")

# 테슬라 데이터 가져오기
ticker = "TSLA"
end_date = datetime.now()
start_date = end_date - timedelta(days=300)
data = yf.download(ticker, start=start_date, end=end_date)

# Bokeh 플롯 생성
p = figure(title="Tesla (TSLA) Closing Prices - Last 30 Days",
           x_axis_label='Date',
           y_axis_label='Closing Price (USD)',
           x_axis_type='datetime',
           width=800,
           height=400)

# 종가 데이터 플롯
p.line(data.index, data['Close'], legend_label='Close', line_width=2, color='blue')

# 플롯 스타일링
p.grid.grid_line_alpha = 0.3
p.legend.location = 'top_left'

# 플롯 저장 및 표시
show(p)
