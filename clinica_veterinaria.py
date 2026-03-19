# -*- coding: utf-8 -*-
# ============================================================
# EVALUACION FINAL - MODULO 3
# Base de Datos para una Clinica Veterinaria
# Alumno: [Tu nombre aqui]
# Fecha: 19/03/2026
# ============================================================
# Necesitas instalar psycopg2:  pip install psycopg2-binary
import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# ============================================================
# CONFIGURACION DE CONEXION - Cambia estos valores segun tu
# instalacion de PostgreSQL
# ============================================================
CONFIG = {
    "host":     "localhost",
    "port":     5432,
    "user":     "postgres",
    "password": "123456",
    # Forzamos mensajes de error en ingles (ASCII) para evitar
    # problemas de encoding en Windows con PostgreSQL en espanol
    "options":  "-c lc_messages=C",
}
NOMBRE_BD = "clinica_veterinaria"


def conectar(**kwargs):
    """Wrapper de psycopg2.connect que maneja el error de encoding
    en Windows cuando PostgreSQL envia mensajes en Latin-1."""
    try:
        return psycopg2.connect(**kwargs)
    except UnicodeDecodeError as e:
        # El servidor envio el mensaje de error en Latin-1 (cp1252)
        # en lugar de UTF-8. Lo decodificamos manualmente.
        mensaje = e.object.decode("latin-1")
        raise Exception("Error de PostgreSQL: " + mensaje) from None


# ============================================================
# PASO 1: CREAR LA BASE DE DATOS
# ============================================================
print("=" * 60)
print("  BASE DE DATOS: " + NOMBRE_BD)
print("=" * 60)

# Primero nos conectamos a la base 'postgres' (que siempre existe)
# para poder crear nuestra base de datos nueva
conexion_admin = conectar(dbname="postgres", **CONFIG)
conexion_admin.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
cursor_admin = conexion_admin.cursor()
# Forzar encoding UTF-8 para los mensajes del servidor
cursor_admin.execute("SET client_encoding TO 'UTF8'")

# Verificamos si la base de datos ya existe antes de crearla
cursor_admin.execute(
    "SELECT 1 FROM pg_database WHERE datname = %s", (NOMBRE_BD,)
)
existe = cursor_admin.fetchone()

if not existe:
    cursor_admin.execute(
        sql.SQL("CREATE DATABASE {}").format(sql.Identifier(NOMBRE_BD))
    )
    print("[OK] Base de datos '{}' creada.".format(NOMBRE_BD))
else:
    print("[OK] Base de datos '{}' ya existe, continuando...".format(NOMBRE_BD))

cursor_admin.close()
conexion_admin.close()

# Ahora nos conectamos a nuestra base de datos
conexion = conectar(dbname=NOMBRE_BD, **CONFIG)
cursor = conexion.cursor()

# ============================================================
# PASO 2: CREAR LAS TABLAS
# ============================================================
print("\n[TABLAS]")

# Tabla Profesional (va primero porque Atencion la referencia)
cursor.execute("""
    CREATE TABLE IF NOT EXISTS Profesional (
        id_profesional  SERIAL          PRIMARY KEY,
        nombre          VARCHAR(100)    NOT NULL,
        especialidad    VARCHAR(100)    NOT NULL
    )
""")
print("[OK] Tabla 'Profesional' creada.")

# Tabla Dueno
cursor.execute("""
    CREATE TABLE IF NOT EXISTS Dueno (
        id_dueno    SERIAL          PRIMARY KEY,
        nombre      VARCHAR(100)    NOT NULL,
        direccion   VARCHAR(200),
        telefono    VARCHAR(20)
    )
""")
print("[OK] Tabla 'Dueno' creada.")

# Tabla Mascota - con llave foranea a Dueno
cursor.execute("""
    CREATE TABLE IF NOT EXISTS Mascota (
        id_mascota        SERIAL          PRIMARY KEY,
        nombre            VARCHAR(100)    NOT NULL,
        tipo              VARCHAR(50),
        fecha_nacimiento  DATE,
        id_dueno          INT             NOT NULL,
        CONSTRAINT fk_mascota_dueno
            FOREIGN KEY (id_dueno) REFERENCES Dueno(id_dueno)
    )
""")
print("[OK] Tabla 'Mascota' creada.")

# Tabla Atencion - con llaves foraneas a Mascota y Profesional
cursor.execute("""
    CREATE TABLE IF NOT EXISTS Atencion (
        id_atencion     SERIAL          PRIMARY KEY,
        fecha_atencion  DATE            NOT NULL,
        descripcion     TEXT,
        id_mascota      INT             NOT NULL,
        id_profesional  INT             NOT NULL,
        CONSTRAINT fk_atencion_mascota
            FOREIGN KEY (id_mascota)     REFERENCES Mascota(id_mascota),
        CONSTRAINT fk_atencion_profesional
            FOREIGN KEY (id_profesional) REFERENCES Profesional(id_profesional)
    )
""")
print("[OK] Tabla 'Atencion' creada.")

conexion.commit()
print("[OK] Todas las tablas creadas con relaciones y restricciones.")

# ============================================================
# PASO 3: INSERTAR DATOS DE EJEMPLO
# ============================================================
print("\n[DATOS]")

# Profesionales
profesionales = [
    (1, "Dr. Martinez",  "Veterinario"),
    (2, "Dr. Perez",     "Especialista en dermatologia"),
    (3, "Dr. Lopez",     "Cardiologo veterinario"),
]
for p in profesionales:
    cursor.execute("""
        INSERT INTO Profesional (id_profesional, nombre, especialidad)
        VALUES (%s, %s, %s)
        ON CONFLICT (id_profesional) DO NOTHING
    """, p)
# Ajustamos la secuencia para que el proximo SERIAL empiece desde 4
cursor.execute("SELECT setval('profesional_id_profesional_seq', (SELECT MAX(id_profesional) FROM Profesional))")
print("[OK] Profesionales insertados.")

# Duenos
duenos = [
    (1, "Juan Perez",   "Calle Falsa 123",           "555-1234"),
    (2, "Ana Gomez",    "Avenida Siempre Viva 456",  "555-5678"),
    (3, "Carlos Ruiz",  "Calle 8 de Octubre 789",    "555-8765"),
]
for d in duenos:
    cursor.execute("""
        INSERT INTO Dueno (id_dueno, nombre, direccion, telefono)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (id_dueno) DO NOTHING
    """, d)
cursor.execute("SELECT setval('dueno_id_dueno_seq', (SELECT MAX(id_dueno) FROM Dueno))")
print("[OK] Duenos insertados.")

# Mascotas
mascotas = [
    (1, "Rex",  "Perro", "2020-05-10", 1),
    (2, "Luna", "Gato",  "2019-02-20", 2),
    (3, "Fido", "Perro", "2021-03-15", 3),
]
for m in mascotas:
    cursor.execute("""
        INSERT INTO Mascota (id_mascota, nombre, tipo, fecha_nacimiento, id_dueno)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (id_mascota) DO NOTHING
    """, m)
cursor.execute("SELECT setval('mascota_id_mascota_seq', (SELECT MAX(id_mascota) FROM Mascota))")
print("[OK] Mascotas insertadas.")

# Atenciones
atenciones = [
    (1, "2025-03-01", "Chequeo general",           1, 1),
    (2, "2025-03-05", "Tratamiento dermatologico",  2, 2),
    (3, "2025-03-07", "Consulta cardiologica",      3, 3),
]
for a in atenciones:
    cursor.execute("""
        INSERT INTO Atencion (id_atencion, fecha_atencion, descripcion, id_mascota, id_profesional)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (id_atencion) DO NOTHING
    """, a)
cursor.execute("SELECT setval('atencion_id_atencion_seq', (SELECT MAX(id_atencion) FROM Atencion))")
print("[OK] Atenciones insertadas.")

conexion.commit()

# ============================================================
# PASO 4: CONSULTAS
# ============================================================
print("\n" + "=" * 60)
print("  CONSULTAS")
print("=" * 60)

# --- Consulta 1: Duenos y sus mascotas ---
print("\n--- Consulta 1: Duenos y sus mascotas ---")
cursor.execute("""
    SELECT
        d.id_dueno,
        d.nombre        AS dueno,
        d.telefono,
        m.nombre        AS mascota,
        m.tipo,
        m.fecha_nacimiento
    FROM Dueno d
    JOIN Mascota m ON d.id_dueno = m.id_dueno
    ORDER BY d.id_dueno
""")
print("{:>3}  {:<15} {:<12} {:<8} {:<6} {}".format(
    "ID", "Dueno", "Telefono", "Mascota", "Tipo", "Nacimiento"))
print("-" * 60)
for fila in cursor.fetchall():
    print("{:>3}  {:<15} {:<12} {:<8} {:<6} {}".format(*fila))

# --- Consulta 2: Atenciones con detalle del profesional ---
print("\n--- Consulta 2: Atenciones con detalles del profesional ---")
cursor.execute("""
    SELECT
        a.id_atencion,
        a.fecha_atencion,
        a.descripcion,
        m.nombre        AS mascota,
        p.nombre        AS profesional,
        p.especialidad
    FROM Atencion a
    JOIN Mascota     m ON a.id_mascota     = m.id_mascota
    JOIN Profesional p ON a.id_profesional = p.id_profesional
    ORDER BY a.fecha_atencion
""")
print("{:>3}  {:<12} {:<30} {:<6} {:<15} {}".format(
    "ID", "Fecha", "Descripcion", "Mascota", "Profesional", "Especialidad"))
print("-" * 90)
for fila in cursor.fetchall():
    print("{:>3}  {:<12} {:<30} {:<6} {:<15} {}".format(*fila))

# --- Consulta 3: Cantidad de atenciones por profesional (COUNT) ---
print("\n--- Consulta 3: Atenciones por profesional ---")
cursor.execute("""
    SELECT
        p.nombre                    AS profesional,
        p.especialidad,
        COUNT(a.id_atencion)        AS total_atenciones
    FROM Profesional p
    LEFT JOIN Atencion a ON p.id_profesional = a.id_profesional
    GROUP BY p.id_profesional
    ORDER BY total_atenciones DESC
""")
print("{:<15} {:<30} {:>16}".format("Profesional", "Especialidad", "Total atenciones"))
print("-" * 65)
for fila in cursor.fetchall():
    print("{:<15} {:<30} {:>16}".format(*fila))

# ============================================================
# PASO 5: ACTUALIZACION Y ELIMINACION
# ============================================================
print("\n" + "=" * 60)
print("  ACTUALIZACIONES Y ELIMINACIONES")
print("=" * 60)

# --- Consulta 4: Actualizar direccion de Juan Perez ---
print("\n--- Consulta 4: Actualizar direccion de Juan Perez ---")
cursor.execute("""
    UPDATE Dueno
    SET direccion = %s
    WHERE nombre = 'Juan Perez'
""", ("Calle Nueva 999",))
conexion.commit()
print("[OK] Direccion actualizada. Filas afectadas: {}".format(cursor.rowcount))

cursor.execute("SELECT nombre, direccion FROM Dueno WHERE nombre = 'Juan Perez'")
fila = cursor.fetchone()
print("     Verificacion -> {}: {}".format(fila[0], fila[1]))

# --- Consulta 5: Eliminar atencion con id = 2 ---
print("\n--- Consulta 5: Eliminar atencion con id = 2 ---")
cursor.execute("DELETE FROM Atencion WHERE id_atencion = %s", (2,))
conexion.commit()
print("[OK] Atencion con id=2 eliminada. Filas afectadas: {}".format(cursor.rowcount))

cursor.execute("SELECT COUNT(*) FROM Atencion")
print("     Atenciones restantes: {}".format(cursor.fetchone()[0]))

# ============================================================
# PASO 6: TRANSACCION
# ============================================================
print("\n" + "=" * 60)
print("  TRANSACCION")
print("=" * 60)
print("\n--- Consulta 6: Nueva mascota + atencion + actualizar dueno ---")

# Con psycopg2 la transaccion ya esta activa por defecto.
# Si algo falla usamos rollback() para revertir todo.
try:
    # 1. Agregar nueva mascota solo si no existe ya para este dueno
    cursor.execute("""
        SELECT id_mascota FROM Mascota
        WHERE nombre = %s AND id_dueno = %s
    """, ("Toby", 1))
    mascota_existente = cursor.fetchone()

    if mascota_existente:
        id_nueva_mascota = mascota_existente[0]
        print("  [INFO] Mascota 'Toby' ya existe con id={}, reutilizando...".format(id_nueva_mascota))
    else:
        cursor.execute("""
            INSERT INTO Mascota (nombre, tipo, fecha_nacimiento, id_dueno)
            VALUES (%s, %s, %s, %s)
            RETURNING id_mascota
        """, ("Toby", "Perro", "2023-07-20", 1))
        id_nueva_mascota = cursor.fetchone()[0]
        print("  [OK] Nueva mascota 'Toby' insertada con id={}".format(id_nueva_mascota))

    # 2. Registrar atencion para la nueva mascota
    cursor.execute("""
        INSERT INTO Atencion (fecha_atencion, descripcion, id_mascota, id_profesional)
        VALUES (%s, %s, %s, %s)
        RETURNING id_atencion
    """, ("2026-03-19", "Primera consulta y vacunacion", id_nueva_mascota, 1))
    id_nueva_atencion = cursor.fetchone()[0]
    print("  [OK] Atencion registrada con id={}".format(id_nueva_atencion))

    # 3. Actualizar telefono de Juan Perez
    cursor.execute("""
        UPDATE Dueno SET telefono = %s WHERE id_dueno = %s
    """, ("555-9999", 1))
    print("  [OK] Telefono de Juan Perez actualizado a '555-9999'")

    # Todo salio bien: confirmamos los 3 cambios juntos
    conexion.commit()
    print("\n[OK] TRANSACCION COMPLETADA EXITOSAMENTE (COMMIT)")

except Exception as error:
    # Algo fallo: revertimos TODOS los cambios
    conexion.rollback()
    print("\n[ERROR] TRANSACCION FALLIDA - cambios revertidos (ROLLBACK)")
    print("  Detalle: {}".format(error))

# ============================================================
# VERIFICACION FINAL
# ============================================================
print("\n" + "=" * 60)
print("  ESTADO FINAL DE LA BASE DE DATOS")
print("=" * 60)
for tabla in ["Dueno", "Mascota", "Profesional", "Atencion"]:
    cursor.execute("SELECT COUNT(*) FROM {}".format(tabla))
    total = cursor.fetchone()[0]
    print("  Tabla {:<15}: {} registro(s)".format(tabla, total))

conexion.close()
print("\n[OK] Conexion cerrada.")
print("=" * 60)
