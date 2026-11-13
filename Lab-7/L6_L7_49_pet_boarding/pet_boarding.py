def parse_booking(text):
    if not isinstance(text, str):
        return None
    parts = text.split(':')
    if len(parts) != 2:
        return None
    pet = parts[0].strip()
    days_str = parts[1].strip()
    if not pet:
        return None
    try:
        days = float(days_str)
        if days < 0 or days != days:  # NaN check
            return None
        return pet.title(), days
    except (ValueError, TypeError):
        return None


def stay_average(days_csv):
    if not isinstance(days_csv, str):
        return 0
    parts = [r.strip() for r in days_csv.split(',') if r.strip()]
    if not parts:
        return 0
    values = []
    for r in parts:
        try:
            val = int(r)
            if val >= 0:
                values.append(val)
        except (ValueError, TypeError):
            continue
    if not values:
        return 0
    return sum(values) // len(values)


def payable_fee(text):
    if not isinstance(text, str):
        return 0.0
    parts = text.split('|')
    if len(parts) != 2:
        return 0.0
    try:
        fee = float(parts[0].strip())
        discount = float(parts[1].strip())
        if fee < 0 or discount < 0 or fee != fee or discount != discount:
            return 0.0
        total = fee * 1.18 - discount
        return round(max(total, 0.0), 2)
    except (ValueError, TypeError):
        return 0.0


def main():
    print("==== Running parse_booking ====")
    user_input = input("Enter pet:days (e.g. dog:5): ")
    result = parse_booking(user_input)
    print("Pet and Days:", result)

    print("\n==== Running stay_average ====")
    user_input = input("Enter stay lengths in days as CSV (e.g. 2,5,7): ")
    result = stay_average(user_input)
    print("Average Stay:", result)

    print("\n==== Running payable_fee ====")
    user_input = input("Enter fee|discount (e.g. 1500|100): ")
    result = payable_fee(user_input)
    print("Payable Fee:", result)


if __name__ == "__main__":
    main()
