[![hacs_badge](https://img.shields.io/badge/HACS-Default-yellow.svg?style=for-the-badge)](https://github.com/custom-components/hacs) [![GitHub release (latest by date)](https://img.shields.io/github/v/release/IgnacioHR/de-dietrich-c230-ha?label=Latest%20release&style=for-the-badge)](https://github.com/IgnacioHR/de-dietrich-c230-ha/releases) [![GitHub all releases](https://img.shields.io/github/downloads/IgnacioHR/de-dietrich-c230-ha/total?style=for-the-badge)](https://github.com/IgnacioHR/de-dietrich-c230-ha/releases)

# de-dietrich-c230-ha
De Dietrich C-230 boiler to Home Assistant integration

## Features

Allows to visualize the status of the boiler from Home Assistant. In some cases it is possible to modify the bolier parameters.
I tried to implement functionality to program the timers from Home Assistant but that doesn't work because of lack of an Entity
in HA with the capacity to store the start-end time information. I managed to hack the "number" entity to store that info but
ended up thinking it is not apropriate for this purpose. So, I'm waiting for HA to become more flexible about how to add entities
otherwise this will not be possible.

### Sensors

- Provides temperature sensors for circuits A, B, C and ACS.
- Allows to edit every circuit target temperature for day and night
- Provides access to see the calibration offset for every circuit
- Provides a sensor with boiler status. useful in case of boiler errors
- Provides capacity to visualize if the circuits are in ON or OFF status (day or night) via scheduler helpers
- Provides binary sensors for the status of the different boiler pumps

### Installation using HACS

1. Open `Integrations` inside the HACS configuration.
2. Click the + button in the bottom right corner, select `De Dietrich C-230 boiler` and then `Install this repository in HACS`.
3. Once installation is complete, restart Home Assistant

### **Manual installation**

1. Download `de_dietrich_c230_ha.zip` from the latest release in https://github.com/IgnacioHR/de-dietrich-c230-ha/releases/latest
2. Unzip into `<hass_folder>/config/custom_components`
    ```shell
    $ unzip de_dietrich_c230_ha.zip -d <hass_folder>/custom_components/diematic_3_c230_eco
    ```
3. Restart Home Assistant

# Configuration

TBD

# Current status

I've a RPi with a RS-485 to USB (serial) converted connected to the C-230 boiler. I installed the code from Germain Masse () repository in order to extract the values and store them into an influx-db database. That database is also available from Home Assistant so I started to create sensors based on the data from the Influx DB.

Later I wanted to modify values in the boiler form HA so I had to re-think the entire architecture. I started to rewrite completely the diematicd daemon add writing capabilities, and RESTFull services as well as keeping the same influxdb backend running for compatibility reasons.

I also conigured the diematicd daemon more like a unix daemon and provided systemctl integration.

That part of the code is stable, but it is not publicly available yet. It will be at some moment in time as I'm doing this for fun.

Now, I'm trying to create a front-end for some services in my Home Assistant and due to the big number of sensors to be created and values to be stored in the influx-db it makes more sense to develop a custom component based on sensors using only the RESTful services.

# Change history

2023-02-06: Added unique id for binary sensors
2023-07-01: Maintenance vesion to fix initialization issues
2024-11-16: The new backend, in progress, publishes diematic data to mqtt if configured, the unit written as "CelsiusTemperature" required to be converted into "°C" or "K" in the diematic.yaml file so this component required a fix to keep working with the old and new backends.

# Note

This integration works for me! There is no guarantee it will work for your use case. You need an RPI connected to the Boiler
