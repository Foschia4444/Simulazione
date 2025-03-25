import random
import time

def randomFloat(max_val, min_val, decimal_places):
    r = random.uniform(min_val, max_val)
    # Round the number to the specified number of decimal places
    r = round(r, decimal_places)
    return r

class BandSaw:
    def __init__(self):
        self.is_on = False
        self.is_cutting = False
        self.is_automatic = False
        self.proximity_sensor = False
        self.ambient_temperature = 15.0
        self.blade_temperature = self.ambient_temperature
        self.machine_temperature = self.ambient_temperature
        self.consumption = 0.0
        self.speed = 0.0
        self.max_speed=0.0
        self.vibration = 0.0
        self.tear = 0.0
        self.alarms = []

    def getIsOn(self):
        return self.is_on

    def getIsCutting(self):
        return self.is_cutting
    
    def getIsAutomatic(self):
        return self.is_automatic

    def getProximity(self):
        return self.proximity_sensor

    def getConsumption(self):
        return self.consumption
    
    def getBladeTemp(self):
        return self.blade_temperature
    
    def getMachineTemp(self):
        return self.machine_temperature
    
    def getAmbientTemp(self):
        return self.ambient_temperature
    
    def getSpeed(self):
        return self.speed
    
    def getVibration(self):
        return self.vibration
    
    def getTear(self):
        return self.tear
    
    # By the name of Christ, we're done with the getters

    def startCutting(self):
        self.is_cutting = not self.is_cutting

    def redButton(self):
        self.is_on = not self.is_on # si accende / spegne
        if not self.is_on:
            self.is_cutting = False
            self.speed = 0
            self.consumption = 0
        
    def setMaxSpeed(self, speed):
        self.max_speed = speed
            
    def varyMachineTemp(self):
        if self.is_on:
            var = randomFloat(0.1, 1, 2)  # Base variation
            speed_factor = self.speed / 100  # Factor proportional to speed (normalized)
            var = var * (1 + speed_factor/2)
            self.machine_temperature += var
        elif self.machine_temperature > self.ambient_temperature:  # Machine not in use: cools down
            var = -randomFloat(0.1, 0.5, 2)
            self.machine_temperature += var
            self.machine_temperature = max(self.ambient_temperature, self.machine_temperature)  # Don't go below ambient temperature
        else:
            var = 0  # Keep stable
            self.machine_temperature += var

    def varyBladeTemp(self):
        if self.is_on and self.is_cutting:
            var = randomFloat(0.3, 2, 2)  # Base variation
            speed_factor = self.speed / 100  # Factor proportional to speed (normalized)
            var = var * (1 + speed_factor)
            self.blade_temperature += var
        elif self.blade_temperature > self.ambient_temperature:  # Blade not in use: cools down
            var = -randomFloat(0.1, 0.5, 2)
            self.blade_temperature += var
            self.blade_temperature = max(self.ambient_temperature, self.blade_temperature)  # Don't go below ambient temperature
        else:
            var = 0  # Keep stable
            self.blade_temperature += var
        
    def consumeBlade(self):
        if(self.is_cutting):
            base = 0.5  # Base consumption
            variable = self.speed * 0.03  # Proportional to speed
            self.tear += base + variable + randomFloat(-0.1, 0.1, 2)  # Add small random fluctuation

    def consumptionMachine(self):
        if self.is_on:  # Machine consumes when on, regardless of cutting
            base = 3  # Base consumption in kW (e.g., motor idle)
            self.consumption = base + randomFloat(-0.05, 0.05, 2)  # Small random fluctuation
    
    def replaceBlade(self):
        self.blade_temperature = self.ambient_temperature  # New piece
        self.tear = 0
    
    def varyVibration(self):
        vib = self.getSpeed()
        vib = vib*(1+ self.tear) 
        self.vibration = vib

    def varySpeed(self):
        if self.is_on and self.is_cutting:  # Check state
            if self.speed >= self.max_speed:  # Maximum limit
                self.speed = self.max_speed
            else:
                var = randomFloat(5, 10, 2)  # Accelerate blade
                self.speed += var
        else:
            if self.speed <= 0:  # Minimum limit
                self.speed = 0
            else:
                var = -randomFloat(10, 20, 2)  # Slow down blade
                self.speed += var
                self.speed= max (self.speed, 0)

    def work(self):
        self.consumeBlade()
        self.varyVibration()
        self.consumptionMachine()
        self.varySpeed()
        self.varyBladeTemp()
        self.varyMachineTemp()

    def simulate(self):
            i=0
            while self.is_on:
                i=i+1
                if(i%10==0):
                    self.startCutting()
                self.work()
                print(f"Status: {self.getIsOn()}")
                print(f"Cutting: {self.getIsCutting()}")
                print(f"Speed: {self.getSpeed():.2f}")
                print(f"Max Speed: {self.max_speed:.2f}")
                print(f"Blade Temp: {self.getBladeTemp():.2f}")
                print(f"Machine Temp: {self.getMachineTemp():.2f}")
                print(f"Consumption: {self.getConsumption():.2f}")
                print(f"Vibration: {self.getVibration():.2f}")
                print(f"Tear: {self.getTear():.2f}")
                print("---")
                time.sleep(1)


macchinaDeSatana=BandSaw()
macchinaDeSatana.redButton()
macchinaDeSatana.setMaxSpeed(80)
macchinaDeSatana.startCutting()

macchinaDeSatana.simulate()
    