import tkinter as tk
from tkinter import ttk
import psycopg2
import easygui

# Función para ejecutar una consulta SQL en la base de datos
def ejecutar_consulta(tabla):
    try:
        conexion = psycopg2.connect(
            host='localhost',
            database='NotasNur',
            user='postgres',
            password='0204'
        )
        print("Conexión exitosa")
    except Exception as ex:
        print(f"Error de conexión: {ex}")
        return None

    cursor = conexion.cursor()
    cursor.execute(f'SELECT * FROM {tabla}')
    datos = cursor.fetchall()

    # Obtener los nombres de las columnas
    nombres_columnas = [desc[0] for desc in cursor.description]

    conexion.close()

    return nombres_columnas, datos

# Función para mostrar una ventana con los datos de una tabla
def mostrar_cuadro(tabla):
    columnas, datos = ejecutar_consulta(tabla)


    if columnas and datos:
        ventana = tk.Toplevel()
        ventana.title(f'Tabla de {tabla}')

        tree = ttk.Treeview(ventana)
        tree["columns"] = tuple(columnas)

        for col in tree["columns"]:
            tree.heading(col, text=col)
            tree.column(col, anchor="center")

        for dato in datos:
            tree.insert("", "end", values=dato)



        tree.pack()

        ventana.mainloop()
    else:
        easygui.msgbox("No se pudieron obtener datos de la tabla seleccionada.", "Error")

# Función para mostrar una ventana de inserción de datos en una tabla
def mostrar_cuadro_insertar(tabla):
    ventana_insertar = tk.Toplevel()
    ventana_insertar.title(f'Insertar datos en {tabla}')

    nombres_columnas, _ = ejecutar_consulta(tabla)
    etiquetas = []
    entradas = []

    for col in nombres_columnas:
        etiqueta = tk.Label(ventana_insertar, text=col)
        entrada = tk.Entry(ventana_insertar)

        etiquetas.append(etiqueta)
        entradas.append(entrada)

        etiqueta.pack()
        entrada.pack()

    def insertar():
        valores = [entrada.get() for entrada in entradas]
        insertar_datos(tabla, valores)
        ventana_insertar.destroy()

    boton_insertar = tk.Button(ventana_insertar, text='Insertar datos', command=insertar)
    boton_insertar.pack()

# Función para insertar datos en una tabla
def insertar_datos(tabla, valores):
    try:
        conexion = psycopg2.connect(
            host='localhost',
            database='NotasNur',
            user='postgres',
            password='0204'
        )
        cursor = conexion.cursor()

        cadena_insercion = f"INSERT INTO {tabla} VALUES ({', '.join(['%s'] * len(valores))})"

        cursor.execute(cadena_insercion, tuple(valores))
        conexion.commit()
        conexion.close()

        easygui.msgbox("Datos insertados correctamente.", "Resultado")

    except Exception as ex:
        easygui.msgbox(f"Error al insertar datos: {ex}", "Error")

# Función para mostrar una ventana de actualización de datos en una tabla
def mostrar_cuadro_actualizar(tabla):
    columnas, datos = ejecutar_consulta(tabla)

    if columnas and datos:
        ventana = tk.Tk()
        ventana.title(f'Tabla de {tabla}')

        tree = ttk.Treeview(ventana)
        tree["columns"] = tuple(columnas)

        for col in tree["columns"]:
            tree.heading(col, text=col)
            tree.column(col, anchor="center")

        for dato in datos:
            tree.insert("", "end", values=dato)

        tree.pack()

        tree.bind("<ButtonRelease-1>", lambda event, t=tree, tabla=tabla: obtener_datos_seleccionados(event, t, tabla))

        ventana.mainloop()
    else:
        easygui.msgbox("No se pudieron obtener datos de la tabla seleccionada.", "Error")

# Función para obtener los datos seleccionados en el Treeview
def obtener_datos_seleccionados(event, tree, tabla):
    item = tree.focus()

    if item:
        valores_seleccionados = tree.item(item, "values")
        if valores_seleccionados:
            mostrar_cuadro_actualizar_ventana(tabla, tree, item, valores_seleccionados)
    else:
        easygui.msgbox("Selecciona una fila para actualizar.", "Error")

# Función para mostrar una ventana de actualización de datos específicos en una tabla
def mostrar_cuadro_actualizar_ventana(tabla, tree, item, valores):
    ventana_actualizar = tk.Toplevel()
    ventana_actualizar.title(f'Actualizar datos en {tabla}')

    etiquetas = []
    entradas = []

    for col, valor in zip(tree["columns"], valores):
        etiqueta = tk.Label(ventana_actualizar, text=col)
        entrada = tk.Entry(ventana_actualizar)
        entrada.insert(0, str(valor))

        etiquetas.append(etiqueta)
        entradas.append(entrada)

        etiqueta.pack()
        entrada.pack()

    def actualizar():
        nuevos_valores = [entrada.get() for entrada in entradas]
        actualizar_datos(tabla, tree, item, nuevos_valores, ventana_actualizar)

    boton_actualizar = tk.Button(ventana_actualizar, text='Actualizar datos', command=actualizar)
    boton_actualizar.pack()

# Función para actualizar datos en una tabla
def actualizar_datos(tabla, tree, item, nuevos_valores, ventana_actualizar):
    id_seleccionado = tree.item(item, "values")[0]

    try:
        conexion = psycopg2.connect(
            host='localhost',
            database='NotasNur',
            user='postgres',
            password='0204'
        )
        cursor = conexion.cursor()

        cadena_actualizacion = f"UPDATE {tabla} SET {', '.join([f'{col} = %s' for col in tree['columns']])} WHERE id = %s"

        nuevos_valores.append(id_seleccionado)

        cursor.execute(cadena_actualizacion, tuple(nuevos_valores))
        conexion.commit()
        conexion.close()

        easygui.msgbox("Datos actualizados correctamente.", "Resultado")

        # Actualiza la fila en el Treeview
        tree.item(item, values=nuevos_valores[:-1])
        ventana_actualizar.destroy()

    except Exception as ex:
        easygui.msgbox(f"Error al actualizar datos: {ex}", "Error")

# Función para mostrar una ventana de eliminación de datos en una tabla
def mostrar_cuadro_eliminar(tabla):
    ventana_eliminar = tk.Toplevel()
    ventana_eliminar.title(f'Eliminar datos en {tabla}')

    etiqueta_id = tk.Label(ventana_eliminar, text="ID a eliminar:")
    entrada_id = tk.Entry(ventana_eliminar)
    etiqueta_id.pack()
    entrada_id.pack()

    def eliminar():
        id_eliminar = entrada_id.get()
        eliminar_datos(tabla, id_eliminar)
        ventana_eliminar.destroy()

    boton_eliminar = tk.Button(ventana_eliminar, text='Eliminar datos', command=eliminar)
    boton_eliminar.pack()

# Función para eliminar datos de una tabla
def eliminar_datos(tabla, id_eliminar):
    try:
        conexion = psycopg2.connect(
            host='localhost',
            database='NotasNur',
            user='postgres',
            password='0204'
        )
        cursor = conexion.cursor()

        cursor.execute(f"DELETE FROM {tabla} WHERE id = %s", (id_eliminar,))
        conexion.commit()
        conexion.close()

        easygui.msgbox("Datos eliminados correctamente.", "Resultado")

    except Exception as ex:
        easygui.msgbox(f"Error al eliminar datos: {ex}", "Error")

# Función para mostrar las materias inscritas por un estudiante y el promedio de notas en cada materia
def mostrar_materias_estudiante(id_estudiante):
    try:
        conexion = psycopg2.connect(
            host='localhost',
            database='NotasNur',
            user='postgres',
            password='0204'
        )
        cursor = conexion.cursor()

        # Consulta para obtener las materias inscritas por el estudiante y el promedio de notas
        cursor.execute("""
            SELECT E.id, E.nombre_completo,
                   STRING_AGG(M.nombre, ', ') AS materias_inscrito
            FROM Estudiante E
            JOIN Notas N ON E.id = N.id_estudiante
            JOIN Materia M ON N.codigo_materia = M.id
            WHERE E.id = %s
            GROUP BY E.id, E.nombre_completo
        """, (id_estudiante,))
        datos = cursor.fetchall()

        conexion.close()

        # Mostrar los resultados en una ventana
        if datos:
            ventana_materias = tk.Toplevel()
            ventana_materias.title(f'Materias inscritas por Estudiante {id_estudiante}')

            tree_materias = ttk.Treeview(ventana_materias)
            tree_materias["columns"] = ("ID Estudiante", "Nombre Completo", "Materias Inscritas")

            tree_materias.heading("ID Estudiante", text="ID Estudiante")
            tree_materias.heading("Nombre Completo", text="Nombre Completo")
            tree_materias.heading("Materias Inscritas", text="Materias Inscritas")

            for id_est, nombre, materias in datos:
                tree_materias.insert("", "end", values=(id_est, nombre, materias))

            tree_materias.pack()

            ventana_materias.mainloop()
        else:
            easygui.msgbox(f"No se encontraron materias inscritas para el Estudiante {id_estudiante}.", "Error")

    except Exception as ex:
        easygui.msgbox(f"Error al obtener materias inscritas: {ex}", "Error")



def mostrar_notas_completas(id_estudiante, codigo_materia):
    try:
        conexion = psycopg2.connect(
            host='localhost',
            database='NotasNur',
            user='postgres',
            password='0204'
        )
        cursor = conexion.cursor()

        # Query para obtener las notas de un estudiante en una materia específica, incluyendo las notas de los parciales
        query = """
            SELECT E.nombre_completo AS Estudiante, M.nombre AS Materia,
                   N.tarea AS Tarea, N.proyecto AS Proyecto,
                   P.nombre AS Parcial, P.valor AS Nota_Parcial
            FROM Estudiante E
            JOIN Notas N ON E.id = N.id_estudiante
            JOIN Materia M ON N.codigo_materia = M.id
            JOIN Parciales P ON N.id_estudiante = P.id_estudiante
                            AND N.codigo_materia = P.codigo_materia
            WHERE E.id = %s  
              AND M.id = %s; 
        """

        cursor.execute(query, (id_estudiante, codigo_materia))
        datos = cursor.fetchall()

        conexion.close()

        # Mostrar los resultados en una ventana
        if datos:
            ventana_notas = tk.Toplevel()
            ventana_notas.title(f'Notas de Estudiante {id_estudiante} en Materia {codigo_materia}')

            tree_notas = ttk.Treeview(ventana_notas)
            tree_notas["columns"] = ("Estudiante", "Materia", "Tarea", "Proyecto", "Parcial", "Nota_Parcial")

            tree_notas.heading("Estudiante", text="Estudiante")
            tree_notas.heading("Materia", text="Materia")
            tree_notas.heading("Tarea", text="Tarea")
            tree_notas.heading("Proyecto", text="Proyecto")
            tree_notas.heading("Parcial", text="Parcial")
            tree_notas.heading("Nota_Parcial", text="Nota ")

            for estudiante, materia, tarea, proyecto, parcial, nota_parcial in datos:
                tree_notas.insert("", "end", values=(estudiante, materia, tarea, proyecto, parcial, nota_parcial))

            tree_notas.pack()

            ventana_notas.mainloop()
        else:
            easygui.msgbox(f"No se encontraron datos para el Estudiante {id_estudiante} y la Materia {codigo_materia}.", "Error")

    except Exception as ex:
        easygui.msgbox(f"Error al obtener notas de parciales: {ex}", "Error")
# Ejemplo de uso de las funciones

def obtener_ids_estudiantes():
    try:
        conexion = psycopg2.connect(
            host='localhost',
            database='NotasNur',
            user='postgres',
            password='0204'
        )
        print("Conexión exitosa")
    except Exception as ex:
        print(f"Error de conexión: {ex}")
        return []

    cursor = conexion.cursor()
    cursor.execute('SELECT id FROM Estudiante')
    ids_estudiantes = [fila[0] for fila in cursor.fetchall()]

    conexion.close()

    return ids_estudiantes

def mostrar_inscritos_materia(codigo_materia):
    try:
        conexion = psycopg2.connect(
            host='localhost',
            database='NotasNur',
            user='postgres',
            password='0204'
        )
        cursor = conexion.cursor()

        # Consulta para obtener los estudiantes inscritos en una materia y el nombre de la materia
        query = """
            SELECT E.nombre_completo, M.nombre as Materia
            FROM Estudiante E
            JOIN Notas N ON E.id = N.id_estudiante
            JOIN Materia M ON N.codigo_materia = M.id 
            WHERE M.id = %s;
        """

        cursor.execute(query, (codigo_materia,))
        datos = cursor.fetchall()

        conexion.close()

        # Mostrar los resultados en una ventana
        if datos:
            ventana_inscritos = tk.Toplevel()
            ventana_inscritos.title(f'Inscritos en Materia {codigo_materia}')

            tree_inscritos = ttk.Treeview(ventana_inscritos)
            tree_inscritos["columns"] = ("Nombre Completo", "Materia")

            tree_inscritos.heading("Nombre Completo", text="Nombre Completo")
            tree_inscritos.heading("Materia", text="Materia")

            for nombre, materia in datos:
                tree_inscritos.insert("", "end", values=(nombre, materia))

            tree_inscritos.pack()

            ventana_inscritos.mainloop()
        else:
            easygui.msgbox(f"No se encontraron inscritos para la Materia {codigo_materia}.", "Error")

    except Exception as ex:
        easygui.msgbox(f"Error al obtener inscritos en la materia: {ex}", "Error")

def obtener_ids_materias():
    try:
        conexion = psycopg2.connect(
            host='localhost',
            database='NotasNur',
            user='postgres',
            password='0204'
        )
        cursor = conexion.cursor()

        cursor.execute("SELECT id FROM Materia")
        ids_materias = [row[0] for row in cursor.fetchall()]

        conexion.close()
        return ids_materias

    except Exception as ex:
        easygui.msgbox(f"Error al obtener las IDs de materias: {ex}", "Error")
        return []


def mostrar_promedio_estudiante_materia(id_estudiante, codigo_materia):
    try:
        conexion = psycopg2.connect(
            host='localhost',
            database='NotasNur',
            user='postgres',
            password='0204'
        )
        cursor = conexion.cursor()

        # Query con la estructura WITH para obtener el promedio de notas de un estudiante en una materia específica
        query = """
            WITH NotasParciales AS (
                SELECT n.id_estudiante, n.codigo_materia, n.tarea AS nota_tarea, n.proyecto AS nota_proyecto
                FROM Notas n
                JOIN Parciales p ON n.id_estudiante = p.id_estudiante AND n.codigo_materia = p.codigo_materia
            )
            SELECT e.nombre_completo AS nombre_estudiante, m.nombre AS nombre_materia,
                   AVG((np.nota_tarea + np.nota_proyecto) / 2.0) AS promedio
            FROM NotasParciales np
            JOIN Estudiante e ON np.id_estudiante = e.id 
            JOIN Materia m ON np.codigo_materia = m.id 
            WHERE np.id_estudiante = %s 
              AND np.codigo_materia = %s 
            GROUP BY e.nombre_completo, m.nombre;
        """

        cursor.execute(query, (id_estudiante, codigo_materia))
        datos = cursor.fetchall()

        conexion.close()

        # Mostrar los resultados en una ventana
        if datos:
            ventana_promedio = tk.Toplevel()
            ventana_promedio.title(f'Promedio de Estudiante {id_estudiante} en Materia {codigo_materia}')

            tree_promedio = ttk.Treeview(ventana_promedio)
            tree_promedio["columns"] = ("Estudiante", "Materia", "Promedio")

            tree_promedio.heading("Estudiante", text="Estudiante")
            tree_promedio.heading("Materia", text="Materia")
            tree_promedio.heading("Promedio", text="Promedio")

            for estudiante, materia, promedio in datos:
                tree_promedio.insert("", "end", values=(estudiante, materia, promedio))

            tree_promedio.pack()

            ventana_promedio.mainloop()
        else:
            easygui.msgbox(f"No se encontraron datos para el Estudiante {id_estudiante} y la Materia {codigo_materia}.", "Error")

    except Exception as ex:
        easygui.msgbox(f"Error al obtener promedio de notas: {ex}", "Error")


def mostrar():
    opciones = ["Estudiante", "Materia", "Notas", "Parciales"]
    eleccion = easygui.choicebox("Selecciona una tabla:", choices=opciones)

    if eleccion:
        mostrar_cuadro(eleccion)
    else:
        easygui.msgbox("No seleccionaste ninguna opción.", "Resultado")

def insertar():
    opciones = ["Estudiante", "Materia", "Notas", "Parciales"]
    eleccion = easygui.choicebox("Selecciona una tabla:", choices=opciones)

    if eleccion:
        mostrar_cuadro_insertar(eleccion)
    else:
        easygui.msgbox("No seleccionaste ninguna opción.", "Resultado")

def actualizar():
    opciones = ["Estudiante", "Materia", "Notas", "Parciales"]
    eleccion = easygui.choicebox("Selecciona una tabla:", choices=opciones)

    if eleccion:
        mostrar_cuadro_actualizar(eleccion)
    else:
        easygui.msgbox("No seleccionaste ninguna opción.", "Resultado")

def eliminar():
    opciones = ["Estudiante", "Materia", "Notas", "Parciales"]
    eleccion = easygui.choicebox("Selecciona una tabla:", choices=opciones)

    if eleccion:
        mostrar_cuadro_eliminar(eleccion)
    else:
        easygui.msgbox("No seleccionaste ninguna opción.", "Resultado")

def materias_inscritas():
    ids_estudiantes = obtener_ids_estudiantes()
    eleccion = easygui.choicebox("Selecciona un estudiante:", choices=ids_estudiantes)
    if eleccion:
        mostrar_materias_estudiante(eleccion)
    else:
        easygui.msgbox("No seleccionaste ninguna opción.", "Resultado")


def estuadientes_Materias():
    ids_materias = obtener_ids_materias()
    eleccion = easygui.choicebox("Seleccione una materia:", choices=ids_materias)
    if eleccion:
        mostrar_inscritos_materia(eleccion)
    else:
        easygui.msgbox("No seleccionaste ninguna opción.", "Resultado")


def promedios():
    ids_materias = obtener_ids_materias()
    eleccionMaterias = easygui.choicebox("Seleccione una materia:", choices=ids_materias)
    ids_estudiantes = obtener_ids_estudiantes()
    eleccionEstudiantes = easygui.choicebox("Selecciona un estudiante:", choices=ids_estudiantes)
    if eleccionEstudiantes and eleccionMaterias:
        mostrar_promedio_estudiante_materia(eleccionEstudiantes, eleccionMaterias)
    else:
        easygui.msgbox("No seleccionaste ninguna opción.", "Resultado")


def notas():
    ids_materias = obtener_ids_materias()
    eleccionMaterias = easygui.choicebox("Seleccione una materia:", choices=ids_materias)
    ids_estudiantes = obtener_ids_estudiantes()
    eleccionEstudiantes = easygui.choicebox("Selecciona un estudiante:", choices=ids_estudiantes)
    if eleccionEstudiantes and eleccionMaterias:
        mostrar_notas_completas(eleccionEstudiantes, eleccionMaterias)
    else:
        easygui.msgbox("No seleccionaste ninguna opción.", "Resultado")

# Interfaz principal
ventana = tk.Tk()
ventana.title('Gestión de Base de Datos Notas Nur')

boton_mostrar = tk.Button(ventana, text='Mostrar datos', command=mostrar)
boton_insertar = tk.Button(ventana, text='Insertar datos', command=insertar)
boton_actualizar = tk.Button(ventana, text='Actualizar datos', command=actualizar)
boton_eliminar = tk.Button(ventana, text='Eliminar datos', command=eliminar)
boton_Estudiantes = tk.Button(ventana,text='Estudiantes ID', command=materias_inscritas)
boton_Materias = tk.Button(ventana,text='Materias ID', command=estuadientes_Materias)
boton_promedios = tk.Button(ventana,text='Promedios por Materias', command=promedios)
boton_notas = tk.Button(ventana,text='Notas Estudiante', command=notas)

boton_mostrar.pack()
boton_insertar.pack()
boton_actualizar.pack()
boton_eliminar.pack()
boton_Estudiantes.pack()
boton_Materias.pack()
boton_promedios.pack()
boton_notas.pack()


ventana.mainloop()
