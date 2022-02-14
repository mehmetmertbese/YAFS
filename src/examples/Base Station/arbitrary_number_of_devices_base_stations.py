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

from examples.Tutorial.simpleSelection import MinimunPath, MinPath_RoundRobin, MertsPath
from examples.Tutorial.simplePlacement import FullEdgePlacement, Mert_FullEdgePlacement, \
    Mert_FullEdgePlacement_Arbitrary_Number

from yafs.stats import Stats
from yafs.distribution import deterministic_distribution, deterministicDistributionStartPoint
from yafs.application import fractional_selectivity
from examples.Tutorial.csv_reader import tim_out_read
import pandas as pd
import threading

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
UPLINK_RATE_ARRAY = [(x * ((10 / 8) * (10 ** -3))) for x in range(40, 41)]
DOWNLINK_RATE = (1000) * (10 ** -3)
USERS_PER_BS = 3
NUM_OF_BS = 2
NUM_OF_USERS = USERS_PER_BS * NUM_OF_BS

global ID_COUNTER_BS
ID_COUNTER_BS = 1907

global ID_EDGE_SERVER
ID_EDGE_SERVER = 1966

global ID_COUNTER_ENTITY
ID_COUNTER_ENTITY = 0

global ID_COUNTER_USER
ID_COUNTER_USER = 0

global links
links = list()

global entities
entities = list()

folder_results = Path("results/")
folder_results.mkdir(parents=True, exist_ok=True)
folder_results = str(folder_results) + "/"
CSV_FILE = folder_results + 'base_station_arbitrary_number_of_devices.csv'
from yafs.placement import Placement


def id_counter_entity():
    global ID_COUNTER_ENTITY
    prev_id_count = ID_COUNTER_ENTITY
    ID_COUNTER_ENTITY += 1
    return prev_id_count

def id_counter_bs():
    global ID_COUNTER_BS
    prev_bs_count = ID_COUNTER_BS
    ID_COUNTER_BS += 1
    return prev_bs_count

def id_counter_user():
    global ID_COUNTER_USER
    prev_user_count = ID_COUNTER_USER
    ID_COUNTER_USER += 1
    return prev_user_count



# @profile
def up_rate_evaluation_fnc(simulated_time, uplink_rate):
    def add_drone(uplink_rate, user_id, attached_bs_id):

        id_camera = ID_COUNTER_ENTITY
        camera_user = {"id": id_counter_entity(), "model": "camera", "IPT": 100 * (10 ** 6), "RAM": 400000, "COST": 3,
                       "WATT": 40.0, "user": user_id}

        id_imu = ID_COUNTER_ENTITY
        imu_user = {"id": id_counter_entity(), "model": "imu", "IPT": 100 * (10 ** 9), "RAM": 400000, "COST": 3,
                    "WATT": 40.0, "user": user_id}

        id_actuator = ID_COUNTER_ENTITY
        actuator_user = {"id": id_counter_entity(), "model": "actuator_device", "IPT": 1 * (10 ** 6), "RAM": 400000,
                         "COST": 3,
                         "WATT": 40.0, "user": user_id}

        id_drone = ID_COUNTER_ENTITY
        drone_user = {"id": id_counter_entity(), "model": "drone", "mytag": "drone", "IPT": DRONE_CPU, "RAM": 40000,
                      "COST": 3,
                      "WATT": 40.0, "user": user_id}

        links.append({"s": id_camera, "d": id_drone, "BW": 1000, "PR": 0})
        links.append({"s": id_imu, "d": id_drone, "BW": 1000, "PR": 0})
        links.append({"s": id_drone, "d": id_actuator, "BW": 1000, "PR": 0})
        links.append({"s": id_drone, "d": attached_bs_id, "BW": uplink_rate, "PR": 0})
        links.append({"s": attached_bs_id, "d": id_drone, "BW": uplink_rate, "PR": 0})

        entities.append(camera_user)
        entities.append(imu_user)
        entities.append(actuator_user)
        entities.append(drone_user)

    def add_bs_and_drones(attached_edge_server_ids):

        id_bs = ID_COUNTER_BS
        base_station = {"id": id_counter_bs(), "model": "base_station", "mytag": "base_station", "IPT": 20 * (10 ** 9),
                        "RAM": 400000,
                        "COST": 3, "WATT": 40.0}

        entities.append(base_station)

        for i in range(USERS_PER_BS):
            add_drone(uplink_rate, id_counter_user(), id_bs)

        for i in range(len(attached_edge_server_ids)):
            links.append({"s": id_bs, "d": attached_edge_server_ids[i], "BW": 1000, "PR": 0})
            links.append({"s": attached_edge_server_ids[i], "d": id_bs, "BW": 1000, "PR": 0})

        return id_bs

    def create_application(name):
        # APLICATION
        a = Application(name)

        # (S) --> (ServiceA) --> (A)
        a.set_modules([{"Camera": {"Type": Application.TYPE_SOURCE}},
                       {"IMU": {"Type": Application.TYPE_SOURCE}},
                       {"Image_Acquisition": {"RAM": 5000, "Type": Application.TYPE_MODULE}},
                       {"IMU_Measurement_Acquisition": {"RAM": 5000, "Type": Application.TYPE_MODULE}},
                       {"Feature_Extraction": {"RAM": 5000, "Type": Application.TYPE_MODULE}},
                       {"MSCKF_Update": {"RAM": 5000, "Type": Application.TYPE_MODULE}},
                       {"Prediction": {"RAM": 5000, "Type": Application.TYPE_MODULE}},
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

        edge_device = {"id": ID_EDGE_SERVER, "model": "edge_server", "mytag": "edge",
                       "IPT": DRONE_CPU * EDGE_DRONE_CMPT_PWR_RATIO, "RAM": 100000, "COST": 3,
                       "WATT": 20.0}

        edge_server_ids = [ID_EDGE_SERVER]
        entities.append(edge_device)

        for i in range(NUM_OF_BS):
            add_bs_and_drones(edge_server_ids)

        #link_bs_edge = {"s": ID_BASE_STATION, "d": ID_EDGE_SERVER, "BW": 1000, "PR": 0}
        #link_edge_bs = {"s": ID_EDGE_SERVER, "d": ID_BASE_STATION, "BW": 1000, "PR": 0}
        #links.append(link_bs_edge)
        #links.append(link_edge_bs)

        for i in range(len(entities)):
            topology_json["entity"].append(entities[i])

        for j in range(len(links)):
            topology_json["link"].append(links[j])

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

    nx.write_gexf(t.G,
                  folder_results + "graph_main1.xml")  # you can export the Graph in multiples format to view in tools like Gephi, and so on.

    """
    APPLICATION
    """
    apps = list()
    for user in range(NUM_OF_USERS):
        app = create_application("6G_DRONE_" + str(user))
        apps.append(app)

    # app_1 = create_application("6G_Drone_1")
    # app_2 = create_application("6G_Drone_2")

    """
    PLACEMENT algorithm
    """
    placements = list()
    for user in range(NUM_OF_USERS):
        placement = Mert_FullEdgePlacement_Arbitrary_Number("Placement_" + str(user))
        placement.scaleService({"Image_Acquisition": 1, "IMU_Measurement_Acquisition": 1, "Feature_Extraction": 1,
                                "MSCKF_Update": 1, "Prediction": 1})
        placements.append(placement)

    """
    placement_1 = Mert_FullEdgePlacement("Mert_1")  # it defines the deployed rules: module-device
    placement_1.scaleService({"Image_Acquisition": 1, "IMU_Measurement_Acquisition": 1, "Feature_Extraction": 1,
                            "MSCKF_Update": 1, "Prediction": 1})

    placement_2 = Mert_FullEdgePlacement("Mert_2")  # it defines the deployed rules: module-device
    placement_2.scaleService({"Image_Acquisition": 1, "IMU_Measurement_Acquisition": 1, "Feature_Extraction": 1,
                              "MSCKF_Update": 1, "Prediction": 1})
    """

    """
    POPULATION algorithm
    """
    # In ifogsim, during the creation of the application, the Sensors are assigned to the topology, in this case no. As mentioned, YAFS differentiates the adaptive sensors and their topological assignment.
    # In their case, the use a statical assignment.
    populations = list()
    for user in range(NUM_OF_USERS):
        population = Statical("Statical_" + str(user))
        population.set_sink_control(
            {"model": "actuator_device", "number": 1, "module": apps[user].get_sink_modules(), "user": user})
        dDistribution = deterministicDistributionStartPoint(name="Deterministic_" + str(user) + "_1", time=10000,
                                                            start=10)
        population.set_src_control(
            {"model": "camera", "number": 1, "message": apps[user].get_message("Image_Acquirement"),
             "distribution": dDistribution, "user": user})
        dDistribution_2 = deterministicDistributionStartPoint(name="Deterministic_" + str(user) + "_2", time=10000,
                                                              start=10)
        population.set_src_control(
            {"model": "imu", "number": 1, "message": apps[user].get_message("Inertial_Data_Acquirement"),
             "distribution": dDistribution_2, "user": user})
        populations.append(population)

    # For each type of sink modules we set a deployment on some type of devices
    # A control sink consists on:
    #  args:
    #     model (str): identifies the device or devices where the sink is linked
    #     number (int): quantity of sinks linked in each device
    #     module (str): identifies the module from the app who receives the messages
    # pop.set_sink_control({"model": "client", "number": 3, "module": app.get_sink_modules()})
    # Their "selector" is actually the shortest way, there is not type of orchestration algorithm.
    # This implementation is already created in selector.class,called: First_ShortestPath

    selectorPath = MertsPath()

    """
    SIMULATION ENGINE
    """

    stop_time = simulated_time
    s = Sim(t, default_results_path=folder_results + "base_station_arbitrary_number_MULTIPLE_BS")

    for user in range(NUM_OF_USERS):
        s.deploy_app2(apps[user], placements[user], populations[user], selectorPath)

    s.run(stop_time, show_progress_monitor=False)  # To test deployments put test_initial_deploy a TRUE
    # s.print_debug_assignaments()
    folder_name = os.path.splitext(CSV_FILE)[0] + '_test20.csv'

    # tim_out_read(CSV_FILE, uplink_rate)

    #s.draw_allocated_topology() # for debugging


def main():
    for i in range(len(UPLINK_RATE_ARRAY)):
        up_rate_evaluation_fnc(simulated_time=15000, uplink_rate=UPLINK_RATE_ARRAY[i])


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
