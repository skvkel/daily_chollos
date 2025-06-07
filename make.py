import asyncio

import os
import subprocess


def load_env(file_path=".env"):
    with open(file_path, "r") as file:
        for line in file:
            line = line.strip()
            if line and not line.startswith("#"):
                key, value = line.split("=", 1)
                os.environ[key.strip()] = value.strip()


load_env()

def aerich_initialized():
    return os.path.exists("migrations")


async def init_db():
    from daily_chollos.infrastructure.model import init_db as tortoise_init_db

    if not aerich_initialized():
        subprocess.run(["aerich", "init", "-t", "daily_chollos.infrastructure.model.TORTOISE_ORM"])
        subprocess.run(["aerich", "init-db"])
    else:
        await tortoise_init_db()
        print("Aerich ya inicializado. Usa limpiar migraciones si necesitas reiniciar.")


def migrate():
    subprocess.run(["aerich", "migrate"])


def upgrade():
    subprocess.run(["aerich", "upgrade"])


def downgrade():
    subprocess.run(["aerich", "downgrade"])


def clean_migrations():
    if os.path.exists("migrations"):
        import shutil
        shutil.rmtree("migrations")
        print("Migraciones eliminadas")
    else:
        print("No hay migraciones para eliminar.")

    if os.path.exists("pyproject.toml"):
        os.remove("pyproject.toml")
        print("Archivo pyproject.toml eliminado.")
    else:
        print("No existe archivo pyproject.toml")


async def main():
    while True:
        print("\nOpciones:")
        print("1. Inicializar base de datos")
        print("2. Crear migración")
        print("3. Aplicar migraciones (upgrade)")
        print("4. Aplicar migraciones (downgrade)")
        print("5. Limpiar migraciones")
        print("6. Salir")

        choice = input("Seleccione una opción: ")

        if choice == "1":
            await init_db()
        elif choice == "2":
            migrate()
        elif choice == "3":
            upgrade()
        elif choice == "4":
            downgrade()
        elif choice == "5":
            clean_migrations()
        elif choice == "6":
            print("Saliendo...")
            break
        else:
            print("Opción no válida. Intente de nuevo.")


if __name__ == "__main__":
    asyncio.run(main())
