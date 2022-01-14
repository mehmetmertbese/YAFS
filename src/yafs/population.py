"""
    This type of algorithm have two main functions:

        *initial_allocation*: invoked at the start of the simulation

        *run* invoked according to the assigned temporal distribution.

"""
import logging
import threading


class Population(object):
    """
    A population algorithm controls how the message generation of the sensor modules is associated in the nodes of the topology.
    This assignment is based on a generation controller to each message. And a generation control is assigned to a node or to several
    in the topology both during the initiation and / or during the execution of the simulation.

    .. note:: A class interface

    Args:
        name (str): associated name

        activation_dist (function): a distribution function to active the *run* function in execution time

    Kwargs:
        param (dict): the parameters of the *activation_dist*

    """
    def __init__(self, name, activation_dist=None, logger=None):
        self.logger = logger or logging.getLogger(__name__)
        self.name = name
        self.activation_dist = activation_dist

        # self.id_process = -1
        self.src_control = []
        self.sink_control = []

    def set_sink_control(self, values):
        """
        localization of sink modules
        """
        self.sink_control.append(values)

    def get_next_activation(self):
        """
        Returns:
            the next time to be activated in the simulation
        """
        return self.activation_dist.next()


    def set_src_control(self,values):
        """
        Stores the drivers of each message generator.

        Args:
            values (dict):
        """
        self.src_control.append(values)


    def initial_allocation(self,sim,app_name):
        """
        Given an ecosystem and an application, it starts the allocation of pure sources in the topology.

        .. attention:: override required
        """
        self.run()

    # override
    def run(self, sim):
        """
        This method will be invoked during the simulation to change the assignment of the modules that generate the messages.

        Args:
            sim (:mod: yafs.core.Sim)
        """
        self.logger.debug("Activiting - RUN - Population")
        """ User definition of the Population evolution """




class Statical(Population):
    """
    This implementation of a population algorithm statically assigns the generation of a source in a node of the topology. It is only invoked in the initialization.

    Extends: :mod: Population
    """

    def initial_allocation(self,sim,app_name):
        #Assignment of SINK and SOURCE pure modules

        #print("ATTRIBUTES")
        #print(sim.topology.nodeAttributes)

        for id_entity in sim.topology.nodeAttributes:

            #print("ID ENTITY")
            #print(id_entity)

            entity = sim.topology.nodeAttributes[id_entity]
            for ctrl in self.sink_control:
                #A node can have several sinks modules
                if entity["model"]==ctrl["model"]:

                    print()
                    print("SINK CONTROL")
                    print(self.sink_control)
                    print("IM HERE")
                    print(entity["model"])
                    print(id_entity)
                    print()

                    #In this node there is a sink
                    module = ctrl["module"]
                    for number in range(ctrl["number"]):
                        sim.deploy_sink(app_name, node=id_entity, module=module)
            #end for sink control

            for ctrl in self.src_control:
                # A node can have several source modules
                if entity["model"] == ctrl["model"]:

                    print()
                    print("SOURCE CONTROL")
                    print(self.src_control)
                    print("IM HERE2")
                    print(entity["model"])
                    print(id_entity)
                    print()

                    msg = ctrl["message"]
                    dst = ctrl["distribution"]
                    source_threads = list()
                    for number in range(ctrl["number"]):
                        #logging.info("BEING DEPLOYED: ")
                        #logging.info(ctrl)
                        #logging.info("DEPLOYED ENTITY: ")
                        #logging.info(id_entity)
                        #source_thread = threading.Thread(target=sim.deploy_source, kwargs= {'app_name': app_name, 'id_node':id_entity,'msg' : msg,'distribution':dst})
                        idsrc = sim.deploy_source(app_name,id_node=id_entity,msg=msg,distribution=dst)
                        # the idsrc can be used to control the deactivation of the process in a dynamic behaviour

            #end for src control

        #end assignments
