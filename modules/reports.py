from utils.database import DatabaseConnection
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
from modules.data_generator import get_standard_weight

class ReportGenerator:
    def __init__(self):
        self.db = DatabaseConnection()

    def generate_daily_report(self, date=None):
        if date is None:
            date = datetime.now()

        data = self.db.get_daily_stats(date)
        if not data:
            return None

        stats = data[0]
        day = (date - datetime(2025, 2, 8)).days
        std_weight = get_standard_weight(day)

        report = {
            'date': date.date(),
            'day': day,
            'average_weight': stats['avg_weight'],
            'max_weight': stats['max_weight'],
            'min_weight': stats['min_weight'],
            'total_readings': stats['count'],
            'standard_weight': std_weight,
            'weight_status': self._get_weight_status(stats['avg_weight'], std_weight)
        }

        return report
    
    def generate_weight_chart(self, days=7):
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        weights = self.db.collection.find({
            'timestamp': {
                '$gte': start_date,
                '$lte': end_date
            }
        })
        
        df = pd.DataFrame(list(weights))
        
        # Add standard weight line
        current_day = (end_date - datetime(2025, 2, 8)).days
        days_range = range(max(0, current_day - days), current_day + 1)
        std_weights = pd.DataFrame({
            'day': days_range,
            'standard_weight': [get_standard_weight(d) for d in days_range]
        })
        
        fig = px.line()
        fig.add_scatter(x=df['timestamp'], y=df['average_weight'],
                       name='Actual Weight',
                       line=dict(color='#0bbfb3', width=2))
        fig.add_scatter(x=std_weights['day'], y=std_weights['standard_weight'],
                       name='Standard Weight',
                       line=dict(color='#850c0c', width=2))
        
        fig.update_layout(
            title=f'Weight Trend - Last {days} Days',
            xaxis_title='Date',
            yaxis_title='Weight (g)',
            height=600
        )
        
        return fig

    def generate_real_time_report(self):
        latest_readings = self.db.get_latest_readings(100)
        df = pd.DataFrame(latest_readings)
        
        if df.empty:
            return None

        current_day = (datetime.now() - datetime(2025, 2, 8)).days
        std_weight = get_standard_weight(current_day)

        return {
            'timestamp': df['timestamp'].max(),
            'day': current_day,
            'latest_weight': df['average_weight'].iloc[-1],
            'average_weight': df['average_weight'].mean(),
            'standard_weight': std_weight,
            'status': self._get_weight_status(df['average_weight'].iloc[-1], std_weight),
            'readings_count': len(df)
        }

    def _get_weight_status(self, weight, std_weight):
        if weight < 4:
            return 'empty'
        elif weight > std_weight * 1.8:
            return 'multiple'
        elif weight < std_weight * 0.9:
            return 'underweight'
        elif weight > std_weight * 1.1:
            return 'overweight'
        return 'standard'
