import traceback

from script.extra.mobile.actions.login_and_switch.LoginAndSwitchContext import (
    LoginAndSwitchContext,
)


class SessionRunner:
    """
    One session for one account on a device — the mobile mirror of the web
    LoginContext + ModuleManager for a single account (phase 7).

    Same shape as the browser side:
      1. Login/switch is mandatory and runs FIRST, hardcoded here exactly like
         the web side hardcodes LoginContext before ModuleManager. If it reports
         the account is unusable (suspended, login failed), the session is
         skipped — the workflow modules never run for this account.
      2. Then the workflow's modules run in priority order, each once to
         completion, and Instagram is returned to a main tab after each one.
         SessionRunner is otherwise workflow-driven: adding a work module is
         just a new row in `modules`, no code change here.

    Modules are Contexts (mirror of the web LoginContext): each exposes
    execute(). They're imported dynamically from module_path/class_name and
    reach everything through the device (the mobile 'ig'), which carries
    device.account. `modules` arrives already priority-ordered from
    MobileProcessManager.
    """

    def __init__(self, device, account, modules, service, mobile):
        self.device = device
        self.account = account
        self.modules = modules
        self.service = service
        self.mobile = mobile

    # ── entry ───────────────────────────────────────────────────────────────
    def run(self):
        # Bind this session's account onto the device so every context/event
        # reads it as device.account (the mobile 'ig' pattern).
        self.device.account = self.account
        self.account.add_cli(f'session start on mobile {self.mobile.duo_id}')

        try:
            if not self._login():
                # Login/switch said this account is unusable this round; skip it.
                return

            self._run_workflow_modules()

        except Exception as e:
            # One account's failure must not poison the rest of the rotation.
            # The screen is left wherever the error happened, so reset the app
            # to a known state before the next account starts — the mobile
            # equivalent of the web side closing the browser and profile.
            self.account.add_cli(f'session error: {e}')
            self.account.add_log(traceback.format_exc())
            try:
                self.device.hard_reset()
            except Exception as reset_error:
                self.account.add_cli(f'could not reset device: {reset_error}')
        finally:
            # Don't leak this account onto the device between sessions.
            self.device.account = None

    # ── step 1: mandatory login/switch (hardcoded, like web LoginContext) ───
    def _login(self):
        return LoginAndSwitchContext(self.device).execute() is not False

    # ── step 2: workflow modules, priority order, each to completion ────────
    def _run_workflow_modules(self):
        for module in self.modules:
            context = self._instantiate(module)
            if context is None:
                continue
            try:
                context.execute()
            except Exception as e:
                # One module failing shouldn't abort the rest of the session.
                self.account.add_cli(f'{module.class_name} failed: {e}')
                self.account.add_log(traceback.format_exc())
            finally:
                # Every module hands over Instagram on a main tab, whether it
                # finished or blew up. Enforced here rather than trusting each
                # module to tidy up, so a module left mid-reel can never break
                # the next one — the same reason the web side closes the
                # browser between accounts.
                self.device.go_home()

    # ── module loading ──────────────────────────────────────────────────────
    def _instantiate(self, module):
        """
        Dynamic import from module_path / class_name, mirroring the web
        ModuleManager. Contexts take only the device (the mobile 'ig'), which
        already carries the account, so no per-module wiring is needed.
        """
        import importlib

        try:
            mod = importlib.import_module(module.module_path)
            cls = getattr(mod, module.class_name)
        except (ImportError, AttributeError) as e:
            self.account.add_cli(
                f'could not load {module.module_path}.{module.class_name}: {e}'
            )
            return None

        return cls(self.device)