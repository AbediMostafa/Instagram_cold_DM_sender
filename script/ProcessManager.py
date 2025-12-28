import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import time
from script.extra.routes import process_verify, get_initial_data, select_account
from script.models.Process import Process
from script.models.Account import Account
from script.extra.exceptions import ProcessShouldStop
import traceback


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

    def __init__(self):
        self.initial_data = get_initial_data()

    def run(self):

        try:
            self.initialize()
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

    def initialize(self):
        self.pid = os.getpid()
        self.remote_process = process_verify(self.pid)
        self.process = Process.get_by_id(self.remote_process['id'])

    def check_stop_statuses(self):
        if self.remote_process['status'] in self.initial_data['stopped_statuses']:
            err = f'Process status : {self.remote_process['status']}, going to sleep {self.sleep_time} seconds ...'
            raise ProcessShouldStop(err)

        if self.remote_process['workflow'] is None:
            err = f"There's no workflow assigned to the process, going to sleep {self.sleep_time} seconds ..."
            raise ProcessShouldStop(err)

        if self.remote_process['workflow']['service'] is None:
            err = f"There's no service assigned to this workflow, going to sleep {self.sleep_time} seconds ..."
            raise ProcessShouldStop(err)

        if self.remote_process['workflow']['service'] is None:
            err = f"There's no service assigned to this workflow, going to sleep {self.sleep_time} seconds ..."
            raise ProcessShouldStop(err)

        if not self.remote_process['workflow']["modules"]:
            err = f"There's no modules assigned to this workflow, going to sleep {self.sleep_time} seconds ..."
            raise ProcessShouldStop(err)

        if self.remote_process['should_run'] is False:
            err = f"We shouldn't run the process, going to sleep {self.sleep_time} seconds ..."
            raise ProcessShouldStop(err)

    def get_modules(self):

        self.workflow = self.remote_process["workflow"]
        self.service = self.workflow["service"]
        self.modules = self.workflow["modules"]
        module_titles = [module['title'] for module in self.modules]
        self.process.add_cli(
            f"workflow : {self.workflow['title']}, service: {self.service['service']} modules: {module_titles}")

    def select_account(self):
        account = select_account(service_id=self.service['id'])

        if account is None:
            err = "There's no account for this service"
            raise ProcessShouldStop(err)

        self.process.add_cli(f"Current account: {account['id']} -- {account['username']}")

        self.account = Account.get_by_id(account['id'])

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

            module_manager.run(shuffle=True)

        except ProxyStuck:
            raise

        except Exception as e:
            self.account.add_cli(str(e))
            self.account.add_log(traceback.format_exc())

        finally:
            if self.browser_ig:
                self.browser_ig.cleanup()

            self.account.set_state('idle', 'app_state')
