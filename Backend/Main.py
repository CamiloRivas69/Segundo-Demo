from fastapi import FastAPI, Request, Form # Importa FastAPI y utilidades para peticiones y formularios
from fastapi.responses import HTMLResponse, RedirectResponse # Importa respuestas HTML y redirecciones
from fastapi.templating import Jinja2Templates # Importa Jinja2 para plantillas
from starlette.middleware.sessions import SessionMiddleware # Importa middleware para sesiones
from Conexion_BD import get_db_connection, close_db_connection # Importa funciones para manejar la base de datos

app = FastAPI() # Crea una instancia de FastAPI
app.add_middleware(SessionMiddleware, secret_key="mi_clave_ultra_secreta_123456")# Añade middleware para manejar sesiones
templates = Jinja2Templates(directory="../frontend") # Configura el directorio de plantillas

# ─────────────────────────────────────────────────────────────
# RUTAS GENERALES
# ─────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse) # Página de inicio
def pagina_inicio(request: Request): 
    return templates.TemplateResponse("Inicio.html", {"request": request})# Página de inicio

@app.get("/menu", response_class=HTMLResponse) # Página de menú 
def mostrar_bienvenida(request: Request):
    return templates.TemplateResponse("Menu_usuario.html", {"request": request}) # Página de menú

@app.get("/servicios", response_class=HTMLResponse) # Página de servicios
def mostrar_bienvenida(request: Request):
    return templates.TemplateResponse("Servicios.html", {"request": request}) # Página de servicios


# ─────────────────────────────────────────────────────────────
# CERRAR SESIÓN
# ─────────────────────────────────────────────────────────────


@app.get("/logout") # Ruta para cerrar sesión
def cerrar_sesion(request: Request):
    request.session.clear()  # Elimina todos los datos de sesión
    return RedirectResponse(url="/Login", status_code=303) # Redirige a la página de inicio de sesión

# ─────────────────────────────────────────────────────────────
# GESTIÓN DE USUARIOS EXISTENTES
# ─────────────────────────────────────────────────────────────

@app.get("/Login", response_class=HTMLResponse) # Página de inicio de sesión
@app.get("/ingreso_usuario", response_class=HTMLResponse) # Página de inicio de sesión
def mostrar_formulario_ingreso(request: Request, mensaje: str = ""): 
    return templates.TemplateResponse("ingreso_usuario.html", {"request": request, "mensaje": mensaje}) # Página de inicio de sesión
@app.post("/Login", response_class=HTMLResponse) # Ruta para validar el usuario (inicio de sesión)
async def validar_usuario(
    request: Request, # Objeto de la petición HTTP
    correo: str = Form(...), #obtiene el correo del formulario
    contrasena: str = Form(...) # Obtiene la contraseña del formulario
):
    db = get_db_connection() # Conexión a la base de datos
    if db: 
        try: 
            with db.cursor() as cursor: 
                # Consulta SQL para buscar el usuario con el correo y contraseña proporcionados
                sql = "SELECT * FROM usuario WHERE correo = %s AND contrasena = %s" 
                cursor.execute(sql, (correo, contrasena))
                resultado = cursor.fetchone() # Obtiene el primer resultado de la consulta 

                if resultado:
                    #si se encuentra un usuario, guarda los datos en la sesión
                    request.session["correo"] = correo 
                    request.session["contrasena"] = contrasena 
                    
                    usuario_id = resultado["Codigo"] # Obtiene el ID del usuario
                    request.session["usuario_id"] = usuario_id #guarda el ID del usuario en la sesión
                    
                    #redirige a la página de menú del usuario
                    return templates.TemplateResponse("Menu_usuario.html",{"request": request,"usuario_id":usuario_id,})
                else:
                    # Si no se encuentra el usuario, muestra un mensaje de error
                    mensaje = "Correo o contraseña incorrectos" 
                    return templates.TemplateResponse("ingreso_usuario.html",{"request": request, "mensaje": mensaje})
        except Exception as e:
            #si hay un error al validar el usuario, muestra un mensaje de error
            mensaje = f"Error al validar usuario: {e}"
            return templates.TemplateResponse("ingreso_usuario.html",{"request": request, "mensaje": mensaje})
        finally:
            close_db_connection(db)# Cierra la conexión a la base de datos
    else:
        # Si no se pudo conectar a la base de datos, muestra un mensaje de error
        return templates.TemplateResponse("ingreso_usuario.html", {"request": request, "mensaje": "Error de conexión a la base de datos"})

# ─────────────────────────────────────────────────────────────
# GESTIÓN DE USUARIOS
# ─────────────────────────────────────────────────────────────

@app.get("/nuevo_ingreso", response_class=HTMLResponse) # Página de registro de usuario
@app.get("/Menu_entrada", response_class=HTMLResponse) # Página de registro de usuario
def mostrar_formulario_usuario(request: Request, mensaje: str = ""):
    return templates.TemplateResponse("Nuevo_Ingreso.html", {"request": request, "mensaje": mensaje})

@app.post("/Menu_entrada", response_class=HTMLResponse) # Ruta para guardar el usuario (registro)
def guardar_usuario(
    request: Request,# Objeto de la petición HTTP
    Nombre: str = Form(...),# Obtiene el nombre del formulario
    Apellido: str = Form(...),# Obtiene el apellido del formulario
    correo: str = Form(...),# Obtiene el correo del formulario
    contrasena: str = Form(...),# Obtiene la contraseña del formulario
    Codigo: str = Form(...)# Obtiene el ID del formulario
):
    db = get_db_connection() # Conexión a la base de datos
    if db: 
        try:
            with db.cursor() as cursor:
                 # Consulta SQL para insertar un nuevo usuario
                sql = """
                    INSERT INTO usuario (Codigo, Nombre, Apellido, correo, contrasena)
                    VALUES (%s, %s, %s, %s, %s) 
                """
                # Ejecuta la consulta con los datos del formulario
                cursor.execute(sql, (Codigo, Nombre, Apellido, correo, contrasena))
                db.commit()  # Guarda los cambios en la base de datos
                request.session["usuario_id"] = Codigo #Guarda el ID del usuario en la sesión
            mensaje = "Usuario guardado con éxito"
        except Exception as e:
            #Si hay un error al guardar el usuario, muestra un mensaje de error
            mensaje = f"Error al guardar: {e}"
            return templates.TemplateResponse("Nuevo_Ingreso.html", {"request": request, "mensaje": mensaje})
        finally:
            close_db_connection(db)

        #if Codigo == "10A34":
            #return RedirectResponse(url="/Panel_Administrador", status_code=303)# Página de administrador
        #else:
            return templates.TemplateResponse("Menu_usuario.html", {"request": request, "mensaje": mensaje})
    else:
        # Si no se pudo conectar a la base de datos, muestra un mensaje de error
        return templates.TemplateResponse("Nuevo_Ingreso.html", {"request": request, "mensaje": "Error de conexión a la base de datos"})

# ─────────────────────────────────────────────────────────────
# INGRESO DE PACIENTES
# ─────────────────────────────────────────────────────────────

@app.get("/crear_cita", response_class=HTMLResponse)# Página de creación de cita
def redirigir_a_crear_cita(request: Request):
    usuario_id = request.session.get("usuario_id")# Obtiene el ID del usuario de la sesión
    if not usuario_id:# Si no hay un usuario autenticado, redirige a la página de inicio
        return RedirectResponse(url="/", status_code=303)# Página de inicio
        
    db = get_db_connection()# Conexión a la base de datos
    doctores = []# Lista de doctores
    if db:# Si se pudo conectar a la base de datos
        try:
            with db.cursor() as cursor:# Crea un cursor para ejecutar consultas
                cursor.execute("SELECT Nombre_completo, Especialidad, Telefono, Correo, Academia FROM fisioterapeuta")# Consulta SQL para obtener la lista de doctores
                doctores = cursor.fetchall()# Obtiene la lista de doctores
        finally:
            close_db_connection(db)# Cierra la conexión a la base de datos
    return templates.TemplateResponse("Ingreso_Paciente.html", {# Página de creación de cita
        "request": request,# Página de creación de cita
        "doctores": doctores,# Lista de doctores
        "usuario_id": usuario_id# Obtiene el ID del usuario de la sesión
    })

@app.post("/ingreso_paciente")# Ruta para guardar el paciente (registro)
def ingresar_paciente(# Página de creación de cita
    request: Request,# Objeto de la petición HTTP
    id: str = Form(...),# Obtiene el ID del formulario
    nombre: str = Form(...),# Obtiene el nombre del formulario
    apellido: str = Form(...),# Obtiene el apellido del formulario
    fecha_nacimiento: str = Form(...),# Obtiene la fecha de nacimiento del formulario
    sexo: str = Form(...),# Obtiene el sexo del formulario
    direccion: str = Form(...),# Obtiene la dirección del formulario
    telefono: str = Form(...),# Obtiene el teléfono del formulario
    correo: str = Form(...),# Obtiene el correo del formulario
    razon_cita: str = Form(...),# Obtiene la razón de la cita del formulario
    doctor_en_cargo: str = Form(...),# Obtiene el doctor a cargo del formulario
    fecha_cita: str = Form(...),# Obtiene la fecha de la cita del formulario
    hora_cita: str = Form(...),# Obtiene la hora de la cita del formulario

    cedula_acudiente: str = Form(None),# Obtiene la cédula del acudiente del formulario
    nombre_acudiente: str = Form(None),# Obtiene el nombre del acudiente del formulario
    apellido_acudiente: str = Form(None),# Obtiene el apellido del acudiente del formulario
    direccion_acudiente: str = Form(None),# Obtiene la dirección del acudiente del formulario
    telefono_acudiente: str = Form(None)# Obtiene el teléfono del acudiente del formulario
):
    usuario_id = request.session.get("usuario_id")# Obtiene el ID del usuario de la sesión
    if not usuario_id: # Si no hay un usuario autenticado, redirige a la página de inicio
        return HTMLResponse("No tienes permiso para registrar con este ID.", status_code=403)

    db = get_db_connection()# Conexión a la base de datos
    if db:# Si se pudo conectar a la base de datos
        try:
            with db.cursor() as cursor:# Crea un cursor para ejecutar consultas
                # Consulta SQL para insertar un nuevo paciente
                # Se insertan los datos del paciente en la tabla paciente
                sql_paciente = """
                    INSERT INTO paciente
                    (ID, Nombre, Apellido, Fecha_Nacimiento, Sexo, Direccion, Telefono, Correo, 
                    Razon_cita, Doctor_En_Cargo, Fecha_Cita, Hora_Cita)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                #" Se ejecuta la consulta con los datos del formulario
                # Se insertan los datos del paciente en la tabla paciente
                cursor.execute(sql_paciente, (
                    id, nombre, apellido, fecha_nacimiento, sexo, direccion, telefono, correo,
                    razon_cita, doctor_en_cargo, fecha_cita, hora_cita
                ))# Se guardan los cambios en la base de datos

                if cedula_acudiente and nombre_acudiente:# Si se proporciona la cédula y el nombre del acudiente
                    # Se inserta el acudiente en la tabla acudiente
                    # Se insertan los datos del acudiente en la tabla acudiente
                    sql_acudiente = """
                        INSERT INTO acudiente 
                        (Cedula_acudiente, Nombre, Apellido, Direccion, Telefono, Paciente_ID)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """
                    # Se ejecuta la consulta con los datos del formulario
                    cursor.execute(sql_acudiente, (
                        cedula_acudiente, nombre_acudiente, apellido_acudiente,
                        direccion_acudiente, telefono_acudiente, id
                    ))
                    # Se actualiza el ID del acudiente en la tabla paciente
                    sql_update = """
                        UPDATE paciente SET Acudiente_ID = %s WHERE ID = %s
                    """
                    # Se ejecuta la consulta con los datos del formulario
                    # Se actualiza el ID del acudiente en la tabla paciente
                    cursor.execute(sql_update, (cedula_acudiente, id))
                # Se guardan los cambios en la base de datos
                db.commit()
                # Se muestra un mensaje de éxito
                mensaje = "Paciente y acudiente registrados correctamente" if cedula_acudiente else "Paciente registrado con éxito"
        except Exception as e:# Si hay un error al guardar el paciente, muestra un mensaje de error
            mensaje = f"Error al guardar: {e}"
        finally:
            close_db_connection(db)# Cierra la conexión a la base de datos
        # Se redirige a la página de ingreso de paciente
        return templates.TemplateResponse("Ingreso_Paciente.html", {"request": request, "mensaje": mensaje, "doctores": []})
    else:
        # Si no se pudo conectar a la base de datos, muestra un mensaje de error
        return templates.TemplateResponse("Ingreso_Paciente.html", {"request": request, "mensaje": "Error de conexión a la base de datos", "doctores": []})

@app.get("/asignar_servicio", response_class=HTMLResponse)# Página de asignación de servicio
def solicitar_id_paciente(request: Request, codigo_servicio: str):# Obtiene el ID del paciente de la URL
    return templates.TemplateResponse("Asignar_Servicio.html", {# Página de asignación de servicio
        "request": request,# Página de asignación de servicio
        "codigo_servicio": codigo_servicio# Página de asignación de servicio
    })
@app.post("/asignar_servicio", response_class=HTMLResponse)# Ruta para asignar el servicio al paciente
def guardar_servicio_en_paciente(# Página de asignación de servicio
    request: Request,# Objeto de la petición HTTP
    codigo_servicio: str = Form(...),# Obtiene el código del servicio del formulario
    id_paciente: str = Form(...)# Obtiene el ID del paciente del formulario
):
    usuario_id = request.session.get("usuario_id")# Obtiene el ID del usuario de la sesión
    if not usuario_id:  # Si no hay un usuario autenticado, redirige a la página de inicio
        return templates.TemplateResponse("error.html", {"request": request,"mensaje": "No hay un usuario autenticado."})
    
    db = get_db_connection()# Conexión a la base de datos
    if db:# Si se pudo conectar a la base de datos
        try:
            with db.cursor() as cursor:# Crea un cursor para ejecutar consultas
                # Consulta SQL para asignar el servicio al paciente
                sql = "UPDATE paciente SET Servicio = %s WHERE ID = %s"
                cursor.execute(sql, (codigo_servicio, id_paciente))# Se ejecuta la consulta con los datos del formulario
                db.commit()# Se guardan los cambios en la base de datos
            mensaje = "Servicio asignado correctamente"# Se muestra un mensaje de éxito
        except Exception as e:#" Si hay un error al asignar el servicio, muestra un mensaje de error
            mensaje = f"Error al asignar servicio: {e}"
        finally:
            close_db_connection(db)# Cierra la conexión a la base de datos
        return templates.TemplateResponse("Servicios.html", {"request": request,"mensaje": mensaje})# Página de asignación de servicio
    else:
        # Si no se pudo conectar a la base de datos, muestra un mensaje de error
        return templates.TemplateResponse("Servicios.html", {"request": request,"mensaje": "Error de conexión a la base de datos"})
# ─────────────────────────────────────────────────────────────
# PANEL DE ADMINISTRADOR
# ─────────────────────────────────────────────────────────────

@app.get("/admin_access", response_class=HTMLResponse)# Página de acceso al administrador
def formulario_admin(request: Request):#
    return templates.TemplateResponse("Admin_Login.html", {"request": request})#

@app.post("/admin_access", response_class=HTMLResponse)# Ruta para validar el acceso del administrador
def acceso_admin(request: Request, Codigo: str = Form(...)):# Obtiene el código del formulario
    if Codigo == "10A34":# Si el código es correcto
        request.session["usuario_id"] = Codigo# Guarda el ID del usuario en la sesión
        return RedirectResponse(url="/Panel_Administrador", status_code=303)## Redirige a la página de administrador
    return templates.TemplateResponse("Admin_Login.html", {"request": request, "mensaje": "Código incorrecto"})

@app.get("/Panel_Administrador", response_class=HTMLResponse)# Página de administrador
def panel_admin(request: Request):
    db = get_db_connection()# Conexión a la base de datos
    pacientes = []# Lista de pacientes
    if db:# Si se pudo conectar a la base de datos
        try:
            with db.cursor() as cursor:# Crea un cursor para ejecutar consultas
                cursor.execute("SELECT * FROM paciente") # Consulta SQL para obtener la lista de pacientes
                pacientes = cursor.fetchall()# Obtiene la lista de pacientes
        finally:
            close_db_connection(db)# Cierra la conexión a la base de datos
    # Si no se pudo conectar a la base de datos, muestra un mensaje de error
    return templates.TemplateResponse("Panel_Administrador.html", {"request": request, "pacientes": pacientes})

@app.post("/editar_paciente")# Ruta para editar el paciente
def editar_paciente(# Página de edición de paciente
    request: Request,# Objeto de la petición HTTP
    id: str = Form(...),#  Obtiene el ID del formulario
    nombre: str = Form(...),# Obtiene el nombre del formulario
    apellido: str = Form(...),# Obtiene el apellido del formulario
    fecha_nacimiento: str = Form(...),# Obtiene la fecha de nacimiento del formulario
    sexo: str = Form(...),# Obtiene el sexo del formulario
    direccion: str = Form(...),# Obtiene la dirección del formulario
    telefono: str = Form(...),# Obtiene el teléfono del formulario
    correo: str = Form(...),# Obtiene el correo del formulario
    razon_cita: str = Form(...),# Obtiene la razón de la cita del formulario
    doctor: str = Form(...),# Obtiene el doctor a cargo del formulario
    fecha_cita: str = Form(...),# Obtiene la fecha de la cita del formulario
    hora_cita: str = Form(...),# Obtiene la hora de la cita del formulario
    estado: str = Form(...)# Obtiene el estado del formulario
):
    db = get_db_connection()# Conexión a la base de datos
    if db:# Si se pudo conectar a la base de datos
        try:
            with db.cursor() as cursor:# Crea un cursor para ejecutar consultas
                # Consulta SQL para actualizar el paciente
                sql = """
                UPDATE paciente SET 
                    Nombre=%s, Apellido=%s, Fecha_nacimiento=%s, Sexo=%s, 
                    Direccion=%s, Telefono=%s, Correo=%s, Razon_cita=%s,
                    Doctor_En_Cargo=%s, Fecha_Cita=%s, Hora_Cita=%s, Estado=%s
                WHERE ID=%s
                """
                # Se ejecuta la consulta con los datos del formulario
                cursor.execute(sql, (nombre, apellido, fecha_nacimiento, sexo,
                                     direccion, telefono, correo, razon_cita,
                                     doctor, fecha_cita, hora_cita, estado, id))
                db.commit()# Se guardan los cambios en la base de datos
        finally:
            close_db_connection(db)# Cierra la conexión a la base de datos
    # Se redirige a la página de administrador
    return RedirectResponse(url="/Panel_Administrador", status_code=303)

@app.post("/eliminar_paciente")# Ruta para eliminar el paciente
def eliminar_paciente(id: str = Form(...)):# Obtiene el ID del formulario
    db = get_db_connection()# Conexión a la base de datos
    if db:# Si se pudo conectar a la base de datos
        try:
            with db.cursor() as cursor:# Crea un cursor para ejecutar consultas
                # Consulta SQL para eliminar el paciente
                cursor.execute("DELETE FROM paciente WHERE ID = %s", (id,))
                db.commit()# Se guardan los cambios en la base de datos
        finally:
            close_db_connection(db)# Cierra la conexión a la base de datos
    # Se redirige a la página de administrador
    return RedirectResponse(url="/Panel_Administrador", status_code=303)
