import os
from .beam_flow_rack_customdata import BeamFlowRackModelCustomData 
from omni.usd._impl.utils import get_prim_at_path
from pxr import UsdGeom, Gf, Usd
from pxr.Usd import Prim
from pxr import Ar
from pxr import Tf 
import math 
from .geo_utils import GeoUtils
from .beam_flow_rack_model import BeamFlowRackModel, BeamShelfModel

class ItemElementBuilder:
    def __init__(self, bom_path, templates_path) -> None:    
        self._bom_path = bom_path 
        self._templates_path = templates_path
        self._bom_element_offset = 25
        self._next_bom_element_x = 0 
        self._40x40_profile_template = f"{self._templates_path}/g___g_2_1_7x2_obj.usd"
        self._d100_wheel_template = f"{self._templates_path}/g__54_g_61_1_554x61_obj.usd"
        self._d30_wheel_heavy_template = f"{self._templates_path}/wheel_heavy_1.usd"
        self._d30_profile_template = f"{self._templates_path}/g__7_g_1_1_17x1_obj.usd"
        self._d30_connector90_template = f"{self._templates_path}/g__76_g_2_1_376x2_obj.usd"
        self._d30_connector_d30_template = f"{self._templates_path}/g__64_g_1_1_364x1_obj.usd"
        self._d30_connector_parallel_template = f"{self._templates_path}/g__76_g_9_1_576x9_obj.usd"
        self._d30_connector_angle_template = [
            f"{self._templates_path}/g__56_g_1_1_556x1_obj.usd",
            f"{self._templates_path}/g__56_g_3_1_556x3_obj.usd"]
        self._d30_wheelbar_connector_high =f"{self._templates_path}/g__60_g_4_1_460x4_obj.usd"
        self._d30_wheelbar_connector_low =f"{self._templates_path}/g__60_g_8_1_460x8_obj.usd"
        self._d30_wheelbar_profile_template = f"{self._templates_path}/g__57_g_1_2_457x1_obj.usd"
        self._d30_wheelbar_side_template = f"{self._templates_path}/g__41_g_12_1_541x12_obj.usd"
        self._d30_wheelbar_wheel_template = f"{self._templates_path}/wheelbar_wheel.usd"


        
        
        
        
    def clear_bom(self):
        print("-- clear bom --")
        print(self._bom_path)
        parts_dir = f"{self._bom_path}"
        for f in os.listdir(parts_dir):
            os.remove(f"{parts_dir}/{f}")

        #print(tl)


    def bounds(self, prim) -> Gf.BBox3d:
        cache = UsdGeom.BBoxCache(Usd.TimeCode.Default(), ["default", "render"])
        return cache.ComputeWorldBound(prim)
        return UsdGeom.Imageable(prim).ComputeWorldBound(
            Usd.TimeCode(1),
            purpose1='default',
        )

    
    #def part_prim_path(self, part_name) ->str:
    #    parts_prim_path = f"{self._bom_path}/parts"
    #    return f"{parts_prim_path}/{part_name}"

    #def part_prim(self, part_name) ->Prim:         
    #    return self._stage.GetPrimAtPath(self.part_prim_path(part_name))

    def create_part_stage(self, part_name) -> Usd.Stage:
        part_stage = Usd.Stage.CreateNew(self.part_usd_path(part_name))         
        return part_stage 

    def create_component_stage(self, part_name) -> Usd.Stage:
        cmp_stage = Usd.Stage.CreateNew(self.component_usd_path(part_name))         
        return cmp_stage 


    #def create_part_prim(self, part_name) ->Prim:         
    #    return self._stage.DefinePrim(self.part_prim_path(part_name), 'Xform') 

    def create_cube(self, path, size=2.0) ->Prim:
        prim = self._stage.DefinePrim(path, 'Xform') 
        cube = self._stage.DefinePrim(path+"/geo", "Cube")
        cube.GetAttribute("size").Set(size)
        return prim

    def part_usd_path(self, part_name) -> str:
        return f"{self._bom_path}/part_{Tf.MakeValidIdentifier(part_name)}.usd"

    def component_usd_path(self, part_name) -> str:
        return f"{self._bom_path}/component_{Tf.MakeValidIdentifier(part_name)}.usd"

    def component_exists(self, part_name) -> bool:           
        resolved = Ar.GetResolver().Resolve(self.component_usd_path(part_name))        
        return not (resolved == "") 

    def part_exists(self, part_name) -> bool:                 
        resolved = Ar.GetResolver().Resolve(self.part_usd_path(part_name))        
        return not (resolved == "") 

    def get_or_create_part(self, part_name, creator) -> str:
        path = self.part_usd_path(part_name)
        if self.part_exists(part_name):            
            return path
        part_stage = Usd.Stage.CreateNew(path)         
        part_prim_path = "/World"
        profile_prim = part_stage.DefinePrim(part_prim_path, "Xform")
        creator(self, part_stage, part_prim_path)        
        part_stage.SetDefaultPrim( part_stage.GetPrimAtPath("/World"))
        part_stage.Save()
        return path  

    def part_from_template(self, part_name, template_path) -> str: 
        def creator(self, stage, profile_prim_path):
            stage.GetPrimAtPath(profile_prim_path).GetReferences().AddReference(template_path)        
        return self.get_or_create_part(part_name, creator)

    def part_d30_angle_connector(self)->str:
        
        part_name = "D30_angle_connector"
        
        def creator(self, stage, part_prim_path):            
            root_prim = stage.DefinePrim(f"{part_prim_path}/root", "Xform")
            geo_a_prim = stage.DefinePrim(f"{part_prim_path}/root/geo_a", "Xform")
            geo_b_prim = stage.DefinePrim(f"{part_prim_path}/root/geo_b", "Xform")
            geo_a_prim.GetReferences().AddReference(self._d30_connector_angle_template[0])
            geo_b_prim.GetReferences().AddReference(self._d30_connector_angle_template[1])
        return self.get_or_create_part(part_name, creator)

    def set_d30_angle_connector_angle(self, prim, angle):
        
        obj = prim.GetObjectAtPath("root/geo_b")
        xf = UsdGeom.Xformable(obj)
        xf.ClearXformOpOrder () 
        xf.AddRotateXYZOp().Set(Gf.Vec3f(0,0,angle))            

    def d30_angle_connector_angle_xf(self, prim)->Gf.Matrix4d:
        prim_xf = UsdGeom.Xformable(prim)
        obj = prim.GetObjectAtPath("root/geo_b")
        xf = UsdGeom.Xformable(obj)
        return xf.GetLocalTransformation()*prim_xf.GetLocalTransformation()
        
    def part_d30_connector_parallel(self) -> str:
        return self.part_from_template("D30_connector_parallel", self._d30_connector_parallel_template)

    def part_d30_wheelbar_connector_high(self) -> str:
        return self.part_from_template("D30_wheelbar_connector_high", self._d30_wheelbar_connector_high)

    def part_d30_wheelbar_connector_low(self) -> str:        
        return self.part_from_template("D30_wheelbar_connector_low", self._d30_wheelbar_connector_low)

    def part_d30_wheelbar_wheel(self)->str:
        return self.part_from_template("D30_wheelbar_wheel", self._d30_wheelbar_wheel_template)

    def part_d30_wheel(self) -> str:        
        return self.part_from_template("D30_wheel", self._d100_wheel_template)
    
    def part_d30_wheel_heavy(self) -> str:
        return self.part_from_template("D30_wheel_heavy", self._d30_wheel_heavy_template)                
        
    def part_d30_connector90(self) -> str:
        return self.part_from_template("D30_connector90", self._d30_connector90_template)

    def part_d30_connector_d30(self) -> str:
        return self.part_from_template("D30_connector_30", self._d30_connector_d30_template)
        
    def part_40x40_profile(self, size) -> str:
        return self.part_profile_from_template(size, "Profil_8", self._40x40_profile_template, 1)

    def part_d30_wheelbar_profile(self, size)->str:
        return self.part_profile_from_template(size, "Profil_Wheelbar", self._d30_wheelbar_profile_template, 1) 

    def part_d30_wheelbar_side_profile(self, size)->str:
        return self.part_profile_from_template(size, "Profil_Wheelbar_Side", self._d30_wheelbar_side_template, 1)         

    def part_d30_profile(self, size) -> str:
        return self.part_profile_from_template(size, "Profil_D30", self._d30_profile_template, 0.05)

    def part_profile_from_template(self, size, profile_name, template_path, scaling ) -> str:
        part_name = f"{profile_name}_{int(size)}"
        if self.part_exists(part_name):
            return self.part_usd_path(part_name)
        
        part_stage = self.create_part_stage(part_name)

        profile_prim = part_stage.DefinePrim(f"/World/beam", "Xform")
        profile_prim.GetReferences().AddReference(template_path)
        profile_xf = UsdGeom.Xformable(profile_prim)
        profile_xf.ClearXformOpOrder ()
        
        profile_xf.AddScaleOp().Set(Gf.Vec3f(1,1,size*scaling))    
        part_stage.SetDefaultPrim( part_stage.GetPrimAtPath("/World"))
        part_stage.Save()
        return self.part_usd_path(part_name)
        
    def add_part(self, stage, part_path, prim_path, position=[0,0,0], orientation=[0,0,0], parent_xf=None)->Prim:
        
        root_prim  = stage.DefinePrim(prim_path, 'Xform') 
        xf = UsdGeom.Xformable(root_prim)
        pos = Gf.Vec3d(position)
        rotEuler = Gf.Vec3f(orientation)
        if parent_xf is None:            
            # if there's no parent_xf just use pos & rot ops for better readability
            xf.ClearXformOpOrder ()
            xf.AddTranslateOp().Set(pos)    
            xf.AddRotateXYZOp().Set(rotEuler)    
        else:                                    
            # for elements with parent_xf we use a matrix transform op 
            t = Gf.Transform()
            t.SetTranslation(pos)
            rot = Gf.Rotation(Gf.Vec3d(1,0,0), rotEuler[0])*Gf.Rotation(Gf.Vec3d(0,1,0), rotEuler[1])*Gf.Rotation(Gf.Vec3d(0,0,1), rotEuler[2])
            t.SetRotation(rot)            
            xf.ClearXformOpOrder ()
            localMat = t.GetMatrix()
            xf.AddTransformOp().Set(localMat*parent_xf)
                
        root_prim.GetReferences().AddReference(part_path)
        return root_prim
    
    def component_40x40_frame(self, width, depth)->str:
        part_40x40_w = self.part_40x40_profile(width-80)
        part_40x40_d = self.part_40x40_profile(depth)
        part_name = f"40x40_frame_{width}x{depth}"        

        def creator(self, part_stage, part_prim_path):
            front = self.add_part(stage=part_stage, part_path=part_40x40_w, position=[40,0,40], orientation=[0,90,0], prim_path=f"{part_prim_path}/front")
            back = self.add_part(stage=part_stage,part_path=part_40x40_w, position=[40,0,depth], orientation=[0,90,0],  prim_path=f"{part_prim_path}/back")
            left = self.add_part(stage=part_stage,part_path=part_40x40_d, position=[0,0,0],  prim_path=f"{part_prim_path}/left") 
            right = self.add_part(stage=part_stage,part_path=part_40x40_d, position=[width-40,0,0],  prim_path=f"{part_prim_path}/right")
        
        return self.get_or_create_component(part_name, creator)

    def component_d30_wheelbar(self, length, high_front=True, with_side=0)->str:
        part_name = f"D30_wheelbar_{int(length)}_{with_side}_{high_front}"
       
        def creator(self, part_stage, part_prim_path):
            top_offset = 50 
            beam_len = math.sqrt(length*length-top_offset*top_offset)
            angle = math.asin(top_offset/length) 
            if not high_front:
                angle = -angle 
            parent_xf = Gf.Matrix4d()
            parent_xf.SetRotate(Gf.Rotation(Gf.Vec3d(1,0,0), math.degrees(angle)))
            if high_front:
                y = -10
            else:
                y = -60
            if high_front:
                self.add_part(stage=part_stage, part_path=self.part_d30_wheelbar_connector_high(),                 
                        prim_path=f"{part_prim_path}/_connector_a",
                        parent_xf=parent_xf
                        )
                self.add_part(part_path=self.part_d30_wheelbar_connector_low(),                 
                        prim_path=f"{part_prim_path}/_connector_b",
                        position=[0,50,beam_len],
                        orientation=[0,180,0],
                        parent_xf=parent_xf,
                        stage=part_stage
                        )
            else:
                self.add_part(part_path=self.part_d30_wheelbar_connector_low(),                 
                        prim_path=f"{part_prim_path}/_connector_a",
                        position=[0,0,0],
                        parent_xf=parent_xf,
                        stage=part_stage
                        )
                self.add_part(part_path=self.part_d30_wheelbar_connector_high(),                 
                        prim_path=f"{part_prim_path}/_connector_b",
                        position=[0,-50,beam_len],
                        orientation=[0,180,0],
                        parent_xf=parent_xf,
                        stage=part_stage
                        )
            
            

            self.add_part(stage=part_stage, part_path=self.part_d30_wheelbar_profile(beam_len-40), prim_path=f"{part_prim_path}/_3"
            , position=[0,y,length/2],parent_xf=parent_xf)

            if with_side == 1:
                self.add_part(stage=part_stage,part_path=self.part_d30_wheelbar_side_profile(beam_len-160), prim_path=f"{part_prim_path}/_4"
                , position=[0,y,beam_len/2],parent_xf=parent_xf)
            elif with_side == 2:
                self.add_part(part_path=self.part_d30_wheelbar_side_profile(beam_len-160), prim_path=f"{part_prim_path}/_4"
                , position=[0,y,beam_len/2]
                , orientation=[0,180,0],parent_xf=parent_xf,stage=part_stage)
            wheel_distance = 50
            num_wheels = int((beam_len-30) / wheel_distance)
            for i in range(0,num_wheels):
                self.add_part(part_path=self.part_d30_wheelbar_wheel(), prim_path=f"{part_prim_path}/w{i}"
                , position=[0,y+20,i*wheel_distance+50]
                , orientation=[0,180,0],parent_xf=parent_xf,stage=part_stage)
        
        return self.get_or_create_component(part_name, creator)
        

    def component_d30_beam(self, length, connector_on_bottom=True, connector_on_top=True)->str:
        connector_info = ""
        if connector_on_bottom and connector_on_top:
            connector_info = "_both"
        elif connector_on_bottom:
            connector_info = "_bottom"
        elif connector_on_top:
            connector_info = "_top"
        

        part_name = f"D30_beam_{int(length)}{connector_info}"
        
        def creator (self, part_stage, part_prim_path):
        
        
            d30_connector90_center_offset = 17.2

            #self.add_part(prim=self.part_d30_connector90(), position=[0, d30_connector90_center_offset, 0], orientation=[-90,0,90], prim_path=f"{part_prim_path}/connector")
            
            profile_length = length 
            profile_offset = 0 
            if connector_on_bottom:
                profile_length -= 25 
                profile_offset += 25
                self.add_part(stage=part_stage, part_path=self.part_d30_connector_d30(), position=[0, 0, d30_connector90_center_offset], orientation=[0,-90,0], prim_path=f"{part_prim_path}/connector_bottom")
            if connector_on_top:
                profile_length -= 25
                self.add_part(stage=part_stage, part_path=self.part_d30_connector_d30(), position=[0, 0, length-d30_connector90_center_offset], orientation=[180,90,0], prim_path=f"{part_prim_path}/connector_top")


            
            self.add_part(stage=part_stage, part_path=self.part_d30_profile(profile_length), position=[0, 0, profile_offset], prim_path=f"{part_prim_path}/profile")
        
        return self.get_or_create_component(part_name=part_name, creator=creator)  

    def component_d30_leg(self, height, connector_on_top=True)->Prim:
        part_name = f"D30_leg_{height}{'_connector_top' if connector_on_top else ''}"        
        
        path = self.component_usd_path(part_name)
        if self.component_exists(part_name):
            return path
        part_stage = self.create_component_stage(part_name)
        part_prim_path = "/World"
        
        part_prim  = self._stage.DefinePrim(part_prim_path, 'Xform')
        
        d30_connector90_center_offset = 17.2

        #self.add_part(prim=self.part_d30_connector90(), position=[0, d30_connector90_center_offset, 0], orientation=[-90,0,90], prim_path=f"{part_prim_path}/connector")
        self.add_part(stage=part_stage,parth_path=self.part_d30_connector90(), position=[0, 0, d30_connector90_center_offset], orientation=[0,-90,0], prim_path=f"{part_prim_path}/connector_bottom")
        self.add_part(stage=part_stage,parth_path=self.part_d30_profile(height-25), position=[0, 0, 25], prim_path=f"{part_prim_path}/profile")
        if connector_on_top:
            self.add_part(stage=part_stage,parth_path=self.part_d30_connector_d30(), position=[0, 0, height], orientation=[180,90,0], prim_path=f"{part_prim_path}/connector_top")
        part_stage.SetDefaultPrim( part_stage.GetPrimAtPath("/World"))
        part_stage.Save()            
        return path  

        

    def create_40x40_base(self, width, depth)->Prim:
        base_path = "/World/rack/base"
        base_prim = self._stage.DefinePrim(base_path, 'Xform') 
        self.add_part(prim=self.component_40x40_frame(width,depth), position=[0,120,0], prim_path=f"{base_path}/frame")
        wheels_path = f"{base_path}/wheels"
        self.add_part(prim=self.part_d30_wheel(), position=[20,120,80], orientation=[-90,0,0], prim_path=f"{wheels_path}/_1")
        self.add_part(prim=self.part_d30_wheel(), position=[width-20,120,80], orientation=[-90,0,0], prim_path=f"{wheels_path}/_2")
        self.add_part(prim=self.part_d30_wheel(), position=[20,120,depth-40], orientation=[-90,0,0], prim_path=f"{wheels_path}/_3")
        self.add_part(prim=self.part_d30_wheel(), position=[width-20,120,depth-40], orientation=[-90,0,0], prim_path=f"{wheels_path}/_4")
        return base_prim

    def get_or_create_component(self, part_name, creator )->str:        
        path = self.component_usd_path(part_name)
        if self.component_exists(part_name):
            return path
        part_stage = self.create_component_stage(part_name)
        part_prim_path = "/World"
        part_prim  = part_stage.DefinePrim(part_prim_path, 'Xform')
        creator(self, part_stage, part_prim_path)
        part_stage.SetDefaultPrim( part_stage.GetPrimAtPath("/World"))
        part_stage.Save()            
        return path


    def component_d30_frame_wheels(self, width, depth)->str:
        def creator (self, part_stage, part_prim_path):
            self.add_part(stage=part_stage, part_path=self.part_d30_wheel_heavy(),
                            prim_path=f"{part_prim_path}/_1", 
                            position=[70,-15+170,150],
                            orientation=[-90,180,0])
            self.add_part(stage=part_stage, part_path=self.part_d30_wheel_heavy(),
                            prim_path=f"{part_prim_path}/_2", 
                            position=[width-70,-15+170,150],
                            orientation=[-90,180,0])
            self.add_part(stage=part_stage, part_path=self.part_d30_wheel_heavy(),
                            prim_path=f"{part_prim_path}/_3", 
                            position=[70,-15+170,depth-150],
                            orientation=[-90,180,0])
            self.add_part(stage=part_stage, part_path=self.part_d30_wheel_heavy(),
                            prim_path=f"{part_prim_path}/_4", 
                            position=[width-70,-15+170,depth-150],
                            orientation=[-90,180,0])                        
        
        return self.get_or_create_component(
            part_name=f"D30_frame_wheels_{int(width)}_{int(depth)}", creator=creator)
        

    def component_d30_base_frame(self, width, depth)->str:
        part_name = f"D30_frame_base_{int(width)}_{int(depth)}"
    
        def creator(self, part_stage, part_prim_path):

            self.add_part(part_path=self.component_d30_beam(depth, False, False), 
                            prim_path=f"{part_prim_path}/frame/_1", 
                            position=[15,0,0],stage=part_stage)
            self.add_part(part_path=self.component_d30_beam(depth, False, False), 
                            prim_path=f"{part_prim_path}/frame/_2", 
                            position=[width-15,0,0],stage=part_stage)
            self.add_part(part_path=self.component_d30_beam(width-50), 
                            prim_path=f"{part_prim_path}/frame/_3", 
                            position=[25,0,20], orientation=[90,0,90],stage=part_stage)
            self.add_part(part_path=self.component_d30_beam(width-50), 
                            prim_path=f"{part_prim_path}/frame/_4", 
                            position=[25,0,depth-20], orientation=[90,0,90],stage=part_stage) 
            dist = 140                        
            self.add_part(part_path=self.component_d30_beam(depth-60), 
                            prim_path=f"{part_prim_path}/frame/_5", 
                            position=[dist-15,0,30], orientation=[0,0,90],stage=part_stage)
            self.add_part(part_path=self.component_d30_beam(depth-60), 
                            prim_path=f"{part_prim_path}/frame/_6", 
                            position=[width-dist+15,0,30], orientation=[0,0,90],stage=part_stage)                              
        return self.get_or_create_component(part_name, creator)

    def component_d30_frame_side(self, depth, height, front_height, top_offset, angle, use_legs):
        part_name = f"D30_frame_side_{int(depth)}_{int(height)}_{int(front_height)}_{int(top_offset)}"        
        def creator(self, part_stage, part_prim_path):
            if use_legs:
                leg_front = self.add_part(  prim_path=f"{part_prim_path}/leg_front", 
                                            part_path=self.component_d30_leg(front_height), 
                                            stage= part_stage ,
                                            position=[0,0,20], 
                                            orientation=[-90,0,0] )
                leg_middle = self.add_part( prim_path=f"{part_prim_path}/leg_middle" , 
                                            part_path=self.component_d30_leg(height-25-20), 
                                            stage= part_stage ,
                                            position=[0,0,depth/2-20], 
                                            orientation=[-90,0,0], )
                leg_back = self.add_part(   prim_path=f"{part_prim_path}/leg_back" , 
                                            part_path=self.component_d30_leg(height, connector_on_top=False), 
                                            stage= part_stage ,
                                            position=[0,0,depth-20], 
                                            orientation=[-90,0,0])
            else:
                beam_front = self.add_part( prim_path=f"{part_prim_path}/beam_front", 
                                            part_path=self.component_d30_beam(front_height-15), 
                                            stage= part_stage ,
                                            position=[0,15,20], 
                                            orientation=[-90,0,0] )
                beam_middle = self.add_part( prim_path=f"{part_prim_path}/beam_middle" , 
                                            part_path=self.component_d30_beam(height-30), 
                                            stage= part_stage ,
                                            position=[0,0,depth/2-20], 
                                            orientation=[-90,0,0], )
                beam_back = self.add_part(  prim_path=f"{part_prim_path}/beam_back" , 
                                            part_path=self.component_d30_beam(height, connector_on_top=False), 
                                            stage= part_stage ,
                                            position=[0,0,depth-20], 
                                            orientation=[-90,0,0])

            angle_connector_front = self.add_part(
                                            prim_path=f"{part_prim_path}/angle_connector_front_left" , 
                                            part_path=self.part_d30_angle_connector(), 
                                            stage= part_stage ,
                                            position=[0, front_height+20, 20], 
                                            orientation=[90,0,90] )

            beam_top = self.add_part(   prim_path=f"{part_prim_path}/beam_top_left" , 
                                        part_path=self.component_d30_beam(depth-top_offset-30, connector_on_top=False), 
                                        stage= part_stage ,
                                        position=[0, height-20, depth-30], 
                                        orientation=[180,0,0] )
            connector_top = self.add_part(
                                        prim_path=f"{part_prim_path}/connector_top_left", 
                                        part_path=self.part_d30_connector_parallel(), 
                                        stage= part_stage ,
                                        position=[0, height-45, top_offset+20], 
                                        orientation=[90,0,90] )
            
            angle_connector_top = self.add_part(
                                        prim_path=f"{part_prim_path}/angle_connector_top_left" , 
                                        part_path=self.part_d30_angle_connector(), 
                                        stage= part_stage ,
                                        position=[0, height-80, top_offset+20], 
                                        orientation=[-90,0,-90] )
            
            
            self.set_d30_angle_connector_angle(angle_connector_top, angle)
            self.set_d30_angle_connector_angle(angle_connector_front, angle)
            top_connector_xf = self.d30_angle_connector_angle_xf(angle_connector_top)        
            front_connector_xf = self.d30_angle_connector_angle_xf(angle_connector_front)
            posA = top_connector_xf.Transform(Gf.Vec3d(20,0,0))
            posB = front_connector_xf.Transform(Gf.Vec3d(20,0,0))
            dist = (posB-posA).GetLength()
            dia_beam = self.add_part(
                                part_path=self.component_d30_beam(dist), 
                                stage= part_stage,
                                position=[20, 0, 0], 
                                orientation=[0,90,0],
                                parent_xf=top_connector_xf,
                                prim_path=f"{part_prim_path}/diagonal_profile_left")        
        return self.get_or_create_component(part_name, creator)
    
    def component_d30_frame(self, width, depth, top_offset, front_height, height, angle):
        part_name = f"D30_frame_{int(width)}_{int(depth)}_{int(height)}_{int(front_height)}_{int(top_offset)}"        
        def creator(self, part_stage, part_prim_path):
            #-- legs 
            frame_side = self.component_d30_frame_side(depth=depth, height=height, front_height=front_height, top_offset = top_offset, angle=angle, use_legs=False)
            side_left = self.add_part(  prim_path=f"{part_prim_path}/leg_front_left", 
                                        part_path=frame_side, 
                                        position=[15,10,0] ,
                                        stage = part_stage)
            side_right = self.add_part( prim_path=f"{part_prim_path}/leg_front_right", 
                                        part_path=frame_side, 
                                        position=[width-15,10,0],
                                        stage = part_stage)
        
        return self.get_or_create_component(part_name, creator)

    def component_shelf(self, width, depth, top_offset, front_height, height)->Prim:
        part_name = f"D30_shelf_{int(width)}_{int(depth)}_{int(height)}_{int(back_offset)}_{int(top_offset)}"        
        part_prim_path = f"{self._bom_path}/components/{part_name}"
        
        existing = self._stage.GetPrimAtPath(part_prim_path)
        if existing.IsValid(): 
            return existing
        part_prim  = self._stage.DefinePrim(part_prim_path, 'Xform')
        front_connector_beam = self.add_part(
                            prim=self.component_d30_beam(width-50), 
                            position=[25, height-10, top_offset+20], 
                            orientation=[90,0,90],                            
                            prim_path=f"{part_prim_path}/front_beam")        
        back_connector_beam = self.add_part(
                            prim=self.component_d30_beam(width-50), 
                            position=[25, height-10-back_offset, depth-20], 
                            orientation=[90,0,90],                            
                            prim_path=f"{part_prim_path}/back_beam")        
        return part_prim
    

    def build_flow_rack(self, stage, rack:BeamFlowRackModel, zUp:bool=True, scaleM:bool=True)->str:
            # wheels 
            if zUp:
                UsdGeom.SetStageUpAxis(stage, UsdGeom.Tokens.z)
            rack_path = f"/World/FlowRack"            
            
            self._rack_path = rack_path 
            frame_path = f"{rack_path}"

            cd = BeamFlowRackModelCustomData(rack)
            cd.write(stage, rack_path)
            rack_prim = stage.GetPrimAtPath(rack_path)                

            self.add_part(part_path=self.component_d30_frame_wheels(width=rack.width, depth=rack.depth), 
                position=[0,0,0], 
                stage =stage,
                prim_path=f"{frame_path}/wheels")
            # frame base 
            if rack.heavy_duty:
                self.add_part(part_path=self.component_40x40_frame(width=rack.width, depth=rack.depth), 
                    position=[0,rack.frame_floor_offset,0], 
                    prim_path=f"{frame_path}/base",stage=stage)
            else:
                self.add_part(part_path=self.component_d30_base_frame(width=rack.width, depth=rack.depth), 
                    position=[0,rack.frame_floor_offset+rack.base_frame_height/2,0], 
                    prim_path=f"{frame_path}/base",stage=stage)
            # sides 
            self.add_part(part_path=self.component_d30_frame(            
                depth=rack.depth,
                height=rack.frame_height(), 
                width=rack.width,
                front_height=rack.frame_front_height, 
                top_offset=rack.frame_top_offset,
                angle=rack.front_beam_angle()
                ),
                position=[0,rack.frame_floor_offset,0], 
                prim_path=f"{frame_path}/sides",
                stage=stage
                )

            idx = 0 
            for shelf in rack.shelves:                
                shelf_prim_path = f"{frame_path}/shelves/_{idx}"
                back_position = [25, rack.abs_shelf_back_height(shelf), rack.depth-20]
                front_position = [25,rack.abs_shelf_front_beam_height(shelf),
                                rack.shelf_front_beam_offset(shelf)]
                    
                is_back = front_position[1] > back_position[1]
                beam_length = rack.width-50
                front_connector_beam = self.add_part(
                        part_path=self.component_d30_beam(beam_length), 
                        position=front_position,
                        orientation=[90,90- rack.shelf_front_beam_angle(shelf),90],                            
                        prim_path=f"{shelf_prim_path}/front_beam",
                        stage=stage)   

                self.add_part(
                        part_path=self.component_d30_wheelbar(length=rack.wheelbar_length_on_shelf(shelf), high_front=is_back, with_side=2), 
                        position= [front_position[0]+70,front_position[1],front_position[2]],
                        orientation=[rack.shelf_angle(shelf), 0,0],
                        prim_path=f"{shelf_prim_path}/wheel_1",
                        stage=stage)

                self.add_part(part_path=self.component_d30_wheelbar(length=rack.wheelbar_length_on_shelf(shelf), high_front=is_back, with_side=1), 
                        position= [front_position[0]+rack.width-120,front_position[1],front_position[2]],
                        orientation=[rack.shelf_angle(shelf), 0,0],
                        prim_path=f"{shelf_prim_path}/wheel_2",
                        stage=stage) 
                num_inners = math.ceil(beam_length / shelf.wheelbar_distance)-2
                for i in range(1,num_inners+1):
                    self.add_part(part_path=self.component_d30_wheelbar(length=rack.wheelbar_length_on_shelf(shelf), high_front=is_back, with_side=0), 
                        position= [front_position[0]+70 + i*shelf.wheelbar_distance,front_position[1],front_position[2]],
                        orientation=[rack.shelf_angle(shelf), 0,0],
                        prim_path=f"{shelf_prim_path}/wheel_{2+i}",
                        stage=stage)

                back_connector_beam = self.add_part(
                            part_path=self.component_d30_beam(beam_length), 
                            position=back_position, 
                            orientation=[90,90,90],                            
                            prim_path=f"{shelf_prim_path}/back_beam",
                            stage=stage)
                idx += 1  
            
            xf = UsdGeom.Xformable(rack_prim)
            scale = 1 
            if scaleM:
                scale = 0.1 
            if zUp:                
                pos = Gf.Vec3d(rack.width*scale,0,0)
                rotEuler = Gf.Vec3f(-90,180,0)
                xf.ClearXformOpOrder ()
                xf.AddTranslateOp().Set(pos)    
                xf.AddRotateXYZOp().Set(rotEuler)    
            if scaleM:
                
                xf.AddScaleOp().Set(Gf.Vec3f(scale, scale, scale))
            return rack_path