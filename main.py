import json
import os
import re
import tkinter as tk
from tkinter import ttk, messagebox


CARPETA_PROYECTO = os.path.dirname(os.path.abspath(__file__))
ARCHIVO_CONTACTOS = os.path.join(
    CARPETA_PROYECTO,
    "contactos.json"
)

contactos = []
id_contacto_edicion = None


def cargar_contactos():
    if not os.path.exists(ARCHIVO_CONTACTOS):
        return []

    try:
        with open(
            ARCHIVO_CONTACTOS,
            "r",
            encoding="utf-8"
        ) as archivo:
            datos = json.load(archivo)

        if not isinstance(datos, list):
            return []

        contactos_cargados = []

        for indice, contacto in enumerate(datos, start=1):
            if not isinstance(contacto, dict):
                continue

            contactos_cargados.append({
                "id": contacto.get("id", indice),
                "nombre": contacto.get("nombre", ""),
                "telefono": contacto.get("telefono", ""),
                "correo": contacto.get("correo", "")
            })

        return contactos_cargados

    except (json.JSONDecodeError, OSError):
        messagebox.showerror(
            "Error",
            "No se pudieron cargar los contactos."
        )
        return []


def guardar_contactos():
    try:
        with open(
            ARCHIVO_CONTACTOS,
            "w",
            encoding="utf-8"
        ) as archivo:
            json.dump(
                contactos,
                archivo,
                ensure_ascii=False,
                indent=4
            )

        return True

    except OSError:
        messagebox.showerror(
            "Error",
            "No se pudieron guardar los contactos."
        )
        return False


def generar_nuevo_id():
    if not contactos:
        return 1

    return max(contacto["id"] for contacto in contactos) + 1


def actualizar_tabla(lista_contactos=None):
    if lista_contactos is None:
        lista_contactos = contactos

    for elemento in tabla.get_children():
        tabla.delete(elemento)

    for contacto in lista_contactos:
        tabla.insert(
            "",
            tk.END,
            iid=str(contacto["id"]),
            values=(
                contacto["nombre"],
                contacto["telefono"],
                contacto["correo"]
            )
        )

    etiqueta_resultados.config(
        text=f"Contactos mostrados: {len(lista_contactos)}"
    )


def limpiar_campos():
    global id_contacto_edicion

    entrada_nombre.delete(0, tk.END)
    entrada_telefono.delete(0, tk.END)
    entrada_correo.delete(0, tk.END)

    id_contacto_edicion = None
    boton_guardar.config(text="Guardar contacto")

    for elemento in tabla.selection():
        tabla.selection_remove(elemento)

    entrada_nombre.focus()


def correo_valido(correo):
    patron = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return re.match(patron, correo) is not None


def telefono_valido(telefono):
    telefono_limpio = (
        telefono
        .replace(" ", "")
        .replace("-", "")
        .replace("(", "")
        .replace(")", "")
        .replace("+", "")
    )

    return telefono_limpio.isdigit() and len(telefono_limpio) >= 7


def contacto_duplicado(telefono, correo, id_ignorar=None):
    for contacto in contactos:
        if contacto["id"] == id_ignorar:
            continue

        mismo_telefono = (
            contacto["telefono"].lower() == telefono.lower()
        )

        mismo_correo = (
            contacto["correo"].lower() == correo.lower()
        )

        if mismo_telefono or mismo_correo:
            return True

    return False


def obtener_datos_formulario():
    nombre = entrada_nombre.get().strip()
    telefono = entrada_telefono.get().strip()
    correo = entrada_correo.get().strip().lower()

    if nombre == "" or telefono == "" or correo == "":
        messagebox.showwarning(
            "Datos incompletos",
            "Debes llenar todos los campos."
        )
        return None

    if not telefono_valido(telefono):
        messagebox.showwarning(
            "Teléfono inválido",
            "Escribe un teléfono válido de al menos 7 números."
        )
        return None

    if not correo_valido(correo):
        messagebox.showwarning(
            "Correo inválido",
            "Escribe un correo válido, por ejemplo: nombre@gmail.com"
        )
        return None

    if contacto_duplicado(
        telefono,
        correo,
        id_contacto_edicion
    ):
        messagebox.showwarning(
            "Contacto duplicado",
            "Ya existe un contacto con ese teléfono o correo."
        )
        return None

    return {
        "nombre": nombre,
        "telefono": telefono,
        "correo": correo
    }


def guardar_contacto():
    global id_contacto_edicion

    datos = obtener_datos_formulario()

    if datos is None:
        return

    if id_contacto_edicion is None:
        nuevo_contacto = {
            "id": generar_nuevo_id(),
            "nombre": datos["nombre"],
            "telefono": datos["telefono"],
            "correo": datos["correo"]
        }

        contactos.append(nuevo_contacto)

        titulo_mensaje = "Contacto guardado"
        mensaje = "El contacto se registró correctamente."

    else:
        contacto_encontrado = buscar_contacto_por_id(
            id_contacto_edicion
        )

        if contacto_encontrado is None:
            messagebox.showerror(
                "Error",
                "No se encontró el contacto que quieres editar."
            )
            return

        contacto_encontrado["nombre"] = datos["nombre"]
        contacto_encontrado["telefono"] = datos["telefono"]
        contacto_encontrado["correo"] = datos["correo"]

        titulo_mensaje = "Contacto actualizado"
        mensaje = "El contacto se actualizó correctamente."

    if not guardar_contactos():
        return

    mostrar_todos()
    limpiar_campos()

    messagebox.showinfo(
        titulo_mensaje,
        mensaje
    )


def buscar_contacto_por_id(id_contacto):
    for contacto in contactos:
        if contacto["id"] == id_contacto:
            return contacto

    return None


def cargar_contacto_para_editar():
    global id_contacto_edicion

    seleccionado = tabla.selection()

    if not seleccionado:
        messagebox.showwarning(
            "Sin selección",
            "Primero selecciona un contacto de la tabla."
        )
        return

    id_contacto_edicion = int(seleccionado[0])

    contacto = buscar_contacto_por_id(
        id_contacto_edicion
    )

    if contacto is None:
        messagebox.showerror(
            "Error",
            "No se encontró el contacto seleccionado."
        )
        return

    entrada_nombre.delete(0, tk.END)
    entrada_telefono.delete(0, tk.END)
    entrada_correo.delete(0, tk.END)

    entrada_nombre.insert(
        0,
        contacto["nombre"]
    )

    entrada_telefono.insert(
        0,
        contacto["telefono"]
    )

    entrada_correo.insert(
        0,
        contacto["correo"]
    )

    boton_guardar.config(
        text="Guardar cambios"
    )

    entrada_nombre.focus()


def eliminar_contacto():
    seleccionado = tabla.selection()

    if not seleccionado:
        messagebox.showwarning(
            "Sin selección",
            "Primero selecciona un contacto de la tabla."
        )
        return

    id_contacto = int(seleccionado[0])
    contacto = buscar_contacto_por_id(id_contacto)

    if contacto is None:
        messagebox.showerror(
            "Error",
            "No se encontró el contacto seleccionado."
        )
        return

    confirmar = messagebox.askyesno(
        "Confirmar eliminación",
        f"¿Seguro que quieres eliminar a {contacto['nombre']}?"
    )

    if not confirmar:
        return

    contactos.remove(contacto)

    if not guardar_contactos():
        return

    mostrar_todos()
    limpiar_campos()

    messagebox.showinfo(
        "Contacto eliminado",
        "El contacto se eliminó correctamente."
    )


def buscar_contactos():
    texto = entrada_busqueda.get().strip().lower()

    if texto == "":
        messagebox.showwarning(
            "Búsqueda vacía",
            "Escribe un nombre, teléfono o correo para buscar."
        )
        return

    resultados = []

    for contacto in contactos:
        nombre = contacto["nombre"].lower()
        telefono = contacto["telefono"].lower()
        correo = contacto["correo"].lower()

        if (
            texto in nombre
            or texto in telefono
            or texto in correo
        ):
            resultados.append(contacto)

    actualizar_tabla(resultados)

    if not resultados:
        messagebox.showinfo(
            "Sin resultados",
            "No se encontraron contactos."
        )


def mostrar_todos():
    entrada_busqueda.delete(0, tk.END)
    actualizar_tabla(contactos)


def buscar_al_escribir(evento=None):
    texto = entrada_busqueda.get().strip().lower()

    if texto == "":
        actualizar_tabla(contactos)
        return

    resultados = []

    for contacto in contactos:
        if (
            texto in contacto["nombre"].lower()
            or texto in contacto["telefono"].lower()
            or texto in contacto["correo"].lower()
        ):
            resultados.append(contacto)

    actualizar_tabla(resultados)


def seleccionar_con_doble_clic(evento=None):
    if tabla.selection():
        cargar_contacto_para_editar()


contactos = cargar_contactos()


ventana = tk.Tk()
ventana.title("Agenda de contactos")
ventana.geometry("900x650")
ventana.resizable(False, False)

titulo = tk.Label(
    ventana,
    text="Agenda de contactos",
    font=("Arial", 24, "bold")
)
titulo.pack(pady=15)


marco_busqueda = tk.LabelFrame(
    ventana,
    text="Buscar contacto",
    padx=10,
    pady=10
)
marco_busqueda.pack(
    padx=20,
    pady=5,
    fill="x"
)

entrada_busqueda = tk.Entry(
    marco_busqueda,
    width=45
)
entrada_busqueda.grid(
    row=0,
    column=0,
    padx=5
)

boton_buscar = tk.Button(
    marco_busqueda,
    text="Buscar",
    width=14,
    command=buscar_contactos
)
boton_buscar.grid(
    row=0,
    column=1,
    padx=5
)

boton_mostrar_todos = tk.Button(
    marco_busqueda,
    text="Mostrar todos",
    width=14,
    command=mostrar_todos
)
boton_mostrar_todos.grid(
    row=0,
    column=2,
    padx=5
)

entrada_busqueda.bind(
    "<KeyRelease>",
    buscar_al_escribir
)


marco_formulario = tk.LabelFrame(
    ventana,
    text="Datos del contacto",
    padx=15,
    pady=10
)
marco_formulario.pack(
    padx=20,
    pady=10
)

tk.Label(
    marco_formulario,
    text="Nombre:"
).grid(
    row=0,
    column=0,
    padx=10,
    pady=8,
    sticky="e"
)

entrada_nombre = tk.Entry(
    marco_formulario,
    width=40
)
entrada_nombre.grid(
    row=0,
    column=1,
    padx=10,
    pady=8
)

tk.Label(
    marco_formulario,
    text="Teléfono:"
).grid(
    row=1,
    column=0,
    padx=10,
    pady=8,
    sticky="e"
)

entrada_telefono = tk.Entry(
    marco_formulario,
    width=40
)
entrada_telefono.grid(
    row=1,
    column=1,
    padx=10,
    pady=8
)

tk.Label(
    marco_formulario,
    text="Correo:"
).grid(
    row=2,
    column=0,
    padx=10,
    pady=8,
    sticky="e"
)

entrada_correo = tk.Entry(
    marco_formulario,
    width=40
)
entrada_correo.grid(
    row=2,
    column=1,
    padx=10,
    pady=8
)


marco_botones = tk.Frame(ventana)
marco_botones.pack(pady=5)

boton_guardar = tk.Button(
    marco_botones,
    text="Guardar contacto",
    width=18,
    command=guardar_contacto
)
boton_guardar.grid(
    row=0,
    column=0,
    padx=5,
    pady=5
)

boton_editar = tk.Button(
    marco_botones,
    text="Editar contacto",
    width=18,
    command=cargar_contacto_para_editar
)
boton_editar.grid(
    row=0,
    column=1,
    padx=5,
    pady=5
)

boton_eliminar = tk.Button(
    marco_botones,
    text="Eliminar contacto",
    width=18,
    command=eliminar_contacto
)
boton_eliminar.grid(
    row=0,
    column=2,
    padx=5,
    pady=5
)

boton_limpiar = tk.Button(
    marco_botones,
    text="Limpiar campos",
    width=18,
    command=limpiar_campos
)
boton_limpiar.grid(
    row=0,
    column=3,
    padx=5,
    pady=5
)


marco_tabla = tk.Frame(ventana)
marco_tabla.pack(
    padx=20,
    pady=10,
    fill="both",
    expand=True
)

columnas = (
    "nombre",
    "telefono",
    "correo"
)

tabla = ttk.Treeview(
    marco_tabla,
    columns=columnas,
    show="headings",
    height=12
)

tabla.heading(
    "nombre",
    text="Nombre"
)

tabla.heading(
    "telefono",
    text="Teléfono"
)

tabla.heading(
    "correo",
    text="Correo"
)

tabla.column(
    "nombre",
    width=260,
    anchor="w"
)

tabla.column(
    "telefono",
    width=180,
    anchor="center"
)

tabla.column(
    "correo",
    width=320,
    anchor="w"
)

barra_vertical = ttk.Scrollbar(
    marco_tabla,
    orient="vertical",
    command=tabla.yview
)

tabla.configure(
    yscrollcommand=barra_vertical.set
)

tabla.pack(
    side="left",
    fill="both",
    expand=True
)

barra_vertical.pack(
    side="right",
    fill="y"
)

tabla.bind(
    "<Double-1>",
    seleccionar_con_doble_clic
)

etiqueta_resultados = tk.Label(
    ventana,
    text="Contactos mostrados: 0"
)
etiqueta_resultados.pack(pady=5)


actualizar_tabla()
entrada_nombre.focus()

ventana.mainloop()