from utils.lastdate import save_current_date, leer_last_date, nombre_fichero
import configSonar

def main():
    last_date = leer_last_date(configSonar.DIR_SONAR + 'last_date.txt')
    print(nombre_fichero("metrica", last_date))

if __name__ == '__main__':
    main()
