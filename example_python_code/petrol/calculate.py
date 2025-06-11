from example_python_code.petrol.cost import (calculate_total_cost, round_cost)

def calculate_monthly_distance(daily_distance):
    days_in_month = 30
    monthly_distance = daily_distance * days_in_month
    return monthly_distance * 1.01

def calculate_fuel_needed(distance, consumption_per_100km):
    units = distance / 100
    fuel_needed = units * consumption_per_100km
    return fuel_needed

if __name__ == "__main__":
    distance_per_day = 30
    fuel_consumption = 7.5
    fuel_price = 50

    monthly_distance = calculate_monthly_distance(distance_per_day)
    fuel_needed = calculate_fuel_needed(monthly_distance, fuel_consumption)
    total_cost = calculate_total_cost(fuel_needed, fuel_price)
    rounded_cost = round_cost(total_cost)
    print(rounded_cost)
