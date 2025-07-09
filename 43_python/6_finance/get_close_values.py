import yfinance as yf
from bokeh.plotting import figure, show
from bokeh.io import output_file
from bokeh.models import HoverTool, ColumnDataSource
from datetime import datetime, timedelta

# HTML 파일로 출력 설정
output_file("tsla_nvda_plot.html")

# 테슬라와 엔비디아 데이터 가져오기
tickers = ["TSLA", "NVDA"]
end_date = datetime.now()
start_date = end_date - timedelta(days=1000)
data = yf.download(tickers, start=start_date, end=end_date)['Close']

# ColumnDataSource로 데이터 준비
source_tsla = ColumnDataSource(data={
    'date': data.index,
    'close': data['TSLA'],
    'date_str': [d.strftime('%Y-%m-%d') for d in data.index]  # 툴팁용 날짜 문자열
})
source_nvda = ColumnDataSource(data={
    'date': data.index,
    'close': data['NVDA'],
    'date_str': [d.strftime('%Y-%m-%d') for d in data.index]
})

# Bokeh 플롯 생성
p = figure(title="Tesla (TSLA) and NVIDIA (NVDA) Closing Prices - Last 30 Days",
           x_axis_label='Date',
           y_axis_label='Closing Price (USD)',
           x_axis_type='datetime',
           width=800,
           height=400)

# 테슬라와 엔비디아 선 그래프 추가
p.line('date', 'close', source=source_tsla, legend_label='TSLA', line_width=2, color='blue')
p.line('date', 'close', source=source_nvda, legend_label='NVDA', line_width=2, color='green')

# HoverTool 추가
hover = HoverTool(
    tooltips=[
        ('Date', '@date_str'),
        ('Close', '@close{0.2f}')
    ],
    formatters={'@date': 'datetime'},
    mode='vline'  # 수직선에 따라 툴팁 표시
)
p.add_tools(hover)

# 플롯 스타일링
p.grid.grid_line_alpha = 0.3
p.legend.location = 'top_left'
p.legend.click_policy = 'hide'  # 범례 클릭 시 선 숨김/표시

# 플롯 저장 및 표시
show(p)
