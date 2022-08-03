from .utils import GeoUtils
import omni.ext
import omni.ui as ui
from omni.ui import scene as sc
from .item_configurator import ItemElementBuilder
import os 
import carb 
from .beam_flow_rack_model import BeamFlowRackModel
from .beam_flow_rack_semantics import BeamFlowRackSemantics
from pxr import Sdf, Gf, Usd, UsdGeom, UsdLux



class ItemConfiguratorLiteExtension(omni.ext.IExt):
    # ext_id is current extension id. It can be used with extension manager to query additional information, like where
    # this extension is located on filesystem.
    def __init__(self) -> None:
        super().__init__()
        self._viewport_scene = None 

    def add_dir_light(self):
        omni.kit.commands.execute(
            "CreatePrimCommand",
            prim_path="/World/Light",
            prim_type="DistantLight",
            select_new_prim=False,
            attributes={UsdLux.Tokens.angle: 1.0, UsdLux.Tokens.intensity: 3000},
            create_default_xform=True,
        )

    def add_floor(self):
        floor_path = "/World/Floor"
        omni.kit.commands.execute(
            "CreatePrimCommand",
            prim_path=floor_path,
            prim_type="Cube",
            select_new_prim=False,
            attributes={UsdGeom.Tokens.size: 100},
        )
        floor_prim = self.ctx.get_stage().GetPrimAtPath(floor_path)
        floor_prim.CreateAttribute("xformOp:scale", Sdf.ValueTypeNames.Double3, False).Set(Gf.Vec3d(25, 0.1, 25))
        floor_prim.CreateAttribute("xformOpOrder", Sdf.ValueTypeNames.String, False).Set(["xformOp:scale"])
        
    
    def set_dirty(self):
        self._rebuild_button.text = "create..."
        self._rebuild_button.enabled = True 

    def settings_value(self, key, default_value="")->str : 
        settings = carb.settings.get_settings()
        result=settings.get(key)
        if result == None:
            result = default_value
        return result 

    def on_startup(self, ext_id):
        print("[ai.synctwin.itemconfiguratorlite] item configurator startup")
        
        self._selection = omni.usd.get_context().get_selection()
        self._SCRIPT_ROOT = os.path.dirname(os.path.realpath(__file__))
        self._bom_path = self.settings_value("bom_path", f"{self._SCRIPT_ROOT}/bom")
        self._templates_path = self.settings_value("templates_path", f"{self._SCRIPT_ROOT}/templates") 
        self._pedestal_path = f"{self._SCRIPT_ROOT}/models/pedestal.usd"
        print(f"bom path {self._bom_path}")
        print(f"templates path {self._templates_path}")
        
        self._rack = BeamFlowRackModel() 
                
        self._window = ui.Window("SyncTwin Flow Rack Configurator (Lite)", width=240, height=300)

        with self._window.frame:
            
            with ui.VStack():        
                ui.Label("Standard Size, 3 Feed", height=25)        
                with ui.HStack():
                    def on_2foot3feedclick():
                        self._width_field.model.set_value(755)
                        self.rebuild_rack()
                    def on_3foot3feedclick():
                        self._width_field.model.set_value(1100)
                        self.rebuild_rack()
                    def on_4foot3feedclick():
                        self._width_field.model.set_value(1376)
                        self.rebuild_rack()
                    ui.Button("2 Foot", width=75, height=85, clicked_fn=lambda: on_2foot3feedclick(),
                                style = {
                                    "Button":{
                                        "stack_direction":ui.Direction.BACK_TO_FRONT
                                    },
                                    "Button.Image": {            
                                    "image_url": f'{self._SCRIPT_ROOT}/img/rack_2foot_3feed.png',
                                    "alignment": ui.Alignment.CENTER,        },
                                    "Button.Label": {
                                        "alignment": ui.Alignment.CENTER_BOTTOM,
                                        "color":0xFF000000
                                    }
                                }
                    )
                    ui.Button("3 Foot", width=75, height=85, clicked_fn=lambda: on_3foot3feedclick(),
                                style = {
                                    "Button":{
                                        "stack_direction":ui.Direction.BACK_TO_FRONT
                                    },
                                    "Button.Image": {            
                                        "image_url": f'{self._SCRIPT_ROOT}/img/rack_3foot_3feed.png',
                                        "alignment": ui.Alignment.CENTER,        

                                    },
                                    "Button.Label": {
                                        "alignment": ui.Alignment.CENTER_BOTTOM,
                                        "color":0xFF000000
                                    }
                                }
                    )
                    ui.Button("4 Foot", width=75, height=85, clicked_fn=lambda: on_4foot3feedclick(),
                                style = {
                                    "Button":{
                                        "stack_direction":ui.Direction.BACK_TO_FRONT
                                    },
                                    "Button.Image": {            
                                        "image_url": f'{self._SCRIPT_ROOT}/img/rack_4foot_3feed.png',
                                        "alignment": ui.Alignment.CENTER,        

                                    },
                                    "Button.Label": {
                                        "alignment": ui.Alignment.CENTER_BOTTOM,
                                        "color":0xFF000000
                                    }
                                }
                                )
                    
                def on_rebuild_click(): 
                    self.rebuild_rack()
                
                ui.Label("Details:", height=25)        
                with ui.VStack():                                    
                    
                    label_width = 75
                    with ui.HStack():
                        
                        ui.Label("Width (mm):", width=label_width)
                        self._width_field = ui.IntField()
                        self._width_field.model.set_value(self._rack.width)
                        
                        self._width_field.model.add_end_edit_fn(lambda m: self.set_dirty())
                        

                    with ui.HStack(): 
                        ui.Label("Height (mm):", width=label_width)
                        self._height_field = ui.IntField()
                        self._height_field.model.set_value(self._rack.height)
                        self._height_field.model.add_end_edit_fn(lambda m: self.set_dirty())
                    with ui.HStack():
                        ui.Label("Depth (mm):", width=label_width)
                        self._depth_field = ui.IntField()
                        self._depth_field.model.set_value(self._rack.depth)
                        self._depth_field.model.add_end_edit_fn(lambda m: self.set_dirty())
                self._rebuild_button = ui.Button("rebuild", height=25, clicked_fn=lambda: on_rebuild_click())

    def on_shutdown(self):
        print("[ai.synctwin.itemconfigurator] shutdown")
        self._window = None
    
    

    def focus_prim(self):
        # omni.kit.viewport_legacy is optional dependancy
        try:
            import omni.kit.viewport_legacy

            viewport = omni.kit.viewport_legacy.get_viewport_interface()
            if viewport:
                viewport.get_viewport_window().focus_on_selected()
        except:
            pass

    def rebuild_rack(self):
        context = omni.usd.get_context()               
        context.open_stage(self._pedestal_path )
        editor_stage = context.get_stage()

        stage = editor_stage

        
        stage.SetEditTarget(Usd.EditTarget(stage.GetSessionLayer()))
        
        self._itemElm = ItemElementBuilder ( bom_path=self._bom_path, templates_path=self._templates_path)
        
                
        self._rack.width = self._width_field.model.get_value_as_float()
        self._rack.depth = self._depth_field.model.get_value_as_float()
        self._rack.height = self._height_field.model.get_value_as_float()

        rack_path = self._itemElm.build_flow_rack(stage, self._rack) 
        self._rebuild_button.text = "up to date."
        self._rebuild_button.enabled = False 
        self.add_dir_light()
        omni.kit.commands.execute(
            "SelectPrimsCommand", old_selected_paths=[], new_selected_paths=[rack_path], expand_in_stage=True
        )
        self.focus_prim()
