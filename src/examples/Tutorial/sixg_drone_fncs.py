from yafs.placement import Placement


class EdgePlacement(Placement):
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
                    print(app_name, module, services[module], edge)
                    idDES = sim.deploy_module(app_name, module, services[module], edge)

    # end function
