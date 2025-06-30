import json
from pathlib import Path
from panchoneta.models_mongo import * 

json_path = Path("panchoneta/fixtures/initial_data.json").resolve()


with open(json_path, encoding='utf-8') as f:
    data = json.load(f)

model_map = {
    "panchoneta.pancho": Pancho,
    "panchoneta.bebida": Bebida,
    "panchoneta.salsa": Salsa,
    "panchoneta.sucursal": Sucursal,
    "panchoneta.detallepancho": DetallePancho,
    "panchoneta.venta": Venta,
    "panchoneta.detallepanchoventa": DetallePanchoVenta,
    "panchoneta.detallebebidaventa": DetalleBebidaVenta 
}

for entry in data:
    model_label = entry["model"]
    pk = entry["pk"]
    fields = entry["fields"]
    fields["postgres_id"] = pk
    
    model_class = model_map.get(model_label)
    if not model_class:
        print(f"Modelo no encontrado: {model_label}")
        continue

    try:
        obj = model_class(**fields)
        obj.save()
        print(f"Insertado: {model_label} (postgres_id={pk})")
    except Exception as e:
        print(f"Error insertando {model_label} (postgres_id={pk}): {e}")






