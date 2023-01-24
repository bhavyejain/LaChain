class Request:
    def __init__(self, source, requestType, clock=None, transaction=None):
        self.source = source
        self.requestType = requestType
        self.clock = clock
        self.transaction = transaction

class LClock:
    def __init__(self, time, pid):
        self.time = time
        self.pid = pid

    def increment(self):
        self.time += 1

    def update(self, clock):
        self.time = max(self.time, clock.time) + 1
    
    def current(self):
        return (self.time, self.pid)

class Transaction:
    def __init__(self, source, destination, amount):
        self.source = source
        self.destination = destination
        self.amount = amount

    def transaction(self):
        return (self.source, self.destination, self.amount)

    def __str__(self):
        return f'<{self.source},{self.destination},{self.amount}>'

class Block:
    def __init__(self, prevHash, transaction):
        self.prevHash = prevHash
        self.transaction = transaction
    
    def __str__(self):
        return f'[{self.prevHash | self.transaction}]'