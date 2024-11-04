from Packages import Package
from Trucks import Truck
import csv

# Read Package CSV File
with open('Packages.csv') as csvfile, open('Location_Address_Data.csv') as csvfile2:
    readCSV = csv.reader(csvfile, delimiter=",")
    readLocCSV = list(csv.reader(csvfile2, delimiter=","))

    # Manually set the packages to go in each truck based on special notes
    truck1_packages = [1, 4, 7, 13, 14, 15, 16, 19, 20, 21, 29, 30, 34, 37, 39, 40]
    truck2_packages = [3, 5, 6, 18, 25, 26, 28, 31, 32, 36, 38]
    truck3_packages = [2, 8, 9, 10, 11, 12, 17, 22, 23, 24, 27, 33, 35]

    # Create truck objects: O(1)
    truck1 = Truck("Truck 1", "8:00")
    truck2 = Truck("Truck 2", "9:05")

    # Truck 3 is created without a leaving time. Leaving time will be the finished time of truck 1
    truck3 = Truck("Truck 3")

    # For loops to read package data and get numbers that correspond to address: O(n^2)
    for row in readCSV:
        # Store csv package data into variables
        pack_id = row[0]
        address = row[1]
        city = row[2]
        state = row[3]
        zipcode = row[4]
        deadline = row[5]
        weight = row[6]

        for line in readLocCSV:
            if line[2] == address:
                # The address id will make it easy to index rows and columns from the distance table
                address_id = line[0]

                # If the deadline is a specific time, add AM
                if deadline != "EOD":
                    deadline = f"{deadline} AM"

                # Create package object
                new_package = Package(pack_id, address, address_id, city, state, zipcode, deadline, weight)

                # Insert package objects into respective truck objects
                if int(pack_id) in truck1_packages:
                    new_package.truck = truck1
                    truck1.packages.append(new_package)
                elif int(pack_id) in truck2_packages:
                    new_package.truck = truck2
                    truck2.packages.append(new_package)
                elif int(pack_id) in truck3_packages:
                    new_package.truck = truck3
                    truck3.packages.append(new_package)

    # Getter functions for each truck: O(1)
    def get_truck1():
        return truck1


    def get_truck2():
        return truck2


    def get_truck3():
        return truck3
