import importlib
import random
from script.extra.exceptions import ProcessShouldStop


class ModuleManager:
    def __init__(self, browser_ig, modules, process):
        """
        browser_ig : BasePlaywright instance
        modules    : list of modules from Laravel API
        process    : Process peewee model (for logging)
        """
        self.browser_ig = browser_ig
        self.modules = modules
        self.process = process
        self.loaded_modules = []

    def load_modules(self):
        """
        Dynamically import module classes from DB definition
        """
        for module in self.modules:
            try:
                module_path = module.module_path
                class_name = module.class_name

                imported_module = importlib.import_module(module_path)
                module_class = getattr(imported_module, class_name)

                self.loaded_modules.append(module_class)

                self.process.add_cli(
                    f"Loaded module: {module.title} ({class_name})"
                )

            except Exception as e:
                self.process.add_cli(
                    f"Failed to load module {module.title} → {str(e)}"
                )

        if not self.loaded_modules:
            raise ProcessShouldStop("No valid modules loaded")

    def run(self, shuffle=True):
        """
        Execute loaded modules
        """
        if not self.loaded_modules:
            self.load_modules()

        actions = self.loaded_modules[:]

        if shuffle:
            random.shuffle(actions)

        for action_class in actions:
            try:
                self.browser_ig.pause(800, 1100)

                self.process.add_cli(
                    f"Running module: {action_class.__name__}"
                )

                action = action_class(self.browser_ig)
                action.fire()

            except ProcessShouldStop:
                raise

            except Exception as e:
                # module-level failure should NOT kill the whole process
                self.process.add_cli(
                    f"Module {action_class.__name__} failed → {str(e)}"
                )
