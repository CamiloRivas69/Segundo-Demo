from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from Conexion_BD import get_db_connection, close_db_connection

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="mi_clave_ultra_secreta_123456")

templates = Jinja2Templates(directory="../frontend")

# ─────────────────────────────────────────────────────────────
# RUTAS GENERALES
# ─────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
def pagina_inicio(request: Request):
    return templates.TemplateResponse("Inicio.html", {"request": request})

@app.get("/menu", response_class=HTMLResponse)
def mostrar_bienvenida(request: Request):
    return templates.TemplateResponse("Menu_usuario.html", {"request": request})

@app.get("/servicios", response_class=HTMLResponse)
def mostrar_bienvenida(request: Request):
    return templates.TemplateResponse("Servicios.html", {"request": request})


# ─────────────────────────────────────────────────────────────
# GESTIÓN DE USUARIOS
# ─────────────────────────────────────────────────────────────

@app.get("/nuevo_ingreso", response_class=HTMLResponse)
@app.get("/Menu_entrada", response_class=HTMLResponse)
def mostrar_formulario_usuario(request: Request, mensaje: str = ""):
    return templates.TemplateResponse("Nuevo_Ingreso.html", {"request": request, "mensaje": mensaje})

@app.post("/Menu_entrada", response_class=HTMLResponse)
def guardar_usuario(
    request: Request,
    Nombre: str = Form(...),
    Apellido: str = Form(...),
    Correo: str = Form(...),
    Contrasena: str = Form(...),
    Codigo: str = Form(...)
):
    db = get_db_connection()
    if db:
        try:
            with db.cursor() as cursor:
                sql = """
                    INSERT INTO usuario (Codigo, Nombre, Apellido, Correo, Contraseña)
                    VALUES (%s, %s, %s, %s, %s)
                """
                cursor.execute(sql, (Codigo, Nombre, Apellido, Correo, Contrasena))
                db.commit()
                request.session["usuario_id"] = Codigo  
            mensaje = "Usuario guardado con éxito"
        except Exception as e:
            mensaje = f"Error al guardar: {e}"
            return templates.TemplateResponse("Nuevo_Ingreso.html", {"request": request, "mensaje": mensaje})
        finally:
            close_db_connection(db)

        if Codigo == "10A34":
            return RedirectResponse(url="/Panel_Administrador", status_code=303)
        else:
            return templates.TemplateResponse("Menu_usuario.html", {"request": request, "mensaje": mensaje})
    else:
        return templates.TemplateResponse("Nuevo_Ingreso.html", {"request": request, "mensaje": "Error de conexión a la base de datos"})

# ─────────────────────────────────────────────────────────────
# INGRESO DE PACIENTES
# ─────────────────────────────────────────────────────────────

@app.get("/crear_cita", response_class=HTMLResponse)
def redirigir_a_crear_cita(request: Request):
    usuario_id = request.session.get("usuario_id")
    if not usuario_id:
        return RedirectResponse(url="/", status_code=303)

    db = get_db_connection()
    doctores = []
    if db:
        try:
            with db.cursor() as cursor:
                cursor.execute("SELECT Nombre_completo, Especialidad, Telefono, Correo, Academia FROM fisioterapeuta")
                doctores = cursor.fetchall()
        finally:
            close_db_connection(db)
    return templates.TemplateResponse("Ingreso_Paciente.html", {
        "request": request,
        "doctores": doctores,
        "usuario_id": usuario_id
    })

@app.post("/ingreso_paciente")
def ingresar_paciente(
    request: Request,
    id: str = Form(...),
    nombre: str = Form(...),
    apellido: str = Form(...),
    fecha_nacimiento: str = Form(...),
    sexo: str = Form(...),
    direccion: str = Form(...),
    telefono: str = Form(...),
    correo: str = Form(...),
    razon_cita: str = Form(...),
    doctor_en_cargo: str = Form(...),
    fecha_cita: str = Form(...),
    hora_cita: str = Form(...),

    cedula_acudiente: str = Form(None),
    nombre_acudiente: str = Form(None),
    apellido_acudiente: str = Form(None),
    direccion_acudiente: str = Form(None),
    telefono_acudiente: str = Form(None)
):
    usuario_id = request.session.get("usuario_id")
    if not usuario_id or id != usuario_id:
        return HTMLResponse("No tienes permiso para registrar con este ID.", status_code=403)

    db = get_db_connection()
    if db:
        try:
            with db.cursor() as cursor:
                sql_paciente = """
                    INSERT INTO paciente 
                    (ID, Nombre, Apellido, Fecha_Nacimiento, Sexo, Direccion, Telefono, Correo, 
                    Razon_cita, Doctor_En_Cargo, Fecha_Cita, Hora_Cita)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(sql_paciente, (
                    id, nombre, apellido, fecha_nacimiento, sexo, direccion, telefono, correo,
                    razon_cita, doctor_en_cargo, fecha_cita, hora_cita
                ))

                if cedula_acudiente and nombre_acudiente:
                    sql_acudiente = """
                        INSERT INTO acudiente 
                        (Cedula_acudiente, Nombre, Apellido, Direccion, Telefono, Paciente_ID)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """
                    cursor.execute(sql_acudiente, (
                        cedula_acudiente, nombre_acudiente, apellido_acudiente,
                        direccion_acudiente, telefono_acudiente, id
                    ))

                    sql_update = """
                        UPDATE paciente SET Acudiente_ID = %s WHERE ID = %s
                    """
                    cursor.execute(sql_update, (cedula_acudiente, id))

                db.commit()
                mensaje = "Paciente y acudiente registrados correctamente" if cedula_acudiente else "Paciente registrado con éxito"
        except Exception as e:
            mensaje = f"Error al guardar: {e}"
        finally:
            close_db_connection(db)

        return templates.TemplateResponse("Ingreso_Paciente.html", {"request": request, "mensaje": mensaje, "doctores": []})
    else:
        return templates.TemplateResponse("Ingreso_Paciente.html", {"request": request, "mensaje": "Error de conexión a la base de datos", "doctores": []})

@app.get("/asignar_servicio", response_class=HTMLResponse)
def solicitar_id_paciente(request: Request, codigo_servicio: str):
    return templates.TemplateResponse("Asignar_Servicio.html", {
        "request": request,
        "codigo_servicio": codigo_servicio
    })
@app.post("/asignar_servicio", response_class=HTMLResponse)
def guardar_servicio_en_paciente(
    request: Request,
    codigo_servicio: str = Form(...),
    id_paciente: str = Form(...)
):
    db = get_db_connection()
    if db:
        try:
            with db.cursor() as cursor:
                sql = "UPDATE paciente SET Servicio = %s WHERE ID = %s"
                cursor.execute(sql, (codigo_servicio, id_paciente))
                db.commit()
            mensaje = "Servicio asignado correctamente"
        except Exception as e:
            mensaje = f"Error al asignar servicio: {e}"
        finally:
            close_db_connection(db)
        return templates.TemplateResponse("Servicios.html", {
            "request": request,
            "mensaje": mensaje
        })
    else:
        return templates.TemplateResponse("Servicios.html", {
            "request": request,
            "mensaje": "Error de conexión a la base de datos"
        })

# ─────────────────────────────────────────────────────────────
# PANEL DE ADMINISTRADOR
# ─────────────────────────────────────────────────────────────

@app.get("/admin_access", response_class=HTMLResponse)
def formulario_admin(request: Request):
    return templates.TemplateResponse("Admin_Login.html", {"request": request})

@app.post("/admin_access", response_class=HTMLResponse)
def acceso_admin(request: Request, Codigo: str = Form(...)):
    if Codigo == "10A34":
        request.session["usuario_id"] = Codigo
        return RedirectResponse(url="/Panel_Administrador", status_code=303)
    return templates.TemplateResponse("Admin_Login.html", {"request": request, "mensaje": "Código incorrecto"})

@app.get("/Panel_Administrador", response_class=HTMLResponse)
def panel_admin(request: Request):
    db = get_db_connection()
    pacientes = []
    if db:
        try:
            with db.cursor() as cursor:
                cursor.execute("SELECT * FROM paciente")
                pacientes = cursor.fetchall()
        finally:
            close_db_connection(db)
    return templates.TemplateResponse("Panel_Administrador.html", {"request": request, "pacientes": pacientes})

@app.post("/editar_paciente")
def editar_paciente(
    request: Request,
    id: str = Form(...),
    nombre: str = Form(...),
    apellido: str = Form(...),
    fecha_nacimiento: str = Form(...),
    sexo: str = Form(...),
    direccion: str = Form(...),
    telefono: str = Form(...),
    correo: str = Form(...),
    razon_cita: str = Form(...),
    doctor: str = Form(...),
    fecha_cita: str = Form(...),
    hora_cita: str = Form(...),
    estado: str = Form(...)
):
    db = get_db_connection()
    if db:
        try:
            with db.cursor() as cursor:
                sql = """
                UPDATE paciente SET 
                    Nombre=%s, Apellido=%s, Fecha_nacimiento=%s, Sexo=%s, 
                    Direccion=%s, Telefono=%s, Correo=%s, Razon_cita=%s,
                    Doctor_En_Cargo=%s, Fecha_Cita=%s, Hora_Cita=%s, Estado=%s
                WHERE ID=%s
                """
                cursor.execute(sql, (nombre, apellido, fecha_nacimiento, sexo,
                                     direccion, telefono, correo, razon_cita,
                                     doctor, fecha_cita, hora_cita, estado, id))
                db.commit()
        finally:
            close_db_connection(db)
    return RedirectResponse(url="/Panel_Administrador", status_code=303)

@app.post("/eliminar_paciente")
def eliminar_paciente(id: str = Form(...)):
    db = get_db_connection()
    if db:
        try:
            with db.cursor() as cursor:
                cursor.execute("DELETE FROM paciente WHERE ID = %s", (id,))
                db.commit()
        finally:
            close_db_connection(db)
    return RedirectResponse(url="/Panel_Administrador", status_code=303)
