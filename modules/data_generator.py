from datetime import datetime

def get_standard_weight(day):
    standard_weights = {
        0: 44, 1: 61, 2: 79, 3: 99, 4: 122, 5: 147, 6: 176, 7: 209, 
        8: 244, 9: 284, 10: 326, 11: 373, 12: 423, 13: 477, 14: 535, 
        15: 597, 16: 662, 17: 730, 18: 803, 19: 878, 20: 957, 21: 1040, 
        22: 1125, 23: 1213, 24: 1304, 25: 1397, 26: 1493, 27: 1591, 
        28: 1691, 29: 1793, 30: 1896, 31: 2001, 32: 2107, 33: 2215, 
        34: 2323, 35: 2432, 36: 2542, 37: 2652, 38: 2762, 39: 2873, 
        40: 2983, 41: 3094, 42: 3204, 43: 3313, 44: 3422, 45: 3531, 
        46: 3638, 47: 3745, 48: 3851, 49: 3956, 50: 4059, 51: 4162, 
        52: 4263, 53: 4363, 54: 4461, 55: 4558, 56: 4654
    }
    return standard_weights.get(day, 4654)

def get_weight_status(weight, min_weight, max_weight):
    if weight < -10:
        return 'invalid_low'
    elif weight < 4:
        return 'empty'
    elif weight > max_weight * 1.8:
        return 'multiple'
    elif min_weight <= weight <= max_weight:
        return 'standard'
    elif weight < min_weight:
        return 'underweight'
    else:
        return 'overweight'

def get_weight_ranges(day):
    std_weight = get_standard_weight(day)
    return {
        'min': std_weight * 0.9,
        'max': std_weight * 1.1,
        'standard': std_weight
    }

def calculate_chicken_age(measurement_time=None):
    birth_date = datetime(2025, 2, 8)
    current_date = measurement_time or datetime.now()
    age_days = (current_date - birth_date).days
    return max(0, min(age_days, 56))
