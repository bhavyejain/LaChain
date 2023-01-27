from enum import Enum
from hashlib import sha256

M_TYPE = Enum('M_TYPE', ['MUTEX', 'REPLY', 'RELEASE'])
RESULT = Enum('RESULT', ['SUCCESS', 'ABORTED', 'WAITING'])

class Message:
    def __init__(self, messageType, source, clock, req_clock=None, transaction=None, status=None):
        self.messageType = messageType
        self.source = source
        self.clock = clock
        self.req_clock = req_clock
        self.transaction = transaction
        self.status = status
    
    @classmethod
    def getFromString(cls, msgStr):
        components = msgStr.split('|')
        messageType = M_TYPE[components[0]]
        if messageType == M_TYPE.MUTEX:
            return cls(messageType, components[1], LClock.getFromString(components[2]), None, Transaction.getFromString(components[3]), None)
        elif messageType == M_TYPE.REPLY:
            return cls(messageType, components[1], LClock.getFromString(components[2]), LClock.getFromString(components[3]), None, None)
        else:
            return cls(messageType, components[1], LClock.getFromString(components[2]), LClock.getFromString(components[3]), None, RESULT[components[4]])

    def __str__(self):
        if self.messageType == M_TYPE.MUTEX:
            return f'{self.messageType.name}|{self.source}|{self.clock.__str__()}|{self.transaction.__str__()}'
        if self.messageType == M_TYPE.REPLY:
            return f'{self.messageType.name}|{self.source}|{self.clock.__str__()}|{self.req_clock.__str__()}'
        if self.messageType == M_TYPE.RELEASE:
            return f'{self.messageType.name}|{self.source}|{self.clock.__str__()}|{self.req_clock.__str__()}|{self.status.name}'
        return ""

class LClock:
    def __init__(self, time, pid):
        self.time = time
        self.pid = pid
    
    @classmethod
    def getFromString(cls, clockStr):
        components = clockStr.split('.')
        return cls(time=int(components[0]), pid=int(components[1]))

    def increment(self):
        self.time += 1
        print(f'----- CLOCK : {self.__str__()} -----')
        return LClock(self.time, self.pid)

    def update(self, clock):
        self.time = max(self.time, clock.time) + 1
        print(f'----- CLOCK : {self.__str__()} -----')
    
    def __lt__(self, clock):
        if self.time < clock.time:
            return True
        elif self.time == clock.time and self.pid < clock.pid:
            return True
        return False
    
    def __str__(self):
        return f'{self.time}.{self.pid}'

class Transaction:
    def __init__(self, source, destination, amount):
        self.source = source
        self.destination = destination
        self.amount = amount

    @classmethod
    def getFromString(cls, tStr):
        components = tStr.split(',')
        return cls(source=components[0], destination=components[1], amount=components[2])

    def __str__(self):
        return f'{self.source},{self.destination},{self.amount}'

class Block:
    def __init__(self, timestamp, transaction):
        self.timestamp = timestamp
        self.transaction = transaction
        self.prev_hash = ""
        self.status = RESULT.WAITING
    
    def resolve(self, status):
        self.status = status
    
    def is_resolved(self):
        return self.status != RESULT.WAITING
    
    def get_hash(self):
        hash = sha256(bytes(self.prev_hash + self.transaction.__str__(), "utf-8"))
        return hash.hexdigest()
    
    def __str__(self):
        return f'[{self.prev_hash}|{self.transaction}|{self.timestamp}|{self.status.name}]'

class BlockChain:
    def __init__(self):
       self._chain = []
       self._current = -1
    
    def __rehash(self, idx):
        if idx == 0:
            p_hash = sha256(b"").hexdigest()
        else:
            p_hash = self._chain[idx-1].get_hash()
        
        for i in range (idx, len(self._chain)):
            self._chain[i].prev_hash = p_hash
            p_hash = self._chain[i].get_hash()

    def insert(self, block):
        curr_block = self.current()
        if curr_block == None:
            self._chain.append(block)
            self._current = 0
            self.__rehash(0)
        elif curr_block.timestamp.__lt__(block.timestamp):
            if self._chain[-1].timestamp.__lt__(block.timestamp):
                self._chain.append(block)
                self.__rehash(len(self._chain)-1)
                if self.current().is_resolved():
                    self._current += 1
            else:
                for i in range (self._current, len(self._chain)):
                    if block.timestamp.__lt__(self._chain[i].timestamp):
                        self._chain.insert(i, block)
                        self.__rehash(i)
                        break
        else:
            self._chain.insert(self._current, block)
            self.__rehash(self._current)
    
    def current(self):
        if self._current == -1:
            return None
        return self._chain[self._current]

    def resolve_current(self, status):
        self._chain[self._current].status = status
        if self._current != len(self._chain)-1:
            self._current += 1
    
    def current_client(self):
        curr_block = self.current()
        if curr_block == None:
            return None
        else:
            return curr_block.transaction.source

    def print_chain(self):
        for block in self._chain:
            print(block.__str__())
            print("\t |")
        print("\t []")
        print(f'Current hash: {self.current().prev_hash}')
    
    def print_current(self):
        print(f'{self.current().__str__()}')