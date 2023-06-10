from Detector import main_app
from create_classifier import train_classifer
from create_dataset import start_capture
from smartlock import readPad
names = set()

# Leer los nombres existentes desde el archivo
with open("nameslist.txt", "r") as f:
    x = f.read()
    z = x.rstrip().split(" ")
    for i in z:
        names.add(i)

def main():
    while True:
        print("\n--- Menu ---")
        print("1. Agregar un usuario")
        print("2. Verificar un usuario")
        print("*. Salir")
        choice = readPad()

        if choice == '1':
            add_user()
        elif choice == '2':
            check_user()
        elif choice == '*':
            print("Hasta pronto!")
            break
        else:
            print("Opción inválida, intente nuevamente")

def add_user():
    print("\nElige 1, 2 o 3")
    name = readPad()
    if name == "1":
        print("Error: El nombre no puede ser 'None'")
    elif name in names:
        print("Error: ¡El usuario ya existe!")
    elif len(name) == 0:
        print("Error: ¡El nombre no puede estar vacío!")
    else:
        names.add(name)
        start_capture(name)
        train_classifer(name)
        print("El modelo ha sido entrenado exitosamente!")
        
def check_user():
    print("\nUsuarios registrados: ")
    for name in names:
        print(name)
    print("Seleccione el usuario con su número correspondiente o * para salir.")
    name = readPad()
    if name == '*':
        return
    if name not in names:
        print("Error: El usuario no existe")
    else:
        main_app(name)

if __name__ == "__main__":
    main()
