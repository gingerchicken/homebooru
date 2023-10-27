from booru.models.tags import Tag
from booru.models.posts import Post
from booru.models.automation import TagAutomationRecord

import booru.boorutils as boorutils

class TagAutomation:
    """A semi-abstract class for tag automation."""

    execution_order = 0 # The order in which the automation is executed, lower numbers are executed first

    def __init__(self, order_override : int = None):
        """Initializes the automation."""

        # Check if the order override is set
        if order_override is not None:
            # If it is, set the execution order
            self.execution_order = order_override

        pass

    def get_tags(self, post : Post) -> list[Tag]:
        """Returns a list of tags to be added to the post, or an empty list if no tags are to be added."""
        return []
    
    def update_post(self, post : Post) -> bool:
        """Returns True if the post was updated, False otherwise, please note that this function automatically saves the post."""

        # Get the tags
        tags = self.get_tags(post)

        # Have a counter for the number of tags added
        appendices = 0

        # Loop through the tags
        for tag in tags:
            # Check if the tag is already on the post
            if post.tags.all().contains(tag):
                # If it is, skip it
                continue

            # Add the tag to the post
            post.tags.add(tag)

            # Increment the counter
            appendices += 1

        # Check if any tags were added
        if appendices == 0:
            # If not, return False
            return False
        
        # Save the post
        post.save()

        # Success!
        return True

    def get_state_hash(self) -> str:
        """Returns a hash of the state of the automation, this should be extended to change depending on the given parameters."""

        # Get the hash of the class name and the execution order
        name_hash = boorutils.hash_str(self.__class__.__name__)
        order_hash = boorutils.hash_str(self.execution_order)

        # Return the hash of the two hashes
        return boorutils.hash_str(name_hash + order_hash)

class TagAutomationRegistry:
    """A class for registering tag automation."""

    _cached_hash = None

    def __new__(cls):
        """This class is a singleton."""

        if not hasattr(cls, 'instance'):
            cls.instance = super(TagAutomationRegistry, cls).__new__(cls)
            cls.instance._registry = [] # List of registered automations
        
        return cls.instance
    
    def register(self, automation : TagAutomation):
        """Registers a tag automation."""

        self._cached_hash = None # Reset the cached hash

        # Check if the automation is already registered
        if automation in self._registry:
            # If it is, raise an exception
            raise ValueError("Automation already registered.")
        
        # Add the automation to the registry
        self._registry.append(automation)

    def get_state_hash(self) -> str:
        """Returns the hash of the current state of the registry."""

        # Check if the hash is cached
        if self._cached_hash is not None:
            # If it is, return it
            return self._cached_hash

        # Create a list of hashes
        hashes = [automation.get_state_hash() for automation in self._registry]

        # Create a string from the hashes
        hash_string = "".join([str(hash) for hash in hashes])

        # Get the hash of the string
        h = boorutils.hash_str(hash_string)

        # Cache the hash
        self._cached_hash = h

        # Return the hash
        return h
    
    def get_automations(self) -> list[TagAutomation]:
        """Returns a list of automations."""

        return self._registry
    
    def get_automations_sorted(self) -> list[TagAutomation]:
        """Returns a list of automations sorted by execution order."""

        # Get the automations
        automations = self.get_automations()

        # Sort the automations
        automations = sorted(automations, key=lambda automation: automation.execution_order)

        # Return the automations
        return automations
    
    def perform_automation(self, post : Post, force_perform = False) -> None:
        """Performs all automation on a post."""

        # Get the current state hash
        current_state_hash = self.get_state_hash()
        
        # Create a new record (this shall be used as a lock.)
        record = TagAutomationRecord(post=post, state_hash=current_state_hash)

        # Try to save it but return false if it already exists
        try:
            # Check if the record already exists
            if TagAutomationRecord.objects.filter(post=post).exists():
                raise Exception("Record already exists.")
            
        except Exception as e:
            # Check if we should force perform
            if not force_perform:
                return False
            
            # Delete the already existing record
            existing_record = TagAutomationRecord.objects.get(post=post)

            # Delete the record
            existing_record.delete()

        # Get the automations
        automations = self.get_automations_sorted()

        # Check if the post has been updated
        updated = False

        # Loop through the automations
        for automation in automations:
            # Update the post
            if automation.update_post(post):
                # If the post was updated, set the updated flag
                updated = True

        try:
            # Save the record
            record.save()
        except Exception as e:
            # Show a warning
            print(f"Warning: Failed to save record for post {post}.")
            print(e)

        # Return whether or not the post was updated
        return updated

    def print_state(self):
        """Prints the state of the registry."""

        # Get the automations
        automations = self.get_automations_sorted()

        print("Tag Automation Registry State (" + self.get_state_hash() + "):")

        for i in range(len(automations)):
            automation = automations[i]
            print(f"{i + 1}.) {automation.__class__.__name__} (order: {automation.execution_order})")
        
        print("")