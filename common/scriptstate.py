
from common.types import eventData

class IScriptState:
    """
    Represents a state the script can be in.

    This interface is implemented by various classes to allow the script to
    switch between states. For example:
    * Waiting to recognise device
    * Main state (processing events and stuff)
    * Error state (something went horribly wrong)
    """
    def initialise(self) -> None:
        """
        Initialise this context
        """
        raise NotImplementedError("This method must be overridden by child classes")

    def processEvent(self, event: eventData) -> None:
        """Process a MIDI event

        ### Args:
        * `event` (`event`): event to process
        """
        raise NotImplementedError("This method must be overridden by child classes")
    
    def tick(self) -> None:
        """
        Called frequently to allow any required updates to the controller
        """
        raise NotImplementedError("This method must be overridden by child classes")
