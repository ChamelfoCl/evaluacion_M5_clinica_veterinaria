# Evaluacion Final - Modulo 5
## Base de Datos para una Clinica Veterinaria

### Descripcion
Script en Python que crea y gestiona una base de datos PostgreSQL para una clinica veterinaria.
Implementa tablas relacionadas, consultas SQL, actualizaciones, eliminaciones y transacciones.

---

### Requisitos
- Python 3.x
- PostgreSQL instalado y corriendo en `localhost:5432`
- Libreria `psycopg2`:
  ```
  pip install psycopg2-binary
  ```

---

### Configuracion
Antes de ejecutar, editar las credenciales en `clinica_veterinaria.py` (lineas 17-25):
```python
CONFIG = {
    "host":     "localhost",
    "port":     5432,
    "user":     "postgres",
    "password": "TU_CONTRASENA",  # <-- cambiar aqui
    "options":  "-c lc_messages=C",
}
```

---

### Ejecucion
```bash
python clinica_veterinaria.py
```

---

### Estructura de la base de datos

```
Dueno (id_dueno, nombre, direccion, telefono)
  |
  +-- Mascota (id_mascota, nombre, tipo, fecha_nacimiento, id_dueno)
                |
                +-- Atencion (id_atencion, fecha_atencion, descripcion,
                              id_mascota, id_profesional)
                                |
                              Profesional (id_profesional, nombre, especialidad)
```

---

### Funcionalidades implementadas

| # | Criterio | Descripcion |
|---|----------|-------------|
| 1 | Creacion de BD | Base de datos `clinica_veterinaria` |
| 2 | Creacion de tablas | 4 tablas con FOREIGN KEY y restricciones |
| 3 | Insercion de datos | 3 duenos, 3 mascotas, 3 profesionales, 3 atenciones |
| 4 | SELECT + JOIN | Duenos con sus mascotas; atenciones con profesional |
| 5 | Agregacion | COUNT de atenciones por profesional |
| 6 | UPDATE | Actualizar direccion de un dueno |
| 7 | DELETE | Eliminar una atencion |
| 8 | Transaccion | INSERT + INSERT + UPDATE con COMMIT/ROLLBACK |

---

### Tecnologias utilizadas
- **Python 3** - lenguaje de programacion
- **PostgreSQL 18** - motor de base de datos relacional
- **psycopg2** - conector Python para PostgreSQL
