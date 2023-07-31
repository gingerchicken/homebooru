from .tag_automation import *
from .metadata import *
from .tags import *

def perform_setup():
    """Performs setup for the automation module."""

    # Register the automations
    TagAutomationRegistry().register(AnimatedContentTagAutomation())
    TagAutomationRegistry().register(LargeFileSizeTagAutomation())
    TagAutomationRegistry().register(TagmeTagAutomation(order_override=1))

    # Print the state
    TagAutomationRegistry().print_state()

perform_setup()