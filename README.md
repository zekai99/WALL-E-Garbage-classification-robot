## 1. Web Panel 

At first, we use Python’s built-in [`http.server`](https://docs.python.org/3.5/library/http.server.html#module-http.server) module to make a video streaming server through PICamera, than we demonstrate an HTML file by using [`Bootstrap`](https://getbootstrap.com) and dynamically update images and buttons on the web by JavaScript, we also use [`Bottle`](http://www.bottlepy.com/docs/dev/) python web framework to build website background. Finally, it worked like this:

<div align="center">
<img src="https://i.loli.net/2019/07/24/5d384a10e27d560404.png" style="width:75% ;height:75%;" /> </div>



### 1.1. Bottle: Python Web Framework

Bottle is a fast, simple and lightweight [`WSGI`](http://www.wsgi.org/) micro web-framework for [`Python`](http://python.org/). It is distributed as a single file module and has no dependencies other than the [`Python Standard Library`](http://docs.python.org/library/).

- **Routing:** Requests to function-call mapping with support for clean and dynamic URLs.
- **Templates:** Fast and pythonic [`built-in template engine`](http://www.bottlepy.com/docs/dev/tutorial.html#tutorial-templates) and support for [`mako`](http://www.makotemplates.org/), [`jinja2`](http://jinja.pocoo.org/)and [`cheetah`](http://www.cheetahtemplate.org/) templates.
- **Utilities:** Convenient access to form data, file uploads, cookies, headers and other HTTP-related metadata.
- **Server:** Built-in HTTP development server and support for [`paste`](http://pythonpaste.org/), [`fapws3`](https://github.com/william-os4y/fapws3), [`bjoern`](https://github.com/jonashaag/bjoern), [`gae`](https://developers.google.com/appengine/), [`cherrypy`](http://www.cherrypy.org/) or any other [`WSGI`](http://www.wsgi.org/) capable HTTP server.

To run this web page, point your browser to`http://pi-address:8080/`.



### 1.2. Camera Streaming

Streaming video over the web is surprisingly complicated. At the time of writing, there are still no video standards that are universally supported by all web browsers on all platforms. Furthermore, HTTP was originally designed as a one-shot protocol for serving web-pages. Since its invention, various additions have been bolted on to cater for its ever-increasing use cases (file downloads, resumption, streaming, etc.) but the fact remains there’s no “simple” solution for video streaming at the moment.

However, we decide to use a much simpler format: MJPEG. So we use Python’s built-in [`http.server`](https://docs.python.org/3.5/library/http.server.html#module-http.server) module to make a simple video streaming server. Once the script is running, visit `http://pi-address:8000/` with web-browser we could view the video stream.



### 1.3. Autopilot

When we receive the returned images that have been classified, we need to update it on the web page in real-time. We can simply use JavaScript to change the URL of the image to achieve a partial refresh of the web page. Since the name of the returned image does not change, we need to add a timestamp after the image to make the browser reacquire the image instead of using images in the cache.

<div align="center">
<img src="https://i.loli.net/2019/07/24/5d385a7c2bb1167211.png" style="width:75% ;height:75%;" /> </div>

Based on the classified images, we can know the number of objects, the page will dynamically update the number of objects and use each button to represent each object as follow.:

<div align="center"><img src="https://i.loli.net/2019/07/24/5d385a0b948a164662.png" style="width:50% ;height:50%;" /></div>

When we select an object, the web page will send the selection signal back to the background. The background determines the rotation direction of the car according to the pixel distance of the object offset image center point and communicates with the [`Arduino`](https://www.arduino.cc) through the serial port to control the movement of the car. Once the car is adjusted to the direction of the objects, the car begins to advance automatically, and in the meanwhile detecting the distance from the object through the ultra sonar and automatically stopping in front of the object. Isn’t that cool?



### 1.4. Manual control

We created 5 icons like: 

<div align="center"><img src="https://i.loli.net/2019/07/24/5d3859177505793431.png" style="width:50% ;height:50%" /></div>

 that control car moves forward, left, right, backward and stop. You can click on the corresponding button on the touch screen and control the car. Of course, for better user experience, we also did monitoring the keyboard keys and triggering the corresponding actions. You can simply press `W` `A` `S` `D` to control the direction of the car and press `X` to stop the car.



## 2. Deep Learning

First, we use the object detection algorithm [`Mask RCNN`](https://github.com/matterport/Mask_RCNN) to perform object detection on the video stream acquired by the Raspberry Pi. The identified objects are then classified by the `InceptionV3`. We learned to train the `InceptionV3` model through migration to get good results.

We find it difficult (and slow) to run the deep learning networks on your Pi. (In fact, we found that it is difficult to load the model we built.) So we instead run our deep learning networks on the laptop. The easiest way to do this is to set up an MQTT Broker on the Pi, then modify our MQTT programs to connect to this new broker.



### 2.1. Mask RCNN

We use the [`Mask RCNN`](https://github.com/matterport/Mask_RCNN) project implemented by Keras on GitHub for object detection. Without discussing the excellent performance of `Mask RCNN` on target detection, we found that its presentation of results is very suitable for garbage classification. It not only performs target detection but also splits the target at the pixel level to more intuitively display the location of the garbage.



### 2.2. InceptionV3

It is easy to found that if you were to train a CNN on 30,000 images on a GPU, it can take up to 2 to 3 weeks to complete training.

For this exercise, we will use an extremely deep CNN called `InceptionV3`. `InceptionV3` has over 300 layers, and tens of millions of parameters to train. Here we will use a version of `InceptionV3` that has been pre-trained on over 3 million images in over 4,000 categories. If we wanted to train our `InceptionV3` model from scratch it would take several weeks even on a machine with several good GPUs.

`InceptionV3` consists of “modules” that try out the various filter and pooling configurations, and chooses the best ones.

<div align="center"><img src="https://i.postimg.cc/dVjzY8Jh/1.jpg" style="width:75% ;height:75%" /></div>

Many of these modules are chained together to produce very deep neural networks:

<div align="center"><img src="https://i.postimg.cc/g0c1kn0N/2.jpg" style="width:75% ;height:75%" /></div>

The greatest beauty about `InceptionV3` is that someone has already taken the time to train the hundreds of layers and tens of millions of parameters. All we have to do is to adapt the top layers.



### 2.3. MQTT

[`MQTT`](http://MQTT.org/) (Message Queue Telemetry Transport) was created in 1999 by IBM to allow remotely connected systems with a “small code footprint” to transfer data efficiently over a TCP/IP network.

`MQTT` uses a publish/subscribe mechanism that requires a broker to be running. The broker is special software that receives subscription requests from systems connected to it. It also receives messages published by other systems connected to it, and forwards these messages to systems subscribed to them. `MQTT` has become very popular for the Internet of Things (IoT) applications, particularly for sending data from sensors to a server, and for sending commands from a server to actuators.

<div align="center"><img src="https://i.postimg.cc/XJSFkyyg/MQTT.jpg" style="width:60% ;height:60%" /></div>

We run the classifier on our laptop, and the program to take pictures and send to the classifier on the Pi, and both will connect to the [`MQTT broker`](https://moquette-io.github.io/moquette/) running on the Pi.
