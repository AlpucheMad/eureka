import pymysql
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración de la conexión
host = 'localhost'
port = 3306
user = 'root'  # Usuario root de MySQL
password = ''  # Contraseña del usuario root (vacía para instalaciones por defecto de Laragon)
db_name = 'eureka_app'
new_user = 'eureka_app'
new_password = 'Pal@dio95'

print(f"Intentando conectar a MySQL como {user}@{host}:{port}")

# Conectar a MySQL
try:
    connection = pymysql.connect(
        host=host,
        port=port,
        user=user,
        password=password,
    )
    
    print("Conexión exitosa a MySQL")
    
    with connection.cursor() as cursor:
        # Crear la base de datos si no existe
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
        print(f"Base de datos '{db_name}' creada o ya existente.")
        
        try:
            # Verificar si el usuario ya existe
            cursor.execute(f"SELECT User FROM mysql.user WHERE User = '{new_user}';")
            user_exists = cursor.fetchone()
            
            if not user_exists:
                # Crear el usuario
                cursor.execute(f"CREATE USER '{new_user}'@'localhost' IDENTIFIED BY '{new_password}';")
                print(f"Usuario '{new_user}' creado.")
            else:
                print(f"El usuario '{new_user}' ya existe.")
            
            # Otorgar privilegios al usuario
            cursor.execute(f"GRANT ALL PRIVILEGES ON {db_name}.* TO '{new_user}'@'localhost';")
            cursor.execute("FLUSH PRIVILEGES;")
            print(f"Privilegios otorgados a '{new_user}' para la base de datos '{db_name}'.")
        except pymysql.MySQLError as e:
            print(f"Error al configurar usuario: {e}")
    
    connection.close()
    print("Configuración de la base de datos completada con éxito.")
    
    # Actualizar el archivo .env con las nuevas credenciales
    env_file = '.env'
    with open(env_file, 'r') as file:
        lines = file.readlines()
    
    with open(env_file, 'w') as file:
        for line in lines:
            if line.startswith('DB_USER='):
                file.write(f'DB_USER={new_user}\n')
            elif line.startswith('DB_PASSWORD='):
                file.write(f'DB_PASSWORD={new_password}\n')
            else:
                file.write(line)
    
    print("Archivo .env actualizado con las nuevas credenciales.")
    
except pymysql.MySQLError as e:
    print(f"Error al conectar a MySQL: {e}")
except Exception as e:
    print(f"Error inesperado: {e}") 