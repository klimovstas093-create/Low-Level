from components.PowerBlock import PowerBlock
from components.StorageBlock import Storage

class Generator(PowerBlock):
    def __init__(self, *args, **kwargs):
        self.mining_progress = 0
        
        super().__init__(*args, **kwargs)
        self.max_storage = self.states.get("max_storage", 10)
        self.storage = Storage(max_size=self.max_storage)
        self.mining_speed = self.states.get("mining_speed", 1)
        self.mining_type = self.states.get("mining_type", "coal")
        self.energy_add = self.states.get("energy_add", 1)


    def update(self, tick, dt):
        self.mining_progress += dt
        if self.mining_progress >= self.mining_speed:
            self.mining_progress = 0
            if self.mining_type in self.storage.lst: 
                self.storage.lst.remove(self.mining_type)
                self.energy = min(self.energy+self.energy_add, self.max_energy)
        super().update(tick, dt)
