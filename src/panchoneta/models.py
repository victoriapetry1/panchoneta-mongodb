from django.db import models
from django.utils.translation import gettext_lazy as _

#clases abstractas
class NombreAbstract(models.Model):
    nombre = models.CharField(
        _('Nombre'),
        help_text=_('Nombre descriptivo'),
        max_length=200,
    )

    def save(self, *args, **kwargs):
        self.nombre = self.nombre.upper()
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.nombre

    class Meta:
        abstract = True
        ordering = ['nombre']

class BaseModel(models.Model):
    class Meta:
        abstract = True


#clases del modelo
class Bebida(NombreAbstract):
    nombre = models.CharField(_('nombre'), 
            help_text=_('nombre de la bebida'),
            blank=True,
            null=True,
            max_length=120
        )
    precio = models.DecimalField( _('precio'),
            help_text=_('Precio de la bebida'),
            max_digits=10,
            decimal_places=2,
            blank=True,
            null=True
        )
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs) #Asignacion del id

        try:
            from .models_mongo import Bebida as BebidaMongo
            BebidaMongo.objects(postgres_id=self.id).update_one(
                set__nombre=self.nombre,
                set__precio=self.precio,
                upsert=True
            )
        except Exception as e:
            print(f"Error sincronizando con MongoDB: {e}")

class Pancho(NombreAbstract):
    #idPancho, nombre, precio
    nombre = models.CharField(_('nombre'),
                              help_text=_('nombre del pancho'),
                              blank=False,
                              null=False,
                             max_length=120
                            )
    
    precio = models.DecimalField(_('precio'),
                                    max_digits=15,
                                    decimal_places=2,
                                    help_text=_('precio del pancho expresado en pesos'),
                                    default=0
                                )
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs) #Asignacion del id

        try:
            from .models_mongo import Pancho as PanchoMongo
            PanchoMongo.objects(postgres_id=self.id).update_one(
                set__nombre=self.nombre,
                set__precio=self.precio,
                upsert=True
            )
        except Exception as e:
            print(f"Error sincronizando con MongoDB: {e}")

    class Meta:
        verbose_name= 'pancho'
        verbose_name_plural = 'panchos'

class Salsa(NombreAbstract):
    
    #idSalsa, nombreSalsa, descripcion
    nombre = models.CharField(_('nombre'),
                                   help_text=_('nombre de la salsa'),
                                   blank = True,
                                   null=True,
                                    max_length=120
                                )
    
    descripcion = models.TextField(_('descripcion'),
                                   help_text=_('descripcion de la salsa'),
                                   blank=True,
                                   null=True)
    
    class Meta:
        verbose_name='salsa'
        verbose_name_plural='salsas'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs) #Asignacion del id

        try:
            from .models_mongo import Salsa as SalsaMongo
            SalsaMongo.objects(postgres_id=self.id).update_one(
                set__nombre=self.nombre,
                set__descripcion=self.descripcion,
                upsert=True
            )
        except Exception as e:
            print(f"Error sincronizando con MongoDB: {e}")

    
    
class Sucursal(NombreAbstract):
    #nombre, calle, nroCalle, piso
    nombre = models.CharField(_('nombre'), 
                                help_text=_('nombre de la sucursal'),
                                blank=True,
                                null=True,
                                max_length=120
                            )
    
    calle = models.CharField(_('calle'), 
                             help_text=_('calle de la sucursal'),
                             blank=True,
                             null=True,
                             max_length=120
                             )
    
    nroCalle = models.BigIntegerField(_('nroCalle'),
                                      help_text=_('nro. de la calle'),
                                      blank=True,
                                      null=True
                            )
    
    piso = models.BigIntegerField(_('piso'),
                                  help_text=_('nro. de piso'),
                                  blank=True,
                                  null=True
                                 )
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs) #Asignacion del id

        try:
            from .models_mongo import Sucursal as SucursalMongo
            SucursalMongo.objects(postgres_id=self.id).update_one(
                set__nombre=self.nombre,
                set__calle=self.calle,
                set__nroCalle=self.nroCalle,
                set__piso=self.piso,
                upsert=True
            )
        except Exception as e:
            print(f"Error sincronizando con MongoDB: {e}")
    

#tabla intermedia
class DetallePancho(models.Model):
    idSalsa = models.ForeignKey(Salsa, on_delete=models.PROTECT, verbose_name='Salsa')
    idPancho = models.ForeignKey(Pancho, on_delete=models.PROTECT, verbose_name='Pancho')

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs) #Asignacion del id

        try:
            from .models_mongo import DetallePancho as DetallePMongo,Salsa as SalsaMongo,Pancho as PanchoMongo
            DetallePMongo.objects(postgres_id=self.id).update_one(
                set__idSalsa=SalsaMongo.objects.get(postgres_id=self.idSalsa),
                set__idPancho=PanchoMongo.objects.get(postgres_id=self.idPancho),
                upsert=True
            )
        except Exception as e:
            print(f"Error sincronizando con MongoDB: {e}")

    


#venta y detalles separados
#por un lado tenemos detalle pancho ventas que incluye los detalles de la venta pero referidos a panchos
#y por otro lado tenemos detalle bebida venta que incluye los detalles de la venta pero referidos a bebidas


class Venta(models.Model):
    fecha = models.DateField(_('fecha'), blank=True, null=True)
    hora = models.TimeField(_('hora'), blank=True, null=True)
    sucursal = models.ForeignKey(Sucursal, on_delete=models.PROTECT)

    def __str__(self):
        return f"Venta #{self.pk} - {self.fecha} - {self.sucursal.nombre}"

    #total de la venta, se suman los detalles tanto de panchos como de bebidas
    def calcular_total(self):
        total_panchos = sum(dp.subtotal for dp in self.detalles_panchos.all())
        total_bebidas = sum(db.subtotal for db in self.detalles_bebidas.all())
        return total_panchos + total_bebidas
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs) #Asignacion del id

        try:
            from .models_mongo import Venta as VentaMongo, Sucursal as SucursalMongo
            VentaMongo.objects(postgres_id=self.id).update_one(
                set__fecha=self.fecha,
                set__hora=str(self.hora),
                set__sucursal=SucursalMongo.objects.get(postgres_id=self.sucursal.id),
                upsert=True
            )
        except Exception as e:
            print(f"Error sincronizando con MongoDB: {e}")

    class Meta:
        verbose_name = 'venta'
        verbose_name_plural = 'ventas'

#detalle pancho venta, se relaciona con venta (venta tiene detallepanchoventa:DetallePanchoVenta)

class DetallePanchoVenta(models.Model):
    venta = models.ForeignKey(Venta, on_delete=models.PROTECT, related_name='detalles_panchos')
    pancho = models.ForeignKey(Pancho, on_delete=models.PROTECT)
    cantidad = models.PositiveIntegerField(default=0)

    @property
    def subtotal(self):
        return (self.pancho.precio or 0) * self.cantidad

    def __str__(self):
        return f"{self.pancho.nombre} x{self.cantidad}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs) #Asignacion del id

        try:
            from .models_mongo import DetallePanchoVenta as DetallePVM, Pancho as PanchoMongo, Venta as VentaMongo
            DetallePVM.objects(postgres_id=self.id).update_one(
                set__venta=VentaMongo.objects.get(postgres_id=self.venta.id),
                set__pancho=PanchoMongo.objects.get(postgres_id=self.pancho.id),
                set__cantidad=self.cantidad,
                #ver
                upsert=True
            )
        except Exception as e:
            print(f"Error sincronizando con MongoDB: {e}")



#detalle bebida venta, se relaciona con venta (venta tiene detallepbebidaventa:DetalleBebidaVenta)
class DetalleBebidaVenta(models.Model):
    venta = models.ForeignKey(Venta, on_delete=models.PROTECT, related_name='detalles_bebidas')
    bebida = models.ForeignKey(Bebida, on_delete=models.PROTECT)
    cantidad = models.PositiveIntegerField(default=0)

    @property
    def subtotal(self):
        return (self.bebida.precio or 0) * self.cantidad

    def __str__(self):
        return f"{self.bebida.nombre} x{self.cantidad}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs) #Asignacion del id

        try:
            from .models_mongo import DetalleBebidaVenta as DetalleBVM, Venta as VentaMongo, Bebida as BebidaMongo
            DetalleBVM.objects(postgres_id=self.id).update_one(
                set__venta=VentaMongo.objects.get(postgres_id=self.venta.id),
                set__bebida=BebidaMongo.objects.get(postgres_id=self.bebida.id),
                set__cantidad=self.cantidad,
                #ver
                upsert=True
            )
        except Exception as e:
            print(f"Error sincronizando con MongoDB: {e}")

