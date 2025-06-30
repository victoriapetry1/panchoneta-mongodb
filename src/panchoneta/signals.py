from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from decimal import Decimal
from .models import Venta, DetallePanchoVenta, DetalleBebidaVenta
from decimal import Decimal

def actualizar_total_venta(venta):
    total = Decimal('0')

    for detalle in venta.detalles_panchos.all():
        if detalle.subtotal:
            total += Decimal(detalle.subtotal)

    for detalle in venta.detalles_bebidas.all():
        if detalle.subtotal:
            total += Decimal(detalle.subtotal)

    venta.total = total
    venta.save()

#signals para DetallePanchoVenta
@receiver(post_save, sender=DetallePanchoVenta)
@receiver(post_delete, sender=DetallePanchoVenta)
def actualizar_total_venta_por_pancho(sender, instance, **kwargs):
    if instance.venta:
        actualizar_total_venta(instance.venta)

#signals para DetalleBebidaVenta
@receiver(post_save, sender=DetalleBebidaVenta)
@receiver(post_delete, sender=DetalleBebidaVenta)
def actualizar_total_venta_por_bebida(sender, instance, **kwargs):
    if instance.venta:
        actualizar_total_venta(instance.venta)
