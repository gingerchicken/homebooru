from .tag_automation import *
from .metadata import *

def perform_setup():
    """Performs setup for the automation module."""

    # Register the automations
    TagAutomationRegistry().register(AnimatedContentTagAutomation())

    # Print the state
    TagAutomationRegistry().print_state()

perform_setup()