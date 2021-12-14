"""
    This type of algorithm have two obligatory functions:

        *initial_allocation*: invoked at the start of the simulation

        *run* invoked according to the assigned temporal distribution.

"""

from yafs.placement import Placement

class CloudPlacement(Placement):
    """
    This implementation locates the services of the application in the cheapest cloud regardless of where the sources or sinks are located.

    It only runs once, in the initialization.

    """
    def initial_allocation(self, sim, app_name):
        #We find the ID-nodo/resource
        value = {"mytag": "cloud"} # or whatever tag

        id_cluster = sim.topology.find_IDs(value)
        app = sim.apps[app_name]
        services = app.services

        for module in services:
            if module in self.scaleServices:
                for rep in range(0, self.scaleServices[module]):
                    idDES = sim.deploy_module(app_name,module,services[module],id_cluster)



    #end function

class PartialEdgePlacement(Placement):
    """
    This implementation locates the services of the application in the cheapest cloud regardless of where the sources or sinks are located.

    It only runs once, in the initialization.

    """

    def initial_allocation(self, sim, app_name):
        # We find the ID-nodo/resource
        edge = {"mytag": "edge"}  # or whatever tag
        ground_station = {"mytag": "ground_station"}
        drone = {"mytag": "drone"}

        drone_cluster = sim.topology.find_IDs(drone)
        gs_cluster = sim.topology.find_IDs(ground_station)
        edge_cluster = sim.topology.find_IDs(edge)
        app = sim.apps[app_name]
        services = app.services
        for module in services:
            if module in self.scaleServices:
                for rep in range(0, self.scaleServices[module]):
                    #print(app_name, module, services[module], edge)
                    print("MODULE NAME")
                    print(module)
                    if((module == 'Image_Acquisition') or (module == 'IMU_Measurement_Acquisition') or (module == 'Prediction')
                            or (module == 'Feature_Extraction')):
                        idDES = sim.deploy_module(app_name, module, services[module], drone_cluster)
                        print("DRONE DEPLOYMENT")
                    else:
                        idDES = sim.deploy_module(app_name, module, services[module], edge_cluster)
                        print("EDGE DEPLOYMENT")

class FullEdgePlacement(Placement):
    """
    This implementation locates the services of the application in the cheapest cloud regardless of where the sources or sinks are located.

    It only runs once, in the initialization.

    """

    def initial_allocation(self, sim, app_name):
        # We find the ID-nodo/resource
        edge = {"mytag": "edge"}  # or whatever tag
        ground_station = {"mytag": "ground_station"}
        drone = {"mytag": "drone"}

        drone_cluster = sim.topology.find_IDs(drone)
        gs_cluster = sim.topology.find_IDs(ground_station)
        edge_cluster = sim.topology.find_IDs(edge)
        app = sim.apps[app_name]
        services = app.services
        for module in services:
            if module in self.scaleServices:
                for rep in range(0, self.scaleServices[module]):
                    #print(app_name, module, services[module], edge)
                    print("MODULE NAME")
                    print(module)
                    if (module == 'Image_Acquisition') or (module == 'IMU_Measurement_Acquisition') or (module == 'Prediction'):
                        idDES = sim.deploy_module(app_name, module, services[module], drone_cluster)
                        print("DRONE DEPLOYMENT")
                    else:
                        idDES = sim.deploy_module(app_name, module, services[module], edge_cluster)
                        print("EDGE DEPLOYMENT")





