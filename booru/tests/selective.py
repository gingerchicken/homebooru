import os

def __get_disabled_test_names():
    """Returns a list of disabled test names"""

    # Get the environment variable "DISABLED_TESTS" and split it by commas
    disabled_tests = os.environ.get("DISABLED_TESTS", "").split(",")
    
    # Remove any empty strings from the list
    disabled_tests = [test.lower() for test in disabled_tests if test]
    
    # Convert the list to a set to remove duplicates
    disabled_tests = set(disabled_tests)

    return disabled_tests

__DISABLED_SET = __get_disabled_test_names()

def is_disabled(test_name : str):
    """Returns True if the test is disabled, False otherwise"""
    global __DISABLED_SET

    return test_name.lower() in __DISABLED_SET

class TestInstance:
    """A class that maps a test name to a module to be imported"""
    def __init__(self, name : str, module):
        self.name = name
        self.module = module

    def __repr__(self):
        return f"TestInstance({self.name}, {self.module})"

    def __str__(self):
        return f"{self.name} -> {self.module}"

def generate_imports(instances : list):
    """Generates the script in the list of TestInstances"""

    # TODO this is a hacky way to do this!

    imports = []

    for instance in instances:
        if is_disabled(instance.name):
            print(f"Skipping {instance.name}...")
            continue

        print(f"Importing {instance.name}...")
        imports.append(f"from {instance.module} import *")

    
    return "\n".join(imports)

def import_required(instances : list, other_globals : dict, other_locals : dict):
    """Imports the required modules"""

    exec(generate_imports(instances), other_globals, other_locals)