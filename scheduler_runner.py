from scheduler.tasks import start_scheduler
import time

print("Starting Mathesis Scheduler")

start_scheduler()

print("Scheduler is running")

while True:
    time.sleep(60)