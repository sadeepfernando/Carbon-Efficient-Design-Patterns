from common.utils import generate_messages
from common.telemetry import Telemetry

class Observer:
    def update(self, message):
        pass

class ConcreteObserver(Observer):
    def update(self, message):
        # Simulate computational work
        result = message["value"] * 2.5
        return result

class Subject:
    def __init__(self):
        self.observers = []

    def register(self, obs):
        self.observers.append(obs)

    def notify(self, message):
        for obs in self.observers:
            obs.update(message)

    def process(self, messages):
        for message in messages:
            self.notify(message)

def run(count):
    messages = generate_messages(count)

    subject = Subject()

    # Register 4 observers (same structure as Java)
    subject.register(ConcreteObserver())
    subject.register(ConcreteObserver())
    subject.register(ConcreteObserver())
    subject.register(ConcreteObserver())

    subject.process(messages)

if __name__ == "__main__":
    import sys
    count = int(sys.argv[1])
    print(Telemetry.measure(run, count))
