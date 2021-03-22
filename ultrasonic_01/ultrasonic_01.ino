#include <TFMPI2C.h>

// ---------------------------------------------------------------- //
// Arduino Ultrasoninc Sensor HC-SR04
// Inspired by by Arbi Abdul Jabbaar
// Using HC-SR04
// ---------------------------------------------------------------- //

// Set up sensor HC-SR04 number 1
#define echo_pin_1 2
#define trigger_pin_1 3

// Set up sensor HC-SR04 number 2
#define echo_pin_2 4
#define trigger_pin_2 5

// Set up sensor HC-SR04 number 3
#define echo_pin_3 6
#define trigger_pin_3 7

// variable for the timer that is part of the packet
long timer_millis;

// variable for the timer to throttle the sensor readings
long timer_millis_for_throttle;

// variable for each of the distance_sensor measurements
int distance_sensor_1;
int distance_sensor_2;
int distance_sensor_3;
long check_sum;

// Keep a packet_id of how many measurements we've done
long packet_id;

void setup()
{

    // set the initial value of the millis for throttling
    timer_millis_for_throttle = millis();

    // set the packet_id to zero
    packet_id = 0;

    // Sets the trigger_pins as an OUTPUT
    // Sets the echo_pins as an INPUT
    pinMode(trigger_pin_1, OUTPUT);
    pinMode(echo_pin_1, INPUT);

    // Sets the trigger_pins as an OUTPUT
    // Sets the echo_pins as an INPUT
    pinMode(trigger_pin_2, OUTPUT);
    pinMode(echo_pin_2, INPUT);

    // Sets the trigger_pins as an OUTPUT
    // Sets the echo_pins as an INPUT
    pinMode(trigger_pin_3, OUTPUT);
    pinMode(echo_pin_3, INPUT);

    // Set the Serial Communication baudrate speed
    Serial.begin(115200);

    // Print the initial log message
    Serial.println("Three Ultrasonic Sensors HC-SR04 Test v2");
}
void loop()
{
    // keep a packet_id so I can see how fast the data is transferr

    // Serial.print(get_distance(echo_pin_1, trigger_pin_1));
    // Serial.print(get_distance(echo_pin_2, trigger_pin_2));
    // Serial.print(get_distance(echo_pin_3, trigger_pin_3));

    Serial.print("Distances in mm. # start # ");
    Serial.print(" { ");
    Serial.print("'packet_id':");
    Serial.print(packet_id);
    Serial.print(", 'milliseconds':");
    timer_millis = millis();
    Serial.print(timer_millis);

    Serial.print(", 'distance_1':");
    distance_sensor_1 = get_distance(echo_pin_1, trigger_pin_1);
    Serial.print(distance_sensor_1);

    Serial.print(", 'distance_2':");
    distance_sensor_2 = get_distance(echo_pin_2, trigger_pin_2);
    Serial.print(distance_sensor_2);

    Serial.print(", 'distance_3':");
    distance_sensor_3 = get_distance(echo_pin_3, trigger_pin_3);
    Serial.print(distance_sensor_3);

    Serial.print(", 'check_sum':");
    check_sum = packet_id +
                timer_millis +
                distance_sensor_1 +
                distance_sensor_2 +
                distance_sensor_3;

    Serial.print(check_sum);

    Serial.print(" } ");
    Serial.println("  # end # ");

    // increment the packet_id
    packet_id = packet_id + 1;
}

int get_distance(int echo_pin, int trigger_pin)
{
    // it is recommended to throttle the sensor readings to a max of 
    // 1 every 60 milliseconds 
    // Therefor we store the millis in a global and wait here 
    // until that limit is reached 
    while (millis() < timer_millis_for_throttle + 60){

    }

    // Clears the trigger_pin condition
    digitalWrite(trigger_pin, LOW);
    delayMicroseconds(2);
    // Sets the trigger_pin HIGH (ACTIVE) for 10 microseconds
    // That in turn triggers 8 bursts of 40khz ultrasonic
    // When the sensor detects an echo repsonse, it calculates 
    // the length of time between the burst and the echo
    // It then sets the echo pin high for the same duration
    digitalWrite(trigger_pin, HIGH);
    delayMicroseconds(10);
    digitalWrite(trigger_pin, LOW);
    // Reads the echo_pin, returns the sound wave travel time in microseconds
    int duration = pulseIn(echo_pin, HIGH);
    // Calculating the distance_sensor_1
    // Speed of sound wave divided by 2 (go and back)
    int distance_sensor = duration * 0.34 / 2;

    // set the revised value of the millis for throttling next time
    timer_millis_for_throttle = millis();

    return distance_sensor;
}
