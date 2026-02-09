import os
from dataclasses import dataclass
import xml.etree.ElementTree as ET
import pygame

__all__ = ["TiledTMX"]

# En Tiled, los 3 bits superiores del GID se usan para flips/rotaciones.
# Como aquí NO soportamos flips, aplicamos una máscara para quedarnos con el ID real.
_TILED_GID_MASK = 0x1FFFFFFF


@dataclass(frozen=True, slots=True)
class TileSet:
    image_path: str
    firstgid: int = 1
    tile_width: int = 32
    tile_height: int = 32
    margin: int = 0
    spacing: int = 0
    colorkey: tuple[int, int, int] | None = None


class TileAtlas:
    """Corta tiles desde una imagen estilo tileset de Tiled.

    Soporta el concepto de GID global de Tiled con `firstgid`.
    """
    def __init__(self, tileset: TileSet):
        self.tileset = tileset

        image = pygame.image.load(tileset.image_path)
        # convert/convert_alpha requiere display inicializado
        if pygame.display.get_init() and pygame.display.get_surface() is not None:
            self.surface = image.convert_alpha() if image.get_alpha() else image.convert()
        else:
            self.surface = image
        if tileset.colorkey is not None:
            self.surface.set_colorkey(tileset.colorkey)

        usable_w = self.surface.get_width() - 2 * tileset.margin
        usable_h = self.surface.get_height() - 2 * tileset.margin
        step_x = tileset.tile_width + tileset.spacing
        step_y = tileset.tile_height + tileset.spacing

        self.columns = max(1, (usable_w + tileset.spacing) // step_x)
        self.rows = max(1, (usable_h + tileset.spacing) // step_y)
        self.tilecount = self.columns * self.rows

    def contains_gid(self, gid: int) -> bool:
        return self.tileset.firstgid <= gid < (self.tileset.firstgid + self.tilecount)

    def _rect_for_local_id(self, local_id: int) -> pygame.Rect:
        col = local_id % self.columns
        row = local_id // self.columns
        x = self.tileset.margin + col * (self.tileset.tile_width + self.tileset.spacing)
        y = self.tileset.margin + row * (
            self.tileset.tile_height + self.tileset.spacing
        )
        return pygame.Rect(x, y, self.tileset.tile_width, self.tileset.tile_height)

    def get_tile_by_gid(self, gid: int) -> pygame.Surface | None:
        # Tiled suele exportar empty como 0, y en algunos casos -1
        if gid <= 0:
            return None
        if not self.contains_gid(gid):
            return None

        local_id = gid - self.tileset.firstgid
        rect = self._rect_for_local_id(local_id)
        return self.surface.subsurface(rect).copy()


@dataclass(frozen=True, slots=True)
class TiledObject:
    id: int
    name: str
    type: str
    x: float
    y: float
    width: float
    height: float
    properties: dict[str, str]

    @property
    def rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.x), int(self.y), int(self.width), int(self.height))


@dataclass(frozen=True, slots=True)
class SolidTile:
    """Adapter mínimo para colisiones.

    Tu `Player` espera una lista de objetos con atributo `.hitbox`.
    """

    hitbox: pygame.Rect


class TiledTMX:
    """Carga un mapa .tmx de Tiled con múltiples tilesets y layers.

    - Detecta tilesets (incluidos .tsx externos) y sus firstgid
    - Renderiza cada layer a una Surface cacheada
    """

    def __init__(self, tmx_path: str):
        self.tmx_path = tmx_path
        self.base_dir = os.path.dirname(tmx_path)

        tree = ET.parse(tmx_path)
        self.root = tree.getroot()

        self.tile_width = int(self.root.attrib.get("tilewidth", "32"))
        self.tile_height = int(self.root.attrib.get("tileheight", "32"))
        self.width = int(self.root.attrib.get("width", "0"))
        self.height = int(self.root.attrib.get("height", "0"))

        self._atlases: list[TileAtlas] = self._load_tilesets()
        self.layers: list[tuple[str, pygame.Surface]] = self._render_layers()
        self.object_layers: dict[str, list[TiledObject]] = self._parse_object_layers()

        # cachea resultados de colisión (porque `get_tiles()` se llama cada frame)
        self._solid_tiles_cache: dict[str, list[SolidTile]] = {}

    @property
    def object_layer_names(self) -> list[str]:
        return list(self.object_layers.keys())

    def get_objects(
        self,
        *,
        layer: str | None = None,
        name: str | None = None,
        type: str | None = None,
    ) -> list["TiledObject"]:
        if layer is None:
            objs = [o for lst in self.object_layers.values() for o in lst]
        else:
            objs = list(self.object_layers.get(layer, []))

        if name is not None:
            objs = [o for o in objs if o.name == name]
        if type is not None:
            objs = [o for o in objs if o.type == type]
        return objs

    @property
    def layer_names(self) -> list[str]:
        return [name for name, _ in self.layers]

    def get_tiles(self, object_layer: str = "hitbox_fondo") -> list[SolidTile]:
        """Devuelve hitboxes sólidos desde una Object Layer de Tiled.
        """

        if object_layer in self._solid_tiles_cache:
            return self._solid_tiles_cache[object_layer]

        solids: list[SolidTile] = []
        for obj in self.object_layers.get(object_layer, []):
            # Tiled: objetos tipo point tienen w/h = 0
            if obj.width <= 0 and obj.height <= 0:
                continue
            solids.append(SolidTile(obj.rect))

        self._solid_tiles_cache[object_layer] = solids
        return solids

    def _resolve(self, base: str, path: str) -> str:
        if os.path.isabs(path):
            return path
        return os.path.normpath(os.path.join(base, path))

    def _parse_tsx(self, tsx_path: str) -> dict:
        tree = ET.parse(tsx_path)
        root = tree.getroot()
        image_el = root.find("image")
        if image_el is None:
            raise ValueError(f"TSX sin <image>: {tsx_path}")

        return {
            "tilewidth": int(root.attrib.get("tilewidth", str(self.tile_width))),
            "tileheight": int(root.attrib.get("tileheight", str(self.tile_height))),
            "spacing": int(root.attrib.get("spacing", "0")),
            "margin": int(root.attrib.get("margin", "0")),
            "image": image_el.attrib.get("source", ""),
        }

    def _parse_properties(self, props_el: ET.Element | None) -> dict[str, str]:
        if props_el is None:
            return {}

        out: dict[str, str] = {}
        for prop in props_el.findall("property"):
            key = prop.attrib.get("name", "")
            if not key:
                continue
            if "value" in prop.attrib:
                out[key] = str(prop.attrib.get("value", ""))
            else:
                out[key] = str(prop.text or "")
        return out

    def _parse_object_layers(self) -> dict[str, list[TiledObject]]:
        layers: dict[str, list[TiledObject]] = {}

        for obj_group in self.root.findall("objectgroup"):
            layer_name = obj_group.attrib.get("name", "objects")
            objects: list[TiledObject] = []

            for obj in obj_group.findall("object"):
                obj_id = int(obj.attrib.get("id", "0"))
                obj_name = obj.attrib.get("name", "")
                obj_type = obj.attrib.get("type", "")

                # Tiled exporta floats a veces
                x = float(obj.attrib.get("x", "0"))
                y = float(obj.attrib.get("y", "0"))
                w = float(obj.attrib.get("width", "0"))
                h = float(obj.attrib.get("height", "0"))

                props = self._parse_properties(obj.find("properties"))
                objects.append(
                    TiledObject(
                        id=obj_id,
                        name=obj_name,
                        type=obj_type,
                        x=x,
                        y=y,
                        width=w,
                        height=h,
                        properties=props,
                    )
                )

            if objects:
                layers[layer_name] = objects

        return layers

    def _load_tilesets(self) -> list[TileAtlas]:
        atlases: list[TileAtlas] = []

        for ts in self.root.findall("tileset"):
            firstgid = int(ts.attrib.get("firstgid", "1"))

            # tileset externo .tsx
            if "source" in ts.attrib:
                tsx_rel = ts.attrib["source"]
                tsx_path = self._resolve(self.base_dir, tsx_rel)
                meta = self._parse_tsx(tsx_path)
                image_path = self._resolve(os.path.dirname(tsx_path), meta["image"])
                tileset = TileSet(
                    image_path=image_path,
                    firstgid=firstgid,
                    tile_width=meta["tilewidth"],
                    tile_height=meta["tileheight"],
                    spacing=meta["spacing"],
                    margin=meta["margin"],
                )
                atlases.append(TileAtlas(tileset))
                continue

            # tileset inline en el .tmx
            image_el = ts.find("image")
            if image_el is None:
                continue
            image_path = self._resolve(self.base_dir, image_el.attrib.get("source", ""))
            tileset = TileSet(
                image_path=image_path,
                firstgid=firstgid,
                tile_width=int(ts.attrib.get("tilewidth", str(self.tile_width))),
                tile_height=int(ts.attrib.get("tileheight", str(self.tile_height))),
                spacing=int(ts.attrib.get("spacing", "0")),
                margin=int(ts.attrib.get("margin", "0")),
            )
            atlases.append(TileAtlas(tileset))

        # importante: ordenados por firstgid
        return sorted(atlases, key=lambda a: a.tileset.firstgid)

    def _atlas_for_gid(self, gid: int) -> TileAtlas | None:
        chosen: TileAtlas | None = None
        for atlas in self._atlases:
            if atlas.tileset.firstgid <= gid:
                chosen = atlas
            else:
                break
        if chosen is not None and chosen.contains_gid(gid):
            return chosen
        return None

    def _iter_layer_gids(self, layer_el: ET.Element) -> list[int]:
        data_el = layer_el.find("data")
        if data_el is None:
            return []

        encoding = data_el.attrib.get("encoding")

        # encoding="csv" (muy común)
        if encoding == "csv":
            text = (data_el.text or "").strip()
            if not text:
                return []
            # CSV puede contener saltos de línea; separamos por coma
            parts = [p.strip() for p in text.replace("\n", "").split(",")]
            return [int(p) for p in parts if p != ""]

        # Sin encoding: <tile gid="..."/>
        if encoding is None:
            return [int(t.attrib.get("gid", "0")) for t in data_el.findall("tile")]

        raise NotImplementedError(
            "TMX con encoding base64/compresión no soportado aún. Exporta la layer como CSV en Tiled."
        )

    def _render_layers(self) -> list[tuple[str, pygame.Surface]]:
        layers: list[tuple[str, pygame.Surface]] = []
        map_w_px = self.width * self.tile_width
        map_h_px = self.height * self.tile_height

        for layer_el in self.root.findall("layer"):
            name = layer_el.attrib.get("name", "layer")
            gids = self._iter_layer_gids(layer_el)
            if not gids:
                continue

            surf = pygame.Surface((map_w_px, map_h_px), flags=pygame.SRCALPHA)
            for idx, raw_gid in enumerate(gids):
                gid = raw_gid & _TILED_GID_MASK
                if gid <= 0:
                    continue
                atlas = self._atlas_for_gid(gid)
                if atlas is None:
                    continue
                tile_img = atlas.get_tile_by_gid(gid)
                if tile_img is None:
                    continue

                x = (idx % self.width) * self.tile_width
                y = (idx // self.width) * self.tile_height
                surf.blit(tile_img, (x, y))

            layers.append((name, surf))

        return layers

    def draw(self, surface: pygame.Surface, *, only: list[str] | None = None):
        for name, layer_surf in self.layers:
            if only is not None and name not in only:
                continue
            surface.blit(layer_surf, (0, 0))