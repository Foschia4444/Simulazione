import random
import time
import requests

def randomFloat(max_val, min_val, decimal_places):
    r = random.uniform(min_val, max_val)
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
        self.max_speed = 0.0
        self.vibration = 0.0
        self.tear = 0.0
        self.alarms = []

    # Getters
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

    
    # Other methods
    def startCutting(self):
        self.is_cutting = not self.is_cutting

    def redButton(self):
        self.is_on = not self.is_on
        if not self.is_on:
            self.is_cutting = False
            self.speed = 0
            self.consumption = 0
        
    def setMaxSpeed(self, speed):
        self.max_speed = speed
            
    def varyMachineTemp(self):
        if self.is_on:
            var = randomFloat(0.1, 1, 2)
            speed_factor = self.speed / 100
            var = var * (1 + speed_factor/2)
            self.machine_temperature += var
        elif self.machine_temperature > self.ambient_temperature:
            var = -randomFloat(0.1, 0.5, 2)
            self.machine_temperature += var
            self.machine_temperature = max(self.ambient_temperature, self.machine_temperature)
        else:
            var = 0
            self.machine_temperature += var

    def varyBladeTemp(self):
        if self.is_on and self.is_cutting:
            var = randomFloat(0.3, 2, 2)
            speed_factor = self.speed / 100
            var = var * (1 + speed_factor)
            self.blade_temperature += var
        elif self.blade_temperature > self.ambient_temperature:
            var = -randomFloat(0.1, 0.5, 2)
            self.blade_temperature += var
            self.blade_temperature = max(self.ambient_temperature, self.blade_temperature)
        else:
            var = 0
            self.blade_temperature += var
    
    def check_alarms(self):
        if self.blade_temperature > 100:
            self.alarms.append("Blade Overheat")
        if self.machine_temperature > 60:
            self.alarms.append("Machine Overheat")
        if self.vibration > 150:
            self.alarms.append("Excessive Vibration")
        if self.tear > 50:
            self.alarms.append("Blade Replacement Needed")
            
    def handle_server_commands(self, response):
        if response and response.status_code == 200:
            data = response.json()
            if data.get("command") == "shutdown":
                self.redButton()
            elif data.get("speed"):
                self.setMaxSpeed(data["speed"])
    
    def consumeBlade(self):
        if self.is_cutting:
            base = 0.5
            variable = self.speed * 0.03
            self.tear += base + variable + randomFloat(-0.1, 0.1, 2)

    def consumptionMachine(self):
        if self.is_on:
            base = 3
            self.consumption = base + randomFloat(-0.05, 0.05, 2)
    
    def replaceBlade(self):
        self.blade_temperature = self.ambient_temperature
        self.tear = 0
    
    def varyVibration(self):
        vib = self.getSpeed()
        vib = vib * (1 + self.tear) 
        self.vibration = vib

    def varySpeed(self):
        if self.is_on and self.is_cutting:
            if self.speed >= self.max_speed:
                self.speed = self.max_speed
            else:
                var = randomFloat(5, 10, 2)
                self.speed += var
        else:
            if self.speed <= 0:
                self.speed = 0
            else:
                var = -randomFloat(10, 20, 2)
                self.speed += var
                self.speed=max(self.speed,0)

    def work(self):
        self.consumeBlade()
        self.varyVibration()
        self.consumptionMachine()
        self.varySpeed()
        self.varyBladeTemp()
        self.varyMachineTemp()

    def get_data(self):
        """Return simulation data as a dictionary for JSON serialization."""
        return {
            "is_on": self.getIsOn(),
            "is_cutting": self.getIsCutting(),
            "speed": self.getSpeed(),
            "max_speed": self.max_speed,
            "blade_temp": self.getBladeTemp(),
            "machine_temp": round(self.getMachineTemp(),3),
            "consumption": self.getConsumption(),
            "vibration": round(self.getVibration(),3),
            "tear": round(self.getTear(),3)
        }

    def send_data(self, url):
        """Send simulation data to the FastAPI endpoint."""
        try:
            data = self.get_data()
            response = requests.post(url, json=data)
            print(f"Data sent to {url}, status: {response.status_code}, response: {response.text}")
            return response.status_code
        except requests.exceptions.RequestException as e:
            print(f"Error sending data: {e}")
            return None

    def simulate(self, interval=5):
        """Simulate with a configurable interval (in seconds) between sends."""
        i = 0
        while self.is_on:
            i += 1
            if i == 10:
                self.startCutting()
            self.work()
            # Send data to FastAPI
            self.send_data("http://10.0.20.147:8000/")
            # Print to console
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
            time.sleep(interval)  # Configurable delay between sends

# Main execution
macchinaDeSatana = BandSaw()
macchinaDeSatana.redButton()  # Turn on
macchinaDeSatana.setMaxSpeed(80)
macchinaDeSatana.startCutting()
macchinaDeSatana.simulate(interval=5)  # Send data every 5 seconds