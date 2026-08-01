from enum import Enum

class State(Enum):
    IDLE = 0
    ACQUIRING = 1
    PROCESSING = 2
    SENDING = 3

class StateMachine:
    def __init__(self):
        self.state = State.IDLE

    def set_state(self, state):
        self.state = state
        print(f"\nSTATE -> {state.name}")