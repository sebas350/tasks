from fastapi import FastAPI, Form, Request, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from jinja2 import Template
import sqlite3
from pydantic import BaseModel

app = FastAPI()

def get_database():
    conn = sqlite3.connect('tareas.db')
    conn.execute('CREATE TABLE IF NOT EXISTS tasks (id INTEGER PRIMARY KEY, title TEXT, description TEXT, status TEXT)')
    return conn

class Tarea(BaseModel):
    title: str = ''
    description: str = ''
    status: str = 'Por hacer'

app = FastAPI()

#funcion Response configurar un msj flash
def set_flash_message(response: Response, mensaje: str):
    response.set_cookie("msj_flash_tarea", mensaje, max_age=10 )

#funcion para obtener el msj flash
def get_flash_message(request: Request):
    mensaje = request.cookies.get('msj_flash_tarea', '')
    return mensaje


bootstrap = '''<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-QWTKZyjpPEjISv5WaRU9OFeRpok6YctnYmDr5pNlyT2bRjXh0JMhjY6hW+ALEwIH" crossorigin="anonymous">
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js" integrity="sha384-YvpcrYf0tY3lHB60NNkmXc5s9fDVZLESaAA55NDzOxhy9GkcIdslK1eN7N6jIeHz" crossorigin="anonymous"></script>'''

#endpoint inicio frontend

@app.get("/", response_class=HTMLResponse)
def get_table(request : Request):
    conexion = get_database()
    cursor = conexion.cursor()
    cursor.execute('SELECT * FROM tasks')
    tareas = cursor.fetchall()
    conexion.close()
    
    msj = get_flash_message(request)
    
    html_content = """
    <html>
    <head>
        <title>Mis Tareas</title>
        {{bootstrap}}
    </head>
    <body class="container">
        <h1 style="text-align: center;">Mis Tareas</h1>
        {% if msj %}
            <div class="alert alert-success alert-dismissible fade show" role="alert">
  <strong>{{msj}}
  <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
</div>
        {% endif %}
        <p>Agregar Tarea <button type="button" class="btn btn-primary" onclick="window.location.href='/agregar_tarea'">Agregar
</button></p>
        <table class="table">
            <thead class="table-primary">
                <tr>
                    <th>Id</th>
                    <th>Titulo</th>
                    <th>Descripcion</th>
                    <th>Estado</th>
                    <th>Accion</th>
                </tr>
            </thead>
            <tbody>
                {% for registro in tareas %}
                    
                    <tr>
                        <td>{{registro.0}}</td>
                        <td>{{registro.1}}</td>
                        <td>{{registro.2}}</td>
                        <td>{{registro.3}}</td>
                        <td> <button type="button" class="btn btn-primary" onclick="window.location.href='/formulario_modificar/{{registro.0}}'">Modificar
</button>                            
                             <form action="/eliminar_tarea/{{registro.0}}" method="post" style="display: inline;">
                                  <input class="btn btn-danger" type="submit" value="Eliminar" onclick="return confirm('Seguro que quiere eliminar la tarea');">
                             </form>
                                
                        </td>
                    </tr>
                    
                 {% endfor %}
                
            </tbody>
        </table>
    </body>
    </html>
    """
    template = Template(html_content)
    render_template = template.render(tareas = tareas, msj = msj, bootstrap = bootstrap)
    response_html = HTMLResponse(content = render_template)
    response_html.delete_cookie('msj_flash_tarea')
    return response_html

#crear Tarea fastapi

@app.post("/crear_tarea")
def crear_tarea(task: Tarea):
    conexion = get_database()
    cursor = conexion.cursor()
    cursor.execute('INSERT INTO tasks(title, description, status) VALUES (?, ?, ?)', (task.title, task.description, task.status))
    conexion.commit()
    return {'Resultado': 'Tarea Guardada'}

#crear Tarea frontend

@app.post("/agregar_tarea", response_class = HTMLResponse)
def agregar_tarea(title: str = Form(...),
    description: str = Form(...),
    status: str = Form(...)):
    
    conexion = get_database()
    cursor = conexion.cursor()
    cursor.execute('INSERT INTO tasks(title, description, status) VALUES (?, ?, ?)', (title, description, status))
    conexion.commit()
    conexion.close()
     
    response = RedirectResponse(url='/', status_code=303)
    set_flash_message(response, 'Tarea guardada satisfactoriamente')
    return response


@app.get("/agregar_tarea", response_class = HTMLResponse)
def mostrar_formulario():   
    content_html = '''
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>Agregar Tarea</title>
        {{bootstrap}}
    </head>
    <body class="container">
    
    <form action="/agregar_tarea" method="post">
        <fieldset>
            <legend>Agregar Tarea</legend>
            <label for="title">Título:</label>
            <input type="text" name="title">
            <label for="description">Descripción:</label>
            <input type="text" name="description">
            <label for="status">Estado:</label>
            <input type="text" name="status">
            <button class="btn btn-primary" type="submit">Agregar</button>
        
        </fieldset>
        
    </form>
  
    </body>
    </html>
    '''
    
    template = Template(content_html)
    html_render = template.render(bootstrap = bootstrap)
    return HTMLResponse(content = html_render)


#ver tareas fastapi

@app.get("/ver_tarea")
def ver_tarea():
    conexion = get_database()
    cursor = conexion.cursor()
    cursor.execute('SELECT * FROM tasks')
    tareas = cursor.fetchall()
    conexion.close()

    return {'tareas': tareas} #JSON


@app.get('/formulario_modificar/{task_id}')
def form_edit(task_id: int):
    conexion = get_database()
    cursor = conexion.cursor()
    cursor.execute('SELECT * FROM tasks WHERE id=?',(task_id,))
    tarea = cursor.fetchone()
    conexion.close()
    
    content_html = '''
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>Actualizar Tarea</title>
        {{bootstrap}}
    
    </head>
    <body class="container">
        <form action="/modificar_tarea/{{tarea.0}}" method="post">
        <fieldset>
            <legend>Modificar Tarea</legend>
            <label for="id">Id:</label>
            <input type="text" name="id" value="{{tarea.0}}"disabled>
            <label for="title">Título:</label>
            <input type="text" name="title" value="{{tarea.1}}">
            <label for="description">Descripción:</label>
            <input type="text" name="description" value="{{tarea.2}}">
            <label for="status">Estado:</label>
            <input type="text" name="status" value="{{tarea.3}}">
            <input class="btn btn-primary" type="submit" value="Actualizar">
        </fieldset>
    </form>
        
    </body>
    </html>
    '''
    
    template = Template(content_html)
    render = template.render(tarea=tarea, bootstrap = bootstrap)
    response = HTMLResponse(content = render)
    return response


#modificar tarea para fastapi

@app.put("/modificar_tarea_fastapi/{task_id}")
def modificar_tarea(task_id: int, task: Tarea):
    conexion = get_database()
    cursor = conexion.cursor()
    cursor.execute("UPDATE tasks SET title=?, description=?, status=? WHERE id=?", (task.title, task.description, task.status, task_id))
    conexion.commit()
    conexion.close()
    return {'tarea': 'tarea modificada'}

#modificar tarea para frontend

@app.post("/modificar_tarea/{task_id}")
def edit_task(task_id: int,
    title: str = Form(...),
    description: str = Form(...),
    status: str = Form(...)):
    
    conexion = get_database()
    cursor = conexion.cursor()
    cursor.execute("UPDATE tasks SET title=?, description=?, status=? WHERE id=?", (title, description, status, task_id))
    conexion.commit()
    conexion.close()
     
    response = RedirectResponse(url='/', status_code=303)
    set_flash_message(response, 'Tarea Actualizada Satisfactoriamente')
    return response

#eliminar tarea fastapi

@app.delete("/eliminar_tarea_fastapi/{task_id}")
def eliminar_tarea_fastapi(task_id: int):
    conexion = get_database()
    cursor = conexion.cursor()
    cursor.execute("DELETE FROM tasks WHERE id=?", (task_id,))
    conexion.commit()
    conexion.close()
    return {'Resultado': 'Tarea eliminada'}
    
#eliminar tarea frontend

@app.post("/eliminar_tarea/{task_id}")
def eliminar_tarea(task_id: int):
    conexion = get_database()
    cursor = conexion.cursor()
    cursor.execute("DELETE FROM tasks WHERE id=?", (task_id,))
    conexion.commit()
    conexion.close()
    
    response = RedirectResponse(url='/', status_code=303)
    set_flash_message(response, 'Tarea Eliminada satisfactoriamente')
    return response
    
    