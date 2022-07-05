from .beam_flow_rack_model import BeamFlowRackModel
from .geo_utils import GeoUtils 
from pxr import Usd
from pxr import Kind

class BeamFlowRackModelCustomData:
    def __init__(self, model:BeamFlowRackModel) -> None:
        self._model = model 
        pass

    def write(self, stage, path):
        root = stage.DefinePrim(path, "Xform")                
        Usd.ModelAPI(root).SetKind(Kind.Tokens.assembly)        
        root.SetCustomDataByKey("mfgstd:schema", "BeamFlowRack#1.0.0")
        m = self._model 
        d = m.dict(exclude={"shelves"})
        for k in d:
            root.SetCustomDataByKey(f"mfgstd:properties:{k}", d[k]) 
        idx = 1 
        for shelf in m.shelves:
            shelf_prim = stage.DefinePrim(f"{path}/shelves/_{idx}")
            Usd.ModelAPI(shelf_prim).SetKind(Kind.Tokens.component)
            d = shelf.dict()
            for k in d: 
                shelf_prim.SetCustomDataByKey(f"mfgstd:properties:{k}", d[k])             
            root.SetCustomDataByKey("mfgstd:schema", "RackShelf#1.0.0")
        
            idx += 1 

    def read(self, path) -> bool :
        return False 