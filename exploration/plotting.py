import pandas as pd
import plotly.graph_objects as go
import datetime as dt

class CandlePlot:
    """
    A class for creating candlestick charts using Plotly.

    Parameters:
    - df: pandas DataFrame
        Input DataFrame containing candlestick data.
    - candles: bool, optional
        Flag to include candlestick chart (default is True).

    Methods:
    - add_timestring(): Adds a formatted time string column to the DataFrame.
    - create_candle_fig(): Creates a candlestick chart using Plotly.
    - update_layout(width, height, nticks): Updates the layout of the chart.
    - add_traces(line_traces): Adds line traces to the chart.
    - show_plot(width=1500, height=800, nticks=5, line_traces=[]): Displays the candlestick chart with optional line traces.

    Attributes:
    - df_plot: pandas DataFrame
        Copy of the input DataFrame for chart plotting.

    Example:
    cp = CandlePlot(df, candles=True)
    cp.show_plot()
    """
    
    def __init__(self, df, candles=True):
        """
        Initializes the CandlePlot object.

        Parameters:
        - df: pandas DataFrame
            Input DataFrame containing candlestick data.
        - candles: bool, optional
            Flag to include candlestick chart (default is True).
        """
        self.df_plot = df.copy()
        self.candles = candles
        self.create_candle_fig()
    
    def add_timestring(self):
        """
        Adds a formatted time string column to the DataFrame.
        """
        self.df_plot['time'] = pd.to_datetime(self.df_plot['time'])
        self.df_plot['sTime'] = [dt.datetime.strftime(x, "s%Y-%m-%d %H:%M") for x in self.df_plot['time']]


    def create_candle_fig(self):
        """
        Creates a candlestick chart using Plotly.
        """
        self.add_timestring()
        self.fig = go.Figure()
        if self.candles == True:
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
            ))
    
    def update_layout(self, width, height, nticks):
        """
        Updates the layout of the chart.

        Parameters:
        - width: int
            Width of the chart.
        - height: int
            Height of the chart.
        - nticks: int
            Number of ticks on the x-axis.
        """
        self.fig.update_yaxes(gridcolor='gray')
        self.fig.update_xaxes(
            gridcolor='gray', 
            rangeslider=dict(visible=False),
            nticks=nticks)

        self.fig.update_layout(
            width=width,
            height=height,
            title='Bjørn Chart',
            xaxis_title='Time',
            yaxis_title='Mid Prices',
            margin=dict(l=10, r=10, b=10, t=10),
            paper_bgcolor='black',
            plot_bgcolor='black',
            font=dict(color='white', size=12)
        )
    
    def add_traces(self, line_traces):
        """
        Adds line traces to the chart.

        Parameters:
        - line_traces: list
            List of column names to be used as line traces on the chart.
        """
        for t in line_traces:
            self.fig.add_trace(go.Scatter(
                x=self.df_plot.sTime,
                y=self.df_plot[t],
                line=dict(width=2),
                line_shape="spline",
                name=t,
            ))
    
    def show_plot(self, width=1500, height=800, nticks=5, line_traces=[]):
        """
        Displays the candlestick chart with optional line traces.

        Parameters:
        - width: int, optional
            Width of the chart (default is 1500).
        - height: int, optional
            Height of the chart (default is 800).
        - nticks: int, optional
            Number of ticks on the x-axis (default is 5).
        - line_traces: list, optional
            List of column names to be used as line traces on the chart.
        """
        self.add_traces(line_traces)
        self.update_layout(width, height, nticks)
        self.fig.show()
