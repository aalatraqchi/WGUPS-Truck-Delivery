class Package:
    # Constructor
    def __init__(self, pack_id, address, address_id, city, state, zipcode, deadline,
                 weight):
        self.id = pack_id
        self.address = address
        self.addressID = address_id
        self.city = city
        self.state = state
        self.zipcode = zipcode
        self.deadline = deadline
        self.weight = weight
        self.status = "Hub"
        self.time = 0
        self.truck = None
