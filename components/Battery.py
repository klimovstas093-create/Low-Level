from components.PowerBlock import PowerBlock
from base.functions import get_texture

class Battery(PowerBlock):
    def __init__(self, *args, **kwargs):
        self.stored = 0
        super().__init__(*args, **kwargs)
        self.max_stored = self.states.get("max_stored_energy", 10)

        self.center = self.w.scene.addPixmap(get_texture("core_1"))
        self.center.setPos((self.x+self.size[0]/2)*32-8, (self.y+self.size[1]/2)*32-8)
        self.center.setZValue(40)
        self.center.setOpacity(0)

    def update(self, tick, dt):
        super().update(tick, dt)
        self.center.setOpacity(self.stored/self.max_stored)
        if self.energy > 0.08:
            excess = self.energy - 0.05
            charge = min(excess, self.max_stored - self.stored)
            self.stored += charge
            self.energy -= charge
        
        elif self.energy < 0.05 and self.stored > 0:
            discharge = min(0.1 - self.energy, self.stored, 0.5)
            self.energy += discharge
            self.stored -= discharge
