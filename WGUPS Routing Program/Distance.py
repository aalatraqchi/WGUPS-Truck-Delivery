import csv
import math
from Reader import get_truck1, get_truck2, get_truck3
from Hash import HashTable

with open("Distances.csv") as csvfile:
    readCSV = csv.reader(csvfile, delimiter=",")
    distances_info = list(csvfile.readlines())

# Variables for hash table and trucks
pack_hash = HashTable()
truck1, truck2, truck3 = get_truck1(), get_truck2(), get_truck3()


# Gets distance given distance info, row index, and column index
def get_distance(distance_sheet, row, column):
    row_distances = distance_sheet[row].split(",")

    # The row number has to be greater than the colum number to avoid indexing out of range
    if row >= column:
        return float(row_distances[column])


# Updates total distance, time, address that truck is at, and sets time of delivery of package
def update_dist_time(min_dist, curr_dist, curr_time, new_address, truck):

    # Deliver and update time
    truck_mph = 18.0
    curr_dist += min_dist
    elapsed_time = min_dist / truck_mph
    hrs = math.floor(elapsed_time)
    minutes = round((elapsed_time - hrs) * 60)
    time_split = curr_time.split(":")
    new_hr = int(time_split[0]) + hrs
    new_min = int(time_split[1]) + minutes
    curr_address = new_address

    # Add an hour for every time the minutes pass 60
    if new_min >= 60:
        add_hrs = new_min // 60
        new_min -= add_hrs * 60
        new_hr += add_hrs

    # Add a leading 0 to single digit minutes
    if new_min < 10:
        new_min = f"0{new_min}"

    new_time = f"{new_hr}:{new_min}"

    # Updates delivery time variable of the package delivered at the address, and inserts package into hash table
    for pack in truck.packages:
        if pack.address == curr_address:
            pack.time = new_time
            pack_hash.insert(int(pack.id), pack)

    return curr_dist, new_time, curr_address


def get_index(address, curr_truck):
    pack_index = 0

    if address != "4001 South 700 East":
        for pack in curr_truck.packages:
            if pack.address == address:
                pack_index = int(pack.addressID) - 1

    return pack_index


# Nearest-Neighbor algorithm to carry out deliveries
def deliver_packages(start_time, truck):

    # Variables to update with deliveries
    time = start_time
    total_distance = 0.0
    min_dist = 0.0
    current_address = "4001 South 700 East"
    next_address = ""
    delivering = True
    packages_delivered = 0

    # While there are still packages to be delivered, continue the delivering process for truck 1
    while delivering:
        index1 = get_index(current_address, truck)

        for package in truck.packages:
            # Only consider distance of package address if package hasn't been delivered
            if package.time == 0:

                # Correct address for package 9 if it hasn't been corrected
                if package.id == "9" and package.address != "410 S State St":
                    package.address = "410 S State St"
                    package.addressID = "20"

                index2 = int(package.addressID) - 1

                # Larger index must be first parameter to prevent out of range error
                if index1 >= index2:
                    distance = get_distance(distances_info, index1, index2)
                else:
                    distance = get_distance(distances_info, index2, index1)

                # Update min distance if distance to address is lower than current min distance, and update next address
                if min_dist == 0 or distance < min_dist:
                    min_dist = distance
                    next_address = package.address

        # Deliver package: update time, total distance, and current address to the address of the package delivered
        total_distance, time, current_address = update_dist_time(min_dist, total_distance, time, next_address, truck)

        # Reset minimum distance to find next minDist when for loop runs again
        min_dist = 0

        # Count each delivered package
        for package in truck.packages:
            if package.time != 0:
                packages_delivered += 1

        # Stop delivering when all packages have been delivered
        if packages_delivered == len(truck.packages):
            packages_delivered = 0

            # When all packages are delivered, the truck will head back to hub
            final_index = get_index(current_address, truck)
            next_address = "4001 South 700 East"
            final_distance = get_distance(distances_info, final_index, 0)
            min_dist = final_distance
            total_distance, time, current_address = update_dist_time(min_dist, total_distance,
                                                                     time, next_address, truck)

            # Once the truck has returned to hub, set its finished time and distance traveled
            truck.timeFinished = time
            truck.distanceTraveled = total_distance
            delivering = False
        else:
            # If not all packages have been delivered, reset counter to stay in while loop
            packages_delivered = 0


# Call the delivery function for all 3 trucks
deliver_packages(truck1.time_left_hub, truck1)
deliver_packages(truck2.time_left_hub, truck2)
truck3.time_left_hub = truck1.timeFinished
deliver_packages(truck3.time_left_hub, truck3)

final_total = round(truck1.distanceTraveled + truck2.distanceTraveled + truck3.distanceTraveled)


# Function to return hash table
def get_hash_table():
    return pack_hash
