from precise_runner import PreciseRunner, ReadWriteStream, PreciseEngine


class Precise():
    
    def __init__(self):
        # engine data:      https://github.com/mycroftai/precise-data/tree/dist
        # precise models:   https://github.com/MycroftAI/precise-data/tree/models?files=1
        sensitivity = float(0.5)
        trigger_level = int(3)
        model_path = "models/hey-mycroft.pb"
        engine_path = "precise-engine/precise-engine"
        engine = PreciseEngine(
            engine_path, model_path)

        self.stream = ReadWriteStream()
        self.runner = PreciseRunner(
            engine,
            sensitivity=sensitivity,
            trigger_level=trigger_level,
            on_activation=self.on_activation
        )
        print("Starting precise")
        self.runner.start()
        while True:
            data = self.stream.read()
            self.update_runner(data)

    def update_runner(self, data):
        self.stream.write(data)

    def on_activation(self):
        print("Activation!")

Precise()
