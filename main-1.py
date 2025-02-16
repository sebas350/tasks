from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3

app = FastAPI()

# Modelo para representar una tarea
class Tarea(BaseModel):
    title: str
    description: str
    status: str = "Por hacer"  # Valor por defecto

# Función para obtener la conexión de base de datos
def get_database():
    conn = sqlite3.connect("tareas.db")
    conn.execute("CREATE TABLE IF NOT EXISTS tasks (id INTEGER PRIMARY KEY, title TEXT, description TEXT, status TEXT)")
    return conn

@app.get("/")
def read_root():
    return {"message": "Bienvenidos a la aplicación"}

# Endpoint para crear una tarea
@app.post("/crear_tarea")
def crear_tarea(task: Tarea):
    conexion = get_database()
    cursor = conexion.cursor()
    cursor.execute("INSERT INTO tasks (title, description, status) VALUES (?, ?, ?)", (task.title, task.description, task.status))
    conexion.commit()
    conexion.close()
    return {"message": "Tarea creada con éxito"}

# Endpoint para ver todas las tareas
@app.get("/ver_tareas")
def ver_tareas():
    conexion = get_database()
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM tasks")
    tareas = cursor.fetchall()
    conexion.close()
    return {"tareas": tareas}

# Endpoint para modificar una tarea
@app.put("/modificar_tarea")
def modificar_tarea(task_id: int, task: Tarea):
    conexion = get_database()
    cursor = conexion.cursor()
    cursor.execute("UPDATE tasks SET title=?, description=?, status=? WHERE id=?", (task.title, task.description, task.status, task_id))
    conexion.commit()
    conexion.close()
    return {"message": "Tarea modificada con éxito"}

# Endpoint para eliminar una tarea
@app.delete("/eliminar_tarea")
def eliminar_tarea(task_id: int):
    conexion = get_database()
    cursor = conexion.cursor()
    cursor.execute("DELETE FROM tasks WHERE id=?", (task_id,))
    conexion.commit()
    conexion.close()
    return {"message": "Tarea eliminada con éxito"}
