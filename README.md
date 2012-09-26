Addons for Blender 2.5 and 2.6
=========================================================

This repository contains exporters for 3D modeling tool Blender to the formats MD2 and VRML (.wrl).

The MD2 exporters are based on blender2.49 exporter from Damien Thebault and Erwan Mathieu. The coordinate system is adjusted for an export into junaio (http://junaio.com), metaio's augmented reality browser.  Animations, modifiers and also ngons (Blender 2.63+) are supported.

The VRML exporter has been written from scratch. It uses Blenders native coordinate system. Animations, modifiers and also ngons (Blender 2.63+) are supported.

There are currently two exporters because of the internal api change. Possibly, they will be merged.

