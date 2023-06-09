from Detector import main_app
from create_classifier import train_classifer
from create_dataset import start_capture
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
        print("3. Salir")
        choice = input("\nElija una opción: ")

        if choice == '1':
            add_user()
        elif choice == '2':
            check_user()
        elif choice == '3':
            print("Hasta pronto!")
            break
        else:
            print("Opción inválida, intente nuevamente")

def add_user():
    name = input("\nIngrese el nombre del usuario: ")
    if name == "None":
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
    name = input("Seleccione el usuario: ")
    if name not in names:
        print("Error: El usuario no existe")
    else:
        main_app(name)

if __name__ == "__main__":
    main()
