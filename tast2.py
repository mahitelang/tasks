import os
import math
import random
from itertools import combinations

# ==========================================
# CAB BOOKING CHATBOT
# ==========================================

LOCATIONS = [
    "Pune Station",
    "Shivajinagar",
    "Kothrud",
    "Wakad",
    "Swargate",
    "Hinjawadi"
]

CAB_RATES = {
    "1": ("Auto", 12),
    "2": ("Sedan", 18),
    "3": ("SUV", 25)
}

# DEMO DISTANCES IN KM (illustrative, not verified road distances).
# Each route is listed ONCE. Direction does not matter:
# (A, B) and (B, A) always give the same distance and the same fare.
ROUTE_DISTANCES = {
    frozenset(("Pune Station", "Shivajinagar")): 5,
    frozenset(("Pune Station", "Kothrud")): 10,
    frozenset(("Pune Station", "Wakad")): 20,
    frozenset(("Pune Station", "Swargate")): 7,
    frozenset(("Pune Station", "Hinjawadi")): 22,
    frozenset(("Shivajinagar", "Kothrud")): 8,
    frozenset(("Shivajinagar", "Wakad")): 18,
    frozenset(("Shivajinagar", "Swargate")): 6,
    frozenset(("Shivajinagar", "Hinjawadi")): 20,
    frozenset(("Kothrud", "Wakad")): 15,
    frozenset(("Kothrud", "Swargate")): 7,
    frozenset(("Kothrud", "Hinjawadi")): 12,
    frozenset(("Wakad", "Swargate")): 18,
    frozenset(("Wakad", "Hinjawadi")): 10,
    frozenset(("Swargate", "Hinjawadi")): 18,
}

AVERAGE_SPEED_KMPH = 25


def validate_data():
    """Make sure every pair of different locations has a valid distance."""
    for a, b in combinations(LOCATIONS, 2):
        distance = ROUTE_DISTANCES.get(frozenset((a, b)))
        if distance is None or distance <= 0:
            raise ValueError(f"Missing or invalid distance: {a} <-> {b}")


# ==========================================
# SCREEN AND INPUT HELPERS
# ==========================================

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def pause():
    try:
        input("\nPress Enter to continue...")
    except (EOFError, KeyboardInterrupt):
        pass


def safe_input(prompt):
    """Read input safely and handle terminal input interruptions."""
    try:
        return input(prompt).strip()
    except (EOFError, KeyboardInterrupt):
        print("\n[ERROR] Input interrupted.")
        return None


def show_error(message):
    print(f"\n[ERROR] {message}")
    pause()


# ==========================================
# DISTANCE, FARE, TIME
# ==========================================

def get_distance(source, destination):
    """Same distance in both directions. None if same place or unknown."""
    if source == destination:
        return None
    return ROUTE_DISTANCES.get(frozenset((source, destination)))


def calculate_fare(distance, rate):
    return round(distance * rate, 2)


def estimate_minutes(distance):
    return max(1, math.ceil(distance / AVERAGE_SPEED_KMPH * 60))


# ==========================================
# LOCATION SELECTION
# ==========================================

def show_locations(excluded_location=None):
    available = [loc for loc in LOCATIONS if loc != excluded_location]
    for number, location in enumerate(available, start=1):
        print(f"{number}. {location}")
    return available


def choose_location(title, excluded_location=None):
    while True:
        clear_screen()
        print("=" * 42)
        print(title.center(42))
        print("=" * 42)

        if excluded_location:
            print(f"(Pickup is {excluded_location}; it cannot be chosen again)\n")

        available = show_locations(excluded_location)
        print("\n0. Quit Booking")

        choice = safe_input("\nChoose a location: ")

        if choice is None or choice == "0":
            print("\nBooking process stopped. No OTP was shared.")
            pause()
            return None

        if not choice.isdigit():
            show_error("Invalid input. Please enter a location number or 0.")
            continue

        index = int(choice)

        if index < 1 or index > len(available):
            show_error(
                f"Invalid location number. Choose 1 to {len(available)}, "
                "or 0 to quit booking."
            )
            continue

        return available[index - 1]


# ==========================================
# CAB SELECTION
# ==========================================

def choose_cab():
    while True:
        clear_screen()
        print("=" * 42)
        print("CHOOSE YOUR CAB".center(42))
        print("=" * 42)

        for number, (name, rate) in CAB_RATES.items():
            print(f"{number}. {name} - Rs. {rate}/km")

        print("\n0. Quit Booking")

        choice = safe_input("\nSelect cab type: ")

        if choice is None or choice == "0":
            print("\nBooking process stopped. No OTP was shared.")
            pause()
            return None

        if choice in CAB_RATES:
            return CAB_RATES[choice]

        show_error("Invalid cab choice. Select 1, 2, 3, or 0.")


# ==========================================
# BOOK RIDE
# ==========================================

def book_ride():
    source = choose_location("SELECT PICKUP LOCATION")
    if source is None:
        return

    destination = choose_location(
        "SELECT DESTINATION",
        excluded_location=source
    )
    if destination is None:
        return

    # Extra safety: pickup and destination must never match.
    if source == destination:
        show_error("Pickup and destination cannot be the same.")
        return

    distance = get_distance(source, destination)
    if distance is None:
        show_error("Distance is unavailable for this route.")
        return

    cab = choose_cab()
    if cab is None:
        return

    cab_type, rate = cab
    fare = calculate_fare(distance, rate)
    minutes = estimate_minutes(distance)

    clear_screen()
    print("=" * 42)
    print("RIDE SUMMARY".center(42))
    print("=" * 42)
    print(f"\nPickup        : {source}")
    print(f"Destination   : {destination}")
    print(f"Cab type      : {cab_type}")
    print(f"Distance      : {distance} km (demo)")
    print(f"Rate          : Rs. {rate}/km")
    print(f"Calculation   : {distance} km x Rs. {rate} = Rs. {fare:.2f}")
    print(f"Total fare    : Rs. {fare:.2f}")
    print(f"Estimated time: {minutes} minutes (demo)")
    print("\n" + "=" * 42)
    print("1. Confirm & Share OTP")
    print("2. Cancel Ride")
    print("0. Quit Booking")

    while True:
        confirmation = safe_input("\nChoose 1, 2, or 0: ")

        if confirmation is None or confirmation == "0":
            print("\nBooking process stopped. No OTP was shared.")
            pause()
            return

        if confirmation == "2":
            print("\nRide cancelled. No OTP was shared.")
            pause()
            return

        if confirmation == "1":
            break

        show_error("Invalid choice. Enter 1, 2, or 0.")

    otp = random.randint(1000, 9999)

    clear_screen()
    print("=" * 42)
    print("BOOKING CONFIRMED".center(42))
    print("=" * 42)
    print(f"\nPickup      : {source}")
    print(f"Destination : {destination}")
    print(f"Cab         : {cab_type}")
    print(f"Distance    : {distance} km")
    print(f"Fare        : Rs. {fare:.2f}")
    print(f"\nYour OTP is: {otp}")
    print("\nOTP shared successfully.")
    print("Cancellation is NOT allowed after OTP sharing.")
    print("=" * 42)
    pause()


# ==========================================
# MAIN MENU
# ==========================================

def main():
    validate_data()

    while True:
        clear_screen()
        print("=" * 42)
        print("CAB BOOKING CHATBOT".center(42))
        print("=" * 42)
        print("\n1. Book Ride")
        print("2. Exit")

        choice = safe_input("\nEnter your choice: ")

        if choice is None:
            print("\nExiting because input was interrupted.")
            break
        elif choice == "1":
            book_ride()
        elif choice == "2":
            clear_screen()
            print("=" * 42)
            print("Thank you for using our Cab Booking Chatbot!".center(42))
            print("Goodbye!".center(42))
            print("=" * 42)
            break
        else:
            show_error("Invalid menu choice. Please enter 1 or 2.")


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(f"\n[ERROR] An unexpected problem occurred: {error}")
        print("Please check the code and try again.")
