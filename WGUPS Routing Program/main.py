# Ashraf Al-Atraqchi (ID: 011364001)

from Distance import get_hash_table, final_total

# Get hash table from Distance.py
hashtable = get_hash_table()


# Function to parse time strings and return computable hours and minutes
def parse_time(time):
    split_time = time.split(":")
    hours = int(split_time[0])
    minutes = int(split_time[1])

    return hours, minutes


# Sets status of package at a given time
def set_package_status(package_id, hours, minutes):
    package = hashtable.search(package_id)

    # Checks if the package exist: O(1)
    if package is not None:
        delivered_time = package.time
        hours2, minutes2 = parse_time(delivered_time)
        leave_hours, leave_minutes = parse_time(package.truck.time_left_hub)

        # Compare time with truck leaving times to determine if packages are en route
        if hours > leave_hours:
            package.status = f"En route - {package.truck.name}"
        elif hours == leave_hours:
            if minutes >= leave_minutes:
                package.status = f"En route - {package.truck.name}"
            else:
                package.status = "At the hub"
        else:
            package.status = "At the hub"

        # Compare time with delivered times of packages and change status accordingly
        if hours2 < hours:
            # Set correct AM/PM
            if hours2 > 12:
                hours2 -= 12
                package.status = f"Delivered at {hours2}:{minutes2} PM"
            elif hours2 == 12:
                package.status = f"Delivered at {delivered_time} PM"
            else:
                package.status = f"Delivered at {delivered_time} AM"
        elif hours2 == hours:
            if minutes2 <= minutes:
                # Set correct AM/PM
                if hours2 > 12:
                    hours2 -= 12
                    package.status = f"Delivered at {hours2}:{minutes2} PM"
                elif hours2 == 12:
                    package.status = f"Delivered at {delivered_time} PM"
                else:
                    package.status = f"Delivered at {delivered_time} AM"


# Looks up package from hash table and returns information
def look_up_package(package_id):
    # Retrieve package from hash table: O(n)
    package = hashtable.search(package_id)

    # Checks if the package exists: O(1)
    if package is not None:
        return (package.id, package.address, package.city, package.zipcode,
                package.deadline, package.weight, package.status)
    else:
        return None


# Returns valid user input for hours and minutes
def get_hrs_min():
    hrs_input = 0
    min_input = 0

    # Re-prompt until user enters valid input
    while True:
        try:
            # Only valid hours are during the delivery day (8 AM to 5 PM)
            hrs_input = int(input("Enter hours (8-17): "))
        except ValueError:
            print("Value must be between 8 and 17 (8AM - 5PM)")
            continue
        else:
            if hrs_input < 8 or hrs_input > 17:
                print("Value must be between 8 and 17 (8AM - 5PM)")
                continue
            else:
                break

    # Re-prompt until user enters valid input
    while True:
        try:
            # Only allow valid minutes
            min_input = int(input("Enter minutes (0-59): "))
        except ValueError:
            print("Value must be between 0 and 59 minutes")
            continue
        else:
            if min_input < 0 or min_input > 59:
                print("Value must be between 0 and 59 minutes")
                continue
            else:
                break

    # Add leading 0 to single digit minutes
    if min_input < 10:
        min_input = f"0{min_input}"

    return hrs_input, min_input


# UI to be displayed when user runs programs
def print_menu():
    print()
    print("Please select an option:")
    print("1 - Display all package information at a given time")
    print("2 - Display information for a single package at a given time")
    print("3 - End Program")


if __name__ == '__main__':
    print("\n* WGUPS Routing Program *")
    print("--------------------------")
    print(f"All packages have been successfully delivered in {final_total} miles!")

    # Valid menu options to check user input
    valid_options = ["1", "2", "3"]
    print_menu()

    # Get user input for menu option
    user_input = input()

    # Keep displaying menu and receive input until input is valid: O(n)
    while user_input not in valid_options:
        print("Invalid option!")
        print_menu()
        user_input = input()

    # If user selects option 1, display all package info
    if user_input == valid_options[0]:

        user_hrs, user_min = get_hrs_min()

        # Set correct AM/PM based on hour
        if user_hrs > 12:
            new_hrs = user_hrs - 12
            print(f"\nStatus for all packages at {new_hrs}:{user_min} PM:")
        elif user_hrs == 12:
            print(f"\nStatus for all packages at {user_hrs}:{user_min} PM:")
        else:
            print(f"\nStatus for all packages at {user_hrs}:{user_min} AM:")

        # Iterate through every package and call helper functions, then display info: O(1)
        for i in range(1, 41):
            set_package_status(i, user_hrs, int(user_min))
            pack_id, address, city, zipcode, deadline, weight, status = look_up_package(i)
            print(f"{pack_id}, {address}, {city}, {zipcode}, {deadline}, {weight}, {status}")

    elif user_input == valid_options[1]:
        id_input = 0

        # Re-prompt until user enters valid input
        while True:
            try:
                id_input = int(input("Enter package ID: "))
            except ValueError:
                print("Must enter a valid package ID")
                continue
            else:
                if look_up_package(id_input) is None:
                    print(f"No package with id {id_input} was found!")
                    continue
                else:
                    break

        user_hrs, user_min = get_hrs_min()

        # Set correct AM/PM based on hour
        if user_hrs > 12:
            new_hrs = user_hrs - 12
            print(f"\nStatus for package {id_input} at {new_hrs}:{user_min} PM:")
        elif user_hrs == 12:
            print(f"\nStatus for package {id_input} at {user_hrs}:{user_min} PM:")
        else:
            print(f"\nStatus for package {id_input} at {user_hrs}:{user_min} AM:")

        # Display info for single package
        set_package_status(id_input, user_hrs, int(user_min))
        pack_id, address, city, zipcode, deadline, weight, status = look_up_package(id_input)
        print(f"{pack_id}, {address}, {city}, {zipcode}, {deadline}, {weight}, {status}")

    elif user_input == valid_options[2]:
        exit("Program Ended.")
