"""Convenciones geográficas compartidas por procesamiento y pruebas."""
import math
from functools import lru_cache

from shapely import Point, STRtree


def grid_index(value, origin):
    """Replica la cuadrícula del cliente, evitando ruido de coma flotante."""
    return math.floor(math.floor((value - origin) * 1_000_000_000 + 0.5) / 10_000_000)


def cell_of(longitude, latitude):
    if not (math.isfinite(longitude) and math.isfinite(latitude)):
        raise ValueError("Coordenadas no finitas")
    if not (-180 <= longitude < 180 and -90 <= latitude < 90):
        raise ValueError("Coordenadas fuera de la cuadrícula semiabierta")
    return grid_index(longitude, -180), grid_index(latitude, -90)


def cell_center(cell):
    return -180 + (cell[0] + 0.5) * 0.01, -90 + (cell[1] + 0.5) * 0.01


class CanonicalAssignment:
    """Cada celda-día recibe una comuna por centro de celda.

    Un centro sobre borde compartido se asigna al CUT menor. Solapamientos
    interiores quedan sin asignar; nunca se duplican entre comunas.
    """
    def __init__(self, communes):
        self.communes = sorted(communes, key=lambda row: row["cut"])
        self.geometries = [row["geometry"] for row in self.communes]
        self.tree = STRtree(self.geometries)

    @lru_cache(maxsize=150_000)
    def assign_cell(self, cell):
        point = Point(*cell_center(cell))
        candidates = [int(i) for i in self.tree.query(point) if self.geometries[int(i)].covers(point)]
        if not candidates:
            return None, "outside"
        if len(candidates) == 1:
            return self.communes[candidates[0]]["cut"], "inside"
        interior = [i for i in candidates if self.geometries[i].contains(point)]
        if len(interior) > 1:
            return None, "ambiguous-interior-overlap"
        if len(interior) == 1:
            return self.communes[interior[0]]["cut"], "inside"
        return min(self.communes[i]["cut"] for i in candidates), "shared-edge-min-cut"
