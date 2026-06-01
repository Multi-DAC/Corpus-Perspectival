import unreal, math

eas = unreal.EditorActorSubsystem()
ual = unreal.EditorAssetLibrary

# --- 1. Darken: hide sky / fog / clouds / landscape / floor in the editor viewport ---
HIDE_CLASS = ('SkyAtmosphere', 'VolumetricCloud', 'ExponentialHeightFog')
HIDE_LABEL = ('Sky', 'Cloud', 'Fog', 'Floor', 'Landscape', 'Ground')
hidden = 0
for a in eas.get_all_level_actors():
    cls = a.get_class().get_name()
    lbl = a.get_actor_label()
    is_land = isinstance(a, unreal.Landscape) if hasattr(unreal, 'Landscape') else False
    if is_land or any(k in cls for k in HIDE_CLASS) or any(k in lbl for k in HIDE_LABEL):
        try:
            a.set_is_temporarily_hidden_in_editor(True); hidden += 1
        except Exception:
            pass
# dim directional + sky light so the world reads as a dark void (emissive gates self-light)
for a in eas.get_all_level_actors():
    if isinstance(a, unreal.DirectionalLight):
        try: a.light_component.set_intensity(0.15)
        except Exception: pass
    if isinstance(a, unreal.SkyLight):
        try: a.light_component.set_intensity(0.05)
        except Exception: pass

# --- 2. Emissive red gate material (bright -> blooms like the VQ1 gates) ---
pkg = '/Game/FlightSchool'
path = pkg + '/M_GateRed'
if ual.does_asset_exist(path):
    mat = ual.load_asset(path)
else:
    at = unreal.AssetToolsHelpers.get_asset_tools()
    mat = at.create_asset('M_GateRed', pkg, unreal.Material, unreal.MaterialFactoryNew())
    mel = unreal.MaterialEditingLibrary
    node = mel.create_material_expression(mat, unreal.MaterialExpressionConstant3Vector, -350, 0)
    node.set_editor_property('constant', unreal.LinearColor(5.0, 0.04, 0.04, 1.0))
    mel.connect_material_property(node, '', unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    mel.recompile_material(mat)

# --- 3. apply to all gate bars; collect centroid for the camera ---
sx = sy = sz = 0.0; n = 0
for a in eas.get_all_level_actors():
    if isinstance(a, unreal.StaticMeshActor) and a.actor_has_tag('clawd_gate'):
        a.static_mesh_component.set_material(0, mat)
        loc = a.get_actor_location(); sx += loc.x; sy += loc.y; sz += loc.z; n += 1
if n:
    cx, cy, cz = sx/n, sy/n, sz/n
else:
    cx, cy, cz = 1000, 0, 200

# --- 4. camera looking over the course from behind/above the start ---
cam = unreal.Vector(-1200, cy - 200, 900)
d = unreal.Vector(cx - cam.x, cy - cam.y, cz - cam.z)
yaw = math.degrees(math.atan2(d.y, d.x))
pitch = math.degrees(math.atan2(d.z, math.hypot(d.x, d.y)))
unreal.UnrealEditorSubsystem().set_level_viewport_camera_info(cam, unreal.Rotator(0.0, pitch, yaw))

print('hidden=%d gates_recolored=%d centroid=(%.0f,%.0f,%.0f)' % (hidden, n, cx, cy, cz))
