import unreal, math, json

OUT = r"C:\Users\mercu\clawd\repo-staging\Corpus-Perspectival\Technical-Work\AIGrandPrix\ue5_sim\cpp_validation.json"
res = {"ok": False, "error": None, "tests": {}}

try:
    DronePawn = getattr(unreal, "DronePawn", None)
    if DronePawn is None:
        res["error"] = "unreal.DronePawn not found — module not loaded / class not registered"
        with open(OUT, "w") as f: json.dump(res, f, indent=2)
        raise SystemExit

    eas = unreal.EditorActorSubsystem()
    ual = unreal.EditorAssetLibrary
    cube = ual.load_asset('/Engine/BasicShapes/Cube.Cube')

    # emissive cyan material so the drone + trail are visible in any lighting
    pkg = '/Game/FlightSchool'; cpath = pkg + '/M_DroneCyan'
    if ual.does_asset_exist(cpath):
        mcyan = ual.load_asset(cpath)
    else:
        at = unreal.AssetToolsHelpers.get_asset_tools()
        mcyan = at.create_asset('M_DroneCyan', pkg, unreal.Material, unreal.MaterialFactoryNew())
        mel = unreal.MaterialEditingLibrary
        nd = mel.create_material_expression(mcyan, unreal.MaterialExpressionConstant3Vector, -350, 0)
        nd.set_editor_property('constant', unreal.LinearColor(0.05, 3.0, 4.0, 1.0))
        mel.connect_material_property(nd, '', unreal.MaterialProperty.MP_EMISSIVE_COLOR)
        mel.recompile_material(mcyan)

    # clear prior validation actors
    for a in eas.get_all_level_actors():
        if isinstance(a, unreal.StaticMeshActor) and a.actor_has_tag('clawd_ghost'):
            eas.destroy_actor(a)
        if isinstance(a, DronePawn) and a.actor_has_tag('clawd_val'):
            eas.destroy_actor(a)

    def ghost(x, y, z, s, tag='clawd_ghost'):
        a = eas.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(x, y, z))
        a.static_mesh_component.set_static_mesh(cube)
        a.set_actor_scale3d(unreal.Vector(s, s, s))
        a.static_mesh_component.set_material(0, mcyan)
        a.tags = [tag]
        return a

    dt = 1.0 / 120.0

    def run_test(name, action, steps=120, start=(0, 0, 200), leave_trail=False):
        pawn = eas.spawn_actor_from_class(DronePawn, unreal.Vector(*start))
        pawn.tags = ['clawd_val']
        pawn.body.set_static_mesh(cube)
        pawn.set_actor_scale3d(unreal.Vector(0.4, 0.4, 0.4))
        pawn.body.set_material(0, mcyan)
        pawn.reset_state(unreal.Vector(*start))
        coll, wx, wy, wz = action
        traj = []
        for i in range(steps):
            pawn.step(coll, wx, wy, wz, dt)
            if leave_trail and i % 20 == 0:
                s = pawn.get_state_vector()
                traj.append((s[0], s[1], s[2]))
        pawn.sync_visual()
        s = list(pawn.get_state_vector())
        if leave_trail:
            for (x, y, z) in traj:
                ghost(x, y, z, 0.15)
        else:
            eas.destroy_actor(pawn)  # keep only the climb drone visible
        return s

    res["tests"]["climb"] = run_test("climb", (0.5, 0, 0, 0), leave_trail=True)
    res["tests"]["pitch"] = run_test("pitch", (0.26, 0, 2, 0))
    res["tests"]["roll"]  = run_test("roll",  (0.26, 2, 0, 0))
    res["tests"]["yaw"]   = run_test("yaw",   (0.26, 0, 0, 2))

    # yaw heading from quaternion
    s = res["tests"]["yaw"]; qw, qx, qy, qz = s[6], s[7], s[8], s[9]
    res["tests"]["yaw_heading_deg"] = math.degrees(
        math.atan2(2 * (qw * qz + qx * qy), 1 - 2 * (qy * qy + qz * qz)))

    res["ok"] = True

    # frame the climb side-on
    unreal.UnrealEditorSubsystem().set_level_viewport_camera_info(
        unreal.Vector(-200, -900, 450), unreal.Rotator(0.0, -5.0, 75.0))

except Exception as e:
    res["error"] = repr(e)

with open(OUT, "w") as f:
    json.dump(res, f, indent=2)
