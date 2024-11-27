from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mysqldb import MySQL

app = Flask(__name__)
app.secret_key = "secret_key"

# Configuración de la base de datos
app.config['MYSQL_HOST'] = 'apimercadoagricola.cp0m2uu08onk.us-east-2.rds.amazonaws.com'
app.config['MYSQL_PORT'] = 3306
app.config['MYSQL_USER'] = 'admin'
app.config['MYSQL_PASSWORD'] = 'Efdade1146'
app.config['MYSQL_DB'] = 'api_mercado_agricola'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

# ------------------- MENÚ PRINCIPAL -------------------

@app.route('/')
def menu():
    return render_template('menu.html')

# ------------------- HISTORIAL -------------------

@app.route('/historial')
def listar_historial():
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("""
            SELECT 
                h.HistorialID AS ID,
                h.Cantidad,
                h.Fecha,
                COALESCE(h.NombreProducto, 'Sin Producto') AS NombreProducto,
                COALESCE(pr.Nombre, 'Sin Proveedor') AS Proveedor
            FROM Historial h
            LEFT JOIN Proveedores pr ON h.ProveedorID = pr.ProveedorID
        """)
        historial = cursor.fetchall()
        cursor.close()  
        return render_template('historial.html', historial=historial)
    except Exception as e:
        flash(f"Error al cargar el historial: {str(e)}", "danger")  
        return render_template('historial.html', historial=[])


@app.route('/historial/add', methods=['POST'])
def historial_add():
    cantidad = request.form['cantidad']
    producto_id = request.form.get('producto_id')
    proveedor_id = request.form.get('proveedor_id')

    try:
        cursor = mysql.connection.cursor()
        query = """
            INSERT INTO Historial (Cantidad, ProductoID, ProveedorID)
            VALUES (%s, %s, %s)
        """
        cursor.execute(query, (cantidad, producto_id, proveedor_id))
        mysql.connection.commit()
        flash('Registro agregado al historial con éxito!', 'success')
        return redirect(url_for('listar_historial'))
    except Exception as e:
        flash(f"Error al agregar al historial: {e}", "danger")
        return redirect(url_for('listar_historial'))

@app.route('/historial/delete/<int:id>', methods=['GET'])
def historial_delete(id):
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("DELETE FROM Historial WHERE HistorialID = %s", (id,))
        mysql.connection.commit()
        flash('Registro eliminado del historial con éxito!', 'success')
        return redirect(url_for('listar_historial'))
    except Exception as e:
        flash(f"Error al eliminar el registro del historial: {e}", "danger")
        return redirect(url_for('listar_historial'))

# ------------------- PROVEEDORES -------------------

@app.route('/index')
def index():
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM Proveedores")
        proveedores = cursor.fetchall()
        return render_template('index.html', proveedores=proveedores)
    except Exception as e:
        flash(f"Error al cargar los proveedores: {e}", "danger")
        return render_template('index.html', proveedores=[])

@app.route('/add', methods=['POST'])
def add():
    nombre = request.form['nombre']
    telefono = request.form['telefono']
    correo = request.form['correo']
    direccion = request.form['direccion']

    try:
        cursor = mysql.connection.cursor()
        query = "INSERT INTO Proveedores (Nombre, Telefono, Correo, Direccion) VALUES (%s, %s, %s, %s)"
        cursor.execute(query, (nombre, telefono, correo, direccion))
        mysql.connection.commit()
        flash('Proveedor agregado con éxito!', 'success')
        return redirect(url_for('index'))
    except Exception as e:
        flash(f"Error al agregar proveedor: {e}", "danger")
        return redirect(url_for('index'))

@app.route('/edit', methods=['POST'])
def edit():
    proveedor_id = request.form['id']
    nombre = request.form['nombre']
    telefono = request.form['telefono']
    correo = request.form['correo']
    direccion = request.form['direccion']

    try:
        cursor = mysql.connection.cursor()
        query = """
            UPDATE Proveedores
            SET Nombre = %s, Telefono = %s, Correo = %s, Direccion = %s
            WHERE ProveedorID = %s
        """
        cursor.execute(query, (nombre, telefono, correo, direccion, proveedor_id))
        mysql.connection.commit()
        flash('Proveedor actualizado con éxito!', 'success')
        return redirect(url_for('index'))
    except Exception as e:
        flash(f"Error al actualizar proveedor: {e}", "danger")
        return redirect(url_for('index'))


@app.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    try:
        cursor = mysql.connection.cursor()
        query = "DELETE FROM Proveedores WHERE ProveedorID = %s"
        cursor.execute(query, (id,))
        mysql.connection.commit()
        flash('Proveedor eliminado con éxito!', 'success')
    except Exception as e:
        flash(f"Error al eliminar el proveedor: {e}", "danger")
    finally:
        cursor.close()
    return redirect(url_for('index'))

# ------------------- PRODUCTOS -------------------

@app.route('/productos')
def productos_index():
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("""
            SELECT Productos.*, Proveedores.Nombre AS Proveedor
            FROM Productos
            LEFT JOIN Proveedores ON Productos.ProveedorID = Proveedores.ProveedorID
        """)
        productos = cursor.fetchall()
        cursor.execute("SELECT ProveedorID, Nombre FROM Proveedores")
        proveedores = cursor.fetchall()
        return render_template('productos.html', productos=productos, proveedores=proveedores)
    except Exception as e:
        flash(f"Error al cargar los productos: {e}", "danger")
        return render_template('productos.html', productos=[], proveedores=[])

@app.route('/productos/add', methods=['POST'])
def productos_add():
    nombre = request.form['nombre']
    categoria = request.form['categoria']
    precio = request.form['precio']
    unidad_medida = request.form['unidad_medida']
    cantidad = request.form['cantidad']
    disponible = request.form.get('disponible', 'off') == 'on'
    proveedor_id = request.form['proveedor_id']

    try:
        cursor = mysql.connection.cursor()
        query = """
            INSERT INTO Productos (Nombre, Categoria, Precio, UnidadMedida, Cantidad, Disponible, ProveedorID)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (nombre, categoria, precio, unidad_medida, cantidad, disponible, proveedor_id))
        mysql.connection.commit()
        flash('Producto agregado con éxito!', 'success')
        return redirect(url_for('productos_index'))
    except Exception as e:
        flash(f"Error al agregar producto: {e}", "danger")
        return redirect(url_for('productos_index'))

@app.route('/productos/edit', methods=['POST'])
def productos_edit():
    producto_id = request.form['id']
    nombre = request.form['nombre']
    categoria = request.form['categoria']
    precio = request.form['precio']
    unidad_medida = request.form['unidad_medida']
    cantidad = request.form['cantidad']
    disponible = request.form.get('disponible', 'off') == 'on'
    proveedor_id = request.form['proveedor_id']

    try:
        cursor = mysql.connection.cursor()
        query = """
            UPDATE Productos
            SET Nombre = %s, Categoria = %s, Precio = %s, UnidadMedida = %s, Cantidad = %s, Disponible = %s, ProveedorID = %s
            WHERE ProductoID = %s
        """
        cursor.execute(query, (nombre, categoria, precio, unidad_medida, cantidad, disponible, proveedor_id, producto_id))
        mysql.connection.commit()
        flash('Producto actualizado con éxito!', 'success')
        return redirect(url_for('productos_index'))
    except Exception as e:
        flash(f"Error al actualizar producto: {e}", "danger")
        return redirect(url_for('productos_index'))

@app.route('/productos/delete/<int:id>', methods=['POST'])
def productos_delete(id):
    try:
        cursor = mysql.connection.cursor()
        query = "DELETE FROM Productos WHERE ProductoID = %s"
        cursor.execute(query, (id,))
        mysql.connection.commit()
        flash('Producto eliminado con éxito!', 'success')
        return redirect(url_for('productos_index'))
    except Exception as e:
        flash(f"Error al eliminar el producto: {e}", "danger")
        return redirect(url_for('productos_index'))

if __name__ == '__main__':
    app.run(debug=True)