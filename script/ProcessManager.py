import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import time
from script.models.Process import Process
from script.models.Account import Account
from script.extra.exceptions import ProcessShouldStop
import traceback
from script.models.AccountHelper import get_next_account


class ProcessManager:
    pid = None

    # python peewee model
    process = None
    remote_process = None
    initial_data = None
    sleep_time = 7
    workflow = None
    service = None
    modules = None
    account = None
    browser_ig = None

    def run(self):
        self.init()

        try:
            self.check_stop_statuses()
            self.get_modules()
            self.select_account()
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
        self.workflow = self.process.workflow

        if self.workflow:
            self.service = self.process.workflow.service

        if self.workflow:
            self.modules = self.workflow.modules()

    def check_stop_statuses(self):

        if self.process.status in Process.stopped_process:
            err = f'Process status : {self.process.status}, going to sleep {self.sleep_time} seconds ...'
            raise ProcessShouldStop(err)

        if self.workflow is None:
            err = f"There's no workflow assigned to the process, going to sleep {self.sleep_time} seconds ..."
            raise ProcessShouldStop(err)

        if self.service is None:
            err = f"There's no service assigned to this workflow, going to sleep {self.sleep_time} seconds ..."
            raise ProcessShouldStop(err)

        if not self.modules:
            err = f"There's no modules assigned to this workflow, going to sleep {self.sleep_time} seconds ..."
            raise ProcessShouldStop(err)

        if self.service.should_run() is False:
            err = f"We shouldn't run the process, going to sleep {self.sleep_time} seconds ..."
            raise ProcessShouldStop(err)

    def get_modules(self):

        module_titles = [module.title for module in self.modules]
        self.process.add_cli(
            f"workflow : {self.workflow.title}, service: {self.service.service} modules: {module_titles}")

    def select_account(self):

        self.account = get_next_account(service_id=self.service.id)

        if self.account is None:
            err = "There's no account for this service"
            raise ProcessShouldStop(err)

    def start(self):
        from script.extra.base.BasePlaywright import BasePlaywright
        from script.extra.strategies.ModuleManager import ModuleManager
        from script.extra.exceptions import ProxyStuck
        from script.extra.actions.login.LoginContext import LoginContext
        import traceback

        try:
            self.browser_ig = BasePlaywright(self.account)
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
