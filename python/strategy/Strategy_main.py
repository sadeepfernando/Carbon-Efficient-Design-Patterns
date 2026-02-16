from common.utils import generate_messages
from common.telemetry import Telemetry

class Strategy:
    def execute(self, message):
        pass

class StrategyA(Strategy):
    def execute(self, message):
        return message["value"] * 3.1

class StrategyB(Strategy):
    def execute(self, message):
        return message["value"] + 2.4

class Context:
    def __init__(self, strategy):
        self.strategy = strategy

    def process(self, messages):
        for message in messages:
            self.strategy.execute(message)

def run(count):
    messages = generate_messages(count)

    # Use Strategy A by default (same logic as Java)
    context = Context(StrategyA())
    context.process(messages)

if __name__ == "__main__":
    import sys
    count = int(sys.argv[1])
    print(Telemetry.measure(run, count))
