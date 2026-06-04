import time
import asyncio
from telegram_client.client import start_client
import telegram_client.async_loop as async_loop

import win32serviceutil
import win32service
import win32event
import servicemanager

import traceback

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
        self.ReportServiceStatus(win32service.SERVICE_START_PENDING)

        try: 

            servicemanager.LogInfoMsg(
                "Mathesis Service Started"
            )

            self.main()
        except Exception as e:
            
            servicemanager.LogErrorMsg(f"Startup failed: {repr(e)}")
            servicemanager.LogErrorMsg(traceback.format_exc())
            servicemanager.LogErrorMsg(
                f"Mathesis crashed: {e}"
            )

            raise

    def main(self):

        async_loop.start_loop_thread()

        async_loop.loop_ready.wait()

        future = asyncio.run_coroutine_threadsafe(
            start_client(),
            async_loop.loop
        )

        try:
            future.result(timeout=30)
        except Exception as e:
            servicemanager.LogErrorMsg(f"Telegram init failed: {repr(e)}")
            raise

        start_scheduler()


        self.ReportServiceStatus(win32service.SERVICE_RUNNING)

        win32event.WaitForSingleObject(self.stop_event, win32event.INFINITE)


if __name__ == "__main__":

    win32serviceutil.HandleCommandLine(MathesisService)