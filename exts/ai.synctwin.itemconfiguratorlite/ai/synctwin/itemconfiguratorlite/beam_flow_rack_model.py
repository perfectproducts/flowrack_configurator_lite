from .geo_utils import GeoUtils
from pydantic import BaseModel, Field
from typing import List 
import math 
from pxr import Gf , Usd, Kind, UsdGeom

# describes a flow rack type 

class BeamShelfModel(BaseModel):
    front_height: float 
    back_height: float
    wheelbar_distance:float = 180

class BeamFlowRackModel(BaseModel):
    width: float = 755
    height: float = 1710
    depth: float = 2100
    name: str = "FlowRack" 
    frame_front_height: float = 400  
    frame_top_offset: float = 200 
    frame_floor_offset: float = 155
    frame_top_connector_distance: float = 40
    beam_radius: float = 15
    beam_connector_radius: float = 20
    base_frame_height: float = 30 
    heavy_duty: bool = False 
    shelves: List[BeamShelfModel] = [ 
        BeamShelfModel( front_height= 236, back_height = 341 ), 
        BeamShelfModel( front_height= 781, back_height = 846 ),
        BeamShelfModel( front_height= 1091, back_height = 1176 ), 
        BeamShelfModel( front_height= 1710-155-40, back_height = 1456 )
    ]

    def frame_height(self) -> float:
        return self.height-self.frame_floor_offset

    def abs_shelf_back_height(self, shelf : BeamShelfModel) -> float:
        return self.frame_floor_offset + shelf.back_height

    def abs_shelf_front_height(self, shelf : BeamShelfModel) -> float:
        return self.frame_floor_offset + shelf.front_height
    
    
    def connector_top_h(self)->float :
        return self.frame_ceil()-2*self.beam_radius-self.frame_top_connector_distance

    def connector_bottom_h(self)->float:
        return self.frame_front_height
    def frame_ceil(self)->float:
        return self.height-self.abs_frame_floor()

    def abs_frame_floor(self)->float:
        return self.frame_floor_offset+self.base_frame_height

    def abs_shelf_front_beam_height(self, shelf: BeamShelfModel) ->float :
        return shelf.front_height+self.abs_frame_floor()

    def shelf_front_beam_offset(self, shelf: BeamShelfModel) -> float:        
        if shelf.front_height >= self.connector_top_h():
            return self.frame_top_offset+ self.beam_connector_radius
        elif shelf.front_height <= self.connector_bottom_h():
            return self.beam_connector_radius        
        else: 
            o = self.frame_top_offset
            d = self.connector_top_h()-self.connector_bottom_h()
            y = shelf.front_height - self.connector_bottom_h()
            x = o*y/d
            return x + self.beam_connector_radius

    def front_beam_angle(self) -> float:
        o = self.frame_top_offset
        d = self.connector_top_h()-self.connector_bottom_h()
        
        a = math.atan(o/d)
        return math.degrees(a)

    def shelf_front_beam_angle(self, shelf: BeamShelfModel) -> float:
        if shelf.front_height <= self.connector_bottom_h():
            return 0
        elif shelf.front_height >= self.connector_top_h():
            return 90
        else: 
            return self.front_beam_angle()
    
    def _shelf_connecting_vector2d(self, shelf: BeamShelfModel) -> Gf.Vec2d:
        p_front = Gf.Vec2d(
            self.abs_shelf_front_beam_height(shelf),
            self.shelf_front_beam_offset(shelf)
        )
        p_back = Gf.Vec2d(self.abs_shelf_back_height(shelf), self.depth-self.beam_connector_radius)
        return p_back-p_front

    def wheelbar_length_on_shelf(self, shelf:BeamShelfModel) -> float:
        v = self._shelf_connecting_vector2d(shelf) 
        return v.GetLength()

    def shelf_angle(self, shelf:BeamShelfModel) -> float:
        v = self._shelf_connecting_vector2d(shelf)
        return -math.degrees(math.atan(v[0]/v[1]))
    
class BeamFlowRackIpoConverter:

    def rack_ipo_prim(self, stage:Usd.Stage)->Usd.Prim:
        root = stage.GetPrimAtPath("/World")
        rack_prim = root.GetChildren()[0]
        ipo_prim = rack_prim.GetChild("ipo")        
        return ipo_prim

    def beam_flow_rack_model_from_ipo(self, stage:Usd.Stage)->BeamFlowRackModel:
        root = stage.GetPrimAtPath("/World")
        rack_prim = root.GetChildren()[0]
        ipo_prim = rack_prim.GetChild("ipo")
        ipo_requirements_prim = ipo_prim.GetChild("requirements")
        bounds_prim = ipo_requirements_prim.GetChild("bounds")
        shelves_prim = ipo_requirements_prim.GetChild("shelves")
        scale = 10.0
        gb = GeoUtils() 
        base_bounds = gb.bounds(bounds_prim)
        total_bounds = gb.bounds(ipo_requirements_prim)
        base_size = base_bounds.GetBox().GetSize()*scale
        total_size = total_bounds.GetBox().GetSize()*scale
        print(f"-> {base_bounds}")
        rack = BeamFlowRackModel()
        rack.width = base_size[0]
        rack.height = total_size[2]
        rack.depth = base_size[1]
        rack.frame_top_offset = 0
        rack.shelves = []
        for shelf_prim in shelves_prim.GetChildren():
            print("-shelf")
            geo = gb.bounds(shelf_prim.GetChild("geo"))
            print(geo.GetBox().GetSize())
            xf = UsdGeom.Xformable(shelf_prim)
            mat = xf.GetLocalTransformation()
            a = mat.Transform(Gf.Vec3d (-1,-1,-1))
            b = mat.Transform(Gf.Vec3d (1, 1,1))#rack.depth/scale,0))
            print(f"{a} {b}")
            ha = a[2]*scale - rack.abs_frame_floor()
            hb = b[2]*scale - rack.abs_frame_floor()
            if "_R" in shelf_prim.GetName():
                hb = ha
                hf = hb
            else: 
                hf = ha
                hb = hb
            print(f"S {hf} {hb}")
            rack.shelves.append(BeamShelfModel(front_height=hf, back_height=hb))
        return rack