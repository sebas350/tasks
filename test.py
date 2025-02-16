from fastapi import FastAPI
app = FastAPI()

@app.get("/")
def root():
    return 'Bienvenidos a mi aplicacion de tareas'
