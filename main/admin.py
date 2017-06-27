from django.contrib import admin

from .models import *

admin.site.register(Usuario)
admin.site.register(Vendedor)
admin.site.register(VendedorFijo)
admin.site.register(Comida)
admin.site.register(Transacciones)
admin.site.register(Favoritos)
