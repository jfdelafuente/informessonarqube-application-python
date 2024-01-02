from datetime import datetime


def main():
    # d = datetime.strptime('2023-11-29T16:48:56+0000', "%Y-%m-%dT%H:%M:%S.%f%z")
    # print(datetime.strptime('2023-11-29T16:48:56+0000', "%Y-%m-%d %H:%M:%S"))
    d = datetime.fromisoformat('2023-11-29T16:48:56+0000')
    print(d)
    
    format = d.strftime('Día :%d, Mes: %m, Año: %Y, Hora: %H, Minutos: %M, Segundos: %S')
    print(format)


if __name__ == '__main__':
    main()