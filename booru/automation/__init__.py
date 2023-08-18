from .tag_automation import *
from .metadata import *
from .tags import *
from .facial_tags import FaceRelatedTagAutomation

__INITIALISED__ = False

def perform_setup():
    """Performs setup for the automation module."""
    global __INITIALISED__

    # Check if the module has already been initialised
    if __INITIALISED__:
        # If it has, return
        return
    
    # Set the initialised flag
    __INITIALISED__ = True

    # Register the automations
    TagAutomationRegistry().register(FaceRelatedTagAutomation())
    TagAutomationRegistry().register(AnimatedContentTagAutomation())
    TagAutomationRegistry().register(LargeFileSizeTagAutomation())
    
    TagAutomationRegistry().register(TagmeTagAutomation(order_override=1))

    TagAutomationRegistry().register(ProbableTagDependenceAutomation(order_override=1024))

    # Print the state
    import homebooru.settings
    if homebooru.settings.DEBUG:
        TagAutomationRegistry().print_state()

perform_setup()