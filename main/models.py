import datetime

from django.contrib.auth.models import User
from django.db import models
from multiselectfield import MultiSelectField


class Usuario(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    tipos = ((0, 'admin'), (1, 'alumno'), (2, 'fijo'), (3, 'ambulante'))
    tipo = models.IntegerField(choices=tipos)
    avatar = models.ImageField(upload_to='avatars')

    def __str__(self):
        return self.user.username

    class Meta:
        ordering = ["user"]
        db_table = 'usuario'


class Vendedor(models.Model):
    user = models.OneToOneField(Usuario, on_delete=models.CASCADE)

    lat = models.IntegerField(null=True)
    long = models.IntegerField(null=True)

    activo = models.BooleanField(default=False, blank=True)
    listaFormasDePago = (
        (0, 'Efectivo'),
        (1, 'Tarjeta de Crédito'),
        (2, 'Tarjeta de Débito'),
        (3, 'Tarjeta Junaeb'),
    )
    formasDePago = MultiSelectField(choices=listaFormasDePago, null=True, blank=True)

    tipos = (
        (1, "fijo"),
        (2, "ambulante"),
    )
    tipo = models.IntegerField(choices=tipos, default=2)

    class Meta:
        ordering = ["user"]

    def __str__(self):
        return str(self.user)


class VendedorFijo(models.Model):
    vendedor = models.OneToOneField(Vendedor, on_delete=models.CASCADE)

    horarioIni = models.TimeField()
    horarioFin = models.TimeField()

    def __str__(self):
        return "Vendedor Fijo: " + str(self.vendedor)


class Comida(models.Model):
    vendedor = models.ForeignKey(Vendedor, on_delete=models.CASCADE)

    nombre = models.CharField(max_length=200, primary_key=True)
    descripcion = models.CharField(max_length=500)
    stock = models.PositiveSmallIntegerField(default=0)
    precio = models.PositiveSmallIntegerField(default=0)

    imagen = models.ImageField(upload_to="productos")

    listaCategorias = (
        (0, 'Cerdo'),
        (1, 'Chino'),
        (2, 'Completos'),
        (3, 'Egipcio'),
        (4, 'Empanadas'),
        (5, 'Ensalada'),
        (6, 'Japones'),
        (7, 'Pan'),
        (8, 'Papas fritas'),
        (9, 'Pasta'),
        (10, 'Pescado'),
        (11, 'Pollo'),
        (12, 'Postres'),
        (13, 'Sushi'),
        (14, 'Vacuno'),
        (15, 'Vegano'),
        (16, 'Vegetariano'),
    )
    categorias = MultiSelectField(choices=listaCategorias)

    def __str__(self):
        return "%s: %s" % (str(self.vendedor), self.nombre)

    class Meta:
        ordering = ["vendedor", "nombre"]
        db_table = 'Comida'


class Favoritos(models.Model):
    alumno = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    vendedor = models.ForeignKey(Vendedor, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return str(self.alumno) + " " + str(self.vendedor)

    class Meta:
        ordering = ["alumno", "vendedor"]
        db_table = 'Favoritos'


class Transacciones(models.Model):
    vendedor = models.ForeignKey(Vendedor, on_delete=models.CASCADE, null=True)

    nombreComida = models.CharField(max_length=200, blank=True, null=True)
    precio = models.IntegerField()
    fecha = models.DateField()  # default=datetime.date.today()

    def __str__(self):
        return "%s: %s-%i" % (str(self.vendedor), self.nombreComida, self.precio)

    class Meta:
        ordering = ["fecha", "nombreComida"]
        db_table = 'transacciones'
