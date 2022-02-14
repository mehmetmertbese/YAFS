from topology import add_link

ENTITY_LIST = {}
ENTITY_ID_COUNTER = 0


def get_entity_from_id(id):
    return ENTITY_LIST.get(id)


def get_entity_list():
    return ENTITY_LIST


class Entity:
    global ENTITY_ID_COUNTER

    def __init__(self, id=None, model=None, ipt=None, ram=None, cost=None, power_consumption=None, user=None,
                 mytag=None, active_tasks=0):
        global ENTITY_ID_COUNTER
        if id is not None:
            self.id = id
        else:
            self.id = ENTITY_ID_COUNTER
            ENTITY_ID_COUNTER += 1
        self.model = model
        self.ipt = ipt
        self.ram = ram
        self.cost = cost
        self.power_consumption = power_consumption
        self.user = user
        self.mytag = mytag
        self.uptime = None
        self.available_ram = ram
        self.active_tasks = active_tasks
        ENTITY_LIST[self.id] = self

    def add_task(self):
        self.active_tasks += 1

    def get_id(self):
        return self.id

    def set_uptime(self, uptime):
        self.uptime = uptime

    def get_uptime(self):
        return self.uptime

    def get_available_ram(self):
        return self.available_ram

    def set_available_ram(self, available_ram):
        self.available_ram = available_ram

    def allocate_ram(self, ram_used):
        if self.available_ram < ram_used:
            raise RuntimeError("There is not enough RAM for the module to be allocated!")
        else:
            self.available_ram -= ram_used

        print("AVAILABLE RAM")
        print(self.available_ram)
        print("RAM USED")
        print(ram_used)


class Base_Station(Entity):
    def __init__(self, id=None, model="base_station", ipt=2000 * (10 ** 9), ram=4000000,
                 cost=3, power_consumption=40.0, user=None, mytag="base_station", active_tasks=0, location=[0, 0]):
        if location is None:
            location = [0, 0]
        global ENTITY_ID_COUNTER
        if id is not None:
            self.id = id
        else:
            self.id = ENTITY_ID_COUNTER
            ENTITY_ID_COUNTER += 1
        self.model = model
        self.ipt = ipt
        self.ram = ram
        self.cost = cost
        self.power_consumption = power_consumption
        self.user = user
        self.mytag = mytag
        self.uptime = None
        self.available_ram = ram
        self.active_tasks = active_tasks
        self.location = location
        ENTITY_LIST[self.id] = self

    def get_location(self):
        return self.location

    def update_location(self, new_location):
        self.location = new_location


class Edge_Server(Entity):
    def __init__(self, id=None, model="edge_server", ipt=None, ram=100000000,
                 cost=3, power_consumption=40.0, user=None, mytag="edge", active_tasks=0):
        global ENTITY_ID_COUNTER
        if id is not None:
            self.id = id
        else:
            self.id = ENTITY_ID_COUNTER
            ENTITY_ID_COUNTER += 1
        self.model = model
        self.ipt = ipt
        self.ram = ram
        self.cost = cost
        self.power_consumption = power_consumption
        self.user = user
        self.mytag = mytag
        self.uptime = None
        self.available_ram = ram
        self.active_tasks = active_tasks
        ENTITY_LIST[self.id] = self


class Sink(Entity):
    def __init__(self, id=None, model=None, ipt=None, ram=1000,
                 cost=3, power_consumption=40.0, user=None, mytag="sink", active_tasks=0):
        global ENTITY_ID_COUNTER
        if id is not None:
            self.id = id
        else:
            self.id = ENTITY_ID_COUNTER
            ENTITY_ID_COUNTER += 1
        self.model = model
        self.ipt = ipt
        self.ram = ram
        self.cost = cost
        self.power_consumption = power_consumption
        self.user = user
        self.mytag = mytag
        self.uptime = None
        self.available_ram = ram
        self.active_tasks = active_tasks
        ENTITY_LIST[self.id] = self


class Source(Entity):
    def __init__(self, id=None, model=None, ipt=None, ram=1000,
                 cost=3, power_consumption=40.0, user=None, mytag="source", active_tasks=0):
        global ENTITY_ID_COUNTER
        if id is not None:
            self.id = id
        else:
            self.id = ENTITY_ID_COUNTER
            ENTITY_ID_COUNTER += 1
        self.model = model
        self.ipt = ipt
        self.ram = ram
        self.cost = cost
        self.power_consumption = power_consumption
        self.user = user
        self.mytag = mytag
        self.uptime = None
        self.available_ram = ram
        self.active_tasks = active_tasks
        ENTITY_LIST[self.id] = self


class Mobile_Device(Entity):
    def __init__(self, id=None, model=None, ipt=None, ram=1000,
                 cost=3, power_consumption=40.0, user=None, mytag="drone", active_tasks=0, location=[0, 0],
                 tx_power=24, bw_used = 10):
        global ENTITY_ID_COUNTER

        if id is not None:
            self.id = id
        else:
            self.id = ENTITY_ID_COUNTER
            ENTITY_ID_COUNTER += 1

        self.model = model
        self.ipt = ipt
        self.ram = ram
        self.cost = cost
        self.power_consumption = power_consumption
        self.user = user
        self.mytag = mytag
        self.uptime = None
        self.available_ram = ram
        self.active_tasks = active_tasks
        ENTITY_LIST[self.id] = self
        self.location = location  # 2D Plane Coordinates
        self.tx_power = tx_power  # in dBm
        self.bw_used = bw_used # in MHz

    def get_location(self):
        return self.location

    def update_location(self, new_location):
        self.location = new_location

    def get_bw_used(self):
        return self.bw_used

    def update_bw_used(self, new_bw_used):
        self.bw_used = new_bw_used

    def get_tx_power(self):
        return self.tx_power

    def update_tx_power(self, new_tx_power):
        self.tx_power = new_tx_power

#TODO: ------------------ CLASSES TO BE EXTENDED AND SCRATCHES ----------------------
# class Drone(Entity):
#     def __init__(self, user_id = -1):
#         super().__init__()
#         camera_drone = Source(model="camera", ipt=100 * (10 ** 6), ram=4000000,
#                                 cost=3, power_consumption=40.0)
#
#        imu_user = Source(model="imu", ipt=100 * (10 ** 9), ram=4000000,
#                           cost=3, power_consumption=40.0, user=user_id)
#
#         actuator_user = Sink(model="actuator_device", ipt=1 * (10 ** 6), ram=4000000,
#                              cost=3, power_consumption=40.0, user=user_id)
#
#         drone_user = Mobile_Device(model="drone_user", ipt=DRONE_CPU, ram=4000000,
#                                    cost=3, power_consumption=40.0, user=user_id, mytag="drone")
