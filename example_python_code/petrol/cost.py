def calculate_total_cost(fuel_liters, price_per_liter):
    total = fuel_liters * price_per_liter
    return total

def round_cost(cost):
    divided = cost / 10
    rounded = round(divided)
    result = rounded * 10
    return result
