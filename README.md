# de-dietrich-c230-ha
De Dietrich C-230 boiler to Home Assistant integration

This is my first HA integration so I'm just exploring how to do it!

# Current status

I've a RPi with a RS-485 to USB (serial) converted connected to the C-230 boiler. I installed the code from Germain Masse () repository in order to extract the values and store them into an influx-db database. That database is also available from Home Assistant so I started to create sensors based on the data from the Influx DB.

Later I wanted to modify values in the boiler form HA so I had to re-think the entire architecture. I started to rewrite completely the diematicd daemon add writing capabilities, and RESTFull services as well as keeping the same influxdb backend running for compatibility reasons.

I also conigured the diematicd daemon more like a unix daemon and provided systemctl integration.

That part of the code is stable, but it is not publicly available yet. It will be at some moment in time as I'm doing this for fun.

Now, I'm trying to create a front-end for some services in my Home Assistant and due to the big number of sensors to be created and values to be stored in the influx-db it makes more sense to develop a custom component based on sensors using only the RESTful services.

# Note

The is under development!