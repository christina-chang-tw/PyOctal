from lib.util import wait_for_next_meas
import time

for i in range(5):
    wait_for_next_meas()
    time.sleep(2)
