from django.contrib import admin
from django.core.exceptions import ValidationError
from django.forms.models import BaseInlineFormSet
from panchoneta.models import *

# registros

@admin.register(Sucursal)
class SucursalAdmin(admin.ModelAdmin):
    #nombre, calle, nroCalle, piso
    list_display = ('nombre','calle','nroCalle','piso')

@admin.register(Salsa)
class SalsaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'descripcion')
    search_fields = ['nombre']


#se realiza la validación de asignar máximo 3 salsas al pancho cuando se crea
class DetallePanchoInlineFormset(BaseInlineFormSet):
    def clean(self):
        super().clean()
        total_forms = len([form for form in self.forms if not form.cleaned_data.get('DELETE', False)])
        if total_forms > 3:
            raise ValidationError('No puede asignar más de 3 salsas a un pancho.')

class DetallePanchoInline(admin.TabularInline):
    model = DetallePancho
    extra = 0
    max_num = 3
    formset = DetallePanchoInlineFormset
    verbose_name = "Detalle del Pancho | Salsa que incluye"
    verbose_name_plural = "Detalles del Pancho | Salsas que incluye"

#registros admin especificos (personalizados)
@admin.register(Pancho)
class PanchoAdmin(admin.ModelAdmin):
    inlines = [DetallePanchoInline] #aca agregaríamos las salsas y se vería como un detalle de pancho
    list_display = ('nombre', 'precio')
    search_fields = ['nombre']

@admin.register(Bebida)
class BebidaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'precio']
    search_fields = ['nombre']

#----INLINES PARA VENTA------
#primer inline, detallepanchoventa, se define las columnas que queremos ver
class DetallePanchoVentaInline(admin.TabularInline):
    model = DetallePanchoVenta
    extra = 0
    readonly_fields = ['subtotal']
    fields = ('pancho', 'cantidad', 'subtotal')
    verbose_name = "Detalle de la venta de Pancho"
    verbose_name_plural = "Detalles de la venta de Pancho"

#segundo inline, detallebebidaventas, se definen las columnas que queremos ver
class DetalleBebidaVentaInline(admin.TabularInline):
    model = DetalleBebidaVenta
    extra = 0
    readonly_fields = ['subtotal']
    fields = ('bebida', 'cantidad', 'subtotal')
    verbose_name = "Detalle de la venta de Bebida"
    verbose_name_plural = "Detalles de la venta de Bebida"

#register venta
@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    inlines = [DetallePanchoVentaInline, DetalleBebidaVentaInline]
    list_display = ('fecha','hora', 'sucursal', 'total')
    ordering = ['fecha']
    list_filter = ['sucursal']
    readonly_fields = ['total']

    def total(self, obj):
        return obj.calcular_total()
    total.short_description = 'Total de la Venta'


