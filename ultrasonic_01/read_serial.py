import serial

# Enter the correct port for the arduino
port = 'com4'

# Set the baud rate correctly to match the rate set in the arduino
arduino = serial.Serial(port,115200,timeout=5)

# Define the tokens for getting the numbers out of the mesages 
start_token = "# start #"
end_token = "# end #"

while True:
    # Serial read section
    serial_message = arduino.readline().decode("utf-8") 

    # find the start and end of the numbers 
    start_index = serial_message.find(start_token) + len(start_token)
    end_index = serial_message.find(end_token)

    # extract the numbers from the message
    data = serial_message[start_index:end_index]

    # Separate out the individual numbers
    data = data.split(",")

    # clean them up and in them 
    for index, number in enumerate (data):
        try:
            data[index] = int(number.strip())
        except:
            pass

    # for now, let's print the data raw
    print(data)
