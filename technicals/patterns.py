import pandas as pd
import json
import numpy as np
import dask.dataframe as dd


def read_config(file_path):
    with open(file_path, 'r') as f:
        config = json.load(f)
    return config


config = read_config('../config.json')
pattern_config_data = config['pattern_config_data']


HANGING_MAN_BODY = pattern_config_data['HANGING_MAN_BODY']
HANGING_MAN_HEIGHT = pattern_config_data['HANGING_MAN_HEIGHT']
SHOOTING_STAR_HEIGHT = pattern_config_data['SHOOTING_STAR_HEIGHT']
SPINNING_TOP_MIN = pattern_config_data['SPINNING_TOP_MIN']
SPINNING_TOP_MAX = pattern_config_data['SPINNING_TOP_MAX']
MARUBOZU = pattern_config_data['MARUBOZU']
ENGULFING_FACTOR = pattern_config_data['ENGULFING_FACTOR']
MORNING_STAR_PREV2_BODY = pattern_config_data['MORNING_STAR_PREV2_BODY']
MORNING_STAR_PREV_BODY = pattern_config_data['MORNING_STAR_PREV_BODY']
TWEEZER_BODY = pattern_config_data['TWEEZER_BODY']
TWEEZER_HL = pattern_config_data['TWEEZER_HL']
TWEEZER_TOP_BODY = pattern_config_data['TWEEZER_TOP_BODY']
TWEEZER_BOTTOM_BODY = pattern_config_data['TWEEZER_BOTTOM_BODY']
DOJI_BODY = pattern_config_data['DOJI_BODY']
HAMMER_UPPER = pattern_config_data['HAMMER_UPPER']
HAMMER_LOWER = pattern_config_data['HAMMER_LOWER']
INVERTED_HAMMER_UPPER = pattern_config_data['INVERTED_HAMMER_UPPER']
INVERTED_HAMMER_LOWER = pattern_config_data['INVERTED_HAMMER_LOWER']
DARK_CLOUD_COVER_PERCENTAGE = pattern_config_data['DARK_CLOUD_COVER_PERCENTAGE']
PIERCING_PERCENTAGE = pattern_config_data['PIERCING_PERCENTAGE']
BULLISH_ENGULFING_PERCENTAGE = pattern_config_data['BULLISH_ENGULFING_PERCENTAGE']
BULLISH_HARAMI_PERCENTAGE = pattern_config_data['BULLISH_HARAMI_PERCENTAGE']
BEARISH_ENGULFING_PERCENTAGE = pattern_config_data['BEARISH_ENGULFING_PERCENTAGE']
BEARISH_HARAMI_PERCENTAGE = pattern_config_data['BEARISH_HARAMI_PERCENTAGE']


def apply_candle_props(df: pd.DataFrame):
    df_an = df.copy()
    direction = df_an['mid_c'] - df_an['mid_o']
    body_size = np.abs(direction)
    direction = np.where(direction >= 0, 1, -1)
    full_range = df_an['mid_h'] - df_an['mid_l']
    body_percentage = (body_size / full_range) * 100
    body_lower = np.minimum(df_an['mid_c'], df_an['mid_o'])
    body_upper = np.maximum(df_an['mid_c'], df_an['mid_o'])
    body_bottom_percentage = ((body_lower - df_an['mid_l']) / full_range) * 100
    body_top_percentage = 100 - \
        (((df_an['mid_h'] - body_upper) / full_range) * 100)

    mid_point = full_range / 2 + df_an['mid_l']

    low_change = df_an['mid_l'].pct_change() * 100
    high_change = df_an['mid_h'].pct_change() * 100
    body_size_change = body_size.pct_change() * 100

    df_an['body_lower'] = body_lower
    df_an['body_upper'] = body_upper
    df_an['body_bottom_percentage'] = body_bottom_percentage
    df_an['body_top_percentage'] = body_top_percentage
    df_an['body_percentage'] = body_percentage
    df_an['direction'] = direction
    df_an['body_size'] = body_size
    df_an['low_change'] = low_change
    df_an['high_change'] = high_change
    df_an['body_size_change'] = body_size_change
    df_an['mid_point'] = mid_point
    df_an['mid_point_prev_2'] = mid_point.shift(2)
    df_an['body_size_prev'] = df_an['body_size'].shift(1)
    df_an['direction_prev'] = df_an['direction'].shift(1)
    df_an['direction_prev_2'] = df_an['direction'].shift(2)
    df_an['body_percentage_prev'] = df_an['body_percentage'].shift(1)
    df_an['body_percentage_prev_2'] = df_an['body_percentage'].shift(2)

    return df_an


def set_candle_patterns(df_an: pd.DataFrame):
    df_an['HANGING_MAN'] = (
        (df_an['body_bottom_percentage'] > HANGING_MAN_HEIGHT) &
        (df_an['body_percentage'] < HANGING_MAN_BODY)
    )
    df_an['SHOOTING_STAR'] = (
        (df_an['body_top_percentage'] < SHOOTING_STAR_HEIGHT) &
        (df_an['body_percentage'] < HANGING_MAN_BODY)
    )
    df_an['SPINNING_TOP'] = (
        (df_an['body_top_percentage'] < SPINNING_TOP_MAX) &
        (df_an['body_bottom_percentage'] > SPINNING_TOP_MIN) &
        (df_an['body_percentage'] < HANGING_MAN_BODY)
    )
    df_an['MARUBOZU'] = (df_an['body_percentage'] > MARUBOZU)
    df_an['ENGULFING'] = (
        (df_an['direction'] != df_an['direction_prev']) &
        (df_an['body_size'] > df_an['body_size_prev'] * ENGULFING_FACTOR)
    )
    df_an['TWEEZER_TOP'] = (
        (np.abs(df_an['body_size_change']) < TWEEZER_BODY) &
        (df_an['direction'] == -1) &
        (df_an['direction'] != df_an['direction_prev']) &
        (np.abs(df_an['low_change']) < TWEEZER_HL) &
        (np.abs(df_an['high_change']) < TWEEZER_HL) &
        (df_an['body_top_percentage'] < TWEEZER_TOP_BODY)
    )
    df_an['TWEEZER_BOTTOM'] = (
        (np.abs(df_an['body_size_change']) < TWEEZER_BODY) &
        (df_an['direction'] == 1) &
        (df_an['direction'] != df_an['direction_prev']) &
        (np.abs(df_an['low_change']) < TWEEZER_HL) &
        (np.abs(df_an['high_change']) < TWEEZER_HL) &
        (df_an['body_bottom_percentage'] > TWEEZER_BOTTOM_BODY)
    )
    df_an['MORNING_STAR'] = (
        (df_an['body_percentage_prev_2'] > MORNING_STAR_PREV2_BODY) &
        (df_an['body_percentage_prev'] < MORNING_STAR_PREV_BODY) &
        (df_an['direction'] == 1) &
        (df_an['direction_prev_2'] != 1) &
        (df_an['mid_c'] > df_an['mid_point_prev_2'])
    )
    df_an['EVENING_STAR'] = (
        (df_an['body_percentage_prev_2'] > MORNING_STAR_PREV2_BODY) &
        (df_an['body_percentage_prev'] < MORNING_STAR_PREV_BODY) &
        (df_an['direction'] == -1) &
        (df_an['direction_prev_2'] != -1) &
        (df_an['mid_c'] < df_an['mid_point_prev_2'])
    )
    df_an['DOJI'] = (
        (df_an['body_percentage'] < DOJI_BODY)
    )
    df_an['HAMMER'] = (
        (df_an['body_bottom_percentage'] > HAMMER_LOWER) &
        (df_an['body_top_percentage'] < HAMMER_UPPER) &
        (df_an['body_percentage'] < HANGING_MAN_BODY)
    )
    df_an['INVERTED_HAMMER'] = (
        (df_an['body_bottom_percentage'] < INVERTED_HAMMER_LOWER) &
        (df_an['body_top_percentage'] > INVERTED_HAMMER_UPPER) &
        (df_an['body_percentage'] < HANGING_MAN_BODY)
    )
    df_an['DARK_CLOUD_COVER'] = (
        (df_an['direction_prev'] == 1) &
        (df_an['direction'] == -1) &
        (df_an['mid_c'].pct_change() < -DARK_CLOUD_COVER_PERCENTAGE)
    )
    df_an['PIERCING_PATTERN'] = (
        (df_an['direction_prev'] == -1) &
        (df_an['direction'] == 1) &
        (df_an['mid_c'].pct_change() > PIERCING_PERCENTAGE)
    )
    df_an['BULLISH_ENGULFING'] = (
        (df_an['direction_prev'] == -1) &
        (df_an['direction'] == 1) &
        (df_an['body_size'] > df_an['body_size_prev']
         * BULLISH_ENGULFING_PERCENTAGE)
    )
    df_an['BULLISH_HARAMI'] = (
        (df_an['direction_prev'] == -1) &
        (df_an['direction'] == 1) &
        (df_an['body_size'] < df_an['body_size_prev']
         * BULLISH_HARAMI_PERCENTAGE)
    )
    df_an['BEARISH_ENGULFING'] = (
        (df_an['direction_prev'] == 1) &
        (df_an['direction'] == -1) &
        (df_an['body_size'] > df_an['body_size_prev']
         * BEARISH_ENGULFING_PERCENTAGE)
    )
    df_an['BEARISH_HARAMI'] = (
        (df_an['direction_prev'] == 1) &
        (df_an['direction'] == -1) &
        (df_an['body_size'] < df_an['body_size_prev']
         * BEARISH_HARAMI_PERCENTAGE)
    )
    df_an['THREE_WHITE_SOLDIERS'] = (
        (df_an['direction'] == 1) &
        (df_an['direction'].shift(1) == 1) &
        (df_an['direction'].shift(2) == 1) &
        (df_an['mid_c'] > df_an['mid_c'].shift(1)) &
        (df_an['mid_c'].shift(1) > df_an['mid_c'].shift(2)) &
        (df_an['mid_o'] < df_an['mid_c'].shift(1)) &
        (df_an['mid_o'].shift(1) < df_an['mid_c'].shift(2))
    )
    df_an['THREE_BLACK_CROWS'] = (
        (df_an['direction'] == -1) &
        (df_an['direction'].shift(1) == -1) &
        (df_an['direction'].shift(2) == -1) &
        (df_an['mid_c'] < df_an['mid_c'].shift(1)) &
        (df_an['mid_c'].shift(1) < df_an['mid_c'].shift(2)) &
        (df_an['mid_o'] > df_an['mid_c'].shift(1)) &
        (df_an['mid_o'].shift(1) > df_an['mid_c'].shift(2))
    )
    df_an['BULLISH_ABANDONED_BABY'] = (
        (df_an['direction'].shift(2) == -1) &
        (df_an['direction'] == 1) &
        (df_an['body_percentage'].shift(1) < DOJI_BODY) &
        (df_an['mid_o'].shift(1) < df_an['mid_c'].shift(2)) &
        (df_an['mid_o'] > df_an['mid_c'].shift(1))
    )
    df_an['BEARISH_ABANDONED_BABY'] = (
        (df_an['direction'].shift(2) == 1) &
        (df_an['direction'] == -1) &
        (df_an['body_percentage'].shift(1) < DOJI_BODY) &
        (df_an['mid_o'].shift(1) > df_an['mid_c'].shift(2)) &
        (df_an['mid_o'] < df_an['mid_c'].shift(1))
    )
    df_an['BULLISH_TRI_STAR'] = (
        (df_an['body_percentage'] < DOJI_BODY) &
        (df_an['body_percentage'].shift(1) < DOJI_BODY) &
        (df_an['body_percentage'].shift(2) < DOJI_BODY) &
        (df_an['mid_o'].shift(1) < df_an['mid_c'].shift(2)) &
        (df_an['mid_o'] > df_an['mid_c'].shift(1))
    )


def apply_patterns(df: pd.DataFrame):
    df_an = apply_candle_props(df)
    set_candle_patterns(df_an)
    return df_an
