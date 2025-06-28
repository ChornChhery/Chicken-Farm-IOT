import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from modules.data_generator import get_standard_weight

def process_weight_data(weight_data):
    df = pd.DataFrame(weight_data)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Calculate day from birth date
    birth_date = datetime(2025, 2, 8)
    df['day'] = (df['timestamp'] - birth_date).dt.days
    
    # Add standard weights
    df['standard_weight'] = df['day'].apply(get_standard_weight)
    
    # Calculate weight deviation
    df['weight_deviation'] = df['average_weight'] - df['standard_weight']
    df['deviation_percentage'] = (df['weight_deviation'] / df['standard_weight']) * 100
    
    return df

def validate_chicken_weight(weight, day):
    """Validate if weight is realistic for chicken age"""
    if day == 0:
        return 35 <= weight <= 45  # Day 0 weight range (40g ± 5g)
    
    std_weight = get_standard_weight(day)
    return 40 <= weight <= (std_weight * 1.5)  # Allow up to 50% above standard

def calculate_growth_rate(df):
    df = df[df['day'].notna()]
    daily_avg = df.groupby('day')['average_weight'].last().reset_index()
    
    daily_avg['growth_rate'] = (
        (daily_avg['average_weight'] - daily_avg['average_weight'].shift(1)) / 
        daily_avg['average_weight'].shift(1) * 100
    ).fillna(0)
    
    daily_avg['standard_growth_rate'] = daily_avg['day'].apply(
        lambda d: (get_standard_weight(d) - get_standard_weight(d-1)) / 
                 get_standard_weight(d-1) * 100 if d > 0 else 0
    )
    
    return daily_avg

def process_sensor_data(readings):
    data = pd.Series(readings)
    
    processed_data = {
        'average': data.mean(),
        'median': data.median(),
        'std_dev': data.std(),
        'min': data.min(),
        'max': data.max(),
        'q1': data.quantile(0.25),
        'q3': data.quantile(0.75)
    }
    
    # Add validation status
    birth_date = datetime(2025, 2, 8)
    current_day = (datetime.now() - birth_date).days
    processed_data['is_valid'] = validate_chicken_weight(processed_data['average'], current_day)
    
    return processed_data

def calculate_moving_averages(df):
    df['MA5'] = df['average_weight'].rolling(window=5).mean()
    df['MA10'] = df['average_weight'].rolling(window=10).mean()
    df['MA20'] = df['average_weight'].rolling(window=20).mean()
    return df

def format_timestamp(df, format='%Y-%m-%d %H:%M:%S'):
    df['formatted_time'] = df['timestamp'].dt.strftime(format)
    return df

def generate_summary_stats(df):
    valid_data = df[df.apply(lambda row: validate_chicken_weight(row['average_weight'], row['day']), axis=1)]
    
    return {
        'current_weight': valid_data['average_weight'].iloc[-1] if not valid_data.empty else None,
        'daily_average': valid_data.groupby('day')['average_weight'].mean().iloc[-1] if not valid_data.empty else None,
        'max_weight': valid_data['average_weight'].max() if not valid_data.empty else None,
        'min_weight': valid_data['average_weight'].min() if not valid_data.empty else None,
        'growth_rate': calculate_growth_rate(valid_data)['growth_rate'].mean() if not valid_data.empty else None,
        'measurement_count': len(valid_data),
        'total_readings': len(df),
        'valid_reading_percentage': (len(valid_data) / len(df) * 100) if len(df) > 0 else 0
    }

def detect_anomalies(df, window_size=5, threshold=2):
    valid_data = df[df.apply(lambda row: validate_chicken_weight(row['average_weight'], row['day']), axis=1)]
    
    rolling_mean = valid_data['average_weight'].rolling(window=window_size).mean()
    rolling_std = valid_data['average_weight'].rolling(window=window_size).std()
    
    z_scores = abs((valid_data['average_weight'] - rolling_mean) / rolling_std)
    
    valid_data['is_anomaly'] = z_scores > threshold
    valid_data['anomaly_score'] = z_scores
    
    return valid_data
