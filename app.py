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

@app.route("/", methods=["GET", "HEAD"])
def menu():
    if request.method == "HEAD":
        return "", 200
    return render_template('menu.html')

# ------------------- HISTORIAL -------------------

@app.route("/historial", methods=["GET", "HEAD"])
def listar_historial():
    if request.method == "HEAD":
        return "", 200
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
        return render_template('historial.html', historial=historial)
    except Exception as e:
        flash(f"Error al cargar el historial: {str(e)}", "danger")
        return render_template('historial.html', historial=[])
    finally:
        cursor.close()

@app.route("/historial/add", methods=["POST"])
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
    except Exception as e:
        flash(f"Error al agregar al historial: {e}", "danger")
    finally:
        cursor.close()
    return redirect(url_for('listar_historial'))

@app.route("/historial/delete/<int:id>", methods=["GET"])
def historial_delete(id):
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("DELETE FROM Historial WHERE HistorialID = %s", (id,))
        mysql.connection.commit()
        flash('Registro eliminado del historial con éxito!', 'success')
    except Exception as e:
        flash(f"Error al eliminar el registro del historial: {e}", "danger")
    finally:
        cursor.close()
    return redirect(url_for('listar_historial'))

# ------------------- PROVEEDORES -------------------

@app.route("/index", methods=["GET", "HEAD"])
def index():
    if request.method == "HEAD":
        return "", 200
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM Proveedores")
        proveedores = cursor.fetchall()
        return render_template('index.html', proveedores=proveedores)
    except Exception as e:
        flash(f"Error al cargar los proveedores: {e}", "danger")
        return render_template('index.html', proveedores=[])
    finally:
        cursor.close()

# ------------------- PRODUCTOS -------------------

@app.route("/productos", methods=["GET", "HEAD"])
def productos_index():
    if request.method == "HEAD":
        return "", 200
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
    finally:
        cursor.close()

if __name__ == "__main__":
    app.run(debug=True)
