def classify_weight(weight, day):
    ranges = {
        15: {'underweight': 300, 'normal': 400, 'overweight': 500},
        30: {'underweight': 1000, 'normal': 1300, 'overweight': 1600},
        45: {'underweight': 1800, 'normal': 2100, 'overweight': 2400},
        60: {'underweight': 2400, 'normal': 2700, 'overweight': 3000}
    }
    
    closest_day = min(ranges.keys(), key=lambda x: abs(x - day))
    thresholds = ranges[closest_day]
    
    if weight < thresholds['underweight']:
        return 'น้ำหนักต่ำ | Underweight'
    elif weight > thresholds['overweight']:
        return 'น้ำหนักเกิน | Overweight'
    else:
        return 'น้ำหนักปกติ | Normal'
