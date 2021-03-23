# Import relevant modules
import secrets
from sqlalchemy.exc import IntegrityError
from flask import (
    render_template_string,
    make_response,
    Flask,
    request,
    render_template,
    url_for,
    redirect,
    flash,
    send_file,
    jsonify,
)
import numpy as np
from io import StringIO
import cv2
import random

from website import Spark_lines, Arduino_logger

# Import the Flask webapp instance that we created in the __init__.py
from flask import current_app as app
from website import db

# Get the serial port from the app config
# And create the logger object 
serial_port = app.config.get("SERIAL_PORT")
arduino_logger = Arduino_logger("test", serial_port=serial_port, baud_rate=2 * 115200)
if not serial_port:
    print(
        "[WARNING] You must have an arduino connected with the ultrasonics and detectors if you want to visualise"
    )

# Store the arduino logger inbto the loggers 
loggers = {}
loggers["arduino"] = arduino_logger

# Create the spark lines object 
spark_lines = Spark_lines("test")

# Define an array of sparkline names
# NB They must contain spaces!!!
spark_line_names = [
    "spark_1",
    "spark_2",
    "spark_3",
    "spark_4",
    "spark_5",
    "spark_6",
    "spark_7",
    "spark_8",
    "spark_9",
    "spark_10",
    "spark_11",
]

# Define all the parameters needed for the creation of the sparkline object
refresh_milliseconds = 250
kwargs = dict(
    width=100,
    height=20,
    background_colour=(204, 246, 244),
    number_of_points=100,
    line_colour=(119, 107, 50),
    border_width=1,
    border_colour=(64, 39, 18),
    minimum_y=0,
    maximum_y=50,
    line_width=1,
    image_class="w-100",
    refresh_milliseconds=refresh_milliseconds,
)

for spark_line_name in spark_line_names:
    spark_lines.add_spark_line(spark_line_name, **kwargs)

interval_in_seconds = refresh_milliseconds / 1000
spark_lines.generate_fake_stream(interval_in_seconds)


# Define our first route (the last part of the url for our website application)
# We can define what urls should land in this function. Let's say / and /index
# We can also define the legitimate methods for this page of GET and POST
@app.route("/")
@app.route("/index")
@app.route("/show_spark_lines")
def show_spark_lines():

    # Use Jinja to render the HTML and resolve any variables that we pass in
    rendered_html = render_template(
        "spark_lines.html", spark_lines=spark_lines, spark_class="card-img-top"
    )

    return rendered_html


@app.route("/get_spark_image")
def get_spark_image():

    # Url arguments can be added to the url like this ?spark_line_name=Peter&age=57
    # Get the url arguments if there are any
    url_arguments = request.args.to_dict(flat=False)
    spark_line_name = url_arguments["spark_line_name"][0]

    # print(f"Name in get_spark_image = {spark_line_name}")

    image = spark_lines.get_image(spark_line_name)

    retval, buffer = cv2.imencode(".png", image)
    response = make_response(buffer.tobytes())
    response.headers["Content-Type"] = "image/png"

    return response


@app.route("/get_spark_data")
def get_spark_data():

    # Get the url arguments if there are any
    url_arguments = request.args.to_dict(flat=False)
    try:
        spark_line_name = url_arguments["spark_line_name"][0]
    except:
        return "[]"

    response = "[0.31, 0.29, 0.3, 0.35, 0.29, 0.85, 0.15, 0.3, 0.32, 0.32,0.31, 0.29, 0.3, 0.35, 0.29, 0.85, 0.15, 0.3, 0.32, 0.32,0.31, 0.29, 0.3, 0.35, 0.29, 0.85, 0.15, 0.3, 0.32, 0.32]"

    data = spark_lines.get_data(spark_line_name)

    return jsonify(data)


@app.route("/visualise_vallon")
def visualise_vallon():

    # Use Jinja to render the HTML and resolve any variables that we pass in
    rendered_html = render_template("visualise_vallon.html")

    return rendered_html


@app.route("/get_arduino_data")
def get_arduino_data():

    # Get the url arguments if there are any
    url_arguments = request.args.to_dict(flat=False)

    try:
        number_of_packets = int(url_arguments["number_of_packets"][0])
    except:
        number_of_packets = 1

    try:
        logger_name = url_arguments["logger_name"][0]
    except:
        logger_name = "arduino"

    logger = loggers[logger_name]

    data = logger.get_n_packets(number_of_packets)

    return jsonify(data)

@app.route("/get_logging_rate")
def get_logging_rate():

    # Get the url arguments if there are any
    url_arguments = request.args.to_dict(flat=False)

    try:
        number_of_packets = int(url_arguments["number_of_packets"][0])
    except:
        number_of_packets = 1

    try:
        logger_name = url_arguments["logger_name"][0]
    except:
        print(f"[WARNING] no logger_name provided. Using arduino to prevent error")
        logger_name = "arduino"

    try:
        logger = loggers[logger_name]
    except:
        print(f"[ERROR] Logger_name of: {logger_name} does not exist. Using arduino to prevent error")
        logger_name = "arduino"


    data = logger.get_logging_rate()

    return jsonify(data)

# Define our first route (the last part of the url for our website application)
# We can define what urls should land in this function. Let's say / and /index
# We can also define the legitimate methods for this page of GET and POST
@app.route("/canvas")
def canvas():

    point_1 = 300
    point_2 = 400
    point_3 = 600

    # Use Jinja to render the HTML and resolve any variables that we pass in
    rendered_html = render_template(
        "canvas.html", point_1=point_1, point_2=point_2, point_3=point_3
    )

    return rendered_html


# Now we can define a page to handle 404 errors
# 404 errors occur when we try to visit a page for
# which there is no route set up
@app.errorhandler(404)
def page_not_found(error):

    # We can do a very simple return of a text string
    # or we could do a full blown template
    # And we could include handling logic in this
    # route as well if we needed to
    return f"There was no such page."
