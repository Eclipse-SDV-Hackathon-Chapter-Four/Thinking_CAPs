FROM threadx-zonal-lights:autosd-build
COPY bridge.py /opt/bridge/bridge.py
COPY controller.py /opt/threadx/controller.py
COPY can_probe.py /opt/threadx/can_probe.py
