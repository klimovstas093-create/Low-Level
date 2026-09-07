from components.StorageBlock import StorageBlock
from base.functions import save

class Drill(StorageBlock):
    def __init__(self, *args, **kwargs):
        self.mining_progress = 0

        super().__init__(*args, **kwargs)
        self.mining_speed = self.states.get("mining_speed", 1)

        self.ores = []
        for cell in self.get_occupied_cells():
            blocks = self.w.block_map.get(cell)
            if blocks is None:
                continue
            for block in blocks:
                if block is None or block is self:
                    continue
                if block.states["z"] not in (14, 15):
                    continue
                if block.states["mining_type"] is not None:
                    self.ores.append(block.states["mining_type"])

    @save
    def update(self, tick, dt):
        super().update(tick, dt)
        self.mining_progress += dt
        if self.mining_progress >= self.mining_speed:
            if self.temperature > self.states["mining_max_temperature"]:
                return
            self.mining_progress = 0
            for ore in self.ores:
                if self.storage.add(ore, 1):
                    self.temperature += 1
