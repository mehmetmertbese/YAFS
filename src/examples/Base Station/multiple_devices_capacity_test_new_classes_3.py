import random
import networkx as nx
import argparse
from pathlib import Path
import time
import datetime
import numpy as np

from yafs.core import Sim
from yafs.application import Application, Message

from yafs.population import *
from yafs.topology import add_link, Topology, Link, LINK_LIST

from examples.Tutorial.simpleSelection import MinimunPath, MinPath_RoundRobin, MertsPath
from examples.Tutorial.simplePlacement import FullEdgePlacement, Mert_FullEdgePlacement, \
    Mert_FullEdgePlacement_Arbitrary_Number

from yafs.stats import Stats
from yafs.distribution import deterministic_distribution, deterministicDistributionStartPoint
from yafs.application import fractional_selectivity
from yafs.entities_mert import Entity, Base_Station, Edge_Server, Sink, Source, Mobile_Device, ENTITY_LIST
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
USERS_PER_BS = 20
NUM_OF_BS = 2
NUM_OF_USERS = USERS_PER_BS * NUM_OF_BS

# global ID_COUNTER_BS
ID_COUNTER_BS = 1907

# global ID_EDGE_SERVER
ID_EDGE_SERVER = 1966

# global ID_COUNTER_ENTITY
ID_COUNTER_ENTITY = 0

# global ID_COUNTER_USER
ID_COUNTER_USER = 0

# global links
links = list()

# global entities
entities = list()

folder_results = Path("results/")
folder_results.mkdir(parents=True, exist_ok=True)
folder_results = str(folder_results) + "/"
CSV_FILE = folder_results + 'base_station_arbitrary_number_of_devices.csv'


# from yafs.placement import Placement

def entity_id_counter():
    global ID_COUNTER_ENTITY
    prev_id_count = ID_COUNTER_ENTITY
    ID_COUNTER_ENTITY += 1
    return prev_id_count


def bs_id_counter():
    global ID_COUNTER_BS
    prev_bs_count = ID_COUNTER_BS
    ID_COUNTER_BS += 1
    return prev_bs_count


def user_id_counter():
    global ID_COUNTER_USER
    prev_user_count = ID_COUNTER_USER
    ID_COUNTER_USER += 1
    return prev_user_count


# @profile
def up_rate_evaluation_fnc(simulated_time, uplink_rate):
    def add_drone(uplink_rate_drone, user_id, attached_bs_id):
        camera_user = Source(model="camera", ipt=100 * (10 ** 6), ram=4000000,
                             cost=3, power_consumption=40.0, user=user_id)

        imu_user = Source(model="imu", ipt=100 * (10 ** 9), ram=4000000,
                          cost=3, power_consumption=40.0, user=user_id)

        actuator_user = Sink(model="actuator_device", ipt=1 * (10 ** 6), ram=4000000,
                             cost=3, power_consumption=40.0, user=user_id)

        drone_user = Mobile_Device(model="drone_user", ipt=DRONE_CPU, ram=4000000,
                                   cost=3, power_consumption=40.0, user=user_id, mytag="drone")

        add_link(source_id=camera_user.id, destination_id=drone_user.id, bandwidth=1000, latency=0)
        add_link(source_id=imu_user.id, destination_id=drone_user.id, bandwidth=1000, latency=0)
        add_link(source_id=drone_user.id, destination_id=actuator_user.id, bandwidth=1000, latency=0)
        add_link(source_id=drone_user.id, destination_id=attached_bs_id, bandwidth=uplink_rate_drone, latency=0)
        add_link(source_id=attached_bs_id, destination_id=drone_user.id, bandwidth=uplink_rate_drone, latency=0)

    def add_bs_and_drones(attached_edge_server_ids):

        id_bs = ID_COUNTER_BS
        base_station = Base_Station(id=entity_id_counter(), user=bs_id_counter())

        for i in range(USERS_PER_BS):
            add_drone(uplink_rate, user_id_counter(), id_bs)

        for i in range(len(attached_edge_server_ids)):
            add_link(source_id=id_bs, destination_id=attached_edge_server_ids[i], bandwidth=1000, latency=0)
            add_link(source_id=attached_edge_server_ids[i], destination_id=id_bs, bandwidth=1000, latency=0)

        return id_bs

    def create_application(name):

        a = Application(name)
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

        edge_device = Edge_Server(id=ID_EDGE_SERVER, ipt=DRONE_CPU * EDGE_DRONE_CMPT_PWR_RATIO)
        edge_server_ids = [ID_EDGE_SERVER]

        for i in range(NUM_OF_BS):
            add_bs_and_drones(edge_server_ids)

        topology_json["entity"] = ENTITY_LIST
        topology_json["link"] = LINK_LIST

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
        app.set_number(user)
        apps.append(app)

    """
    PLACEMENT algorithm
    """
    placements = list()
    for user in range(NUM_OF_USERS):
        placement = Mert_FullEdgePlacement_Arbitrary_Number("Placement_" + str(user))
        placement.scaleService({"Image_Acquisition": 1, "IMU_Measurement_Acquisition": 1, "Feature_Extraction": 1,
                                "MSCKF_Update": 1, "Prediction": 1})
        placements.append(placement)

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
    file_name = "base_station_arbitrary_number_MULTIPLE_BS_RAM_TEST_NEW_CLASSES"
    s = Sim(t, default_results_path=folder_results + "_" + file_name + "_" + datetime.datetime.today().strftime(
        "%Y_%m_%d-%H_%M"))

    for user in range(NUM_OF_USERS):
        s.deploy_app2(apps[user], placements[user], populations[user], selectorPath)

    s.run(stop_time, show_progress_monitor=False)  # To test deployments put test_initial_deploy a TRUE
    folder_name = os.path.splitext(CSV_FILE)[0] + '_test20.csv'


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
