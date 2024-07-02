def adding_mesh_object(
        name, 
        obj_to_load, 
        texture_to_load, 
        model_info_path=None, 
        scale=1, 
        debug=False,
        child_obj_to_load=None,
        child_texture_to_load=None,
        child_scale=1
    ):
    global mesh_loaded, visii_pybullet, names_to_export

    def create_entity(name, obj_to_load, texture_to_load, scale):
        if texture_to_load is None:
            toys = load_obj_scene(obj_to_load)
            if len(toys) > 1: 
                print("more than one model in the object, materials might be wrong!")
            toy_transform = visii.entity.get(toys[0]).get_transform()
            toy_material = visii.entity.get(toys[0]).get_material()
            toy_mesh = visii.entity.get(toys[0]).get_mesh()        

            obj_export = visii.entity.create(
                    name = name,
                    transform = visii.transform.create(
                        name = name, 
                        position = toy_transform.get_position(),
                        rotation = toy_transform.get_rotation(),
                        scale = toy_transform.get_scale(),
                    ),
                    material = toy_material,
                    mesh = visii.mesh.create_from_file(name, obj_to_load),
                )

            toy_transform = obj_export.get_transform()
            obj_export.get_material().set_roughness(random.uniform(0.1, 0.5))

            for toy in toys:
                visii.entity.remove(toy)

            toys = [name]
        else:
            toys = [name]

            if obj_to_load in mesh_loaded:
                toy_mesh = mesh_loaded[obj_to_load]
            else:
                toy_mesh = visii.mesh.create_from_file(name, obj_to_load)
                mesh_loaded[obj_to_load] = toy_mesh

            toy = visii.entity.create(
                name=name,
                transform=visii.transform.create(name),
                mesh=toy_mesh,
                material=visii.material.create(name)
            )

            toy_rgb_tex = visii.texture.create_from_file(name, texture_to_load)
            toy.get_material().set_base_color_texture(toy_rgb_tex)
            toy.get_material().set_roughness(random.uniform(0.1, 0.5))

            toy_transform = toy.get_transform()

        toy_transform.set_scale(visii.vec3(scale))
        toy_transform.set_position(
            visii.vec3(
                random.uniform(0.1, 2),
                random.uniform(-1, 1),
                random.uniform(-1, 1),
            )
        )
        toy_transform.set_rotation(
            visii.quat(
                random.uniform(0, 1),
                random.uniform(0, 1),
                random.uniform(0, 1),
                random.uniform(0, 1),
            )
        )
        return toy_transform, toys

    # Create parent entity
    parent_transform, parent_toys = create_entity(name, obj_to_load, texture_to_load, scale)

    # Create child entity if provided
    if child_obj_to_load:
        child_name = f"{name}_child"
        child_transform, child_toys = create_entity(child_name, child_obj_to_load, child_texture_to_load, child_scale)
        child_transform.set_parent(parent_transform)
        parent_toys.extend(child_toys)

    # Add symmetry_corrected transform
    child_transform = visii.transform.create(f"{parent_transform.get_name()}_symmetry_corrected")
    child_transform.set_parent(parent_transform)

    # Store symmetry transforms for later use.
    symmetry_transforms = get_symmetry_transformations(model_info_path)

    # Create physics for object
    id_pybullet = create_physics(name, mass=(np.random.rand() * 5))

    if model_info_path is not None:
        try:
            with open(model_info_path) as json_file:
                model_info = json.load(json_file)
        except FileNotFoundError:
            model_info = {}
    else:
        model_info = {}

    visii_pybullet.append(
        {
            'visii_id': name,
            'bullet_id': id_pybullet,
            'base_rot': None,
            'model_info': model_info,
            'symmetry_transforms': symmetry_transforms
        }
    )
    gemPos, gemOrn = p.getBasePositionAndOrientation(id_pybullet)
    force_rand = 10
    object_position = 0.01
    p.applyExternalForce(
        id_pybullet,
        -1,
        [random.uniform(-force_rand, force_rand),
         random.uniform(-force_rand, force_rand),
         random.uniform(-force_rand, force_rand)],
        [random.uniform(-object_position, object_position),
         random.uniform(-object_position, object_position),
         random.uniform(-object_position, object_position)],
        flags=p.WORLD_FRAME
    )

    for entity_name in parent_toys:
        names_to_export.append(entity_name)
        add_cuboid(entity_name, scale=scale, debug=debug)
