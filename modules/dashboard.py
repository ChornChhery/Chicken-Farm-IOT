from shiny import ui, render, reactive
import plotly.express as px
import pandas as pd
import shinyswatch
from datetime import datetime
from utils.database import DatabaseConnection
from modules.data_generator import get_standard_weight

db = DatabaseConnection()

def dashboard_ui(request):
    return ui.page_fluid(
        ui.include_css("static/custom.css"),
        ui.panel_title("ระบบติดตามการเจริญเติบโตของไก่"),
        
        # Standard vs Observed Weight Table
        ui.row(
            ui.column(12,
                ui.card(
                    ui.card_header("ตารางเปรียบเทียบน้ำหนักมาตรฐานและน้ำหนักที่วัดได้"),
                    ui.card_body(ui.output_table("standard_comparison"))
                )
            )
        ),
        
        # Dual Line Chart Button
        ui.row(
            ui.column(12,
                ui.div(
                    {"class": "text-center mb-3"},
                    ui.input_action_button("show_graph", "แสดงกราฟเปรียบเทียบนำ้หนักของไก่", class_="btn-primary btn-lg")
                )
            )
        ),
        
        # Standard vs Average Weight Line Chart
        ui.row(
            ui.column(12,
                ui.card(
                    ui.card_header("กราฟเปรียบเทียบน้ำหนักมาตรฐานและค่าเฉลี่ย"),
                    ui.card_body(ui.output_ui("weight_trend"))
                )
            )
        ),
        
        # Daily Raw and Processed Measurements
        ui.row(
            ui.column(12,
                ui.card(
                    ui.card_header("ตารางบันทึกการชั่งน้ำหนักรายวัน"),
                    ui.card_body(
                        ui.div(
                            ui.h6("ข้อมูลดิบและค่าเฉลี่ยรายวัน"),
                            ui.output_table("daily_measurements")
                        )
                    )
                )
            )
        ),
        
        theme=shinyswatch.theme.flatly()
    )

def dashboard_server(input, output, session):
    @output
    @render.table
    def standard_comparison():
        valid_readings = db.get_all_readings()
        if valid_readings:
            df = pd.DataFrame(valid_readings)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df['day'] = (df['timestamp'] - datetime(2025, 2, 8)).dt.days
            
            comparison_data = []
            for day in range(0, 57):
                day_data = df[df['day'] == day]
                if not day_data.empty:
                    std_weight = get_standard_weight(day)
                    
                    # Filter valid readings based on the same criteria
                    valid_weights = day_data[
                        (day_data['raw_weight'] > 0) &  # Positive weights only
                        (abs(day_data['raw_weight'] - std_weight) <= 30) |  # Within ±30g
                        ((day_data['raw_weight'] - std_weight > 30) & 
                        (day_data['raw_weight'] <= std_weight * 1.5))  # Possible two thin chickens
                    ]
                    
                    if not valid_weights.empty:
                        comparison_data.append({
                            'วันที่': day,
                            'น้ำหนักมาตรฐาน': std_weight,
                            'น้ำหนักเฉลี่ยที่วัดได้': round(valid_weights['raw_weight'].mean(), 2),
                            'จำนวนการวัดที่ถูกต้อง': len(valid_weights)
                        })
            
            return pd.DataFrame(comparison_data)
        return pd.DataFrame()


    @output
    @render.ui
    @reactive.event(input.show_graph)
    def weight_trend():
        fig = px.line()
        
        # Standard weight line
        days = list(range(0, 57))
        std_weights = [get_standard_weight(d) for d in days]
        
        fig.add_scatter(
            x=days,
            y=std_weights,
            name='น้ำหนักอ้างอิ้งจากคู่มื่อ',
            line=dict(color='red', width=2),
            mode='lines'
        )
        
        # Create full range of days DataFrame for continuous line
        full_days_df = pd.DataFrame({'day': range(0, 57)})
        
        # Average weight line from measurements
        valid_readings = db.get_all_readings()
        df = pd.DataFrame(valid_readings)
        
        if not df.empty:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df['day'] = (df['timestamp'] - datetime(2025, 2, 8)).dt.days
            
            # Calculate daily averages and merge with full days
            daily_avg = df.groupby('day')['raw_weight'].mean().reset_index()
            daily_avg = pd.merge(full_days_df, daily_avg, on='day', how='left')
            
            fig.add_scatter(
                x=daily_avg['day'],
                y=daily_avg['raw_weight'],
                name='น้ำหนักเฉลี่ยที่วัดได้',
                line=dict(color='green', width=2),
                mode='lines'
            )
        
        fig.update_layout(
            title='กราฟการเติบโตของไก่ (วันที่ 0-56)',
            xaxis_title='วัน',
            yaxis_title='น้ำหนัก (กรัม)',
            height=600,
            xaxis=dict(
                range=[0, 56],
                tickmode='linear',
                tick0=0,
                dtick=1
            ),
            template='plotly_white',
            legend_title="นำ้หนักไก่เนื้อ",
            hovermode='x unified',
            hoverlabel=dict(
                bgcolor="white",
                font_size=12
            )
        )
        
        return ui.HTML(fig.to_html(include_plotlyjs="cdn", config={'responsive': True}))

    @output
    @render.table
    def daily_measurements():
        all_readings = db.get_all_readings()
        if all_readings:
            df = pd.DataFrame(all_readings)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df['day'] = (df['timestamp'] - datetime(2025, 2, 8)).dt.days
            df['timestamp'] = df['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
            
            rows = []
            for _, row in df.iterrows():
                std_weight = get_standard_weight(row['day'])
                raw_weight = row['raw_weight']
                
                # Skip negative weights
                if raw_weight <= 0:
                    continue
                    
                # Calculate weight difference in grams
                weight_diff = raw_weight - std_weight
                weight_diff_percent = (weight_diff / std_weight) * 100
                
                # Define weight ranges
                two_thin_chickens = std_weight * 1.5  # Approximate weight for two thin chickens
                
                # Weight classification logic
                if -5 <= weight_diff <= 5:
                    status = "น้ำหนักปกติ"
                    include_reading = True
                elif -30 < weight_diff < -5:
                    status = "ไก่ตัวผอม"
                    include_reading = True
                elif 5 < weight_diff < 30:
                    status = "ไก่ตัวอ้วน"
                    include_reading = True
                elif 30 <= raw_weight <= two_thin_chickens:
                    status = "น่าจะเป็นไก่ผอม 2 ตัว"
                    include_reading = True
                else:
                    include_reading = False
                
                if include_reading:
                    rows.append({
                        'เวลา': row['timestamp'],
                        'วันที่': row['day'],
                        'น้ำหนักมาตรฐาน (g)': std_weight,
                        'น้ำหนักที่วัดได้ (g)': round(raw_weight, 2),
                        'สถานะ': status
                    })
            
            display_df = pd.DataFrame(rows)
            return display_df.sort_values(['วันที่', 'เวลา'], ascending=[True, False])
        return pd.DataFrame()
