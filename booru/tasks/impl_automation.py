from celery import shared_task
from .skipper import skip_if_running

from booru.models.implications import Implication

@shared_task(bind=True)
@skip_if_running
def perform_all_tag_implications():
    """Performs all tag implications."""
    # Get all implications
    implications = Implication.objects.all() # TODO what if there is a change in the implications?

    # Keep applying implications until there are no more changes to be made (for example, an implication adds a tag that another implication adds)
    
    first_run = True
    total = 0 # The total number of posts affected

    while total > 0 or first_run:
        total = 0 # Reset the total
        first_run = False # We are no longer on the first run

        # Apply all implications
        for implication in implications:
            total += implication.apply() # Apply the implication
        
