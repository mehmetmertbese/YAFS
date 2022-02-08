"""
    This type of algorithm have two obligatory functions:

        *initial_allocation*: invoked at the start of the simulation

        *run* invoked according to the assigned temporal distribution.

"""

from yafs.placement import Placement
from yafs.entities_mert import get_entity_from_id
import yafs.entities_mert


class CloudPlacement(Placement):
    """
    This implementation locates the services of the application in the cheapest cloud regardless of where the sources or sinks are located.

    It only runs once, in the initialization.

    """

    def initial_allocation(self, sim, app_name):
        # We find the ID-nodo/resource
        value = {"mytag": "cloud"}  # or whatever tag

        id_cluster = sim.topology.find_IDs(value)
        app = sim.apps[app_name]
        services = app.services

        for module in services:
            if module in self.scaleServices:
                for rep in range(0, self.scaleServices[module]):
                    idDES = sim.deploy_module(app_name, module, services[module], id_cluster)

    # end function


class PartialEdgePlacement(Placement):
    """
    This implementation locates the services of the application in the cheapest cloud regardless of where the sources or sinks are located.

    It only runs once, in the initialization.

    """

    def initial_allocation(self, sim, app_name):
        # We find the ID-nodo/resource
        edge = {"mytag": "edge"}  # or whatever tag
        base_station = {"mytag": "base_station"}
        drone = {"mytag": "drone"}

        drone_cluster = sim.topology.find_IDs(drone)
        base_cluster = sim.topology.find_IDs(base_station)
        edge_cluster = sim.topology.find_IDs(edge)
        app = sim.apps[app_name]
        services = app.services
        for module in services:
            if module in self.scaleServices:
                for rep in range(0, self.scaleServices[module]):
                    # print(app_name, module, services[module], edge)
                    print("MODULE NAME")
                    print(module)
                    if ((module == 'Image_Acquisition') or (module == 'IMU_Measurement_Acquisition') or (
                            module == 'Prediction')
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
        base_station = {"mytag": "base_station"}
        drone = {"mytag": "drone"}

        drone_cluster = sim.topology.find_IDs(drone)
        # print("DRONE CLUSTER")
        # print(drone_cluster)
        base_cluster = sim.topology.find_IDs(base_station)
        edge_cluster = sim.topology.find_IDs(edge)
        app = sim.apps[app_name]
        services = app.services
        for module in services:
            if module in self.scaleServices:
                for rep in range(0, self.scaleServices[module]):
                    # print(app_name, module, services[module], edge)
                    """
                    print("REP")
                    print(rep)
                    print("MODULE")
                    print(module)
                    print("DRONE")
                    print(drone_cluster[rep])
                    """
                    print(app_name)
                    if (module == 'Image_Acquisition') or (module == 'IMU_Measurement_Acquisition') or (
                            module == 'Prediction'):
                        idDES = sim.deploy_module(app_name, module, services[module], [drone_cluster[rep]])
                        print("DRONE DEPLOYMENT")
                    else:
                        idDES = sim.deploy_module(app_name, module, services[module], edge_cluster)
                        print("EDGE DEPLOYMENT")


class OnboardPlacement(Placement):
    """
    This implementation locates the services of the application in the cheapest cloud regardless of where the sources or sinks are located.

    It only runs once, in the initialization.

    """

    def initial_allocation(self, sim, app_name):
        # We find the ID-nodo/resource
        edge = {"mytag": "edge"}  # or whatever tag
        base_station = {"mytag": "base_station"}
        drone = {"mytag": "drone"}

        drone_cluster = sim.topology.find_IDs(drone)
        base_cluster = sim.topology.find_IDs(base_station)
        edge_cluster = sim.topology.find_IDs(edge)
        app = sim.apps[app_name]
        services = app.services
        for module in services:
            if module in self.scaleServices:
                for rep in range(0, self.scaleServices[module]):
                    # print(app_name, module, services[module], edge)
                    print("MODULE NAME")
                    print(module)
                    idDES = sim.deploy_module(app_name, module, services[module], drone_cluster)
                    print("DRONE DEPLOYMENT")


class Mert_FullEdgePlacement(Placement):
    """
    This implementation locates the services of the application in the cheapest cloud regardless of where the sources or sinks are located.

    It only runs once, in the initialization.

    """

    def initial_allocation(self, sim, app_name):
        # We find the ID-nodo/resource
        edge = {"mytag": "edge"}  # or whatever tag
        base_station = {"mytag": "base_station"}
        drone_1 = {"mytag": "drone_1"}
        drone_2 = {"mytag": "drone_2"}

        drone_cluster_1 = sim.topology.find_IDs(drone_1)
        drone_cluster_2 = sim.topology.find_IDs(drone_2)
        # print("DRONE CLUSTER")
        # print(drone_cluster)
        base_cluster = sim.topology.find_IDs(base_station)
        edge_cluster = sim.topology.find_IDs(edge)
        app = sim.apps[app_name]
        services = app.services
        for module in services:
            if module in self.scaleServices:
                for rep in range(0, self.scaleServices[module]):
                    # print(app_name, module, services[module], edge)
                    """
                    print("REP")
                    print(rep)
                    print("MODULE")
                    print(module)
                    print("DRONE")
                    print(drone_cluster[rep])
                    print("APP NAME")
                    print(sim.apps)
                    """
                    if ((module == 'Image_Acquisition') or (module == 'IMU_Measurement_Acquisition') or (
                            module == 'Prediction')) and app_name == '6G_Drone_1':
                        idDES = sim.deploy_module(app_name, module, services[module], drone_cluster_1)
                        print("DRONE_1 DEPLOYMENT")
                    elif ((module == 'Image_Acquisition') or (module == 'IMU_Measurement_Acquisition') or (
                            module == 'Prediction')) and app_name == '6G_Drone_2':
                        idDES = sim.deploy_module(app_name, module, services[module], drone_cluster_2)
                        print("DRONE_2 DEPLOYMENT")
                    else:
                        idDES = sim.deploy_module(app_name, module, services[module], edge_cluster)
                        print("EDGE DEPLOYMENT")


class Mert_FullEdgePlacement_Arbitrary_Number(Placement):
    def initial_allocation(self, sim, app_name):
        # We find the ID-nodo/resource
        edge = {"mytag": "edge"}  # or whatever tag
        base_station = {"mytag": "base_station"}
        drone = {"mytag": "drone"}
        drone_cluster = sim.topology.find_IDs(drone)

        base_cluster = sim.topology.find_IDs(base_station)
        edge_cluster = sim.topology.find_IDs(edge)
        app = sim.apps[app_name]

        #print("DRONE CLUSTER")
        #print(drone_cluster)

        #print("APP DATA")
        #print(app.data)

        services = app.services
        #print("SERVICES")
        #print(services)

        for module in services:
            if module in self.scaleServices:
                for rep in range(0, self.scaleServices[module]):

                    app_number = app.get_number()

                    if ((module == 'Image_Acquisition') or (module == 'IMU_Measurement_Acquisition') or (
                            module == 'Prediction')):
                        idDES = sim.deploy_module(app_name, module, services[module], [drone_cluster[app_number]])
                        #print("DRONE DEPLOYMENT")
                    else:
                        idDES = sim.deploy_module(app_name, module, services[module], edge_cluster)
                        #print("EDGE DEPLOYMENT")
