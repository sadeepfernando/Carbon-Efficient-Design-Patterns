from common.utils import generate_messages
from common.telemetry import Telemetry

class Processor:
    def handle(self, message):
        return message

class Decorator(Processor):
    def __init__(self, wrapped):
        self.wrapped = wrapped

    def handle(self, message):
        return self.wrapped.handle(message)

class MultiplyDecorator(Decorator):
    def handle(self, message):
        m = super().handle(message)
        m["value"] = m["value"] * 1.5
        return m

class AddNoiseDecorator(Decorator):
    def handle(self, message):
        m = super().handle(message)
        m["value"] += 0.0007
        return m

def run(count):
    messages = generate_messages(count)

    # Build processing pipeline like Java
    pipeline = AddNoiseDecorator(MultiplyDecorator(Processor()))

    for message in messages:
        pipeline.handle(message)

if __name__ == "__main__":
    import sys
    count = int(sys.argv[1])
    print(Telemetry.measure(run, count))
