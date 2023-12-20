from datetime import datetime

# Salva la fecha actual al "file"
def save_current_date(file):
    # Saves the current date to "~/last_date.txt"
    with open(file, mode='w') as file:
        now = datetime.now()
        file.write(now.strftime("%Y-%m-%d %H:%M:%S"))

# Leer la fecha registrada en el "file"        
def leer_last_date(file):
    fecha = ""
    with open(file, mode='r') as file:
        fecha = file.readline()
        
    return fecha