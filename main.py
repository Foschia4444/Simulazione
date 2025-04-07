import random
import time
import threading
import socket
import numpy as np
from fastapi import FastAPI, WebSocket, websockets, WebSocketDisconnect
import asyncio
import queue
import uvicorn
import logging

app = FastAPI()

def randomFloat(max_val, min_val, decimal_places):
    r = random.uniform(min_val, max_val)
    r = round(r, decimal_places)
    return r

class CoolantSystem:
    def __init__(self, initial_temperature=20.0, coolant_volume=10.0, specific_heat_capacity=4.186, time_step=5.0):
        self.ambient_temperature = initial_temperature
        self.coolant_temperature = initial_temperature
        self.coolant_volume = coolant_volume
        self.specific_heat_capacity = specific_heat_capacity
        self.coolant_mass = coolant_volume * 1000
        self.flow_rate = 0.0
        self.heat_transfer_coefficient = 500.0
        self.heat_exchange_area = 0.5
        self.pump_power = 0.0
        self.time_step = time_step

    def calculate_heat_transfer(self, machine_heat_load):
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
        delta_temp = self.calculate_heat_transfer(machine_heat_load)
        self.coolant_temperature += delta_temp
        self.coolant_temperature = max(self.ambient_temperature, self.coolant_temperature)
        if self.coolant_temperature > 60.0:
            print(f"ALLARME: Temperatura refrigerante elevata: {self.coolant_temperature:.2f}°C")

    def set_flow_rate(self, flow_rate):
        self.flow_rate = max(0.0, flow_rate)
        self.pump_power = self.flow_rate * 10.0
        self.heat_transfer_coefficient = 500.0 + 50.0 * (self.flow_rate / 10.0)

    def get_status(self):
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
        self.tear = 0.0
        self.blade_angle = 30.0  # Angolo iniziale del braccio (30°)
        self.shape = "circle"
        self.coolant_system = CoolantSystem(initial_temperature=self.ambient_temperature, time_step=5.0)
        self.machine_thermal_capacity = 50000
        self.blade_thermal_capacity = 5000
        self.h_A_machine = 15.0
        self.h_A_blade = 8.0
        self.max_speed_target=100.0

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
    
    def getTear(self):
        return self.tear

    # Other methods
    def startCutting(self):
        self.is_cutting = not self.is_cutting
        if not self.is_cutting:
            self.raiseBlade()
            self.max_speed=0

    def redButton(self):
        self.is_on = not self.is_on
        if not self.is_on:
            self.is_cutting = False
            self.speed = 0
            self.consumption = 0
            self.machine_temperature = self.ambient_temperature
            self.blade_temperature = self.ambient_temperature
            
    def setMaxSpeed(self, speed):
        self.max_speed = speed

    def varyMachineTemp(self):
        BASE_HEAT_RATE = 0.08
        BLADE_HEAT_TRANSFER = 0.05
        COOLING_RATE = 0.05
        MAX_TEMP = 150
        
        if self.is_on:
            heat = BASE_HEAT_RATE
            speed_effect = (self.speed / 100) * 0.5
            consumption_effect = (self.consumption / 3.0) * 0.4
            blade_effect = 0
            cooling = COOLING_RATE * (1 + (self.machine_temperature - self.ambient_temperature))
            if self.is_cutting:
                blade_effect = (self.blade_temperature / 300) * 0.3
            delta_temp = (heat + speed_effect + consumption_effect + blade_effect -cooling) * self.shapeModifier()
            self.machine_temperature = min(MAX_TEMP, self.machine_temperature + delta_temp)
        else:
            cooling = COOLING_RATE * (1 + (self.machine_temperature - self.ambient_temperature))
            if(self.ambient_temperature>self.machine_temperature):
                self.machine_temperature = min(
                    self.ambient_temperature,
                    self.machine_temperature - cooling
                )
            else:
                self.machine_temperature=self.ambient_temperature

    def varyBladeTemp(self):
        if self.is_on and self.is_cutting:
            BASE_HEATING = 1.5
            SPEED_EXPONENT = 1.8
            speed_factor = (self.speed / 100.0) ** SPEED_EXPONENT
            heating = BASE_HEATING * speed_factor * self.shapeModifier()
            if self.coolant_system.flow_rate > 0:
                cooling_power = 0.8 * (self.coolant_system.flow_rate / 10.0)
                heating -= cooling_power
            self.blade_temperature += max(0, heating)
            self.blade_temperature = min(self.blade_temperature, 300)
        elif self.blade_temperature > self.ambient_temperature:
            cooling_speed = 0.5 if self.blade_temperature > 100 else 0.2
            self.blade_temperature = max(
                self.ambient_temperature,
                self.blade_temperature - cooling_speed
            )
    
    def consumeBlade(self):
        if self.is_cutting:
            base = 0.5
            variable = self.speed * 0.03
            self.tear += base + variable + randomFloat(-0.1, 0.1, 2) * self.shapeModifier()

    def consumptionMachine(self):
        if self.is_on:
            base = 0.9 + 0.1
            self.consumption = base + randomFloat(-0.02, 0.05, 2) 
            if self.is_cutting:
                self.consumption = base + 2 + (randomFloat(-0.1, 1, 2) * self.shapeModifier())
            
    def replaceBlade(self):
        self.blade_temperature = self.ambient_temperature
        self.tear = 0
    
    def vibrate(self):
        vib = randomFloat(-1, 1, 4)
        return round(vib * self.speed * self.shapeModifier() * self.tear/1000, 4)
    
    def vibrateArray(self):
        array = []
        for i in range(50):
            array.append(self.vibrate())
        return array

    def varySpeed(self):
        if self.is_on and self.is_cutting:
            # Se la velocità è maggiore o uguale alla velocità massima
            if self.speed >= self.max_speed:
                var = -randomFloat(6, 2, 2)
                # Gradualità nella decelerazione, usando la velocità attuale
                self.speed += var * (self.speed / self.max_speed)  # Ridurre in modo proporzionale
                self.speed = max(self.speed, 0)  # Evita che la velocità diventi negativa
            else:
                var = randomFloat(6, 2, 2)
                # Modificare l'influenza in base alla forma
                var = var - (1 * self.shapeModifier())
                # La crescita della velocità dovrebbe essere meno influenzata dalla velocità attuale
                self.speed += var * (1 - (self.speed / self.max_speed))
        else:
            # Quando il dispositivo non è in funzione o non sta tagliando
            if self.speed > 0:
                var = -randomFloat(6, 2, 2)
                # La decelerazione deve essere graduale
                var = var - (1 * self.shapeModifier())
                # Applicare la decelerazione in modo graduale, riducendo l'impatto di `var` quando la velocità è altat
                self.speed = min(self.speed, self.max_speed_target) 
                self.speed += var * (1 - (self.speed / self.max_speed_target))
                self.speed = max(self.speed, 0)  # Evita che la velocità diventi negativa
        with open("speed_log.txt", "a") as f:
            f.write(f"{self.speed:.2f}\n")
        if(self.speed<0):
            self.speed=0
        

    def lowerBlade(self):
        self.blade_angle -= randomFloat(5, 2, 1)
        self.blade_angle = max(-20.0, self.blade_angle)  # Limite inferiore a -20°

    def raiseBlade(self):
        self.blade_angle = 30.0  # Angolo massimo (lama alzata)

    def operateBlade(self):
        if self.is_cutting:
            if self.blade_angle <= 5.0:
                self.raiseBlade()
            else:
                self.lowerBlade()

    def circleModifier(self):
        mod = 0
        # Mappiamo blade_angle (30° → 5°) a un modificatore (0 → 2)
        normalized_angle = (self.blade_angle - 5.0) / (30.0 - 5.0)  # Normalizza tra 0 e 1
        if normalized_angle <= 0.8:  # Simuliamo il contatto con il materiale
            mod = np.cos(((normalized_angle * 0.9) * 2) - 90) * 2
        return 1 + mod

    def rectangleModifier(self):
        mod = 0
        if self.blade_angle <= 25.0:  # Simuliamo il contatto con il materiale
            mod = 2
        return 1 + mod
    
    def shapeModifier(self):
        if self.shape == "circle":
            return self.circleModifier()
        elif self.shape == "rectangle":
            return self.rectangleModifier()
        return 1

    def calculate_heat_load(self):
        if self.is_on:
            heat_generated = self.consumption * 1000 * 0.3
            energy_generated = heat_generated * self.coolant_system.time_step
            if self.is_cutting:
                energy_generated_machine = energy_generated * 0.8
                energy_generated_blade = energy_generated * 0.2
            else:
                energy_generated_machine = energy_generated
                energy_generated_blade = 0.0
            energy_transferred_to_coolant_machine = self.h_A_machine * (self.machine_temperature - self.coolant_system.coolant_temperature) * self.coolant_system.time_step
            energy_transferred_to_coolant_blade = self.h_A_blade * (self.blade_temperature - self.coolant_system.coolant_temperature) * self.coolant_system.time_step
            self.machine_temperature += (energy_generated_machine - energy_transferred_to_coolant_machine) / self.machine_thermal_capacity
            self.blade_temperature += (energy_generated_blade - energy_transferred_to_coolant_blade) / self.blade_thermal_capacity
            self.machine_temperature = max(self.ambient_temperature, self.machine_temperature)
            self.blade_temperature = max(self.ambient_temperature, self.blade_temperature)
            total_energy_to_coolant = energy_transferred_to_coolant_machine + energy_transferred_to_coolant_blade
            machine_heat_load = total_energy_to_coolant / self.coolant_system.time_step
            return max(0.0, machine_heat_load)
        return 0.0

    def work(self):
        self.consumeBlade()
        self.vibrate()
        self.consumptionMachine()
        self.varySpeed()
        self.varyBladeTemp()
        self.varyMachineTemp()
        self.operateBlade()
        if self.is_cutting:
            self.coolant_system.set_flow_rate(10.0)
        else:
            self.coolant_system.set_flow_rate(0.0)
        heat_load = self.calculate_heat_load()
        self.coolant_system.update_coolant(heat_load)

    def get_data(self):
        coolant_status = self.coolant_system.get_status()
        return {
            "is_on": self.getIsOn(),
            "is_cutting": self.getIsCutting(),
            "speed": self.getSpeed(),
            "blade_temp": round(self.getBladeTemp(), 3),
            "machine_temp": round(self.getMachineTemp(), 3),
            "consumption": round(self.getConsumption(), 3),
            "coolant_temp": round(coolant_status["coolant_temperature"], 3),
            "vibrations": self.vibrateArray(),
            "blade_angle": self.blade_angle  # Sostituito blade_height con blade_angle
        }

class BandSawManager:
    def __init__(self, data_queue, command_queue):
        self.band_saw = BandSaw()
        self.data_queue = data_queue
        self.command_queue = command_queue

    def simulate(self, interval=0.1):
        while True:
            try:
                while not self.command_queue.empty():
                    command = self.command_queue.get_nowait()
                    self.process_command(command)
            except queue.Empty:
                pass
            if self.band_saw.is_on:
                self.band_saw.work()
                data = self.band_saw.get_data()
                #print(data)
                self.data_queue.put(data)
            time.sleep(interval)

    def process_command(self, command):
        action = command.get("action")
        if action == "toggle_machine":
            self.band_saw.redButton()
        elif action == "toggle_cutting":
            self.band_saw.startCutting()
        elif action == "emergency":
            self.band_saw.redButton()
            self.band_saw.is_cutting = False
        elif action == "replace_blade":
            self.band_saw.replaceBlade()
        elif action == "set_speed":
            speed = command.get("speed", 0)
            self.band_saw.setMaxSpeed(speed)
        elif action == "emergency_solved":
            self.band_saw.redButton()

clients = []

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    clients.append(websocket)
    try:
        while True:
            data = manager.band_saw.get_data()
            await websocket.send_json(data)
            await asyncio.sleep(0.5)
    except WebSocketDisconnect:
        clients.remove(websocket)
        print("Client disconnesso")

def run_server():
    uvicorn.run(app, host="10.0.20.118", port=8000)

def start_simulation(data_queue, command_queue):
    global manager
    manager = BandSawManager(data_queue, command_queue)
    manager.simulate(interval=0.5)


async def run_client():
    while True:
        try:
            async with websockets.connect("ws://10.0.20.75:8081/ws") as client_s:
                while True:
                    data = await client_s.recv()
                    print(data)
                    if(data=="shutdown"):
                        manager.band_saw.redButton()
                    elif(data=="shut_blade"):
                        manager.band_saw.startCutting()
                    elif(data=="change_blade"):
                        manager.band_saw.replaceBlade()

        except Exception as e:
            logging.error(f"WebSocket error: {e}")
            await asyncio.sleep(5)

"""
def tenta_connessione(host, port):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    while True:
        try:
            print(f"Tentativo di connessione a {host}:{port}...")
            client_socket.connect((host, port))
            print(f"\nConnesso al server {host}:{port}")
            return client_socket
            
        except ConnectionRefusedError:
            print("Server non raggiungibile, riprovo tra 5 secondi...")
            time.sleep(5)
            
        except socket.error as e:
            print(f'Errore di connessione: {e}')
            time.sleep(5)
            
        finally:
            client_socket.close()


def run_client():
    host = '10.0.20.75'
    port = 8081
    
    print("Avvio client in attesa di connessione...")
    print("Premi Ctrl+C per terminare")
    
    while True:
        try:
            # Tentativo di connessione con retry automatico
            client_socket = tenta_connessione(host, port)
            print("porcodio sin dentro")
            while True:
                # Ricezione dei messaggi dal server
                dati = client_socket.recv(1024)
                
                if not dati:
                    print('\nConnessione chiusa dal server, ritorno in attesa...')
                    break
                    
                messaggio = dati.decode('utf-8')
                print(f'\nRicevuto dal server: {messaggio}')
                
                # Input per inviare una risposta
                risposta = input('Inserisci il tuo messaggio (o "exit" per uscire): ')
                
                if risposta.lower() == 'exit':
                    print("\nUscita richiesta dall'utente")
                    break
                    
                client_socket.send(risposta.encode('utf-8'))
            
            client_socket.close()
            print("\nRitorno in attesa di nuova connessione...")
            
        except KeyboardInterrupt:
            print("\n\nChiusura del programma...")
            break
            
        except Exception as e:
            print(f'\nErrore imprevisto: {e}')
            print('Riprovo la connessione...')
            
        finally:
            # Attendo prima di riprovare
            time.sleep(5)
"""

if __name__ == "__main__":
    data_queue = queue.Queue()
    command_queue = queue.Queue()
    thread1 = threading.Thread(target=start_simulation, args=(data_queue, command_queue))
    thread2 = threading.Thread(target=run_server)
    thread3 = threading.Thread(target=run_client)
    thread1.daemon = True
    thread2.daemon = True
    thread3.daemon = True
    thread1.start()
    thread2.start()
    thread3.start()

    while True:
        time.sleep(1)