def calculate_paint_cost(liters_needed, price_per_liter):
    base_cost = liters_needed * price_per_liter
    tax = base_cost * 0.2
    service_fee = 150
    total_cost = base_cost + tax + service_fee
    return round(total_cost, 2)


if __name__ == '__main__':
    liters_needed = 10
    price_per_liter = 450
    total_cost = calculate_paint_cost(liters_needed, price_per_liter)
    print(total_cost)
