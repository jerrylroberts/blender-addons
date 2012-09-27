# Addons for Blender 2.5 and 2.6

This repository contains exporters for 3D the modeling tool [Blender](http://blender.org) to the formats MD2 and VRML (.wrl). Both exporters are GPL'd.

## MD2 exporter
The MD2 exporter is based on the Blender2.49 MD2 exporter from Damien Thebault and Erwan Mathieu.
The coordinate system of the exported model is adjusted to be used in [metaio SDK](http://metaio.com) and [junaio](http://junaio.com), metaio's augmented reality browser.  
Export of animations and usage of modifiers are supported.

## VRML (.wrl) exporter
The VRML exporter uses Blenders native coordinate system and export it as-is. Export of animations and usage of modifiers are supported.

## BMesh/Ngon support
Blender 2.63 introduced [BMesh/Ngon support](http://wiki.blender.org/index.php/Dev:Ref/Release_Notes/2.63). 
There are currently two exporters because of the Blender API change with version 2.63.
Please be sure to pick the one corresponding to your blender version (2.58-2.62 use `_258.py`, 2.63+ use `_263.py`). 

