import secrets
import time
import serial
import numpy as np
import cv2
import threading
import time
import os
import json


class Arduino_logger:
    def __init__(
        self,
        name=f"secrets.url_token",
        serial_port=None,
        baud_rate=None,
        start_token="# start #",
        end_token="# end #",
        number_of_readings_to_keep=40,
        readings_per_second=20,
    ):

        self.name = name

        if not serial_port:
            # No, you must have a serial port to connect to
            print("[ERROR] You really must have a serial port")
            1 / 0
        else:
            self.serial_port = serial_port

        if not baud_rate:
            # No, you must have a baud_rate
            print("[ERROR] You really must have a baud_rate")
            1 / 0
        else:
            self.baud_rate = baud_rate

        self.start_token = start_token
        self.end_token = end_token

        self.number_of_readings_to_keep = number_of_readings_to_keep

        self.readings_per_second = readings_per_second

        # somewhere to store them
        self.packets = []

        # rolling averages for filtering
        self.rolling_averages = {}

        self.start_reading_log()

        # define a list to store the last n entries in 
    def start_reading_log(self):

        # start reading the log

        # Fire up the app in a seperate thread and then run the tests in this thread
        kwargs = {}
        args = []
        threaded_function = self.start_reading_log_threaded
        thread = threading.Thread(target=threaded_function, args=args, kwargs=kwargs)
        thread.start()

    def start_reading_log_threaded(self, interval_in_seconds=1, type="random"):
        # Enter the correct port for the arduino
        # port = "com3"

        # Set the baud rate correctly to match the rate set in the arduino
        arduino = serial.Serial(self.serial_port, self.baud_rate, timeout=5)

        # Define the tokens for getting the numbers out of the mesages
        start_token = "# start #"
        end_token = "# end #"

        # time_between_readings 
        time_between_readings = 1000 * 1 / self.readings_per_second

        last_reading_stored_at = 0

        while True:
            # Serial read section
            serial_message = arduino.readline().decode("utf-8")

            # find the start and end of the numbers
            start_index = serial_message.find(start_token) + len(start_token)
            end_index = serial_message.find(end_token)

            # extract the json from the message
            json_text = serial_message[start_index:end_index]

            # the arduino cannot output strings that contain double quotes.
            # json.loads needs key to be in double quotes
            json_text = json_text.replace("'", '"').strip()

            try:
                packet = json.loads(json_text)

                if self.check_packet_fidelity(packet):
                    if self.filter_outliers(packet):
                    # If this is the first reading that we've actually hit then set the previous
                    # stored at to now - time between readings to force this one to be stored 
                        if not last_reading_stored_at:
                            last_reading_stored_at = packet["milliseconds"] - time_between_readings

                        # now check if it's time to store one 
                        if packet["milliseconds"] - last_reading_stored_at >= time_between_readings:
                            # for now, let's print the data raw
                            last_reading_stored_at = last_reading_stored_at + time_between_readings

                            self.store_packet(packet)

                    else:
                        print(f"[ERROR] The packet is an outlier: {packet}")
                else:
                    print(f"[ERROR] The packet is not valid: {packet}")
                    
            except Exception as err:
                print(err)
                print(f"The json dedcode failed. The string was: {json_text}")
                pass

    def check_packet_fidelity(self, packet):

        try:

            # Ignore the first 10 packets to give the electronics time to settle down
            if packet["packet_id"] < 10:
                return False
        
            check_sum = -packet["check_sum"]

            for key, value in packet.items():
                check_sum = check_sum + value

            if check_sum == packet["check_sum"]:
                return True
            else:
                print(f"Failed fidelity: {packet}")
                return False
        except:
            return False

    def filter_outliers(self, packet):

        # if we get a wild reading then it should be ignored 
        # Create a rolling average of the last 5 readings and if this is 
        # greater than 30% different, reject????
        # threshold = 0.2

        # for key in packet:

        #     value = packet[key]

        #     try:
        #         self.rolling_averages[key] = (self.rolling_average[key]*4 + value) / 5
        #     except:
        #         self.rolling_averages[key] = value

        #     delta_from_average = abs(self.rolling_averages[key] - value)

        #     if delta_from_average / self.rolling_averages[key] > threshold:
        #         return False

        return True

    def store_packet(self, packet):

        # remove packets until we've room for one more
        while len(self.packets) >= self.number_of_readings_to_keep:
            self.packets.pop(0)

        # now add the packet to the list
        self.packets.append(packet)

    def get_n_packets(self, number_of_readings):

        # get the corect number of packets from the end of the packets list
        return_packets = self.packets[-number_of_readings:]

        return return_packets




if __name__ == "__main__":

    arduino_Logger = Arduino_logger("test", serial_port="COM4", baud_rate=115200)

    while True:

        
        print(arduino_Logger.get_n_packets(1))
        time.sleep(1)

    1 / 0
