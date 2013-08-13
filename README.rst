pyfbx_render
============

This is a script to automate rendering FBX files from Blender.

The way it works is you can call blender from the command line pass in an
`FBX`, `HDR` and output paths and render out an image.

The script handles importing the FBX, framing the model inside the camera and rendering.

Example command line use::

    blender --background -noaudio \
            --factory-startup \
            --python pyfbx_render.py \
            -- \
            --fbx="/path/to/some.fbx" \
            --hdr="/path/to/image.hdr" \
            --width=800 --height=800 \
            --samples=80 \
            --render="/tmp/render_out_image" \
            --save="/tmp/blend_out.blend"
