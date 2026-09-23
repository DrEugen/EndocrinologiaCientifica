import resend
from flask import Flask, render_template, request, redirect, url_for, flash, make_response, session, jsonify
from flask_sqlalchemy import SQLAlchemy
import cloudinary
import cloudinary.uploader
from dotenv import load_dotenv
import requests
from PIL import Image, ImageOps
import io
import json
import os
import re, unicodedata
from config import CLIENTE, LANDINGS, BLOG_DATA
from datetime import datetime
from google import genai

app = Flask(__name__)


# ==========================================
# 0,1. SQL ALCHEMY
# ==========================================
# Railway proporciona la URL en la variable DATABASE_URL
# TIENES QUE CREAR TU DB EN LA CARPETA INSTANCE
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///blog_local.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Post(db.Model):
    __tablename__ = 'blog_posts'
    
    # Mapeo exacto de tus componentes del JSON
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(255), unique=True, nullable=False) # Para URLs amigables
    resumen = db.Column(db.String(500))
    contenido = db.Column(db.Text, nullable=False) # 'Text' permite HTML largo como el tuyo
    fecha = db.Column(db.String(50), default=lambda: datetime.now().strftime("%d %b, %Y"))
    categoria = db.Column(db.String(100))
    imagen = db.Column(db.String(500)) # URL de Unsplash
    estado = db.Column(db.String(20), nullable=False, default='publicado')

    def __repr__(self):
        return f'<Post {self.titulo}>'



uri = os.getenv("DATABASE_URL")
if uri and uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)
app.config['SQLALCHEMY_DATABASE_URI'] = uri

# ==========================================
# 0,2. CLOUDINARY
# ==========================================

# Configuración de Cloudinary (Pon tus datos aquí o en variables de entorno)
# ES PARA ALMACENAR LAS FOTOS DEL BLOG
load_dotenv() # Esto carga las variables del archivo .env si existe

# Configuración usando variables de entorno
cloudinary.config( 
  cloud_name = os.getenv('CLOUDINARY_CLOUD_NAME'), 
  api_key = os.getenv('CLOUDINARY_API_KEY'), 
  api_secret = os.getenv('CLOUDINARY_API_SECRET'),
  secure = True
)

def crear_slug(texto):
    # 1. Normalizar para quitar acentos (á -> a)
    texto = unicodedata.normalize('NFKD', texto).encode('ascii', 'ignore').decode('utf-8').lower()
    # 2. Quitar todo lo que no sea letras, números o espacios
    texto = re.sub(r'[^\w\s-]', '', texto)
    # 3. Reemplazar espacios por guiones y limpiar extremos
    slug = re.sub(r'[-\s]+', '-', texto).strip('-')
    return slug # Retorna un STRING, no ['string']
    
def procesar_y_subir(archivo):
    # 1. Optimización con Pillow
    img = Image.open(archivo)
    img = ImageOps.exif_transpose(img) # Corregir rotación
    
    if img.mode in ("RGBA", "P"): img = img.convert("RGB")
    
    # Redimensionar a 1200px max
    max_width = 1200
    if img.size[0] > max_width:
        w_percent = (max_width / float(img.size[0]))
        h_size = int((float(img.size[1]) * float(w_percent)))
        img = img.resize((max_width, h_size), Image.Resampling.LANCZOS)
    
    # Guardar en Buffer (Memoria)
    buffer = io.BytesIO()
    img.save(buffer, format="WEBP", quality=80)
    buffer.seek(0)
    
    # 2. Subida a Cloudinary
    upload_result = cloudinary.uploader.upload(buffer, format="webp", folder="blog_posts")
    return upload_result['secure_url']

@app.route('/admin/subir-imagen-cuerpo', methods=['POST'])
def subir_imagen_cuerpo():
    if not session.get('admin'):
        return jsonify({'error': 'No autorizado'}), 401
    
    archivo = request.files.get('image')
    if archivo:
        try:
            # Reutiliza tu función de Pillow + Cloudinary
            url_final = procesar_y_subir(archivo)
            return jsonify({'url': url_final})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
            
    return jsonify({'error': 'No se recibió imagen'}), 400

def descargar_y_subir_imagen(url_externa):
    try:
        res = requests.get(url_externa, timeout=20)
        if res.status_code == 200:
            archivo_memoria = io.BytesIO(res.content)
            return procesar_y_subir(archivo_memoria)
    except Exception as e:
        print(f"Error al descargar y subir imagen de {url_externa} a Cloudinary: {e}")
    return url_externa

@app.route('/api/crear-borrador', methods=['POST'])
def api_crear_borrador():
    token_recibido = request.headers.get('X-API-Key')
    token_esperado = os.environ.get("API_SECRET_TOKEN")
    
    if not token_esperado or token_recibido != token_esperado:
        return jsonify({"error": "No autorizado"}), 401
        
    data = request.get_json()
    if not data:
        return jsonify({"error": "Petición vacía o tipo de contenido incorrecto"}), 400
        
    titulo = data.get('titulo')
    resumen = data.get('resumen')
    contenido = data.get('contenido')
    imagen_url = data.get('imagen_url')
    categoria = data.get('categoria', 'Salud Bucodental')
    
    if not titulo or not contenido:
        return jsonify({"error": "El título y el contenido son obligatorios"}), 400
        
    if imagen_url and "cloudinary.com" not in imagen_url:
        imagen_url = descargar_y_subir_imagen(imagen_url)
        
    try:
        nuevo_articulo = Post(
            titulo=titulo,
            slug=crear_slug(titulo),
            resumen=resumen,
            contenido=contenido,
            imagen=imagen_url,
            categoria=categoria,
            estado='borrador'
        )
        db.session.add(nuevo_articulo)
        db.session.commit()
        return jsonify({
            "mensaje": "Borrador creado correctamente",
            "id": nuevo_articulo.id,
            "slug": nuevo_articulo.slug,
            "imagen_url": nuevo_articulo.imagen
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error al guardar en base de datos: {str(e)}"}), 500

# ==========================================
# 1. FUNCIONES DE UTILIDAD (PERSISTENCIA)
# ==========================================

# Función para LEER artículos del archivo JSON
# SE MIGRO A SQLITE, ESTO YA NO SE USA
'''def cargar_articulos():
    if not os.path.exists('articulos.json'):
        return []
    with open('articulos.json', 'r', encoding='utf-8') as f:
        return json.load(f)

# Función para GUARDAR artículos en el archivo JSON
def guardar_articulos_en_disco(articulos):
    with open('articulos.json', 'w', encoding='utf-8') as f:
        json.dump(articulos, f, ensure_ascii=False, indent=4)'''



# ==========================================
# 2. CONFIGURACIÓN Y CLIENTES
# ==========================================

# Contraseña maestra para el panel
# LA MIGRE AL .ENV INVESTIGA COMO TRAERLA DESDE AHI
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "")






# MIGRADO A N8N
'''
# Configuración del cliente IA
GEMINI_KEY = os.environ.get("GEMINI_API_KEY", "")
client = genai.Client(api_key=GEMINI_KEY)
'''

# ==========================================
# 3. RUTAS DE ADMINISTRACIÓN Y AUTENTICACIÓN
# ==========================================

@app.route('/admin/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == ADMIN_PASSWORD:
            session['admin'] = True
            return redirect('/blog')
        # Si falla, recargamos el login pasando 'info'
        return render_template('admin/login.html', info=CLIENTE, error="Clave incorrecta")
    
    # IMPORTANTE: Aquí pasamos info=info
    return render_template('admin/login.html', info=CLIENTE)

@app.route('/admin/logout')
def logout():
    session.pop('admin', None) # Eliminamos la marca de admin de la sesión
    return redirect('/blog')


# ==========================================
# 4. RUTAS DE GESTIÓN DE CONTENIDO (CRUD & IA)
# ==========================================

@app.route('/admin/nuevo-post')
def nuevo_post():
    if not session.get('admin'):
        return redirect('/admin/login')
    return render_template('admin/editor.html', info=CLIENTE)

# FUNCION EN DESUSO, LA PUEDES ELIMINAR
'''@app.route('/admin/guardar-post', methods=['POST'])
def guardar_post():
    if not session.get('admin'):
        return redirect('/admin/login')

    # Guardamos los datos en variables para reusarlos
    datos = {
        'titulo': request.form.get('titulo'),
        'resumen': request.form.get('resumen'),
        'imagen': request.form.get('imagen'),
        'contenido': request.form.get('contenido')
    }

    # Validación
    if not all(datos.values()):
        flash("¡Error! Todos los campos son obligatorios.")
        # EN LUGAR DE REDIRECT, RENDERIZAMOS CON LOS DATOS
        return render_template('admin/editor.html', info=CLIENTE, post=datos, modo="crear")

    # ... resto de tu lógica de guardado ...
    slug = crear_slug(datos['titulo'])
    articulos = cargar_articulos()
    
    nuevo_articulo = {
        'id': len(articulos) + 1,
        'titulo': datos['titulo'],
        'resumen': datos['resumen'],
        'contenido': datos['contenido'],
        'fecha': datetime.now().strftime("%d %b, %Y"),
        'categoria': 'Salud Bucal',
        'imagen': datos['imagen'],
        'slug': slug
    }

    articulos.insert(0, nuevo_articulo)
    guardar_articulos_en_disco(articulos)
    #flash("Artículo publicado con éxito.")
    return redirect('/blog')'''

@app.route('/admin/guardar-post', methods=['POST'])
def guardar_post():
    if not session.get('admin'): return redirect('/admin/login')

    titulo = request.form.get('titulo')
    url_imagen = request.form.get('imagen') # URL por defecto
    
    # Verificar si se subió un archivo
    if 'archivo_imagen' in request.files:
        archivo = request.files['archivo_imagen']
        if archivo.filename != '':
            # Si hay archivo, lo procesamos y sobreescribimos la URL
            url_imagen = procesar_y_subir(archivo)

    # IMPORTANTE: Capturar el valor del input oculto
    estado_recibido = request.form.get('estado')
    print(f"Estado recibido del formulario: {estado_recibido}")
    
    nuevo_articulo = Post(
        titulo=titulo,
        slug=crear_slug(titulo),
        resumen=request.form.get('resumen'),
        contenido=request.form.get('contenido'),
        imagen=url_imagen,
        categoria='Salud Bucal',
        estado=estado_recibido
    )

    db.session.add(nuevo_articulo)
    db.session.commit()
    return redirect('/blog')

# EN DESUSO
'''@app.route('/admin/editar/<int:post_id>')
def editar_post(post_id):
    if not session.get('admin'):
        return redirect('/admin/login')
    
    articulos = cargar_articulos()
    articulo = next((a for a in articulos if a['id'] == post_id), None)
    
    if not articulo:
        return "Artículo no encontrado", 404
        
    return render_template('admin/editor.html', info=CLIENTE, post=articulo, modo="editar")'''

@app.route('/admin/editar/<int:post_id>')
def editar_post(post_id):
    if not session.get('admin'):
        return redirect('/admin/login')
    
    # Buscamos directamente por ID en la base de datos
    articulo = Post.query.get_or_404(post_id)
    return render_template('admin/editor.html', info=CLIENTE, post=articulo, modo="editar")

@app.route('/admin/actualizar-post/<int:post_id>', methods=['POST'])
def actualizar_post(post_id):
    if not session.get('admin'):
        return redirect('/admin/login')

    articulo = Post.query.get_or_404(post_id)
    
    # 1. Actualizar textos básicos
    articulo.titulo = request.form.get('titulo')
    articulo.resumen = request.form.get('resumen')
    articulo.contenido = request.form.get('contenido')
    articulo.slug = crear_slug(articulo.titulo)

    # 2. Lógica inteligente de imagen
    # Primero vemos si pegaste una URL manual
    nueva_url_texto = request.form.get('imagen')
    
    # Luego revisamos si subiste un archivo desde la PC/Celular
    if 'archivo_imagen' in request.files:
        archivo = request.files['archivo_imagen']
        if archivo.filename != '':
            # Si hay archivo, procesamos, subimos y esa es la nueva URL
            articulo.imagen = procesar_y_subir(archivo)
        elif nueva_url_texto:
            # Si no hay archivo pero cambiaste el link de texto, usamos el link
            articulo.imagen = nueva_url_texto
    
    # Si no se subió archivo ni se cambió el link, se queda la imagen que ya tenía

    articulo.estado = request.form.get('estado')        
    db.session.commit()
    return redirect('/blog')

@app.route('/admin/eliminar/<int:post_id>')
def eliminar_post(post_id):
    if not session.get('admin'):
        return redirect('/admin/login')
    
    articulo = Post.query.get_or_404(post_id)
    db.session.delete(articulo)
    db.session.commit()
    
    return redirect('/blog')


# ==========================================
# 5. RUTAS PÚBLICAS DEL SITIO WEB
# ==========================================

@app.route('/')
def home():
    return render_template('sitio_web/home.html', info=CLIENTE)

@app.route('/nosotros')
def nosotros():
    return render_template('sitio_web/nosotros.html', info=CLIENTE)

@app.route('/en')
def english():
    return render_template('sitio_web/en.html', info=CLIENTE)

@app.route('/servicios')
def servicios():
    return render_template('sitio_web/servicios.html', info=CLIENTE)


@app.route('/servicios/<slug>')
def servicio_detalle(slug):
    servicio_encontrado = None
    
    for s in CLIENTE.get('servicios', []):
        # Primero intentamos comparar con el slug manual que pusiste
        # Si no existe el campo 'slug', usamos el título convertido
        slug_del_servicio = s.get('slug') 
        
        if slug_del_servicio == slug:
            servicio_encontrado = s
            break
    
    if not servicio_encontrado:
        # Imprime esto en tu terminal para ver qué está recibiendo Flask
        print(f"DEBUG: No se encontró el slug: {slug}") 
        return render_template('sitio_web/404.html', info=CLIENTE), 404
        
    return render_template('sitio_web/servicio_detalle.html', servicio=servicio_encontrado, info=CLIENTE)


@app.route('/galeria')
def especialidades():
    return render_template('sitio_web/galeria.html', info=CLIENTE)

@app.route('/beneficios')
def demostracion():
    return render_template('sitio_web/beneficios.html', info=CLIENTE)

#@app.route('/proceso')
#def proceso():
#    return render_template('sitio_web/proceso.html', info=CLIENTE)

@app.route('/contactenos')
def contactenos():
    return render_template('sitio_web/contacto.html', info=CLIENTE)


# ==========================================
# 6. BLOG PÚBLICO
# ==========================================

@app.route('/blog')
def blog_feed():
    if not session.get('admin'):
        # El público SOLO ve los publicados
        # Revisa que diga 'publicado' (en minúsculas, tal cual se guarda en DB)
        articulos = Post.query.filter_by(estado='publicado').order_by(Post.id.desc()).all()
    else:
        # Admin ve todo 
        articulos = Post.query.order_by(Post.id.desc()).all()
    
    return render_template('sitio_web/blog.html', articulos=articulos, info=CLIENTE)

@app.route('/blog/<slug>')
def blog_post(slug):
    # Buscamos el artículo por slug o lanzamos un error 404 si no existe
    articulo = Post.query.filter_by(slug=slug).first_or_404()

    # Si es borrador y NO eres admin, bloqueamos el acceso
    if articulo.estado == 'borrador' and not session.get('admin'):
        return "Este artículo aún no ha sido publicado", 403
    
    # Nota: Asegúrate de que el nombre del archivo sea 'sitio_web/articulo.html'
    return render_template('sitio_web/articulo.html', post=articulo, info=CLIENTE)


# ==========================================
# 7. RUTAS DINÁMICAS Y LEGALES
# ==========================================
# LANDING PAGES
@app.route('/p/<nombre>')
def landing_dinamica(nombre):
    datos_pagina = LANDINGS.get(nombre)
    if not datos_pagina:
        return "Página no encontrada", 404
    return render_template('landing_page.html', info=CLIENTE, contenido=datos_pagina)

@app.route('/legal/privacidad')
def privacidad():
    return render_template('legal/privacidad.html', info=CLIENTE)

@app.route('/legal/terminos')
def terminos():
    return render_template('legal/terminos.html', info=CLIENTE)


# ==========================================
# 8. SISTEMA DE CONTACTO Y CORREO
# ==========================================

def contiene_url(texto):
    # Patrón para detectar http, https, www o extensiones comunes de dominio
    patron_url = r'(https?://[^\s]+)|(www\.[^\s]+)|([a-zA-Z0-9.-]+\.(com|net|org|edu|gov|io|biz|info|lat|me|tk|xyz))'
    if re.search(patron_url, texto, re.IGNORECASE):
        return True
    return False

@app.route('/enviar-contacto', methods=['POST'])
def contacto():
    telefono = request.form.get('telefono')
    email_contacto = 'albertigual@yahoo.com'
    email_cliente = request.form.get('email')
    nombre = request.form.get('nombre')
    #web = request.form.get('web')
    #servicio = request.form.get('servicio')
    mensaje = request.form.get('mensaje')

    # VALIDACIÓN ANTI-SPAM
    if contiene_url(mensaje) or contiene_url(nombre):
        # Ghosting 
        # Haces como que se envió pero no haces nada. El spammer cree que tuvo éxito pero no te llega nada.
        print(f"DEBUG: Intento de Spam bloqueado de: {email_cliente}. Su mensaje fue: {mensaje}")
        return render_template('gracias.html', info=CLIENTE, nombre=nombre, telefono=telefono, email=email_cliente)

    try:
        params = {
            'from': 'Web de contacto <onboarding@resend.dev>',
            'to': email_contacto,
            'subject': f'Nuevo mensaje de: {nombre}',
            'html': f'''
            <h3>Has recibido un nuevo contacto desde la web</h3>
            <p><strong>Nombre: </strong>{nombre}</p>
            <p><strong>Telefono: </strong>{telefono}</p>
            <p><strong>Whatsapp: </strong>https://wa.me/506{telefono}</p>
            <p><strong>Email: </strong>{email_cliente}</p>
            <p><strong>Mensaje: </strong>{mensaje}</p>
            ''',
        }
        resend.Emails.send(params)
        return render_template('gracias.html', info=CLIENTE, nombre=nombre, telefono=telefono, email=email_cliente)
    except Exception as e:
        print(f"Error enviando el correo: {e}")
        return "<h1>Hubo un error al enviar. Revisa la terminal.</h1>"

@app.route('/newsletter-subscribe', methods=['POST'])
def newsletter():
    email_contacto = 'albertigual@yahoo.com'
    email_cliente = request.form.get('correo')

    try:
        params = {
            'from': 'Web de contacto <onboarding@resend.dev>',
            'to': email_contacto,
            'subject': f'Nuevo contacto para Newsletter',
            'html': f'<h3>Nuevo contacto:</h3><p>{email_cliente}</p>',
        }
        resend.Emails.send(params)
        # Retornamos un JSON indicando éxito
        return jsonify({'success': True, 'message': 'Suscripción exitosa'})
    
    except Exception as e:
        print(f"Error: {e}")
        # Retornamos un JSON indicando error
        return jsonify({'success': False, 'message': 'Error al enviar'}), 500


# ==========================================
# 9. SISTEMA (SEO, ERRORES, RUN)
# ==========================================

@app.route('/sitemap.xml', methods=['GET'])
def sitemap():
    now = datetime.now().strftime("%Y-%m-%d")
    base_url = "https://igualdental.com"
    
    # 1. Páginas estáticas principales
    urls = [
        {'loc': '/', 'priority': '1.0'},
        {'loc': '/nosotros', 'priority': '0.8'},
        {'loc': '/servicios', 'priority': '0.8'},
        {'loc': '/galeria', 'priority': '0.8'}, 
        {'loc': '/blog', 'priority': '0.8'},
        {'loc': '/contactenos', 'priority': '0.9'}
    ]

    # 2. Agregar Servicios dinámicamente
    # Asegúrate de que CLIENTE esté definido globalmente o accesible
    for s in CLIENTE.get('servicios', []):
        urls.append({
            'loc': f"/servicios/{s.get('slug')}", 
            'priority': '0.9'
        })
    
    # 3. Agregar Artículos del Blog dinámicamente desde la Base de Datos
    # Solo incluimos los que están publicados para que Google no indexe borradores
    articulos_publicados = Post.query.filter_by(estado='publicado').all()

    for post in articulos_publicados:
        if post.slug:
            urls.append({
                'loc': f"/blog/{post.slug}", 
                'priority': '0.9'
            })
    
    # Generar XML
    sitemap_xml = render_template('sitemap_template.xml', base_url=base_url, urls=urls, now=now)
    response = make_response(sitemap_xml)
    response.headers["Content-Type"] = "application/xml"
    return response


@app.route('/robots.txt')
def robots():
    return app.send_static_file('robots.txt')

@app.route('/llms.txt')
def llms():
    return app.send_static_file('llms.txt')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('sitio_web/404.html', info=CLIENTE), 404

# Esto permite usar la función dentro de tus archivos .html
app.jinja_env.globals.update(crear_slug=crear_slug)

# SE EJECUTA UNA VEZ, LUEGO SE COMENTA (ESTA PENSADO PARA RAILWAT TAMBIEN)
with app.app_context():
    db.create_all()
    print("Tablas creadas/verificadas en la base de datos.")

if __name__ == '__main__':
    app.run(debug=True)
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)