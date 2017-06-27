import datetime
import time

import simplejson
from django.contrib.auth import authenticate, login, logout
from django.core.files.storage import default_storage
from django.db.models import Count
from django.db.models import Sum
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist

from .forms import GestionProductosForm
from .forms import LoginForm
from .models import *


def index(request):
    vendedores_id = []
    vendedores_tipo = []
    vendedores_nombre = []
    vendedores_avatar = []
    vendedores_pago = []
    vendedores_ini = []
    vendedores_fin = []
    vendedores_lat = []
    vendedores_long = []
    # lista de vendedores
    i = 0
    for v in Vendedor.objects.all():
        ini = ""
        fin = ""
        if v.tipo == 2 and v.activo:
            vendedores_id.append(v.user.id)
            vendedores_tipo.append(v.tipo)
            vendedores_nombre.append(v.user.user.first_name)
            vendedores_avatar.append(str(v.user.avatar))
            vendedores_pago.append(v.formasDePago)
            vendedores_lat.append(v.lat)
            vendedores_long.append(v.long)
            vendedores_ini.append(ini)
            vendedores_fin.append(fin)
        if v.tipo == 1:
            vf = v.vendedorfijo
            hora_local = time.localtime()
            hora_local = datetime.time(hora_local.tm_hour, hora_local.tm_min)
            ini = vf.horarioIni.strftime("%H:%M")
            fin = vf.horarioFin.strftime("%H:%M")
            if vf.horarioIni <= hora_local <= vf.horarioFin:
                v.activo = 1
                vendedores_id.append(v.user.id)
                vendedores_tipo.append(v.tipo)
                vendedores_nombre.append(v.user.user.first_name)
                vendedores_avatar.append(str(v.user.avatar))
                vendedores_pago.append(v.formasDePago)
                vendedores_lat.append(v.lat)
                vendedores_long.append(v.long)
                vendedores_ini.append(ini)
                vendedores_fin.append(fin)
            else:
                v.activo = 0
            v.save()
        i = i + 1

    nombre = simplejson.dumps(vendedores_nombre)
    tipo = simplejson.dumps(vendedores_tipo)
    ids = simplejson.dumps(vendedores_id)
    avatar = simplejson.dumps(vendedores_avatar)
    formas_de_pago = simplejson.dumps(vendedores_pago)
    horario_ini = simplejson.dumps(vendedores_ini)
    horario_fin = simplejson.dumps(vendedores_fin)
    lat = simplejson.dumps(vendedores_lat)
    long = simplejson.dumps(vendedores_long)

    return render(request, 'main/baseAlumno-sinLogin.html',
                  {"nombre": nombre, "tipo": tipo, "id": ids, "avatar": avatar, "formasDePago": formas_de_pago,
                   "horarioIni": horario_ini, "horarioFin": horario_fin, "lat": lat, "long": long})


def login_form(request):
    return render(request, 'main/login.html', {})


def fijo_dashboard(request):
    fijo_id = request.POST.get("fijoId")
    v = Usuario.objects.get(id=fijo_id).vendedor

    # transacciones hechas por hoy
    transacciones_diarias = Transacciones.objects.filter(vendedor=v).values('fecha').annotate(conteo=Count('fecha'))
    temp_transacciones_diarias = list(transacciones_diarias)
    transacciones_diarias_arr = []
    for element in temp_transacciones_diarias:
        transacciones_diarias_arr.append([element['fecha'].strftime("%Y-%m-%d"), element['conteo']])

    transacciones_diarias_arr = simplejson.dumps(transacciones_diarias_arr)

    # ganancias de hoy
    ganancias_diarias = Transacciones.objects.filter(vendedor=v).values('fecha').annotate(ganancia=Sum('precio'))
    temp_ganancias_diarias = list(ganancias_diarias)
    ganancias_diarias_arr = []
    for element in temp_ganancias_diarias:
        ganancias_diarias_arr.append([element['fecha'].strftime("%Y-%m-%d"), element['ganancia']])
    ganancias_diarias_arr = simplejson.dumps(ganancias_diarias_arr)

    # todos los productos del vendedor
    productos = Comida.objects.filter(vendedor=v).values('nombre', 'precio')
    temp_productos = list(productos)
    productos_arr = []
    productos_precio_arr = []

    for element in temp_productos:
        productos_arr.append(element['nombre'])
        productos_precio_arr.append([element['nombre'], element['precio']])

    productos_arr = simplejson.dumps(productos_arr)
    productos_precio_arr = simplejson.dumps(productos_precio_arr)

    # productos vendidos hoy con su cantidad respectiva
    fecha_hoy = datetime.date.today()
    productos_hoy = Transacciones.objects.filter(vendedor=v, fecha=fecha_hoy).values('nombreComida').annotate(
        conteo=Count('nombreComida'))
    temp_productos_hoy = list(productos_hoy)
    productos_hoy_arr = []

    for element in temp_productos_hoy:
        productos_hoy_arr.append([element['nombreComida'], element['conteo']])
    productos_hoy_arr = simplejson.dumps(productos_hoy_arr)

    return render(request, 'main/fijoDashboard.html',
                  {"transacciones": transacciones_diarias_arr, "ganancias": ganancias_diarias_arr,
                   "productos": productos_arr, "productosHoy": productos_hoy_arr,
                   "productosPrecio": productos_precio_arr})


def ambulante_dashboard(request):
    amb_id = request.POST.get("ambulanteId")
    v = Usuario.objects.get(id=amb_id).vendedor

    # transacciones hechas por hoy
    transacciones_diarias = Transacciones.objects.filter(vendedor=v).values('fecha').annotate(conteo=Count('fecha'))
    temp_transacciones_diarias = list(transacciones_diarias)
    transacciones_diarias_arr = []
    for element in temp_transacciones_diarias:
        transacciones_diarias_arr.append([element['fecha'].strftime("%Y-%m-%d"), element['conteo']])
    transacciones_diarias_arr = simplejson.dumps(transacciones_diarias_arr)

    # ganancias de hoy
    ganancias_diarias = Transacciones.objects.filter(vendedor=v).values('fecha').annotate(ganancia=Sum('precio'))
    temp_ganancias_diarias = list(ganancias_diarias)
    ganancias_diarias_arr = []
    for element in temp_ganancias_diarias:
        ganancias_diarias_arr.append([element['fecha'].strftime("%Y-%m-%d"), element['ganancia']])
    ganancias_diarias_arr = simplejson.dumps(ganancias_diarias_arr)

    # todos los productos del vendedor
    productos = Comida.objects.filter(vendedor=v).values('nombre', 'precio')
    temp_productos = list(productos)
    productos_arr = []
    productos_precio_arr = []
    for element in temp_productos:
        productos_arr.append(element['nombre'])
        productos_precio_arr.append([element['nombre'], element['precio']])
    productos_arr = simplejson.dumps(productos_arr)

    # productos vendidos hoy con su cantidad respectiva
    fecha_hoy = datetime.date.today()
    productos_hoy = Transacciones.objects.filter(vendedor=v, fecha=fecha_hoy).values('nombreComida').annotate(
        conteo=Count('nombreComida'))
    temp_productos_hoy = list(productos_hoy)
    productos_hoy_arr = []
    for element in temp_productos_hoy:
        productos_hoy_arr.append([element['nombreComida'], element['conteo']])
    productos_hoy_arr = simplejson.dumps(productos_hoy_arr)

    return render(request, 'main/ambulanteDashboard.html',
                  {"transacciones": transacciones_diarias_arr, "ganancias": ganancias_diarias_arr,
                   "productos": productos_arr, "productosHoy": productos_hoy_arr,
                   "productosPrecio": productos_precio_arr})


def admin_edit(request):
    nombre = request.POST.get("adminName")
    contraseña = request.POST.get("adminPassword")
    id_adm = request.POST.get("adminId")
    email = request.POST.get("adminEmail")
    avatar = request.POST.get("adminAvatar")
    return render(request, 'main/adminEdit.html',
                  {"nombre": nombre, "contraseña": contraseña, "id": id_adm, "email": email, "avatar": avatar})


def signup(request):
    return render(request, 'main/signup.html', {})


def signup_admin(request):
    return render(request, 'main/signupAdmin.html', {})


def loggedin(request):
    return render(request, 'main/loggedin.html', {})


def login_admin(request):
    id_adm = request.POST.get("userID")
    email = request.POST.get("email")
    avatar = "avatars/" + request.POST.get("fileName")
    nombre = request.POST.get("name")
    contraseña = request.POST.get("password")
    return admin_post(id_adm, avatar, email, nombre, contraseña, request)


def admin_post(id_adm, avatar, email, nombre, contraseña, request):
    # ids de todos los usuarios no admins
    datos_usuarios = []
    i = 0
    numero_usuarios = Usuario.objects.count()
    numero_de_comidas = Comida.objects.count()
    for usr in Usuario.objects.all():
        if usr.tipo != 0:
            datos_usuarios.append([])
            datos_usuarios[i].append(usr.id)
            datos_usuarios[i].append(usr.user.nombre)
            datos_usuarios[i].append(usr.user.email)
            datos_usuarios[i].append(usr.tipo)
            datos_usuarios[i].append(str(usr.avatar))
            '''
            datos_usuarios[i].append(usr.activo)
            datos_usuarios[i].append(usr.formasDePago)
            datos_usuarios[i].append(usr.horarioIni)
            datos_usuarios[i].append(usr.horarioFin)
            datos_usuarios[i].append(usr.contraseña)
            '''
            i += 1

    lista_de_usuarios = simplejson.dumps(datos_usuarios, ensure_ascii=False).encode('utf8')

    # limpiar argumentos de salida segun tipo de vista
    argumentos = {"nombre": nombre, "id": id_adm, "avatar": avatar, "email": email, "lista": lista_de_usuarios,
                  "numeroUsuarios": numero_usuarios, "numeroDeComidas": numero_de_comidas, "contraseña": contraseña}
    return render(request, 'main/baseAdmin.html', argumentos)


def obtener_favoritos(id_vendedor):
    favoritos = Favoritos.objects.filter(vendedor=Usuario.objects.get(id=id_vendedor).vendedor).count()
    return favoritos


def login_req(request):
    # inicaliar variables
    tipo = 0
    nombre = ''
    url = ''
    id_user = 0
    horario_ini = 0
    horario_fin = 0
    encontrado = False
    email = request.POST.get("email")
    avatar = ''
    contraseña = ''
    password = request.POST.get("password")
    lista_de_productos = []
    formas_de_pago = []
    activo = False

    # buscar vendedor en base de datos
    my_login_form = LoginForm(request.POST)
    if my_login_form.is_valid():
        vendedores = []

        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            usuario = user.usuario
            encontrado = True

            nombre = user.first_name
            id_user = usuario.id
            tipo = usuario.tipo
            avatar = usuario.avatar

            if tipo == 0:
                url = 'main/baseAdmin.html'
                contraseña = password

            elif tipo == 1:
                url = 'main/baseAlumno.html'

            elif tipo == 2:
                url = 'main/vendedor-fijo.html'

                horario_ini = usuario.vendedor.vendedorfijo.horarioIni
                horario_fin = usuario.vendedor.vendedorfijo.horarioFin
                request.session['horarioIni'] = horario_ini.strftime("%H:%M")
                request.session['horarioFin'] = horario_fin.strftime("%H:%M")

                formas_de_pago = usuario.vendedor.formasDePago
                request.session['formasDePago'] = formas_de_pago

                activo = usuario.vendedor.activo
                request.session['activo'] = activo

            elif tipo == 3:
                url = 'main/vendedor-ambulante.html'

                formas_de_pago = usuario.vendedor.formasDePago
                request.session['formasDePago'] = formas_de_pago

                activo = usuario.vendedor.activo
                request.session['activo'] = activo

        # si no se encuentra el usuario, se retorna a pagina de login
        if not encontrado:
            return render(request, 'main/login.html', {"error": "Usuario o contraseña invalidos"})

        # crear datos de sesion
        request.session['id'] = id_user
        request.session['tipo'] = tipo
        request.session['email'] = email
        request.session['nombre'] = nombre
        request.session['avatar'] = str(avatar)
        # si son vendedores, crear lista de productos
        for usuario in Usuario.objects.filter(tipo__in=[2, 3]):
            vendedores.append(usuario.id)
        vendedores_json = simplejson.dumps(vendedores)

        # obtener alimentos en caso de que sea vendedor fijo o ambulante
        if tipo == 2 or tipo == 3:
            i = 0
            for producto in Comida.objects.filter(vendedor=usuario.vendedor):
                lista_de_productos.append([])
                lista_de_productos[i].append(producto.nombre)
                categoria = str(producto.categorias)
                lista_de_productos[i].append(categoria)
                lista_de_productos[i].append(producto.stock)
                lista_de_productos[i].append(producto.precio)
                lista_de_productos[i].append(producto.descripcion)
                lista_de_productos[i].append(str(producto.imagen))
                i += 1

        lista_de_productos = simplejson.dumps(lista_de_productos, ensure_ascii=False).encode('utf8')

        vendedores_id = []
        vendedores_tipo = []
        vendedores_nombre = []
        vendedores_avatar = []
        vendedores_pago = []
        vendedores_ini = []
        vendedores_fin = []
        vendedores_lat = []
        vendedores_long = []
        # lista de vendedores
        i = 0
        for v in Vendedor.objects.all():
            ini = ""
            fin = ""
            if v.tipo == 2 and v.activo:
                vendedores_id.append(v.user.id)
                vendedores_tipo.append(v.tipo)
                vendedores_nombre.append(v.user.user.first_name)
                vendedores_avatar.append(str(v.user.avatar))
                vendedores_pago.append(v.formasDePago)
                vendedores_lat.append(v.lat)
                vendedores_long.append(v.long)
                vendedores_ini.append(ini)
                vendedores_fin.append(fin)
            if v.tipo == 1:
                vf = v.vendedorfijo
                hora_local = time.localtime()
                hora_local = datetime.time(hora_local.tm_hour, hora_local.tm_min)
                ini = vf.horarioIni.strftime("%H:%M")
                fin = vf.horarioFin.strftime("%H:%M")
                vendedores_ini.append(ini)
                vendedores_fin.append(fin)
                if vf.horarioIni <= hora_local <= vf.horarioFin:
                    v.activo = 1
                    vendedores_id.append(v.user.id)
                    vendedores_tipo.append(v.tipo)
                    vendedores_nombre.append(v.user.user.first_name)
                    vendedores_avatar.append(str(v.user.avatar))
                    vendedores_pago.append(v.formasDePago)
                    vendedores_lat.append(v.lat)
                    vendedores_long.append(v.long)
                else:
                    v.activo = 0
                v.save()
            i = i + 1

        nombres_v = simplejson.dumps(vendedores_nombre)
        tipo_v = simplejson.dumps(vendedores_tipo)
        ids = simplejson.dumps(vendedores_id)
        avatar_v = simplejson.dumps(vendedores_avatar)
        formas_de_pago_v = simplejson.dumps(vendedores_pago)
        horario_ini = simplejson.dumps(vendedores_ini)
        horario_fin = simplejson.dumps(vendedores_fin)
        lat = simplejson.dumps(vendedores_lat)
        long = simplejson.dumps(vendedores_long)

        # limpiar argumentos de salida segun tipo de vista
        argumentos = {"email": email, "tipo": tipo, "id": id_user, "vendedores": vendedores_json, "nombre": nombre,
                      "horarioIni": horario_ini, "horarioFin": horario_fin, "avatar": avatar,
                      "listaDeProductos": lista_de_productos}
        if tipo == 0:
            request.session['contraseña'] = contraseña
            return admin_post(id_user, avatar, email, nombre, contraseña, request)
        if tipo == 1:
            argumentos = {"nombresesion": nombre, "tipo": tipo, "vendedores": vendedores_json,
                          "avatarSesion": avatar, "nombre": nombres_v, "tipo": tipo_v, "id": ids, "avatar": avatar_v,
                          "formasDePago": formas_de_pago_v, "horarioIni": horario_ini, "horarioFin": horario_fin,
                          "lat": lat, "long": long}
        if tipo == 2:
            request.session['listaDeProductos'] = str(lista_de_productos)
            request.session['favoritos'] = obtener_favoritos(id_user)
            argumentos = {"nombre": nombre, "tipo": tipo, "id": id_user, "horarioIni": horario_ini,
                          "favoritos": obtener_favoritos(id_user), "horarioFin": horario_fin, "avatar": avatar,
                          "listaDeProductos": lista_de_productos, "activo": activo, "formasDePago": formas_de_pago}
        if tipo == 3:
            request.session['listaDeProductos'] = str(lista_de_productos)
            request.session['favoritos'] = obtener_favoritos(id_user)
            argumentos = {"nombre": nombre, "tipo": tipo, "id": id_user, "avatar": avatar,
                          "favoritos": obtener_favoritos(id_user),
                          "listaDeProductos": lista_de_productos, "activo": activo, "formasDePago": formas_de_pago}

        # enviar a vista respectiva de usuario
        return render(request, url, argumentos)

    # retornar en caso de datos invalidos
    else:
        return render(request, 'main/login.html', {"error": "Usuario o contraseña invalidos"})


def gestionproductos(request):
    path = ''
    if request.session.has_key('id'):
        tipo = request.session['tipo']
        if tipo == 3:
            path = "main/baseVAmbulante.html"
        if tipo == 2:
            path = "main/baseVFijo.html"
    return render(request, 'main/agregar-productos.html', {"path": path})


def vendedorprofilepage(request):
    return render(request, 'main/vendedor-profile-page.html', {})


def form_view(request):
    if request.session.has_key('id'):
        email = request.session['email']
        tipo = request.session['tipo']
        id_user = request.session['id']
        if tipo == 0:
            url = 'main/baseAdmin.html'
        elif tipo == 1:
            url = 'main/baseAlumno.html'
        elif tipo == 2:
            url = 'main/vendedor-fijo.html'
        else:
            url = 'main/vendedor-ambulante.html'
        return render(request, url, {"email": email, "tipo": tipo, "id": id_user})
    else:
        return render(request, 'main/base.html', {})


def log_out(request):
    try:
        del request.session['id']
        logout(request)
    except:
        pass
    return index(request)


def register(request):
    tipo = request.POST.get("tipo")
    nombre = request.POST.get("nombre")
    email = request.POST.get("email")
    password = request.POST.get("password")
    hora_inicial = request.POST.get("horaIni")
    hora_final = request.POST.get("horaFin")
    avatar = request.FILES.get("avatar")
    formas_de_pago = []

    if not (request.POST.get("formaDePago0") is None):
        formas_de_pago.append(request.POST.get("formaDePago0"))
    if not (request.POST.get("formaDePago1") is None):
        formas_de_pago.append(request.POST.get("formaDePago1"))
    if not (request.POST.get("formaDePago2") is None):
        formas_de_pago.append(request.POST.get("formaDePago2"))
    if not (request.POST.get("formaDePago3") is None):
        formas_de_pago.append(request.POST.get("formaDePago3"))

    user = User(username=email, first_name=nombre, email=email)
    user.set_password(password)
    user.save()

    usuario = Usuario(user=user, tipo=tipo, avatar=avatar)
    usuario.save()

    if int(tipo) == 2:
        vendedor = Vendedor(user=usuario, formasDePago=formas_de_pago, activo=False, tipo=1)
        vendedor.save()
        fijo = VendedorFijo(vendedor=vendedor, horarioIni=hora_inicial, horarioFin=hora_final)
        fijo.save()

    if int(tipo) == 3:
        vendedor = Vendedor(user=usuario, formasDePago=formas_de_pago, activo=False, tipo=2)
        vendedor.save()

    return login_req(request)


def producto_req(request):
    url = ''
    tipo = -1
    email = ''
    horario_ini = ''
    horario_fin = ''
    id_user = -1
    vendedor = None

    if request.method == "POST":
        if request.session.has_key('id'):

            id_user = request.session['id']
            email = request.session['email']
            tipo = request.session['tipo']
            path = ''

            if tipo == 3:
                path = "main/baseVAmbulante.html"
                url = "main/vendedor-ambulante.html"
            elif tipo == 2:
                path = "main/baseVFijo.html"
                url = "main/vendedor-fijo.html"
            else:
                return render(request, 'main/agregar-productos.html',
                              {"path": path, "respuesta": "¡Ingrese todos los datos!"})

            vendedor = Vendedor.objects.get(user=Usuario.objects.get(id=id_user))
            if tipo == 2:
                horario_ini = vendedor.vendedorfijo.horarioIni.strftime("%H:%M")
                horario_fin = vendedor.vendedorfijo.horarioFin.strftime("%H:%M")

            formulario = GestionProductosForm(request.POST)
            if formulario.is_valid():
                producto = Comida()
                producto.vendedor = vendedor
                producto.nombre = request.POST.get("nombre")
                producto.imagen = request.FILES.get("comida")
                producto.precio = request.POST.get("precio")
                producto.stock = request.POST.get("stock")
                producto.descripcion = request.POST.get("descripcion")
                producto.categorias = request.POST.get("categoria")
                producto.save()
            else:
                return render(request, 'main/agregar-productos.html',
                              {"path": path, "respuesta": "¡Ingrese todos los datos!"})

    # obtener alimentos en caso de que sea vendedor fijo o ambulante
    i = 0
    lista_de_productos = []
    for producto in Comida.objects.filter(vendedor=vendedor):
        lista_de_productos.append([])
        lista_de_productos[i].append(producto.nombre)
        categoria = str(producto.categorias)
        lista_de_productos[i].append(categoria)
        lista_de_productos[i].append(producto.stock)
        lista_de_productos[i].append(producto.precio)
        lista_de_productos[i].append(producto.descripcion)
        lista_de_productos[i].append(str(producto.imagen))
        i += 1
    lista_de_productos = simplejson.dumps(lista_de_productos, ensure_ascii=False).encode('utf8')

    p = Usuario.objects.get(id=id_user)
    avatar = p.avatar
    nombre = p.user.first_name

    return render(request, url,
                  {"email": email, "tipo": tipo, "id": id_user, "nombre": nombre, "horarioIni": horario_ini,
                   "horarioFin": horario_fin, "avatar": avatar, "listaDeProductos": lista_de_productos})


def vista_vendedor_por_alumno(request):
    if request.method == 'POST':
        id_v = int(request.POST.get("id"))
        v = Usuario.objects.get(id=id_v)

        favorito = 0
        if request.session['id']:
            u = Usuario.objects.get(id=request.session['id'])
            if Favoritos.objects.filter(vendedor=v.vendedor, alumno=u).exists():
                favorito = 1

        tipo = v.tipo
        nombre = v.user.first_name
        avatar = v.avatar
        formas_de_pago = v.vendedor.formasDePago

        horario_ini = ''
        horario_fin = ''
        url = ''
        if tipo == 3:
            url = 'main/vendedor-ambulante-vistaAlumno.html'
        if tipo == 2:
            url = 'main/vendedor-fijo-vistaAlumno.html'
            horario_ini = v.vendedor.vendedorfijo.horarioIni.strftime("%H:%M")
            horario_fin = v.vendedor.vendedorfijo.horarioFin.strftime("%H:%M")

        # obtener alimentos
        i = 0
        lista_de_productos = []
        for producto in Comida.objects.filter(vendedor=v.vendedor):
            lista_de_productos.append([])
            lista_de_productos[i].append(producto.nombre)
            categoria = str(producto.categorias)
            lista_de_productos[i].append(categoria)
            lista_de_productos[i].append(producto.stock)
            lista_de_productos[i].append(producto.precio)
            lista_de_productos[i].append(producto.descripcion)
            lista_de_productos[i].append(str(producto.imagen))
            i += 1
        avatar_sesion = request.session['avatar']
        lista_de_productos = simplejson.dumps(lista_de_productos, ensure_ascii=False).encode('utf8')
        return render(request, url,
                      {"nombre": nombre, "nombresesion": request.session['nombre'], "tipo": tipo, "id": id_v,
                       "avatar": avatar, "listaDeProductos": lista_de_productos, "avatarSesion": avatar_sesion,
                       "favorito": favorito, "formasDePago": formas_de_pago, "horarioIni": horario_ini,
                       "horarioFin": horario_fin, })

    return None


def vista_vendedor_por_alumno_sin_login(request):
    if request.method == 'POST':
        id_user = int(request.POST.get("id"))
        user = Usuario.objects.get(id=id_user)
        tipo = user.tipo
        nombre = user.user.first_name
        avatar = user.avatar
        formas_de_pago = user.vendedor.formasDePago
        url = ''
        horario_ini = ''
        horario_fin = ''
        activo = user.vendedor.activo

        if tipo == 3:
            url = 'main/vendedor-ambulante-vistaAlumno-sinLogin.html'
        if tipo == 2:
            url = 'main/vendedor-fijo-vistaAlumno-sinLogin.html'
            horario_ini = user.vendedor.vendedorfijo.horarioIni.strftime("%H:%M")
            horario_fin = user.vendedor.vendedorfijo.horarioFin.strftime("%H:%M")

        i = 0
        lista_de_productos = []
        for producto in Comida.objects.filter(vendedor=user.vendedor):
            lista_de_productos.append([])
            lista_de_productos[i].append(producto.nombre)
            categoria = str(producto.categorias)
            lista_de_productos[i].append(categoria)
            lista_de_productos[i].append(producto.stock)
            lista_de_productos[i].append(producto.precio)
            lista_de_productos[i].append(producto.descripcion)
            lista_de_productos[i].append(str(producto.imagen))
            i += 1
        lista_de_productos = simplejson.dumps(lista_de_productos, ensure_ascii=False).encode('utf8')

        return render(request, url,
                      {"nombre": nombre, "tipo": tipo, "id": id_user, "avatar": avatar,
                       "listaDeProductos": lista_de_productos,
                       "formasDePago": formas_de_pago, "horarioIni": horario_ini, "horarioFin": horario_fin,
                       "activo": activo})


def editar_vendedor(request):
    if request.session.has_key('id'):
        id_user = request.session['id']
        nombre = request.session['nombre']
        formas_de_pago = request.session['formasDePago']
        avatar = request.session['avatar']
        tipo = request.session['tipo']
        activo = request.session['activo']
        lista_de_productos = request.session['listaDeProductos']
        favoritos = request.session['favoritos']

        url = ''
        argumentos = {}

        if tipo == 2:
            horario_ini = request.session['horarioIni']
            horario_fin = request.session['horarioFin']
            argumentos = {"nombre": nombre, "tipo": tipo, "id": id_user, "horarioIni": horario_ini,
                          "horarioFin": horario_fin,
                          "avatar": avatar, "listaDeProductos": lista_de_productos, "activo": activo,
                          "formasDePago": formas_de_pago, "favoritos": favoritos}
            url = 'main/editar-vendedor-fijo.html'

        elif tipo == 3:
            argumentos = {"nombre": nombre, "tipo": tipo, "id": id_user, "avatar": avatar,
                          "listaDeProductos": lista_de_productos,
                          "activo": activo, "formasDePago": formas_de_pago, "favoritos": favoritos}
            url = 'main/editar-vendedor-ambulante.html'

        return render(request, url, argumentos)

    return render(request, 'main/base.html', {})


def editar_datos(request):
    id_vendedor = request.POST.get("id_vendedor")
    usuario = Usuario.objects.get(id=id_vendedor)

    nombre = request.POST.get("nombre")
    tipo = request.POST.get("tipo")

    if tipo == "2":
        hora_inicial = request.POST.get("horaIni")
        hora_final = request.POST.get("horaFin")
        if hora_inicial is not None:
            usuario.vendedor.vendedorfijo.horarioIni = hora_inicial
        if hora_final is not None:
            usuario.vendedor.vendedorfijo.horarioFin = hora_final

        usuario.vendedor.vendedorfijo.save()

    # actualizar vendedores fijos
    for v in Vendedor.objects.all():
        if v.tipo == 1:
            vf = v.vendedorfijo
            hora_local = time.localtime()
            hora_local = datetime.time(hora_local.tm_hour, hora_local.tm_min)
            if vf.horarioIni <= hora_local <= vf.horarioFin:
                v.activo = 1
            else:
                v.activo = 0
            v.save()

    avatar = request.FILES.get("avatar")
    formas_de_pago = ""
    if request.POST.get("formaDePago0") is not None and request.POST.get("formaDePago0") != "":
        formas_de_pago += '0,'
    if request.POST.get("formaDePago1") is not None and request.POST.get("formaDePago1") != "":
        formas_de_pago += '1,'
    if request.POST.get("formaDePago2") is not None and request.POST.get("formaDePago2") != "":
        formas_de_pago += '2,'
    if request.POST.get("formaDePago3") is not None and request.POST.get("formaDePago3") != "":
        formas_de_pago += '3,'

    if nombre is not None and nombre != "":
        usuario.user.nombre = nombre
    if formas_de_pago != "":
        usuario.vendedor.formasDePago = formas_de_pago[:-1]
    if avatar is not None and avatar != "":
        with default_storage.open('../media/avatars/' + str(avatar), 'wb+') as destination:
            for chunk in avatar.chunks():
                destination.write(chunk)
        usuario.avatar = '/avatars/' + str(avatar)

    usuario.save()

    return redirigir_editar(id_vendedor, request)


def redirigir_editar(id_vendedor, request):
    usr = Usuario.objects.get(id=id_vendedor)

    id_v = usr.id
    nombre = usr.user.first_name
    tipo = usr.tipo
    avatar = usr.avatar
    activo = usr.vendedor.activo
    formas_de_pago = usr.vendedor.formasDePago
    horario_ini = ''
    horario_fin = ''
    if tipo == 2:
        horario_ini = usr.vendedor.vendedorfijo.horarioIni.strftime("%H:%M")
        horario_fin = usr.vendedor.vendedorfijo.horarioFin.strftime("%H:%M")
    favoritos = obtener_favoritos(id_vendedor)

    request.session['id'] = id_v
    request.session['nombre'] = nombre
    request.session['formasDePago'] = formas_de_pago
    request.session['avatar'] = str(avatar)
    request.session['tipo'] = tipo
    request.session['activo'] = activo
    request.session['horarioIni'] = horario_ini
    request.session['horarioFin'] = horario_fin
    request.session['favoritos'] = favoritos

    lista_de_productos = []
    i = 0
    for producto in Comida.objects.filter(vendedor=usr.vendedor):
        lista_de_productos.append([])
        lista_de_productos[i].append(producto.nombre)
        categoria = str(producto.categorias)
        lista_de_productos[i].append(categoria)
        lista_de_productos[i].append(producto.stock)
        lista_de_productos[i].append(producto.precio)
        lista_de_productos[i].append(producto.descripcion)
        lista_de_productos[i].append(str(producto.imagen))
        i += 1

    lista_de_productos = simplejson.dumps(lista_de_productos, ensure_ascii=False).encode('utf8')
    request.session['listaDeProductos'] = str(lista_de_productos)

    url = ''
    argumentos = {}
    if tipo == 2:
        url = 'main/vendedor-fijo.html'
        argumentos = {"nombre": nombre, "tipo": tipo, "id": id_v, "horarioIni": horario_ini, "horarioFin": horario_fin,
                      "avatar": avatar, "listaDeProductos": lista_de_productos, "activo": activo,
                      "formasDePago": formas_de_pago, "favoritos": favoritos}
    elif tipo == 3:
        url = 'main/vendedor-ambulante.html'
        argumentos = {"nombre": nombre, "tipo": tipo, "id": id_v, "avatar": avatar,
                      "listaDeProductos": lista_de_productos,
                      "activo": activo, "formasDePago": formas_de_pago, "favoritos": favoritos}

    return render(request, url, argumentos)


def inicio_alumno(request):
    id_user = request.session['id']
    avatarUser = None
    usuario = None
    for p in Usuario.objects.all():
        if p.id == id_user:
            avatarUser = p.avatar
            usuario = p

    vendedores_id = []
    vendedores_tipo = []
    vendedores_nombre = []
    vendedores_avatar = []
    vendedores_pago = []
    vendedores_ini = []
    vendedores_fin = []
    vendedores_lat = []
    vendedores_long = []
    favoriteado = []
    # lista de vendedores
    i = 0
    for v in Vendedor.objects.all():
        ini = ""
        fin = ""
        try:
            Favoritos.objects.get(alumno=usuario, vendedor = v)
        except ObjectDoesNotExist :
            favoriteado.append(0)
        else:
            favoriteado.append(1)
        if v.tipo == 2 and v.activo:
            vendedores_id.append(v.user.id)
            vendedores_tipo.append(v.tipo)
            vendedores_nombre.append(v.user.user.first_name)
            vendedores_avatar.append(str(v.user.avatar))
            vendedores_pago.append(v.formasDePago)
            vendedores_lat.append(v.lat)
            vendedores_long.append(v.long)
            vendedores_ini.append(ini)
            vendedores_fin.append(fin)
        if v.tipo == 1:
            vf = v.vendedorfijo
            hora_local = time.localtime()
            hora_local = datetime.time(hora_local.tm_hour, hora_local.tm_min)
            ini = vf.horarioIni.strftime("%H:%M")
            fin = vf.horarioFin.strftime("%H:%M")
            vendedores_ini.append(ini)
            vendedores_fin.append(fin)
            if vf.horarioIni <= hora_local <= vf.horarioFin:
                v.activo = 1
                vendedores_id.append(v.user.id)
                vendedores_tipo.append(v.tipo)
                vendedores_nombre.append(v.user.user.first_name)
                vendedores_avatar.append(str(v.user.avatar))
                vendedores_pago.append(v.formasDePago)
                vendedores_lat.append(v.lat)
                vendedores_long.append(v.long)
            else:
                v.activo = 0
            v.save()
        i = i + 1

    nombre = simplejson.dumps(vendedores_nombre)
    tipo = simplejson.dumps(vendedores_tipo)
    id = simplejson.dumps(vendedores_id)
    avatar = simplejson.dumps(vendedores_avatar)
    formas_de_pago = simplejson.dumps(vendedores_pago)
    horario_ini = simplejson.dumps(vendedores_ini)
    horario_fin = simplejson.dumps(vendedores_fin)
    lat = simplejson.dumps(vendedores_lat)
    long = simplejson.dumps(vendedores_long)
    favoritos = simplejson.dumps(favoriteado)

    return render(request, 'main/baseAlumno.html',
                  {"userid": id_user, "avatarSesion": avatarUser,
                   "nombresesion": request.session['nombre'], "nombre": nombre, "tipo": tipo, "id": id,
                   "avatar": avatar, "formasDePago": formas_de_pago, "horarioIni": horario_ini,
                   "horarioFin": horario_fin, "lat": lat, "long": long, "favoritos": favoritos})


@csrf_exempt
def borrar_producto(request):
    if request.method == 'GET':
        if request.is_ajax():
            comida = request.GET.get('eliminar')
            Comida.objects.filter(nombre=comida).delete()
            data = {"eliminar": comida}
            return JsonResponse(data)


@csrf_exempt
def editar_producto(request):
    if request.method == 'POST':
        if request.is_ajax():

            nombre_original = request.POST.get("nombreOriginal")
            nuevo_nombre = request.POST.get('nombre')
            nuevo_precio = (request.POST.get('precio'))
            nuevo_stock = (request.POST.get('stock'))
            nueva_descripcion = request.POST.get('descripcion')
            nueva_categoria = (request.POST.get('categoria'))
            nueva_imagen = request.FILES.get("comida")
            if nuevo_precio != "":
                Comida.objects.filter(nombre=nombre_original).update(precio=int(nuevo_precio))
            if nuevo_stock != "":
                Comida.objects.filter(nombre=nombre_original).update(stock=int(nuevo_stock))
            if nueva_descripcion != "":
                Comida.objects.filter(nombre=nombre_original).update(descripcion=nueva_descripcion)
            if nueva_categoria is not None:
                Comida.objects.filter(nombre=nombre_original).update(categorias=(nueva_categoria))
            if nueva_imagen is not None:
                filename = nombre_original + ".jpg"
                with default_storage.open('../media/productos/' + filename, 'wb+') as destination:
                    for chunk in nueva_imagen.chunks():
                        destination.write(chunk)
                Comida.objects.filter(nombre=nombre_original).update(imagen='/productos/' + filename)

            if nuevo_nombre != "":
                if Comida.objects.filter(nombre=nuevo_nombre).exists():
                    data = {"respuesta": "repetido"}
                    return JsonResponse(data)
                else:
                    Comida.objects.filter(nombre=nombre_original).update(nombre=nuevo_nombre)

            data = {"respuesta": nombre_original}
            return JsonResponse(data)


def cambiar_favorito(request):
    if request.method == "GET":
        if request.is_ajax():
            favorito = request.GET.get('favorito')
            agregar = request.GET.get('agregar')

            alumno = Usuario.objects.get(id=request.session['id'])
            vendedor = Usuario.objects.get(id=favorito).vendedor
            if agregar == "si":
                nuevo_favorito = Favoritos(alumno=alumno, vendedor=vendedor)
                nuevo_favorito.save()
                respuesta = {"respuesta": "si"}
            else:
                Favoritos.objects.filter(alumno=alumno, vendedor=vendedor).delete()
                respuesta = {"respuesta": "no"}
            return JsonResponse(respuesta)


def cambiar_estado(request):
    if request.method == 'GET':
        if request.is_ajax():
            estado = request.GET.get('estado')

            id_vendedor = request.GET.get('id')
            vendedor = Usuario.objects.get(id=id_vendedor).vendedor

            if estado == "true":
                vendedor.activo = True
            else:
                vendedor.activo = False
            vendedor.save()

            data = {"estado": estado}
            return JsonResponse(data)


def editar_perfil_alumno(request):
    avatar = request.session['avatar']
    id_user = request.session['id']
    nombre = request.session['nombre']
    user = Usuario.objects.get(id=id_user)

    favoritos = []
    nombres = []
    for fav in Favoritos.objects.filter(alumno=user):
        favoritos.append(fav.vendedor.user.id)
        nombre = fav.vendedor.user.user.first_name
        nombres.append(nombre)

    return render(request, 'main/editar-perfil-alumno.html',
                  {"id": id_user, "avatarSesion": avatar, "nombre": nombre, "favoritos": favoritos, "nombres": nombres,
                   "nombresesion": request.session['nombre']})


def procesar_perfil_alumno(request):
    if request.method == "POST":
        nombre_original = request.session['nombre']
        nuevo_nombre = request.POST.get("nombre")
        count = request.POST.get("switchs")
        a_eliminar = []
        nueva_imagen = request.FILES.get("comida")

        id_user = request.session['id']
        user = Usuario.objects.get(id=id_user)

        for i in range(int(count)):
            fav = request.POST.get("switch" + str(i))
            if fav != "":
                a_eliminar.append(int(fav))

        if nuevo_nombre != "":
            user.user.nombre = nuevo_nombre
            user.user.save()

        for id_fav in a_eliminar:
            fav = Favoritos.objects.get(alumno=user, vendedor=Usuario.objects.get(id=id_fav).vendedor)
            fav.delete()

        if nueva_imagen is not None:
            filename = nombre_original + ".jpg"
            with default_storage.open('../media/avatars/' + filename, 'wb+') as destination:
                for chunk in nueva_imagen.chunks():
                    destination.write(chunk)

            user.avatar = '/avatars/' + filename
            user.save()

        return JsonResponse({"ejemplo": "correcto"})


@csrf_exempt
def borrar_usuario(request):
    if request.method == 'GET':
        if request.is_ajax():
            u_id = request.GET.get('eliminar')
            Usuario.objects.filter(id=u_id).delete()
            data = {"eliminar": u_id}
            return JsonResponse(data)


@csrf_exempt
def agregar_avatar(request):
    if request.is_ajax() or request.method == 'FILES':
        imagen = request.FILES.get("image")
        # nuevaImagen = Imagen(imagen=imagen)
        # nuevaImagen.save()
        return HttpResponse("Success")


def editar_usuario_admin(request):
    if request.method == 'GET':
        nombre = request.GET.get("name")
        contraseña = request.GET.get('password')
        email = request.GET.get('email')
        avatar = request.GET.get('avatar')
        user_id = request.GET.get('userID')

        user = Usuario.objects.get(id=user_id)

        if email is not None:
            user.user.email = email
        if nombre is not None:
            user.user.first_name = nombre
        if contraseña is not None:
            user.user.set_password(contraseña)
        if avatar is not None:
            user.avatar = avatar

        user.user.save()
        user.save()

        data = {"respuesta": user_id}
        return JsonResponse(data)


def editar_usuario(request):
    if request.method == 'GET':

        nombre = request.GET.get("name")
        contraseña = request.GET.get('password')
        tipo = request.GET.get('type')
        email = request.GET.get('email')
        avatar = request.GET.get('avatar')
        forma0 = request.GET.get('forma0')
        forma1 = request.GET.get('forma1')
        forma2 = request.GET.get('forma2')
        forma3 = request.GET.get('forma3')
        hora_ini = request.GET.get('horaIni')
        hora_fin = request.GET.get('horaFin')
        user_id = request.GET.get('userID')

        nueva_lista_formas_de_pago = ""
        if forma0 is not None:
            nueva_lista_formas_de_pago += "0"
        if forma1 is not None:
            if len(nueva_lista_formas_de_pago) != 0:
                nueva_lista_formas_de_pago += ",1"
            else:
                nueva_lista_formas_de_pago += "1"
        if forma2 is not None:
            if len(nueva_lista_formas_de_pago) != 0:
                nueva_lista_formas_de_pago += ",2"
            else:
                nueva_lista_formas_de_pago += "2"
        if forma3 is not None:
            if len(nueva_lista_formas_de_pago) != 0:
                nueva_lista_formas_de_pago += ",3"
            else:
                nueva_lista_formas_de_pago += "3"

        user = Usuario.objects.get(id=user_id)
        if email is not None:
            user.user.email = email
        if nombre is not None:
            user.user.first_name = nombre
        if contraseña is not None:
            user.user.set_password(contraseña)
        user.user.save()

        if tipo is not None:
            user.tipo = tipo
        if avatar is not None:
            user.avatar = avatar
        user.save()

        if tipo == 2:
            if hora_ini is not None:
                user.vendedor.vendedorfijo.horarioIni = hora_ini
            if hora_fin is not None:
                user.vendedor.vendedorfijo.horarioFin = hora_fin
            user.vendedor.formasDePago = nueva_lista_formas_de_pago

            user.vendedor.save()
            user.vendedor.vendedorfijo.save()

        if tipo == 2:
            user.vendedor.formasDePago = nueva_lista_formas_de_pago
            user.vendedor.save()

        data = {"respuesta": user_id}
        return JsonResponse(data)


def register_admin(request):
    nombre = request.POST.get("nombre")
    email = request.POST.get("email")
    password = request.POST.get("password")

    tipo = request.POST.get("tipo")
    avatar = request.FILES.get("avatar")

    hora_inicial = request.POST.get("horaIni")
    hora_final = request.POST.get("horaFin")
    formas_de_pago = []
    if not (request.POST.get("formaDePago0") is None):
        formas_de_pago.append(request.POST.get("formaDePago0"))
    if not (request.POST.get("formaDePago1") is None):
        formas_de_pago.append(request.POST.get("formaDePago1"))
    if not (request.POST.get("formaDePago2") is None):
        formas_de_pago.append(request.POST.get("formaDePago2"))
    if not (request.POST.get("formaDePago3") is None):
        formas_de_pago.append(request.POST.get("formaDePago3"))

    user = User(first_name=nombre, email=email)
    user.set_password(password)
    usuario = Usuario(user=user, tipo=tipo, avatar=avatar)
    usuario.save()

    id_adm = request.session['id']
    email = request.session['email']
    avatar = request.session['avatar']
    nombre = request.session['nombre']
    contraseña = request.session['contraseña']
    return admin_post(id_adm, avatar, email, nombre, contraseña, request)


@csrf_exempt
def verificar_email(request):
    if request.is_ajax() or request.method == 'POST':
        email = request.POST.get("email")
        if User.objects.filter(email=email).exists():
            data = {"respuesta": "repetido"}
            return JsonResponse(data)
        else:
            data = {"respuesta": "disponible"}
            return JsonResponse(data)


def get_stock(request):
    if request.method == "GET":

        nombre = request.GET.get("nombre")
        comida = Comida.objects.get(nombre=nombre)
        stock = comida.stock

        if request.GET.get("op") == "suma":
            nuevo_stock = stock + 1
            comida.stock = nuevo_stock
            comida.save()

        elif request.GET.get("op") == "resta":
            nuevo_stock = stock - 1
            if stock == 0:
                return JsonResponse({"stock": stock})
            comida.stock = nuevo_stock
            comida.save()

    return JsonResponse({"stock": stock})


def create_transaction(request):
    nombre_producto = request.GET.get("nombre")
    precio = 0
    id_vendedor = request.GET.get("idUsuario")
    if Comida.objects.filter(nombre=nombre_producto).exists():
        precio = Comida.objects.filter(nombre=nombre_producto).values('precio')[0]
        lista_aux = list(precio.values())
        precio = lista_aux[0]
    else:
        return HttpResponse('error message')

    v = Usuario.objects.get(id=id_vendedor).vendedor
    transaccion_nueva = Transacciones(vendedor=v, precio=precio, nombreComida=nombre_producto,
                                      fecha=datetime.date.today())
    transaccion_nueva.save()
    return JsonResponse({"transaccion": "realizada"})
