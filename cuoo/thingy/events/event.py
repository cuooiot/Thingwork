class Event:
    def __init__(self, callback, time):
        self.callback = callback
        self.time = time

        self.is_registered = False
        self.is_resolved = False
        self.is_cancelled = False

    def resolve(self, short_circuit=False):
        if (not self.is_cancelled or short_circuit):
            self.is_resolved = True
            self.callback()

    def cancel(self):
        if (not self.is_resolved):
            self.is_cancelled = True

    def register(self):
        self.is_registered = True

    def tick(self):
        self.time -= 1
        if (self.time <= 0):
            self.resolve()
