from pxr import Gf, UsdGeom, Usd, Sdf, UsdShade
import omni.usd as ou
import unicodedata
import re
class GeoUtils:
    
    def __init__(self) -> None:
        self._stage = None
        
    def bounds(self, prim) -> Gf.BBox3d:
        cache = UsdGeom.BBoxCache(Usd.TimeCode.Default(), ["default", "render"])
        return cache.ComputeWorldBound(prim)
        return UsdGeom.Imageable(prim).ComputeWorldBound(
            Usd.TimeCode(1),
            purpose1='default',
        )

    def make_valid_primname(self, value):
        value = unicodedata.normalize("NFKD", str(value)).encode("ascii", "ignore").decode("ascii")
        value = re.sub(r"[^\w\s-]", "", value)
        return re.sub(r"[-\s]+", "", value).strip("-_")

    def open_or_create_stage(self, path, clear_exist=True) -> Usd.Stage:
        layer = Sdf.Layer.FindOrOpen(path)
        if not layer:
            layer = Sdf.Layer.CreateNew(path)
        elif clear_exist:
            layer.Clear()
            
        if layer:
            self._stage = Usd.Stage.Open(layer)
            return self._stage
        else:
            return None

    def create_material(self, material_path, name, diffuse_color) -> UsdShade.Material:
        #print(f"mat: {material_path} {name}" )
        if not self._stage.GetPrimAtPath(material_path + "/Looks"):
            #print(f"mat: {material_path}")
            self._stage.DefinePrim(material_path + "/Looks", "Scope")
        material_path += "/Looks/" + name
        
        material_path = ou.get_stage_next_free_path(
            self._stage, material_path, False
        )
        material = UsdShade.Material.Define(self._stage, material_path)

        shader_path = material_path + "/Shader"
        shader = UsdShade.Shader.Define(self._stage, shader_path)
        shader.CreateIdAttr("UsdPreviewSurface")
        shader.CreateInput("diffuseColor", Sdf.ValueTypeNames.Color3f).Set(diffuse_color)
        
        material.CreateSurfaceOutput().ConnectToSource(shader, "surface")
        

        return material

    

