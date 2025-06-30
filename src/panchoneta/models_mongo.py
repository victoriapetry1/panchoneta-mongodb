from mongoengine import (
    Document, EmbeddedDocument,
    StringField, DecimalField, IntField, DateField, DateTimeField,
    ReferenceField, ListField, EmbeddedDocumentField, CASCADE
)


# Clases abstractas
class NombreAbstract(Document):
    meta = {
        'abstract': True,
        'ordering': ['nombre']
    }

    nombre = StringField(required=True, max_length=200)

    def clean(self):
        if self.nombre:
            self.nombre = self.nombre.upper()

    def __str__(self):
        return self.nombre


class BaseModel(Document):
    meta = {'abstract': True}


# Entidades del modelo
class Bebida(NombreAbstract):
    postgres_id = IntField(required=True, unique=True)
    nombre = StringField(required=False, max_length=120)
    precio = DecimalField(precision=2, required=False)

class Pancho(NombreAbstract):
    postgres_id = IntField(required=True, unique=True)
    nombre = StringField(required=True, max_length=120)
    precio = DecimalField(precision=2, default=0)

class Salsa(NombreAbstract):
    postgres_id = IntField(required=True, unique=True)
    nombre = StringField(required=False, max_length=120)
    descripcion = StringField(required=False)

class Sucursal(NombreAbstract):
    postgres_id = IntField(required=True, unique=True)
    nombre = StringField(required=False, max_length=120)
    calle = StringField(required=False, max_length=120)
    nroCalle = IntField(required=False)
    piso = IntField(required=False)


# Tabla intermedia 
class DetallePancho(Document):
    postgres_id = IntField(required=True, unique=True)
    idSalsa = ReferenceField(Salsa, reverse_delete_rule=CASCADE)
    idPancho = ReferenceField(Pancho, reverse_delete_rule=CASCADE)


# Venta y detalles

class Venta(Document):
    postgres_id = IntField(required=True, unique=True)
    fecha = DateField(required=False)
    hora = StringField(required=False)
    sucursal = ReferenceField(Sucursal, reverse_delete_rule=CASCADE)

    def __str__(self):
        return f"Venta #{self.pk} - {self.fecha} - {self.sucursal.nombre}"

    def calcular_total(self):
        total_panchos = sum(dp.subtotal for dp in DetallePanchoVenta.objects(venta=self))
        total_bebidas = sum(db.subtotal for db in DetalleBebidaVenta.objects(venta=self))
        return total_panchos + total_bebidas


class DetallePanchoVenta(Document):
    postgres_id = IntField(required=True, unique=True)
    venta = ReferenceField(Venta, reverse_delete_rule=CASCADE)
    pancho = ReferenceField(Pancho, reverse_delete_rule=CASCADE)
    cantidad = IntField(min_value=0, default=0)

    @property
    def subtotal(self):
        return (self.pancho.precio or 0) * self.cantidad

    def __str__(self):
        return f"{self.pancho.nombre} x{self.cantidad}"


class DetalleBebidaVenta(Document):
    postgres_id = IntField(required=True, unique=True)
    venta = ReferenceField(Venta, reverse_delete_rule=CASCADE)
    bebida = ReferenceField(Bebida, reverse_delete_rule=CASCADE)
    cantidad = IntField(min_value=0, default=0)

    @property
    def subtotal(self):
        return (self.bebida.precio or 0) * self.cantidad

    def __str__(self):
        return f"{self.bebida.nombre} x{self.cantidad}"
