# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# <pep8-80 compliant>

# This script is an example of how you can run blender from the command line
# (in background mode with no interface) to automate tasks, in this example it
# creates a text object, camera and light, then renders and/or saves it.
# This example also shows how you can parse command line options to scripts.
#
# Example usage for this test.
#
# blender --background -noaudio \
#         --factory-startup \
#         --python pyfbx_render.py \
#         -- \
#         --fbx="/path/to/some.fbx" \
#         --hdr="/path/to/image.hdr" \
#         --width=800 --height=800 \
#         --samples=80 \
#         --render="/tmp/render_out_image" \
#         --save="/tmp/blend_out.blend"
#
#
# Notice:
# '--factory-startup' is used to avoid the user default settings from
#                     interfearing with automated scene generation.
#
# '--' causes blender to ignore all following arguments so python can use them.
#
# See blender --help for details.

import bpy


def render_hdr_set(scene, hdr_path):
    world = bpy.data.worlds.new(name="World")
    scene.world = world
    world.use_nodes = True
    tree = world.node_tree
    nodes = tree.nodes
    links = tree.links

    node_bg = nodes["Background"]
    node_bg.inputs["Strength"].default_value = 1.5  # XXX, hard coded

    node_env = nodes.new(type='ShaderNodeTexEnvironment')
    node_env.image = bpy.data.images.load(hdr_path)
    node_env.projection = 'MIRROR_BALL'  # XXX, hard coded
    links.new(node_env.outputs["Color"], node_bg.inputs["Color"])

    cycles = world.cycles
    cycles.sample_as_light = True
    cycles.sample_map_resolution = 512

    # so we dont see the HDR image
    world.cycles_visibility.camera = False


def render(fbx_path, hdr_path,
           size_x, size_y, samples,
           save_path, render_path):
    from math import radians

    scene = bpy.context.scene

    # Clear existing objects.
    scene.camera = None
    for obj in scene.objects:
        scene.objects.unlink(obj)

    render = scene.render
    cycles = scene.cycles
    render.engine = 'CYCLES'
    render.resolution_percentage = 100.0
    if render_path:
        render.filepath = render_path
    if samples:
        cycles.samples = samples

    # alpha
    render.image_settings.color_mode = 'RGBA'
    cycles.film_transparent = True

    if size_x:
        render.resolution_x = size_x
    if size_y:
        render.resolution_y = size_y

    # Camera
    cam_data = bpy.data.cameras.new("MyCam")
    cam_ob = bpy.data.objects.new(name="MyCam", object_data=cam_data)
    scene.objects.link(cam_ob)  # instance the camera object in the scene
    scene.camera = cam_ob       # set the active camera

    # Could make this an option
    cam_ob.rotation_euler = radians(60.0), radians(0.0), radians(170.0)

    # Import!
    bpy.ops.import_scene.fbx(
        axis_forward='Y',
        axis_up='Z',
        global_scale=0.001,
        filepath=fbx_path,
        use_alpha_decals=True, decal_offset=0.1)

    # frame the image with a margin
    angle = cam_data.angle
    cam_data.angle *= 0.95
    bpy.ops.view3d.camera_to_view_selected()
    cam_data.angle = angle

    if hdr_path:
        render_hdr_set(scene, hdr_path)

    # Finish up

    if save_path:
        try:
            f = open(save_path, 'w')
            f.close()
            ok = True
        except:
            print("Cannot save to path %r" % save_path)

            import traceback
            traceback.print_exc()

        if ok:
            bpy.ops.wm.save_as_mainfile(filepath=save_path)

    if render_path:
        bpy.ops.render.render(write_still=True)


def main():
    import sys
    import argparse

    argv = sys.argv

    if "--" not in argv:
        argv = []
    else:
        argv = argv[argv.index("--") + 1:]  # all args after "--"

    usage_text = (
        "Run blender in background mode with this script:"
        "  blender --background --python " + __file__ + " -- [options]")

    parser = argparse.ArgumentParser(description=usage_text)

    parser.add_argument("-F", "--fbx", dest="fbx_path", metavar='FILE',
                        help="FBX file to read from")
    parser.add_argument("-H", "--hdr", dest="hdr_path", metavar='FILE',
                        help="HDR file to use for image based lighting")

    parser.add_argument("-S", "--save", dest="save_path", metavar='FILE',
                        help="Save the generated file to the specified path")
    parser.add_argument("-r", "--render", dest="render_path", metavar='FILE',
                        help="Render an image to the specified path")

    parser.add_argument("-x", "--width", dest="size_x", metavar='N', type=int,
                        help="Image width")
    parser.add_argument("-y", "--height", dest="size_y", metavar='N', type=int,
                        help="Image height")
    parser.add_argument("-s", "--samples", dest="samples", metavar='N', type=int,
                        help="Number of samples to render with")

    args = parser.parse_args(argv)  # In this example we wont use the args

    if not argv:
        parser.print_help()
        return

    if not args.fbx_path:
        print("Error: --fbx_path=\"some file\" argument not given, aborting.")
        parser.print_help()
        return

    # Run the example function
    render(
        args.fbx_path, args.hdr_path,
        args.size_x, args.size_y, args.samples,
        args.save_path, args.render_path)

    print("batch job finished, exiting")


if __name__ == "__main__":
    main()
