class Truck:
    # Constructor
    def __init__(self, name, time_left=0):
        self.name = name
        self.time_left_hub = time_left
        self.timeFinished = 0
        self.distanceTraveled = 0
        self.packages = []
