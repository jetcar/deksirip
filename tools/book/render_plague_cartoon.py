"""Render stable stylized 3D scenes for TikTok short 044 with Blender."""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector


ROOT = Path(__file__).resolve().parents[2] / "book"
DEFAULT_OUTPUT = ROOT / "shorts" / "out" / "tiktok" / "short-044-blender-scenes"
FPS = 24
FRAMES = 109

# Blender 5.x APIs used below:
# https://docs.blender.org/api/dev/bpy.ops.mesh.html#bpy.ops.mesh.primitive_uv_sphere_add
# https://docs.blender.org/api/master/bpy.types.bpy_struct.html#bpy.types.bpy_struct.keyframe_insert


def material(name: str, color: tuple[float, float, float, float], metallic: float = 0.0):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.diffuse_color = color
    mat.metallic = metallic
    mat.roughness = 0.52
    shader = mat.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = color
    shader.inputs["Metallic"].default_value = metallic
    shader.inputs["Roughness"].default_value = 0.52
    return mat


def smooth(obj) -> None:
    if hasattr(obj.data, "polygons"):
        for polygon in obj.data.polygons:
            polygon.use_smooth = True


def cube(name: str, location, scale, mat, bevel: float = 0.12, parent=None):
    bpy.ops.mesh.primitive_cube_add(location=location)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel:
        modifier = obj.modifiers.new("Soft edges", "BEVEL")
        modifier.width = bevel
        modifier.segments = 3
    obj.data.materials.append(mat)
    if parent:
        obj.parent = parent
    return obj


def sphere(name: str, location, scale, mat, parent=None, segments: int = 32):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segments, ring_count=16, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    smooth(obj)
    obj.data.materials.append(mat)
    if parent:
        obj.parent = parent
    return obj


def cylinder(name: str, location, radius: float, depth: float, mat, parent=None):
    bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=radius, depth=depth, location=location)
    obj = bpy.context.object
    obj.name = name
    smooth(obj)
    obj.data.materials.append(mat)
    if parent:
        obj.parent = parent
    return obj


def torus(name: str, location, major: float, minor: float, mat, rotation=(math.pi / 2, 0, 0), parent=None):
    bpy.ops.mesh.primitive_torus_add(
        major_radius=major, minor_radius=minor, major_segments=32, minor_segments=12,
        location=location, rotation=rotation,
    )
    obj = bpy.context.object
    obj.name = name
    smooth(obj)
    obj.data.materials.append(mat)
    if parent:
        obj.parent = parent
    return obj


def empty(name: str, location=(0, 0, 0), parent=None):
    obj = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(obj)
    obj.location = location
    obj.empty_display_type = "PLAIN_AXES"
    obj.parent = parent
    return obj


def key(obj, frame: int, *, location=None, rotation=None, scale=None) -> None:
    if location is not None:
        obj.location = location
        obj.keyframe_insert("location", frame=frame)
    if rotation is not None:
        obj.rotation_euler = rotation
        obj.keyframe_insert("rotation_euler", frame=frame)
    if scale is not None:
        obj.scale = scale
        obj.keyframe_insert("scale", frame=frame)


def limb(name: str, pivot, length: float, radius: float, cloth, skin, parent):
    joint = empty(f"{name}.pivot", pivot, parent)
    cylinder(f"{name}.sleeve", (0, 0, -length / 2), radius, length, cloth, joint)
    sphere(f"{name}.hand", (0, -0.02, -length), (radius * 1.25,) * 3, skin, joint)
    return joint


def character(name: str, location, tunic, *, body_scale=1.0, official=False):
    skin = material("Skin", (0.92, 0.55, 0.33, 1))
    dark = material("Hair", (0.12, 0.045, 0.018, 1))
    white = material("Eyes", (0.98, 0.98, 0.92, 1))
    black = material("Pupils", (0.015, 0.012, 0.01, 1))
    brown = material("Boots", (0.15, 0.055, 0.025, 1))
    root = empty(name, location)
    body = sphere(f"{name}.body", (0, 0, 3.9), (0.82 * body_scale, 0.5, 1.05), tunic, root)
    belt = torus(f"{name}.belt", (0, 0, 3.65), 0.72 * body_scale, 0.08, brown, rotation=(0, 0, 0), parent=root)
    head = empty(f"{name}.head", (0, 0, 5.45), root)
    sphere(f"{name}.face", (0, 0, 0), (0.67, 0.56, 0.75), skin, head)
    sphere(f"{name}.nose", (0, -0.56, -0.03), (0.13, 0.18, 0.16), skin, head)
    hair = sphere(f"{name}.hair", (0, 0.08, 0.39), (0.71, 0.58, 0.43), dark, head)
    for x in (-0.23, 0.23):
        sphere(f"{name}.eye.{x}", (x, -0.54, 0.16), (0.14, 0.06, 0.18), white, head)
        sphere(f"{name}.pupil.{x}", (x, -0.605, 0.15), (0.055, 0.025, 0.075), black, head)
        cube(f"{name}.brow.{x}", (x, -0.59, 0.39), (0.16, 0.035, 0.035), dark, 0.03, head)
    mouth = sphere(f"{name}.mouth", (0, -0.585, -0.28), (0.23, 0.035, 0.07), black, head)
    left_arm = limb(f"{name}.arm.L", (-0.72 * body_scale, 0, 4.55), 1.25, 0.18, tunic, skin, root)
    right_arm = limb(f"{name}.arm.R", (0.72 * body_scale, 0, 4.55), 1.25, 0.18, tunic, skin, root)
    left_leg = limb(f"{name}.leg.L", (-0.34, 0, 3.18), 1.55, 0.21, brown, brown, root)
    right_leg = limb(f"{name}.leg.R", (0.34, 0, 3.18), 1.55, 0.21, brown, brown, root)
    if official:
        hat = cylinder(f"{name}.hat", (0, 0, 6.15), 0.48, 0.28, tunic, root)
        hat.scale.x = 1.35
    return {
        "root": root, "body": body, "head": head, "hair": hair, "mouth": mouth,
        "arm_l": left_arm, "arm_r": right_arm, "leg_l": left_leg, "leg_r": right_leg,
    }


def add_house(x: float, z: float, size: float, wall, roof):
    cube(f"House.{x}", (x, 2.8, z + size), (size, 1.2, size), wall, 0.08)
    bpy.ops.mesh.primitive_cone_add(vertices=4, radius1=size * 1.5, radius2=0, depth=size * 1.3,
                                    location=(x, 2.8, z + size * 2.55), rotation=(0, 0, math.pi / 4))
    top = bpy.context.object
    top.data.materials.append(roof)


def setup_world(output: Path, still: bool):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 540
    scene.render.resolution_y = 960
    scene.render.resolution_percentage = 100
    scene.render.fps = FPS
    scene.frame_start = 1
    scene.frame_end = FRAMES
    scene.render.image_settings.media_type = "IMAGE" if still else "VIDEO"
    scene.render.image_settings.file_format = "PNG" if still else "FFMPEG"
    if not still:
        scene.render.ffmpeg.format = "MPEG4"
        scene.render.ffmpeg.codec = "H264"
        scene.render.ffmpeg.constant_rate_factor = "HIGH"
        scene.render.filepath = str(output)
    scene.world = bpy.data.worlds.new("World")
    scene.world.color = (0.055, 0.07, 0.1)
    scene.world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.055, 0.07, 0.1, 1)
    scene.world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.35

    ground = material("Ground", (0.18, 0.20, 0.16, 1))
    wall = material("Plaster", (0.42, 0.33, 0.22, 1))
    roof = material("Roof", (0.16, 0.07, 0.045, 1))
    cube("Ground", (0, 1.2, 0), (8, 7, 0.15), ground, 0)
    for x, size in ((-4.2, 1.5), (4.2, 1.7), (-1.8, 1.1)):
        add_house(x, 0, size, wall, roof)

    bpy.ops.object.light_add(type="AREA", location=(-4, -6, 9))
    bpy.context.object.data.energy = 1100
    bpy.context.object.data.shape = "DISK"
    bpy.context.object.data.size = 7
    bpy.ops.object.light_add(type="AREA", location=(4, -2, 6))
    bpy.context.object.data.energy = 650
    bpy.context.object.data.color = (1.0, 0.55, 0.3)
    bpy.context.object.data.size = 5

    bpy.ops.object.camera_add(location=(0, -18, 5.1))
    camera = bpy.context.object
    camera.data.type = "ORTHO"
    camera.data.ortho_scale = 8.1
    scene.camera = camera
    direction = Vector((0, 0.3, 4.2)) - camera.location
    camera.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    return scene, camera


def scene_one():
    green = material("Worker green", (0.16, 0.33, 0.10, 1))
    wood = material("Cart wood", (0.20, 0.075, 0.025, 1))
    cloth = material("Burial cloth", (0.72, 0.72, 0.65, 1))
    worker = character("Worker", (-1.1, 0, 0), green)
    cart = empty("Cart", (2.25, 0.25, 0))
    cube("Cart.box", (0, 0, 2.2), (1.6, 0.75, 0.35), wood, 0.08, cart)
    for x in (-1.15, 1.15):
        torus(f"Cart.wheel.{x}", (x, -0.64, 1.55), 0.72, 0.12, wood, parent=cart)
    for index, x in enumerate((-0.95, -0.3, 0.4, 1.0)):
        sphere(f"Covered.{index}", (x, 0, 2.75), (0.52, 0.48, 0.34), cloth, cart)

    key(worker["root"], 1, location=(-1.1, 0, 0))
    key(worker["root"], 54, location=(-1.1, 0, 0.08))
    key(worker["root"], FRAMES, location=(-1.1, 0, 0))
    key(worker["head"], 1, rotation=(0.05, 0.12, -0.04))
    key(worker["head"], 54, rotation=(-0.08, -0.18, 0.05))
    key(worker["head"], FRAMES, rotation=(0.05, 0.12, -0.04))
    key(worker["arm_r"], 1, rotation=(0, 0.18, 0))
    key(worker["arm_r"], 38, rotation=(0, 2.45, 0))
    key(worker["arm_r"], 82, rotation=(0, 2.25, 0.12))
    key(worker["arm_r"], FRAMES, rotation=(0, 0.18, 0))
    key(worker["mouth"], 1, scale=(1, 1, 0.8))
    key(worker["mouth"], 54, scale=(1.25, 1, 1.7))
    key(worker["mouth"], FRAMES, scale=(1, 1, 0.8))
    key(cart, 1, location=(2.55, 0.25, 0))
    key(cart, FRAMES, location=(1.95, 0.25, 0))
    return worker


def coin_bag(name: str, location, color, parent=None):
    root = empty(name, location, parent)
    sphere(f"{name}.bag", (0, 0, 0), (0.48, 0.26, 0.58), color, root)
    cylinder(f"{name}.neck", (0, 0, 0.54), 0.16, 0.22, color, root)
    gold = material("Gold", (0.95, 0.55, 0.05, 1), metallic=0.45)
    for index, x in enumerate((-0.18, 0, 0.18)):
        sphere(f"{name}.coin.{index}", (x, -0.18, 0.72), (0.12, 0.04, 0.12), gold, root, 20)
    return root


def parchment(name: str, location, parent=None):
    paper = material("Parchment", (0.78, 0.58, 0.28, 1))
    red = material("Royal wax", (0.55, 0.025, 0.018, 1))
    root = empty(name, location, parent)
    cube(f"{name}.sheet", (0, 0, 0), (0.64, 0.06, 0.92), paper, 0.05, root)
    cylinder(f"{name}.top", (0, 0, 0.92), 0.10, 1.35, paper, root).rotation_euler.y = math.pi / 2
    cylinder(f"{name}.bottom", (0, 0, -0.92), 0.10, 1.35, paper, root).rotation_euler.y = math.pi / 2
    sphere(f"{name}.seal", (0.42, -0.10, -0.58), (0.22, 0.07, 0.22), red, root)
    return root


def scene_two():
    green = material("Worker green", (0.16, 0.33, 0.10, 1))
    red = material("Landowner red", (0.46, 0.035, 0.025, 1))
    blue = material("Landowner blue", (0.035, 0.10, 0.38, 1))
    sack = material("Money sack", (0.45, 0.27, 0.10, 1))
    worker = character("Worker", (0, 0, 0), green)
    owner_l = character("OwnerRed", (-2.35, 0.2, 0), red, body_scale=1.22)
    owner_r = character("OwnerBlue", (2.35, 0.2, 0), blue, body_scale=1.22)
    bag_l = coin_bag("OfferRed", (-1.0, -0.25, 4.55), sack)
    bag_r = coin_bag("OfferBlue", (1.0, -0.25, 4.55), sack)

    key(owner_l["root"], 1, location=(-2.35, 0.2, 0))
    key(owner_l["root"], 34, location=(-2.05, 0.05, 0.12))
    key(owner_l["root"], 70, location=(-2.45, 0.2, 0))
    key(owner_l["root"], FRAMES, location=(-2.35, 0.2, 0))
    key(owner_r["root"], 1, location=(2.35, 0.2, 0))
    key(owner_r["root"], 34, location=(2.45, 0.2, 0))
    key(owner_r["root"], 70, location=(2.05, 0.05, 0.12))
    key(owner_r["root"], FRAMES, location=(2.35, 0.2, 0))
    for arm, direction in ((owner_l["arm_r"], 2.0), (owner_r["arm_l"], -2.0)):
        key(arm, 1, rotation=(0, 0.3 * math.copysign(1, direction), 0))
        key(arm, 34, rotation=(0, direction, 0.12))
        key(arm, 70, rotation=(0, direction * 0.78, -0.10))
        key(arm, FRAMES, rotation=(0, direction, 0.12))
    key(bag_l, 1, location=(-1.15, -0.25, 4.25), rotation=(0, 0, -0.12))
    key(bag_l, 34, location=(-0.85, -0.30, 5.0), rotation=(0, 0, 0.16))
    key(bag_l, 70, location=(-1.05, -0.25, 4.65), rotation=(0, 0, -0.10))
    key(bag_l, FRAMES, location=(-0.85, -0.30, 5.0), rotation=(0, 0, 0.16))
    key(bag_r, 1, location=(1.1, -0.25, 4.45), rotation=(0, 0, 0.12))
    key(bag_r, 34, location=(1.0, -0.25, 4.7), rotation=(0, 0, -0.10))
    key(bag_r, 70, location=(0.78, -0.30, 5.1), rotation=(0, 0, 0.14))
    key(bag_r, FRAMES, location=(1.0, -0.25, 4.7), rotation=(0, 0, -0.10))
    key(worker["head"], 1, rotation=(0, -0.28, 0))
    key(worker["head"], 52, rotation=(0, 0.32, 0))
    key(worker["head"], FRAMES, rotation=(0, -0.28, 0))
    key(worker["mouth"], 1, scale=(0.8, 1, 0.6))
    key(worker["mouth"], 52, scale=(1.35, 1, 0.65))
    key(worker["mouth"], FRAMES, scale=(1.15, 1, 0.55))


def scene_three():
    red = material("Landowner red", (0.46, 0.035, 0.025, 1))
    blue = material("Landowner blue", (0.035, 0.10, 0.38, 1))
    royal = material("Royal robe", (0.50, 0.09, 0.035, 1))
    green = material("Worker green", (0.16, 0.33, 0.10, 1))
    wood = material("Desk wood", (0.18, 0.055, 0.018, 1))
    owner_l = character("OwnerRed", (-2.25, 0.15, 0), red, body_scale=1.18)
    owner_r = character("OwnerBlue", (-0.35, 0.1, 0), blue, body_scale=1.18)
    official = character("Official", (1.65, 0.15, 0), royal, body_scale=1.15, official=True)
    worker = character("Worker", (3.05, 1.3, 0.35), green, body_scale=0.76)
    cube("Desk", (1.45, -0.55, 2.55), (1.7, 0.55, 0.25), wood, 0.10)
    law = parchment("Draft law", (1.5, -0.95, 3.25))

    key(owner_l["arm_r"], 1, rotation=(0, 0.25, 0))
    key(owner_l["arm_r"], 45, rotation=(0, 1.72, -0.18))
    key(owner_l["arm_r"], 78, rotation=(0, 1.30, 0.18))
    key(owner_l["arm_r"], FRAMES, rotation=(0, 1.72, -0.18))
    key(owner_r["arm_r"], 1, rotation=(0, 0.1, 0))
    key(owner_r["arm_r"], 45, rotation=(0, 1.95, 0.15))
    key(owner_r["arm_r"], 78, rotation=(0, 1.55, -0.15))
    key(owner_r["arm_r"], FRAMES, rotation=(0, 1.95, 0.15))
    key(official["head"], 1, rotation=(0, -0.35, 0.02))
    key(official["head"], 45, rotation=(0.12, 0.15, -0.04))
    key(official["head"], 78, rotation=(-0.12, -0.15, 0.02))
    key(official["head"], FRAMES, rotation=(0.12, 0.15, -0.04))
    key(official["arm_l"], 1, rotation=(0, -0.2, 0))
    key(official["arm_l"], 58, rotation=(0, -2.22, 0.18))
    key(official["arm_l"], FRAMES, rotation=(0, -1.85, -0.15))
    key(law, 1, rotation=(0, 0, -0.05), scale=(0.70, 0.70, 0.70))
    key(law, 58, rotation=(0, 0, 0.06), scale=(0.82, 0.82, 0.82))
    key(law, FRAMES, rotation=(0, 0, -0.05), scale=(0.74, 0.74, 0.74))
    key(worker["head"], 1, rotation=(0, -0.25, 0))
    key(worker["head"], 58, rotation=(0, 0.25, 0))
    key(worker["head"], FRAMES, rotation=(0, -0.25, 0))


def scene_four():
    green = material("Worker green", (0.16, 0.33, 0.10, 1))
    red = material("Landowner red", (0.46, 0.035, 0.025, 1))
    blue = material("Landowner blue", (0.035, 0.10, 0.38, 1))
    royal = material("Royal robe", (0.50, 0.09, 0.035, 1))
    sack = material("Money sack", (0.45, 0.27, 0.10, 1))
    worker = character("Worker", (-1.75, -0.15, 0), green)
    official = character("Official", (0.75, 0, 0), royal, body_scale=1.14, official=True)
    owner_l = character("OwnerRed", (2.05, 1.1, 0.35), red, body_scale=0.88)
    owner_r = character("OwnerBlue", (3.00, 1.25, 0.45), blue, body_scale=0.82)
    law = parchment("Law", (0.75, -0.85, 4.05))
    bag_l = coin_bag("BagRed", (2.00, -0.15, 4.75), sack)
    bag_r = coin_bag("BagBlue", (2.90, -0.10, 4.45), sack)

    key(worker["arm_l"], 1, rotation=(0, -0.15, 0))
    key(worker["arm_l"], 45, rotation=(0, -1.75, -0.35))
    key(worker["arm_l"], 78, rotation=(0, -1.95, -0.18))
    key(worker["arm_l"], FRAMES, rotation=(0, -1.75, -0.35))
    key(worker["arm_r"], 1, rotation=(0, 0.15, 0))
    key(worker["arm_r"], 45, rotation=(0, 1.75, 0.35))
    key(worker["arm_r"], 78, rotation=(0, 1.95, 0.18))
    key(worker["arm_r"], FRAMES, rotation=(0, 1.75, 0.35))
    key(worker["head"], 1, rotation=(0, -0.20, 0))
    key(worker["head"], 45, rotation=(0.10, 0.28, -0.08))
    key(worker["head"], 78, rotation=(-0.08, -0.22, 0.10))
    key(worker["head"], FRAMES, rotation=(0.10, 0.28, -0.08))
    key(worker["mouth"], 1, scale=(0.8, 1, 0.7))
    key(worker["mouth"], 45, scale=(1.45, 1, 0.45))
    key(worker["mouth"], FRAMES, scale=(1.45, 1, 0.45))
    key(official["head"], 1, rotation=(0, -0.15, 0))
    key(official["head"], 52, rotation=(0, 0.25, 0.04))
    key(official["head"], FRAMES, rotation=(0, -0.35, -0.06))
    key(law, 1, rotation=(0, 0, -0.08), scale=(0.62, 0.62, 0.62))
    key(law, 52, rotation=(0, 0, 0.08), scale=(0.74, 0.74, 0.74))
    key(law, FRAMES, rotation=(0, 0, -0.08), scale=(0.66, 0.66, 0.66))
    for bag, x in ((bag_l, 2.00), (bag_r, 2.90)):
        key(bag, 1, location=(x, -0.15, 4.6))
        key(bag, 38, location=(x - 0.2, -0.25, 5.25), rotation=(0, 0, -0.12))
        key(bag, 76, location=(x + 0.1, -0.18, 4.8), rotation=(0, 0, 0.12))
        key(bag, FRAMES, location=(x - 0.2, -0.25, 5.25), rotation=(0, 0, -0.12))


def parse_args() -> argparse.Namespace:
    values = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scene", type=int, choices=(1, 2, 3, 4), default=1)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--still", action="store_true")
    return parser.parse_args(values)


def main() -> None:
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    output = args.output_dir / (
        f"preview-scene-{args.scene:02}.png" if args.still else f"scene-{args.scene:02}.mp4"
    )
    scene, _ = setup_world(output, args.still)
    (scene_one, scene_two, scene_three, scene_four)[args.scene - 1]()
    if args.still:
        scene.frame_set(54)
        scene.render.filepath = str(output)
        bpy.ops.render.render(write_still=True)
    else:
        bpy.ops.render.render(animation=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(args.output_dir / f"scene-{args.scene:02}.blend"))


if __name__ == "__main__":
    main()
