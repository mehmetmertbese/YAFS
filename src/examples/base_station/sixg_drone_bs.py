"""

    Created on Wed Nov 22 15:03:21 2017

    @author: isaac

"""
import random
import networkx as nx
import argparse
from pathlib import Path
import time
import numpy as np

from yafs.core import Sim
from yafs.application import Application, Message

from yafs.population import *
from yafs.topology import Topology

from simpleSelection import MinimunPath
import simplePlacement
from yafs.stats import Stats
from yafs.distribution import deterministic_distribution, deterministicDistributionStartPoint
from yafs.application import fractional_selectivity
from examples.Tutorial.csv_reader import tim_out_read
import pandas as pd

RANDOM_SEED = 1
CAMERA_RATE = 10
IMU_RATE = CAMERA_RATE * 10
IMU_SIZE = 24
DRONE_CPU = 10 ** 6
EDGE_DRONE_CMPT_PWR_RATIO = 20
TIMESTAMP = 4
UDP_OVERHEAD = 24
CORRECTED_POSE_SIZE = 28
FRONT_END_CMPT_LOAD = 532.64 * (10 ** 6)
BACK_END_CMPT_LOAD = 59.10 * (10 ** 6)
UNCOMPRESSED_IMAGE_SIZE = 39.3 * (10 ** 6)
NUMBER_OF_UDP_PACKETS = np.ceil(UNCOMPRESSED_IMAGE_SIZE / 508)
NUMBER_OF_FEATURES = 320
FEATURE_SIZE = 12
UPLINK_RATE = (100 / 8) * (10 ** -3)
UPLINK_RATE_ARRAY = [(x * ((10 / 8) * (10 ** -3))) for x in range(11, 81)]
DOWNLINK_RATE = (100) * (10 ** -3)
folder_results = Path("results/")
folder_results.mkdir(parents=True, exist_ok=True)
folder_results = str(folder_results) + "/"
CSV_FILE = folder_results + 'sim_trace_full_r4_n20_faster_connection.csv'

from yafs.placement import Placement


# @profile
def up_rate_evaluation_fnc(simulated_time, uplink_rate):
    def create_application():
        # APLICATION
        a = Application(name="6G_Drone")

        # (S) --> (ServiceA) --> (A)
        a.set_modules([{"Camera": {"Type": Application.TYPE_SOURCE}},
                       {"IMU": {"Type": Application.TYPE_SOURCE}},
                       {"Image_Acquisition": {"RAM": 10, "Type": Application.TYPE_MODULE}},
                       {"IMU_Measurement_Acquisition": {"RAM": 10, "Type": Application.TYPE_MODULE}},
                       {"Feature_Extraction": {"RAM": 10, "Type": Application.TYPE_MODULE}},
                       {"MSCKF_Update": {"RAM": 10, "Type": Application.TYPE_MODULE}},
                       {"Prediction": {"RAM": 10, "Type": Application.TYPE_MODULE}},
                       {"Pose_Correction": {"Type": Application.TYPE_SINK}},
                       ])
        """
        Messages among MODULES (AppEdge in iFogSim)
        """
        m_image_acq = Message("Image_Acquirement", "Camera", "Image_Acquisition", instructions=0, bytes=0)
        m_inertial_data_acq = Message("Inertial_Data_Acquirement", "IMU", "IMU_Measurement_Acquisition",
                                      instructions=0, bytes=0)
        m_image = Message("Image", "Image_Acquisition", "Feature_Extraction", instructions=FRONT_END_CMPT_LOAD,
                          bytes=(UNCOMPRESSED_IMAGE_SIZE + CAMERA_RATE * (
                                  IMU_SIZE + TIMESTAMP) + UDP_OVERHEAD * NUMBER_OF_UDP_PACKETS))
        m_extracted_features = Message("Extracted Features", "Feature_Extraction", "MSCKF_Update",
                                       instructions=BACK_END_CMPT_LOAD,
                                       bytes=NUMBER_OF_FEATURES * FEATURE_SIZE + TIMESTAMP)
        m_inertial_data = Message("Inertial_Data", "IMU_Measurement_Acquisition", "MSCKF_Update", instructions=0,
                                  bytes=CAMERA_RATE * (IMU_SIZE + TIMESTAMP))
        m_corrected_pose = Message("Corrected_Pose", "MSCKF_Update", "Prediction", instructions=0,
                                   bytes=(CORRECTED_POSE_SIZE + TIMESTAMP + UDP_OVERHEAD))
        m_pose_prediction = Message("Pose_Prediction", "Prediction", "Pose_Correction", instructions=0,
                                    bytes=0)

        """
        Defining which messages will be dynamically generated # the generation is controlled by Population algorithm
        """
        a.add_source_messages(m_image_acq)
        a.add_source_messages(m_inertial_data_acq)

        """
        MODULES/SERVICES: Definition of Generators and Consumers (AppEdges and TupleMappings in iFogSim)
        """
        # MODULE SERVICES
        a.add_service_module("Image_Acquisition", m_image_acq, m_image, fractional_selectivity, threshold=1.0)
        a.add_service_module("IMU_Measurement_Acquisition", m_inertial_data_acq, m_inertial_data,
                             fractional_selectivity,
                             threshold=1.0)
        a.add_service_module("Feature_Extraction", m_image, m_extracted_features, fractional_selectivity, threshold=1.0)
        # a.add_service_module("MSCKF_Update", m_extracted_features, m_corrected_pose, fractional_selectivity, threshold=1.0)
        a.add_service_module("MSCKF_Update", [m_extracted_features, m_inertial_data], m_corrected_pose,
                             fractional_selectivity, threshold=1.0)
        a.add_service_module("Prediction", m_corrected_pose, m_pose_prediction, fractional_selectivity, threshold=1.0)
        return a

    def create_json_topology(uplink_rate):
        """
           TOPOLOGY DEFINITION

           Some attributes of fog entities (nodes) are approximate
           """

        ## MANDATORY FIELDS
        topology_json = {}
        topology_json["entity"] = []
        topology_json["link"] = []

        camera = {"id": 0, "model": "camera", "IPT": 100 * (10 ** 6), "RAM": 4000, "COST": 3, "WATT": 40.0}
        imu = {"id": 1, "model": "imu", "IPT": 100 * (10 ** 9), "RAM": 4000, "COST": 3, "WATT": 40.0}
        drone = {"id": 2, "model": "drone", "mytag": "drone", "IPT": DRONE_CPU, "RAM": 4000, "COST": 3, "WATT": 40.0}
        edge_device = {"id": 3, "model": "edge_server", "mytag": "edge",
                       "IPT": DRONE_CPU * EDGE_DRONE_CMPT_PWR_RATIO, "RAM": 40000, "COST": 3,
                       "WATT": 20.0}
        base_station = {"id": 4, "model": "ground_station", "mytag": "ground_station", "IPT": 20 * (10 ** 9),
                          "RAM": 4000,
                          "COST": 3, "WATT": 40.0}
        actuator_dev = {"id": 5, "model": "actuator_device", "IPT": 1 * (10 ** 6), "RAM": 4000, "COST": 3, "WATT": 40.0}

        link1 = {"s": 0, "d": 2, "BW": 1000, "PR": 0}
        link2 = {"s": 1, "d": 2, "BW": 1000, "PR": 0}
        link3 = {"s": 2, "d": 3, "BW": uplink_rate, "PR": 0}
        link4 = {"s": 2, "d": 4, "BW": 1000, "PR": 0}
        link5 = {"s": 2, "d": 5, "BW": 1000, "PR": 0}
        link6 = {"s": 3, "d": 2, "BW": DOWNLINK_RATE, "PR": 0}

        topology_json["entity"].append(camera)
        topology_json["entity"].append(imu)
        topology_json["entity"].append(drone)
        topology_json["entity"].append(edge_device)
        topology_json["entity"].append(ground_station)
        topology_json["entity"].append(actuator_dev)

        topology_json["link"].append(link1)
        topology_json["link"].append(link2)
        topology_json["link"].append(link3)
        topology_json["link"].append(link4)
        topology_json["link"].append(link5)
        topology_json["link"].append(link6)

        print("TOPOLOGY JSON")
        print(topology_json)

        return topology_json

    random.seed(RANDOM_SEED)
    np.random.seed(RANDOM_SEED)

    folder_results = Path("results/")
    folder_results.mkdir(parents=True, exist_ok=True)
    folder_results = str(folder_results) + "/"

    """
    TOPOLOGY from a json
    """
    t = Topology()
    t_json = create_json_topology(uplink_rate)
    t.load(t_json)

    print("T")
    print(t)

    nx.write_gexf(t.G,
                  folder_results + "graph_main1")  # you can export the Graph in multiples format to view in tools like Gephi, and so on.

    """
    APPLICATION
    """
    app = create_application()

    """
    PLACEMENT algorithm
    """
    placement = simplePlacement.FullEdgePlacement("Partial")  # it defines the deployed rules: module-device
    placement.scaleService({"Image_Acquisition": 1, "IMU_Measurement_Acquisition": 1, "Feature_Extraction": 1,
                            "MSCKF_Update": 1, "Prediction": 1})

    """
    POPULATION algorithm
    """
    # In ifogsim, during the creation of the application, the Sensors are assigned to the topology, in this case no. As mentioned, YAFS differentiates the adaptive sensors and their topological assignment.
    # In their case, the use a statical assignment.
    pop = Statical("Statical")
    # For each type of sink modules we set a deployment on some type of devices
    # A control sink consists on:
    #  args:
    #     model (str): identifies the device or devices where the sink is linked
    #     number (int): quantity of sinks linked in each device
    #     module (str): identifies the module from the app who receives the messages
    # pop.set_sink_control({"model": "client", "number": 3, "module": app.get_sink_modules()})
    pop.set_sink_control({"model": "actuator_device", "number": 1, "module": app.get_sink_modules()})
    # In addition, a source includes a distribution function:
    dDistribution = deterministicDistributionStartPoint(name="Deterministic", time=10000, start=10)
    dDistribution_2 = deterministicDistributionStartPoint(name="Deterministic", time=10000, start=10)
    pop.set_src_control(
        {"model": "camera", "number": 1, "message": app.get_message("Image_Acquirement"),
         "distribution": dDistribution})
    pop.set_src_control(
        {"model": "imu", "number": 1, "message": app.get_message("Inertial_Data_Acquirement"),
         "distribution": dDistribution_2})

    """--
    SELECTOR algorithm
    """
    # Their "selector" is actually the shortest way, there is not type of orchestration algorithm.
    # This implementation is already created in selector.class,called: First_ShortestPath
    selectorPath = MinimunPath()

    """
    SIMULATION ENGINE
    """

    stop_time = simulated_time
    s = Sim(t, default_results_path=folder_results + "sim_trace_full_r4_n20_faster_connection")

    s.deploy_app2(app, placement, pop, selectorPath)

    """
    RUNNING - last step
    """
    s.run(stop_time, show_progress_monitor=False)  # To test deployments put test_initial_deploy a TRUE
    s.print_debug_assignaments()
    folder_name = os.path.splitext(CSV_FILE)[0] + '_test7.csv'

    tim_out_read(CSV_FILE, uplink_rate)

    # s.draw_allocated_topology() # for debugging


def main():
    for i in range(len(UPLINK_RATE_ARRAY)):
        up_rate_evaluation_fnc(simulated_time=4000, uplink_rate=UPLINK_RATE_ARRAY[i])



if __name__ == '__main__':
    import logging.config
    import os

    logging.config.fileConfig(os.getcwd() + '/logging.ini')

    start_time = time.time()
    main()

    print("\n--- %s seconds ---" % (time.time() - start_time))
    print(UPLINK_RATE_ARRAY)
    ### Finally, you can analyse the results:
    # print "-"*20
    # print "Results:"
    # print "-" * 20
    # m = Stats(defaultPath="Results") #Same name of the results
    # time_loops = [["M.A", "M.B"]]
    # m.showResults2(1000, time_loops=time_loops)
    # print "\t- Network saturation -"
    # print "\t\tAverage waiting messages : %i" % m.average_messages_not_transmitted()
    # print "\t\tPeak of waiting messages : %i" % m.peak_messages_not_transmitted()PartitionILPPlacement
    # print "\t\tTOTAL messages not transmitted: %i" % m.messages_not_transmitted()
