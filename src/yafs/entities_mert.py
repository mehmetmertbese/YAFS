def get_entity_from_id(id):
    return Entity.entity_list.get(id)

def show_entity_list():
    return Entity.entity_list

class Entity:

    entity_list = {}

    def __init__(self, id=None, model=None, ipt=None, ram=None, cost=None, power_consumption=None, user=None,
                 mytag=None):
        self.id = id
        self.model = model
        self.ipt = ipt
        self.ram = ram
        self.cost = cost
        self.power_consumption = power_consumption
        self.user = user
        self.mytag = mytag
        self.uptime = None
        self.available_ram = ram
        Entity.entity_list[id] = self

    def set_uptime(self, uptime):
        self.uptime = uptime

    def get_uptime(self):
        return self.uptime

    def allocate_ram(self, ram_used):

        print("AVAILABLE RAM")
        print(self.available_ram)
        print("RAM USED")
        print(ram_used)

        if self.available_ram < ram_used:
            raise RuntimeError("There is not enough RAM for the module to be allocated!")
        else:
            self.available_ram -= ram_used