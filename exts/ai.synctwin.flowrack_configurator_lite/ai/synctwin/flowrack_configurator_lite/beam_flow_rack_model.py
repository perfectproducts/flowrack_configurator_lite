from pydantic import BaseModel, Field 
from typing import List 
import math 
from pxr import Gf , Usd, Kind, UsdGeom

# describes a flow rack type 

class BeamFlowRackShelfModel(BaseModel):
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
    shelves: List[BeamFlowRackShelfModel] = [ 
        BeamFlowRackShelfModel( front_height= 236, back_height = 341 ), 
        BeamFlowRackShelfModel( front_height= 781, back_height = 846 ),
        BeamFlowRackShelfModel( front_height= 1091, back_height = 1176 ), 
        BeamFlowRackShelfModel( front_height= 1710-155-40, back_height = 1456 )
    ]

    def frame_height(self) -> float:
        return self.height-self.frame_floor_offset

    def abs_shelf_back_height(self, shelf : BeamFlowRackShelfModel) -> float:
        return self.frame_floor_offset + shelf.back_height

    def abs_shelf_front_height(self, shelf : BeamFlowRackShelfModel) -> float:
        return self.frame_floor_offset + shelf.front_height
    
    
    def connector_top_h(self)->float :
        return self.frame_ceil()-2*self.beam_radius-self.frame_top_connector_distance

    def connector_bottom_h(self)->float:
        return self.frame_front_height
    def frame_ceil(self)->float:
        return self.height-self.abs_frame_floor()

    def abs_frame_floor(self)->float:
        return self.frame_floor_offset+self.base_frame_height

    def abs_shelf_front_beam_height(self, shelf: BeamFlowRackShelfModel) ->float :
        return shelf.front_height+self.abs_frame_floor()

    def shelf_front_beam_offset(self, shelf: BeamFlowRackShelfModel) -> float:        
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

    def shelf_front_beam_angle(self, shelf: BeamFlowRackShelfModel) -> float:
        if shelf.front_height <= self.connector_bottom_h():
            return 0
        elif shelf.front_height >= self.connector_top_h():
            return 90
        else: 
            return self.front_beam_angle()
    
    def _shelf_connecting_vector2d(self, shelf: BeamFlowRackShelfModel) -> Gf.Vec2d:
        p_front = Gf.Vec2d(
            self.abs_shelf_front_beam_height(shelf),
            self.shelf_front_beam_offset(shelf)
        )
        p_back = Gf.Vec2d(self.abs_shelf_back_height(shelf), self.depth-self.beam_connector_radius)
        return p_back-p_front

    def wheelbar_length_on_shelf(self, shelf:BeamFlowRackShelfModel) -> float:
        v = self._shelf_connecting_vector2d(shelf) 
        return v.GetLength()

    def shelf_angle(self, shelf:BeamFlowRackShelfModel) -> float:
        v = self._shelf_connecting_vector2d(shelf)
        return -math.degrees(math.atan(v[0]/v[1]))
