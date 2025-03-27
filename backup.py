import random
import time
import requests
import threading
import numpy as np

def randomFloat(max_val, min_val, decimal_places):
    r = random.uniform(min_val, max_val)
    r = round(r, decimal_places)
    return r

class CoolantSystem:
    def __init__(self, initial_temperature=20.0, coolant_volume=10.0, specific_heat_capacity=4.186, time_step=5.0):
        # Parametri fisici del liquido refrigerante
        self.ambient_temperature = initial_temperature  # °C
        self.coolant_temperature = initial_temperature  # °C
        self.coolant_volume = coolant_volume  # litri
        self.specific_heat_capacity = specific_heat_capacity  # J/g°C
        self.coolant_mass = coolant_volume * 1000  # g (densità ≈ 1 g/cm³, tipica dell'acqua)
        
        # Parametri del sistema di raffreddamento
        self.flow_rate = 0.0  # litri/minuto
        self.heat_transfer_coefficient = 500.0  # W/m²K 
        self.heat_exchange_area = 0.5  # m² (area stimata per una segatrice)
        self.pump_power = 0.0  # W (potenza pompa)
        
        # Parametri temporali
        self.time_step = time_step  # secondi (allineato all'intervallo di simulazione)

    def calculate_heat_transfer(self, machine_heat_load):
        """Calcola il trasferimento di calore e la variazione di temperatura."""
        delta_temperature = self.coolant_temperature - self.ambient_temperature
        heat_dissipated = (
            self.heat_transfer_coefficient * self.heat_exchange_area * delta_temperature
        )
        energy_balance = machine_heat_load - heat_dissipated
        temperature_change = (
            (energy_balance * self.time_step) / (self.coolant_mass * self.specific_heat_capacity)
        )
        return temperature_change
    
    def update_coolant(self, machine_heat_load):
        """Aggiorna lo stato del liquido refrigerante."""
        delta_temp = self.calculate_heat_transfer(machine_heat_load)
        self.coolant_temperature += delta_temp
        self.coolant_temperature = max(self.ambient_temperature, self.coolant_temperature)
        if self.coolant_temperature > 60.0:
            print(f"ALLARME: Temperatura refrigerante elevata: {self.coolant_temperature:.2f}°C")

    def set_flow_rate(self, flow_rate):
        """Imposta la portata del liquido refrigerante."""
        self.flow_rate = max(0.0, flow_rate)
        self.pump_power = self.flow_rate * 10.0  # 10 W per litro/minuto
        self.heat_transfer_coefficient = 500.0 + 50.0 * (self.flow_rate / 10.0)  # W/m²K

    def get_status(self):
        """Restituisce lo stato attuale del sistema."""
        return {
            "coolant_temperature": self.coolant_temperature,
            "flow_rate": self.flow_rate,
            "pump_power": self.pump_power,
            "heat_transfer_coefficient": self.heat_transfer_coefficient
        }

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
        self.blade_height = 120
        self.shape = ""
        # Sistema di raffreddamento integrato
        self.coolant_system = CoolantSystem(initial_temperature=self.ambient_temperature, time_step=5.0)
        # Capacità termiche (J/°C)
        self.machine_thermal_capacity = 50000  # Stima per macchina (es. 100 kg * 500 J/kg°C)
        self.blade_thermal_capacity = 5000  # Stima per lama (es. 10 kg * 500 J/kg°C)
        # Coefficienti di trasferimento termico al refrigerante (W/°C)
        self.h_A_machine = 10.0  # Macchina-refrigerante
        self.h_A_blade = 2.0  # Lama-refrigerante

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
        if not self.is_cutting:
            self.raiseBlade()

    def redButton(self):
        self.is_on = not self.is_on
        if not self.is_on:
            self.is_cutting = False
            self.speed = 0
            self.consumption = 0
        
    def setMaxSpeed(self, speed):
        self.max_speed = speed



    def varyBladeTemp(self):
        if self.is_on and self.is_cutting:
            var = randomFloat(0.3, 2, 2)
            speed_factor = self.speed / 100
            var = var * (1 + speed_factor)
            var = var * self.shapeModifier()
            self.blade_temperature += var
        elif self.blade_temperature > self.ambient_temperature:
            var = -randomFloat(0.1, 0.5, 2)
            self.blade_temperature += var
            self.blade_temperature = max(self.ambient_temperature, self.blade_temperature)
    
    def consumeBlade(self):
        if self.is_cutting:
            base = 0.5
            variable = self.speed * 0.03
            self.tear += base + variable + randomFloat(-0.1, 0.1, 2) * self.shapeModifier()

    def consumptionMachine(self):
        if self.is_on:
            base = 3 + 0.1 #pompa di raffreddamento
            self.consumption = base + randomFloat(-0.02, 0.05, 2) 
            if self.is_cutting:
                self.consumption = base + (randomFloat(-0.1, 0.5, 2) * self.shapeModifier())
                self.consumption = min(self.consumption, 100)
            else:
                self.consumption = min(self.consumption, 20)
            
    def replaceBlade(self):
        self.blade_temperature = self.ambient_temperature
        self.tear = 0
    
    def varyVibration(self):
        vib = self.getSpeed()
        vib = vib * (1 + self.tear) * self.shapeModifier()
        self.vibration = vib

    def varySpeed(self):
        if self.is_on and self.is_cutting:
            if self.speed >= self.max_speed:
                self.speed = self.max_speed
            else:
                var = randomFloat(5, 10, 2)
                var = var - (1 * self.shapeModifier())
                self.speed += var
        else:
            if self.speed <= 0:
                self.speed = 0
            else:
                var = -randomFloat(10, 20, 2)
                self.speed += var
                self.speed = max(self.speed, 0)

    def lowerBlade(self):
        self.blade_height = self.blade_height - randomFloat(10, 5, 1)
        self.blade_height = max(self.blade_height, 0)

    def raiseBlade(self):
        self.blade_height = 120

    def operateBlade(self):
        if self.blade_height == 0:
            self.raiseBlade()
        else:
            self.lowerBlade()

    def circleModifier(self):
        mod = 0
        if self.blade_height <= 100:
            mod = np.cos(((self.blade_height * 0.9) * 2) - 90) * 2
        return 1 + mod

    def rectangleModifier(self):
        mod = 0
        if self.blade_height <= 100:
            mod = 2
        return 1 + mod
    
    def shapeModifier(self):
        if self.shape == "circle":
            return self.circleModifier()
        elif self.shape == "rectangle":
            return self.rectangleModifier()
        return 1  # Default se shape non è definito

    def calculate_heat_load(self):
        """Calcola il calore generato e trasferito al refrigerante."""
        if self.is_on:
            # Calore totale generato dal consumo (W)
            heat_generated = self.consumption * 1000 * 0.3  # 30% del consumo in kW → W
            energy_generated = heat_generated * self.coolant_system.time_step  # J
            
            # Distribuzione del calore
            if self.is_cutting:
                energy_generated_machine = energy_generated * 0.8  # 80% alla macchina
                energy_generated_blade = energy_generated * 0.2    # 20% alla lama
            else:
                energy_generated_machine = energy_generated
                energy_generated_blade = 0.0

            # Calore trasferito al refrigerante (J)
            energy_transferred_to_coolant_machine = self.h_A_machine * (self.machine_temperature - self.coolant_system.coolant_temperature) * self.coolant_system.time_step
            energy_transferred_to_coolant_blade = self.h_A_blade * (self.blade_temperature - self.coolant_system.coolant_temperature) * self.coolant_system.time_step
            
            # Aggiornamento temperature macchina e lama
            self.machine_temperature += (energy_generated_machine - energy_transferred_to_coolant_machine) / self.machine_thermal_capacity
            self.blade_temperature += (energy_generated_blade - energy_transferred_to_coolant_blade) / self.blade_thermal_capacity
            
            # Limiti minimi
            self.machine_temperature = max(self.ambient_temperature, self.machine_temperature)
            self.blade_temperature = max(self.ambient_temperature, self.blade_temperature)
            
            # Calore totale trasferito al refrigerante (W)
            total_energy_to_coolant = energy_transferred_to_coolant_machine + energy_transferred_to_coolant_blade
            machine_heat_load = total_energy_to_coolant / self.coolant_system.time_step  # Convertito in W
            return max(0.0, machine_heat_load)  # Non negativo
        return 0.0

    def work(self):
        self.consumeBlade()
        self.varyVibration()
        self.consumptionMachine()
        self.varySpeed()
        self.varyBladeTemp()
        self.varyMachineTemp()
        self.operateBlade()
        
        # Gestione del sistema di raffreddamento
        if self.is_cutting:
            self.coolant_system.set_flow_rate(10.0)  # Pompa attiva durante il taglio
        else:
            self.coolant_system.set_flow_rate(0.0)  # Pompa spenta
        
        # Calcolo e trasferimento del calore al refrigerante
        heat_load = self.calculate_heat_load()
        self.coolant_system.update_coolant(heat_load)

    def get_data(self):
        """Return simulation data as a dictionary for JSON serialization."""
        coolant_status = self.coolant_system.get_status()
        return {
            "is_on": self.getIsOn(),
            "is_cutting": self.getIsCutting(),
            "speed": self.getSpeed(),
            "max_speed": self.max_speed,
            "blade_temp": round(self.getBladeTemp(), 3),
            "machine_temp": round(self.getMachineTemp(), 3),
            "consumption": self.getConsumption(),
            "vibration": round(self.getVibration(), 3),
            "tear": round(self.getTear(), 3),
            "coolant_temp": round(coolant_status["coolant_temperature"], 3),
            "flow_rate": coolant_status["flow_rate"],
            "pump_power": coolant_status["pump_power"],
            "heat_transfer_coeff": coolant_status["heat_transfer_coefficient"]
        }
    
    def check_alarms(self):
        self.alarms = []
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

    def send_data(self, url):
        """Send simulation data to the FastAPI endpoint."""
        try:
            data = self.get_data()
            response = requests.post(url, json=data)
            print(f"Data sent to {url}, status: {response.status_code}, response: {response.text}")
            return response
        except requests.exceptions.RequestException as e:
            print(f"Error sending data: {e}")
            return None

    def simulate(self, interval=5):
        """Simulate with a configurable interval (in seconds) between sends."""
        while self.is_on:
            self.work()
            self.check_alarms()
            #response = self.send_data("http://10.0.20.147:8000/")
            #self.handle_server_commands(response)
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
            coolant_status = self.coolant_system.get_status()
            print(f"Coolant Temp: {coolant_status['coolant_temperature']:.2f}°C")
            print(f"Flow Rate: {coolant_status['flow_rate']:.2f} L/min")
            print(f"Pump Power: {coolant_status['pump_power']:.2f} W")
            print(f"Heat Transfer Coeff: {coolant_status['heat_transfer_coefficient']:.2f} W/m²K")
            print(f"Alarms: {self.alarms}")
            print("---")
            time.sleep(interval)

def startSimulation():
    macchinaDeSatana = BandSaw()
    macchinaDeSatana.redButton()  # Turn on
    macchinaDeSatana.setMaxSpeed(80)
    macchinaDeSatana.startCutting()
    macchinaDeSatana.simulate(interval=1)

# Main
if __name__ == "__main__":
    thread1 = threading.Thread(target=startSimulation)
    thread1.start()
    thread1.join()