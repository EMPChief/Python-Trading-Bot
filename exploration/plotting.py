import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots


class CandlePlot:
    def __init__(self, df: pd.DataFrame, candles: bool = True):
        self.df_plot = df.copy()
        self.candles = candles
        self.create_candle_fig()

    def add_timestring(self):
        self.df_plot['time'] = pd.to_datetime(self.df_plot['time'])
        self.df_plot['sTime'] = [x.strftime(
            "s%Y-%m-%d %H:%M") for x in self.df_plot['time']]

    def create_candle_fig(self):
        self.add_timestring()
        self.fig = make_subplots(specs=[[{"secondary_y": True}]])
        if self.candles:
            self.fig.add_trace(go.Candlestick(
                x=self.df_plot.sTime,
                open=self.df_plot.mid_o,
                high=self.df_plot.mid_h,
                low=self.df_plot.mid_l,
                close=self.df_plot.mid_c,
                line=dict(width=1),
                opacity=1,
                increasing=dict(fillcolor='#00cc00', line_color='#006600'),
                decreasing=dict(fillcolor='#ff0000', line_color='#990000'),
                hovertext='Candlestick',
                name='Candlestick'
            ))

    def update_layout(self, width: int, height: int, nticks: int):
        self.fig.update_yaxes(gridcolor='lightgray', title_text='Price')
        self.fig.update_xaxes(gridcolor='lightgray', rangeslider=dict(
            visible=False), nticks=nticks, title_text='Time')
        self.fig.update_layout(
            width=width,
            height=height,
            title='Trading Chart',
            margin=dict(l=10, r=10, b=10, t=10),
            paper_bgcolor='black',
            plot_bgcolor='black',
            font=dict(color='white', size=12),
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01
            )
        )

    def add_traces(self, line_traces: list, is_secondary: bool = False):
        for t in line_traces:
            self.fig.add_trace(go.Scatter(
                x=self.df_plot.sTime,
                y=self.df_plot[t],
                line=dict(width=2),
                line_shape="spline",
                name=t,
                hovertext=t,
            ), secondary_y=is_secondary)

    def show_plot(self, width: int = 1500, height: int = 800, nticks: int = 5, line_traces: list = [], sec_traces: list = []):
        self.add_traces(line_traces)
        self.add_traces(sec_traces, is_secondary=True)
        self.update_layout(width, height, nticks)
        self.fig.show()
