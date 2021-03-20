import secrets
import numpy as np
import cv2
import threading
import time
import os


class Spark_lines:
    def __init__(self, name=f"secrets.url_token"):

        self.name = name

        self.spark_lines_list = []
        self.spark_lines_dict = {}

    def add_spark_line(self, name, **kwargs):

        # Instantiate a sparkline and pass the kwargs through
        spark_line = Spark_line(name, **kwargs)

        self.spark_lines_dict[name] = spark_line
        self.spark_lines_list.append(spark_line)

        return True

    def add_data_point(self, name, data_point):

        # get this spark line
        spark_line = self.spark_lines_dict[name]

        spark_line.add_data_point(data_point)

        return True

    def get_image(self, name):

        # get this spark line
        spark_line = self.spark_lines_dict[name]

        image = spark_line.get_image()

        return image

    def get_data(self, name):

        # get this spark line
        spark_line = self.spark_lines_dict[name]

        return spark_line.data_points

    def get_jinja(self, name):

        # get this spark line
        spark_line = self.spark_lines_dict[name]

        jinja = spark_line.get_jinja()

        return jinja

    def generate_fake_stream(self, interval_in_seconds, name=None):

        # start generating fake stream of random data
        if name:
            spark_line = self.spark_lines_dict[name]
            spark_line.generate_fake_stream(interval_in_seconds)
        else:
            for spark_line in self.spark_lines_list:
                spark_line.generate_fake_stream(interval_in_seconds)


class Spark_line:
    def __init__(
        self,
        name,
        width=120,
        height=30,
        background_colour=(255, 255, 255),
        number_of_points=20,
        line_colour=(0, 0, 0),
        border_width=0,
        border_colour=(0, 0, 0),
        minimum_y=-1,
        maximum_y=-1,
        line_width=1,
        image_class="",
        refresh_milliseconds=1000,
    ):

        self.name = name
        self.width = width
        self.height = height
        self.background_colour = background_colour
        self.line_colour = line_colour
        self.number_of_points = number_of_points
        self.border_width = border_width
        self.border_colour = border_colour
        self.minimum_y = minimum_y
        self.maximum_y = maximum_y
        self.line_width = line_width
        self.image_class = image_class
        self.refresh_milliseconds = 0.9 * refresh_milliseconds + np.random.rand() * refresh_milliseconds

        self.base_image = (
            np.zeros((height, width, 3), dtype=np.uint8) + self.background_colour
        )
        if self.border_width:
            top = self.border_width
            bottom = self.border_width
            left = self.border_width
            right = self.border_width
            self.base_image = cv2.copyMakeBorder(
                self.base_image,
                top,
                bottom,
                left,
                right,
                cv2.BORDER_CONSTANT,
                value=self.border_colour,
            )

        self.data_points = []

    def add_data_point(self, data_point):

        self.data_points.append(data_point)
        self.data_points = self.data_points[-self.number_of_points :]

        return True

    def get_image(self):

        # take  acopy of the base and put the lines on
        spark_image = np.copy(self.base_image)

        # plot the points and get the line
        previous_point = None
        for index, data_point in enumerate(self.data_points):

            # ignore the first point
            if not index:
                previous_point = data_point

                x0 = int(
                    self.border_width
                    + (self.width * (index - 1) / (self.number_of_points))
                )

                y0 = int(
                    self.border_width
                    + (
                        self.height
                        * (previous_point - self.minimum_y)
                        / (self.maximum_y - self.minimum_y)
                    )
                )
                # invert the ys as they are starting at top left going to bottom right
                y0 = self.height + 2 * self.border_width - y0
                continue

            y1 = int(
                self.border_width
                + (
                    self.height
                    * (data_point - self.minimum_y)
                    / (self.maximum_y - self.minimum_y)
                )
            )

            y1 = self.height + 2 * self.border_width - y1

            x1 = int(
                self.border_width + (self.width * (index + 1) / (self.number_of_points))
            )
            # Draw a diagonal blue line with thickness of 5 px
            cv2.line(spark_image, (x0, y0), (x1, y1), self.line_colour, self.line_width)

            x0 = x1
            y0 = y1

            previous_point = data_point

        return spark_image

    def get_jinja(
        self,
    ):

        javascript = f"""

            <script>
                var c = document.getElementById("canvas_{self.name}");
                var context = c.getContext("2d");
                context.lineWidth = 1;

                context.beginPath();
                context.rect(0, 0, {self.width}, {self.width});
                context.fillStyle = "rgb{self.background_colour}";
                context.fill();

                // draw a line on the canvas
                // use fixed json for the moment
                context.beginPath();
                var json_points = "[0.31, 0.29, 0.3, 0.35, 0.29, 0.85, 0.15, 0.3, 0.32, 0.32,0.31, 0.29, 0.3, 0.35, 0.29, 0.85, 0.15, 0.3, 0.32, 0.32,0.31, 0.29, 0.3, 0.35, 0.29, 0.85, 0.15, 0.3, 0.32, 0.32]"
                var points = JSON.parse(json_points);

                async function fetchAsync_{self.name} (url) {{
                let data = await (await fetch(url)).json();
                return data;
                }}

                function get_data_{self.name}(){{
                    // trigger async function
                    // log response or catch error of fetch promise
                    url = 'http://127.0.0.1:5000/get_spark_data?name={self.name}'
                    fetchAsync_{self.name}(url)
                        .then(data => update_canvas_{self.name}(data))
                        .catch(reason => console.log(reason.message))  
                }}

                // set the timer to repeat this function as required
                // setInterval(function(){{ get_data_{self.name}(); }}, {self.refresh_milliseconds});

                function update_canvas_{self.name}(data){{

                    var c = document.getElementById("canvas_{self.name}");
                    var context = c.getContext("2d");
                    context.lineWidth = 1;

                    context.beginPath();
                    context.rect(0, 0, {self.width}, {self.width});
                    context.fillStyle = "rgb{self.background_colour}";
                    context.fill();                    

                    points = data;

                    var x_increment = {self.width / self.number_of_points};
                    var x_0;
                    var y_0;
                    var x_1 = 0;
                    var y_1;
                    for(var points_index = 0; points_index < points.length; points_index++){{

                        if (points_index == 0) {{
                            x_0 = 0;
                            y_0 = points[points_index] / ({self.maximum_y} - {self.minimum_y}) * {self.height};

                            // invert the ys as they are starting at top left going to bottom right
                            y_0 = {self.height}  - y_0; 

                            context.moveTo(x_0, y_0);
                            continue
                        }}

                        x_1 =  x_1 + x_increment;
                        y_1 = points[points_index] / ({self.maximum_y} - {self.minimum_y}) * {self.height}; 
                        
                        // invert the ys as they are starting at top left going to bottom right
                        y_1 = {self.height} - y_1;
                    
    
                        context.moveTo(x_0, y_0);
                        context.lineTo(x_1, y_1);

                        console.log("Here is x0, y0, x1, y1", x_0, y_0, x_1, y_1)

                        x_0 = x_1;
                        y_0 = y_1;
                    }}
                    context.stroke();

                    // set the timer to repeat this function as required
                    setTimeout(function(){{ get_data_{self.name}(); }}, {self.refresh_milliseconds});

                }}

                // set the timer to repeat this function as required
                // setInterval(function(){{ get_data_{self.name}(); }},{self.refresh_milliseconds});

                // now start the function initially 
                get_data_{self.name}();
                
            </script> 
        """
        canvas_tag = f'<canvas id="canvas_{self.name}"  style="width: 100%; object-fit: contain; border: {self.border_width}px solid rgb{self.border_colour}" width="{self.width}" height="{self.height}"></canvas>'

        package = dict(
            javascript=javascript,
            name=self.name,
            canvas_tag=canvas_tag,
        )

        # print(package)

        return package

    def generate_fake_stream(self, interval_in_seconds, type="random"):

        # start generating fake stream of random data

        # Fire up the app in a seperate thread and then run the tests in this thread
        kwargs = dict(interval_in_seconds=interval_in_seconds, type=type)
        args = []
        threaded_function = self.generate_fake_stream_threaded
        thread = threading.Thread(target=threaded_function, args=args, kwargs=kwargs)
        thread.start()

    def generate_fake_stream_threaded(self, interval_in_seconds=1, type="random"):

        # start generating fake stream of random data in a seperate thread
        heartbeat = [0.31, 0.29, 0.3, 0.35, 0.29, 0.85, 0.15, 0.3, 0.32, 0.32]

        if np.random.rand() < 0.2:
            type = "heartbeat"
            self.name = f"{self.name}"

        counter = 0
        while True:

            if type == "heartbeat":
                data_point = (
                    heartbeat[counter % len(heartbeat)]
                    * (self.maximum_y - self.minimum_y)
                    + self.minimum_y
                )
            else:
                data_point = (
                    np.random.rand() * (self.maximum_y - self.minimum_y)
                    + self.minimum_y
                )

            self.add_data_point(data_point)
            time.sleep(interval_in_seconds)
            counter = counter + 1


if __name__ == "__main__":

    spark_lines = Spark_lines("test")

    name = "spark 1"

    kwargs = dict(
        width=480,
        height=120,
        background_colour=(128, 255, 255),
        number_of_points=50,
        line_colour=(0, 255, 0),
        border_width=1,
        border_colour=(0, 0, 0),
        minimum_y=0,
        maximum_y=50,
    )

    spark_lines.add_spark_line(name, **kwargs)

    for data_point in range(30):
        spark_lines.add_data_point(name, data_point)

    interval_in_seconds = 1
    spark_lines.generate_fake_stream(interval_in_seconds)

    jinja = spark_lines.get_jinja(name)

    print(jinja)

    counter = 0
    while True:

        cv2.imwrite(
            os.path.join("output_no_git", f"spark_{counter}.png"),
            spark_lines.get_image(name),
        )
        counter = counter + 1

        time.sleep(3)

    print(f"{spark_lines}")

    1 / 0
