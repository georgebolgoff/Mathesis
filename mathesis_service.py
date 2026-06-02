import time
import asyncio
from telegram_client.client import start_client
from telegram_client.async_loop import loop

import win32serviceutil
import win32service
import win32event
import servicemanager

from scheduler.tasks import start_scheduler


class MathesisService(
    win32serviceutil.ServiceFramework
):
    _svc_name_ = "MathesisScheduler"

    _svc_display_name_ = (
        "Mathesis Scheduler"
    )

    _svc_description_ = (
        "Generates and sends"
        "scheduled Mathesis exercises"
    )

    def __init__(self, args):

        super().__init__(args)

        self.stop_event = (
            win32event.CreateEvent(
                None,
                0,
                0,
                None
            )
        )

        self.running = True

    def SvcStop(self):

        self.ReportServiceStatus(
            win32service.SERVICE_STOP_PENDING
        )

        self.running = False

        win32event.SetEvent(
            self.stop_event
        )
    

    def SvcDoRun(self):

        try: 

            servicemanager.LogInfoMsg(
                "Mathesis Service Started"
            )

            self.main()
        except Exception as e:

            servicemanager.LogErrorMsg(
                f"Mathesis crashed: {e}"
            )

            raise

    def main(self):

        asyncio.run_coroutine_threadsafe(
        start_client(),
        loop
        ).result()

        start_scheduler()

        while self.running:

            time.sleep(5)


if __name__ == "__main__":

    win32serviceutil.HandleCommandLine(MathesisService)