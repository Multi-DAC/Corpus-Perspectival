import unreal

eas = unreal.EditorActorSubsystem()

# Remove any prior gate bars (StaticMeshActors sitting on the x=1000 gate plane)
for a in eas.get_all_level_actors():
    if isinstance(a, unreal.StaticMeshActor):
        loc = a.get_actor_location()
        if abs(loc.x - 1000.0) < 1.0:
            eas.destroy_actor(a)

cube = unreal.EditorAssetLibrary.load_asset('/Engine/BasicShapes/Cube.Cube')

def bar(x, y, z, sx, sy, sz):
    a = eas.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(x, y, z))
    a.static_mesh_component.set_static_mesh(cube)
    a.set_actor_scale3d(unreal.Vector(sx, sy, sz))
    return a

# Gate centered (1000, 0, 150), ~2.7m square frame in the Y-Z plane (drone flies +X through it)
bar(1000, 0, 285, 0.2, 2.9, 0.2)    # top   (spans Y)
bar(1000, 0, 15,  0.2, 2.9, 0.2)    # bottom(spans Y)
bar(1000, -135, 150, 0.2, 0.2, 2.9) # left  (spans Z)
bar(1000,  135, 150, 0.2, 0.2, 2.9) # right (spans Z)

# Aim the editor camera at the gate
unreal.UnrealEditorSubsystem().set_level_viewport_camera_info(
    unreal.Vector(300, 0, 150), unreal.Rotator(0, 0, 0))
