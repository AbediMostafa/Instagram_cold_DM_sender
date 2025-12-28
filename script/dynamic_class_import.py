import importlib
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

module_path = 'script.models.Account'  # example from DB
class_name = 'Account'              # example from DB

# Import module dynamically
module = importlib.import_module(module_path)

# Get class
MyClass = getattr(module, class_name)

account = MyClass.get_by_id(33)

print(account)