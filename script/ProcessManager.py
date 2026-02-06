import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import time
from script.models.Process import Process
from script.models.AutomationQueue import AutomationQueue
from script.models.Account import Account
from script.extra.exceptions import ProcessShouldStop
import traceback
from script.models.AccountHelper import get_next_account
from script.models.AutomationQueue import AutomationQueue


class ProcessManager:
    pid = None

    process = None
    sleep_time = 7
    modules = None
    account = None
    browser_ig = None

    automation_queue = None
    data = None

    def run(self):
        self.init()

        try:
            self.check_stop_statuses()
            self.process.add_cli(f" modules: {self.data.modules.classes}")
            self.start()

        except ProcessShouldStop as e:
            self.process.add_cli(str(e)) if self.process else print(str(e))
            time.sleep(ProcessManager.sleep_time)

        except Exception as e:
            self.process.add_cli(str(e)) if self.process else print(str(e))
            self.process.add_cli(traceback.format_exc()) if self.process else print(traceback.format_exc())
            time.sleep(ProcessManager.sleep_time)

    def init(self):
        self.pid = os.getpid()
        self.process = Process.update_or_create_process(self.pid)
        self.automation_queue = AutomationQueue.pop_first()

        if self.automation_queue:
            self.data = self.automation_queue.payload_obj
            self.account = Account.get_by_id(self.data.account.id)

    def check_stop_statuses(self):

        if self.process.status in Process.stopped_process:
            err = f'Process status : {self.process.status}, going to sleep {self.sleep_time} seconds ...'
            raise ProcessShouldStop(err)

        if self.automation_queue is None:
            err = f"There's no automation queue, going to sleep {self.sleep_time} seconds ..."
            raise ProcessShouldStop(err)

    def start(self):
        from script.extra.base.BasePlaywright import BasePlaywright
        from script.extra.strategies.ModuleManager import ModuleManager
        from script.extra.exceptions import ProxyStuck
        from script.extra.actions.login.LoginContext import LoginContext
        import traceback

        try:
            self.browser_ig = BasePlaywright(self.account, self.data.profile.profile_id)
            self.browser_ig.init()
            LoginContext(self.browser_ig).fire()

            self.account.set_state('processing', 'app_state')
            self.account.set_state('active')

            module_manager = ModuleManager(
                browser_ig=self.browser_ig,
                modules=self.modules,
                process=self.process
            )

            module_manager.run()

        except ProxyStuck:
            raise

        except Exception as e:
            self.account.add_cli(str(e))
            self.account.add_log(traceback.format_exc())

        finally:
            if self.browser_ig:
                self.browser_ig.cleanup()

            self.account.set_state('idle', 'app_state')
