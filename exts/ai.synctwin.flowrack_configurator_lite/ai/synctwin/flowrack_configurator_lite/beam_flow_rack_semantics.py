from .beam_flow_rack_model import BeamFlowRackModel, BeamFlowRackShelfModel
from .utils import GeoUtils 
from pxr import Usd, Kind, Sdf

class BeamFlowRackShelfSemantics:
    SCHEMA = "BeamFlowRackShelf"
    SCHEMA_VERSION = "1.0.0"

    def write(self, stage, model:BeamFlowRackShelfModel, path):
        shelf_prim = stage.DefinePrim(path, "Xform")
        Usd.ModelAPI(shelf_prim).SetKind(Kind.Tokens.component)
        shelf_prim.CreateAttribute("mfgstd:schema", Sdf.ValueTypeNames.String).Set(f"{BeamFlowRackShelfSemantics.SCHEMA}#{BeamFlowRackShelfSemantics.SCHEMA_VERSION}")
        shelf_prim.CreateAttribute("mfgstd:properties:front_height", Sdf.ValueTypeNames.Float).Set(model.front_height) 
        shelf_prim.CreateAttribute("mfgstd:properties:front_height", Sdf.ValueTypeNames.Float).Set(model.front_height) 
        shelf_prim.CreateAttribute("mfgstd:properties:wheelbar_distance", Sdf.ValueTypeNames.Float).Set(model.wheelbar_distance) 

    def read(self, stage, path)->BeamFlowRackShelfModel : 
        return BeamFlowRackShelfModel()
        


        

class BeamFlowRackSemantics:
    SCHEMA = "BeamFlowRack"
    SCHEMA_VERSION = "1.0.0"
    
    def write(self, stage, model:BeamFlowRackModel, path):
        root = stage.DefinePrim(path, "Xform")                
        Usd.ModelAPI(root).SetKind(Kind.Tokens.assembly)        
        root.CreateAttribute("mfgstd:schema", Sdf.ValueTypeNames.String).Set(f"{BeamFlowRackSemantics.SCHEMA}#{BeamFlowRackSemantics.SCHEMA_VERSION}")
        root.CreateAttribute("mfgstd:properties:width", Sdf.ValueTypeNames.Float).Set(model.width) 
        root.CreateAttribute("mfgstd:properties:height", Sdf.ValueTypeNames.Float).Set(model.height) 
        root.CreateAttribute("mfgstd:properties:depth", Sdf.ValueTypeNames.Float).Set(model.depth) 
        root.CreateAttribute("mfgstd:properties:name", Sdf.ValueTypeNames.String).Set(model.name)
        root.CreateAttribute("mfgstd:properties:frame_front_height", Sdf.ValueTypeNames.Float).Set(model.frame_front_height)
        root.CreateAttribute("mfgstd:properties:frame_top_offset", Sdf.ValueTypeNames.Float).Set(model.frame_top_offset)
        root.CreateAttribute("mfgstd:properties:frame_floor_offset", Sdf.ValueTypeNames.Float).Set(model.frame_floor_offset)
        root.CreateAttribute("mfgstd:properties:frame_top_connector_distance", Sdf.ValueTypeNames.Float).Set(model.frame_top_connector_distance)
        root.CreateAttribute("mfgstd:properties:beam_radius", Sdf.ValueTypeNames.Float).Set(model.beam_radius)
        root.CreateAttribute("mfgstd:properties:beam_connector_radius", Sdf.ValueTypeNames.Float).Set(model.beam_connector_radius)
        root.CreateAttribute("mfgstd:properties:base_frame_height", Sdf.ValueTypeNames.Float).Set(model.base_frame_height)
        root.CreateAttribute("mfgstd:properties:heavy_duty", Sdf.ValueTypeNames.Bool).Set(model.heavy_duty)
        idx = 1 
        for shelf in model.shelves:
            shelf_path = f"{path}/shelves/_{idx}"
            BeamFlowRackShelfSemantics().write(stage, shelf, shelf_path)
            
       
            idx += 1 

    def read(self, path) -> BeamFlowRackModel :
        return BeamFlowRackModel() 