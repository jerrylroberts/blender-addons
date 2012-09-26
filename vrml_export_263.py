# ***** BEGIN GPL LICENSE BLOCK *****

# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.

# ***** END GPL LICENCE BLOCK *****

#header
bl_info = {
    "name": "Export .wrl",
    "description": "Export to VRML file format (.wrl)",
    "author": "Sebastian Lieberknecht, metaio GmbH",
    "version": (0, 8),
    "blender": (2, 6, 3),
    "api": 46461,
    "location": "File > Export > wrl",
    "warning": '',
    "wiki_url": "http://metaio.com", 
    "tracker_url": "http://metaio.com",
    "category": "Import-Export"}

# open TODOs:
#   DEF/ USE for reuse of materials and textures (when using multiple objects)
#   pack animations (e.g. only export at keys)

import bpy
from bpy.props import *

from datetime import datetime

import math
from math import pi
import mathutils

import struct
import random
import os


class Export_VRML(bpy.types.Operator):
	"""Export to VRML file format (.wrl)"""
	bl_idname = "export.wrl"
	bl_label = "Export to VRML file format (.wrl)"

	filepath = StringProperty(subtype="FILE_PATH")
	filename_ext = ".wrl"
	fnLast = ""

	vrmlHeader = """#VRML V2.0 utf8
#exported by vrml_export258.py - version %i.%i
""" % bl_info["version"]

	rgCachedMaterials = []

	templateMatNode = """
					material DEF %(name)s Material 
					{
						ambientIntensity  %(ambientIntensity)s
						diffuseColor      %(diffuseColor)s
						emissiveColor     %(emissiveColor)s
						shininess         %(shininess)s
						specularColor     %(specularColor)s
						transparency      %(transparency)s
					}
					"""

	precisionXYZ = IntProperty(name = "xyz precision", 
				 default = 4, min = 2, max = 16,
				 description = "How many digits should each coordinate (xyz) have in the vrml.")
	precisionUV = IntProperty(name = "uv precision", 
				 default = 2, min = 1, max = 16,
				 description = "How many digits should each coordinate (uv) have in the vrml.")
	creaseAngle = FloatProperty(name = "crease angle (rad)", 
				 default = 0.0, min = 0.0, max = 6.28,
				 description = "Crease angle - how normals should be shared on creases.")
	globalScale = FloatProperty(name = "global scale", 
				 default = 1.0, 
				 description = "A global scaling can be applied to all coordinates.")

	fExportAnimation = BoolProperty(name = "Export animation", 
				 default = True,
				 description = "Whether the exporter should write the animation")
	iAnimFrameStart = IntProperty(name = "Start frame for animation", 
				 default = bpy.context.scene.frame_start,
				 description = "from which frame to start the animation")
	iAnimFrameStop = IntProperty(name = "Stop frame for animation", 
				 default = bpy.context.scene.frame_end,
				 description = "up to and including which frame to export the animation")
	iAnimStep = IntProperty(name = "Stepsize for animation", 
				 default = bpy.context.scene.frame_step, min=1, max=30,
				 description = "Export each nth frame only.")
	precisionKey = IntProperty(name = "key precision", 
				 default = 3, min=1, max=13,
				 description = "How many digits the key should use.")
	fLoopAnimation = BoolProperty(name = "Loop animation", 
				 default = True,
				 description = "Whether the animation should loop")
	rAnimationDurationSec = FloatProperty(name="Duration [s]",
				 default = ((bpy.context.scene.frame_end - bpy.context.scene.frame_start+1) / float(bpy.context.scene.frame_step * bpy.context.scene.render.fps)),
				 min = 0.0,
				 description = "How long the animation (one loop) should last (in seconds).")
			

	def writeObject(self, flVRML, obj, dirOut):


		# object has material?
		materialNode = ""

		if obj.material_slots:
			# see if we already wrote this material (to save space)
			mat = obj.material_slots[0].material
			sMatNameDEF = mat.name.replace(".","_").replace(" ","_")

			if sMatNameDEF in self.rgCachedMaterials:
				materialNode = "\n material USE %s\n" % sMatNameDEF
			else:
				self.rgCachedMaterials.append(sMatNameDEF)

				diffuseColor = "%.5f %.5f %.5f" % tuple(mat.diffuse_color)
				ambientIntensity = "%.5f" % mat.diffuse_intensity
				specularColor = "%.5f %.5f %.5f" % tuple(mat.specular_color)
				# emissiveColor could be used like this:
				emissiveColor = "%.5f %.5f %.5f" % tuple(mat.diffuse_color * max(mat.emit, 1.0))

				materialNode = self.templateMatNode % {
					'diffuseColor' : diffuseColor,
					'ambientIntensity' : ambientIntensity,
					'emissiveColor' : emissiveColor,
					'shininess' : "0.2",
					'specularColor' : specularColor,
					'transparency' : "0",
					'name' : sMatNameDEF,
				}


		# see if we also have a texture (as image):
		fnTexture = None
		for mat in obj.data.materials:
			for texSlot in mat.texture_slots:
				if texSlot and texSlot.texture.type == "IMAGE":
					# this is now relative to the scene file (important for
					# copying later)
					fnTexture = bpy.path.relpath(texSlot.texture.image.filepath)[2:]
					break
			
		textureNode = ""
		if fnTexture:		
			# a) copy the texture
			import os.path
			import shutil
			# path to blender scene is this:
			fnBlend = bpy.data.filepath
			try:
				shutil.copy2(os.path.join(os.path.dirname(fnBlend), fnTexture),
					os.path.join(dirOut, os.path.basename(fnTexture)))
			except: 
				print("Could not copy texture.")
				
			# ok -> now tell the VRML that we have a texture:
			textureNode = 'texture ImageTexture { url "%s" }' % os.path.basename(fnTexture)
				

		# now deal with the transformation:
		axisAngle = [0.0,0.0,0.0,0.0] # first axis, then angle
		quat = obj.matrix_world.to_quaternion()
		axisAngle[0:3] = quat.axis
		axisAngle[3] = quat.angle

		#tuple(obj.material_slots[0].material.diffuse_color)

		mapValues = { 'name' : obj.name.replace(".", "_"),
			'scale' : "%.5f %.5f %.5f" % obj.matrix_world.to_scale().to_tuple(),
			'location' : "%.5f %.5f %.5f" % obj.matrix_world.to_translation().to_tuple(),
			'rotation' : "%.5f %.5f %.5f %.5f" % tuple(axisAngle),
			'materialNode' : materialNode,
			'textureNode' : textureNode,
			'creaseAngle' : self.creaseAngle,
		}

		# write the first chunk:
		flVRML.write(
"""DEF %(name)s Transform {
	scale %(scale)s
	rotation %(rotation)s
	translation %(location)s
	children [ 
	Shape 
	{
		appearance Appearance 
		{
			%(materialNode)s
			%(textureNode)s
		}
		geometry IndexedFaceSet {
			solid FALSE
			creaseAngle %(creaseAngle).3f
""" % mapValues)

		######### UV COORDS ###########
		# if we have a texture: write the coords.
		if fnTexture:
			# ok -> just trying: (BLENDER MUST BE IN OBJECT MODE FOR THIS)

			# dump all faces.
			iTexCoord = 0
			rgTexIndex = []

			flVRML.write(" texCoord TextureCoordinate { \n point [ \n")
			uvData = obj.data.tessface_uv_textures[0].data # shortcut for below.

			sPrecUV = 2*("%%.%if "% self.precisionUV)+ ", "
			for texFace in uvData:
				rgLocIndex = []
				for uv in texFace.uv:
					rgLocIndex.append(iTexCoord)
					iTexCoord+=1
					flVRML.write(sPrecUV % tuple(uv))
				rgTexIndex.append(tuple(rgLocIndex))

			flVRML.write("] \n } \n")

			# now write the indices
			flVRML.write(" texCoordIndex [ \n" )
			for texIndexFace in rgTexIndex:
				for texIndex in texIndexFace:
					flVRML.write("%i " % texIndex)
				flVRML.write("-1 ")
			flVRML.write("\n]\n")
					

			

		######### XYZ COORDS ###########
		# ok, now on to the actual coordinates of the mesh etc.
		flVRML.write("coordIndex [\n ")
		for face in obj.data.tessfaces:
			for iCoord in face.vertices:
				flVRML.write("%i, " % iCoord)
			flVRML.write("-1, ")

		flVRML.write("] \n coord Coordinate { point [\n ")

		sPrecXYZ = 3*("%%.%if "% self.precisionXYZ) + ", "
		for vertex in obj.data.vertices:
			flVRML.write(sPrecXYZ % tuple(vertex.co))
			
		# close the geometry, and off we go!
		flVRML.write("""]
				} # end of Coordinate""")

		flVRML.write("\n  } # end of indexedFaceSet \n} # end of shape ")

		# this closes the transform.
		flVRML.write("\n ] } # end of transform for '%s'\n\n" % obj.name)

		
	def execute(self, context):
		
		fnVRML = self.filepath
		fnVRML = bpy.path.ensure_ext(fnVRML, self.filename_ext)

		# go into object mode before we start the actual export procedure
		bpy.ops.object.mode_set(mode="OBJECT", toggle=False)


		# open the file
		flVRML = open(fnVRML, "wt")

		print("Exporting to %s" % fnVRML)
		flVRML.write(self.vrmlHeader)
		flVRML.write("# from blender file: '%s'\n" % bpy.data.filepath)
		if self.fExportAnimation:
			flVRML.write("# animation created from frames %i to %i (stepsize %i)\n" %
				(self.iAnimFrameStart, self.iAnimFrameStop, self.iAnimStep))

		# the original names (to restore the selection and active object)
		rgObjNamesOriginal = [obj.name for obj in context.selected_objects]
		objNameActive = bpy.context.active_object.name

		# for the tesselation, we need copies of the data anyhow -> duplicate them.
		bpy.ops.object.duplicate()
		# now apply the modifiers to the current selection:
		bpy.ops.object.convert(keep_original=False)
		# new selection will consist of only modified geometry.
		for obj in context.selected_objects:
			obj.data.update(calc_tessface=True) # compute tesselation from ngons

		scene = bpy.context.scene
		iFrameInitial = scene.frame_current
		if self.fExportAnimation:
			iFrameInitial = scene.frame_current
			scene.frame_set(self.iAnimFrameStart)
			
		# writing global scale info:

		if self.globalScale != 1.0:
			s = self.globalScale
			flVRML.write("DEF GLOBAL_SCALE Transform {\n scale %.5f %.5f %.5f\n children [\n" % (s,s,s))

		print("Exporting geometry...")

		self.rgCachedMaterials = []
		for obj in context.selected_objects:
			print("   ...'%s'" % obj.name)

			# export this one:
			self.writeObject(flVRML, obj, os.path.dirname(fnVRML))

		if self.globalScale != 1.0:
			flVRML.write("\n] } # GLOBAL_SCALE\n\n")

		# now also export the animation:
		if self.fExportAnimation:
			

			print("Exporting animations...")
			# save the affine transformation for every exported object
			mapObjRotation = {}
			mapObjTranslation = {}
			mapObjScale = {}
			for iFrame in range(self.iAnimFrameStart, self.iAnimFrameStop+1, self.iAnimStep):
				scene.frame_set(iFrame)
				# bl 2011-10-18 - for now this is rather stupid - it dumps everything...
				# get the position of each object
				# get the rotation of each object
				# get the scale of each object

				for obj in context.selected_objects:
					
					if obj.name not in mapObjRotation.keys():
						mapObjRotation[obj.name] = []
						mapObjTranslation[obj.name] = []
						mapObjScale[obj.name] = []

					axisAngle = [0.0,0.0,0.0,0.0] # first axis, then angle
					quat = obj.matrix_world.to_quaternion()
					axisAngle[0:3] = quat.axis
					axisAngle[3] = quat.angle


					mapObjRotation[obj.name].append(tuple(axisAngle))
					mapObjTranslation[obj.name].append(obj.matrix_world.to_translation().to_tuple())
					mapObjScale[obj.name].append(obj.matrix_world.to_scale().to_tuple())

			# ok - now we have all affine transforms per object.
			# we further need one timer: #TODO exchange the cycle interval with Hz+FrameDuration
			# TODO make the loop configurable.
			timerDEF = "TIMER"
			sLoop = "TRUE" if self.fLoopAnimation else "FALSE"

			flVRML.write(
"""\n DEF %s TimeSensor {
	cycleInterval %.3f
	loop %s
}\n""" % (timerDEF, self.rAnimationDurationSec, sLoop))


			for obj in context.selected_objects:
				# write the orientations first

				print("   ...exporting animation of '%s'" % obj.name)
				objDEF = obj.name.replace(".", "_")
				sPrecKEY = ("%%.%if "% self.precisionKey) + ", "
				sPrecXYZW = 4*("%%.%if "% self.precisionXYZ) + ", "
				sPrecXYZ = 3*("%%.%if "% self.precisionXYZ) + ", "
				cFrames = len(mapObjRotation[obj.name])
				frameStep = 1.0 / cFrames

				# see if se have rotations
				setRotations = set(mapObjRotation[obj.name])
				if len(setRotations) > 1:
					# yes, we have different rotations:
					orIntDEF = "%s_OriInt" % objDEF
					flVRML.write("""\nDEF %s OrientationInterpolator {
						key [ """ % orIntDEF)

					curFramePercentage = 0
					for iFrame in range(cFrames):
						flVRML.write(sPrecKEY % curFramePercentage) 
						curFramePercentage += frameStep
					flVRML.write("]\n keyValue [ ") 

					for axisAngle in mapObjRotation[obj.name]:
						flVRML.write(sPrecXYZW % axisAngle)
					flVRML.write("]\n}\n")

					# and now route the animation.
					flVRML.write("ROUTE %s.fraction_changed TO %s.set_fraction\n" % (timerDEF, orIntDEF))
					flVRML.write("ROUTE %s.value_changed TO %s.set_rotation\n" % (orIntDEF, objDEF))

				#same for the translation:
				setTranslations = set(mapObjTranslation[obj.name])
				if len(setTranslations) > 1:
					posIntDEF = "%s_PosInt" % objDEF
					flVRML.write("""\nDEF %s PositionInterpolator {
						key [ """ % posIntDEF)

					curFramePercentage = 0
					for iFrame in range(cFrames):
						flVRML.write(sPrecKEY % curFramePercentage)
						curFramePercentage += frameStep
					flVRML.write("]\n keyValue [ ") 


					for translation in mapObjTranslation[obj.name]:
						flVRML.write(sPrecXYZ % translation)
					flVRML.write("]\n}\n")

					# and now route the animation.
					flVRML.write("ROUTE %s.fraction_changed TO %s.set_fraction\n" % (timerDEF, posIntDEF))
					flVRML.write("ROUTE %s.value_changed TO %s.set_translation\n" % (posIntDEF, objDEF))

				# and finally for the scale
				setScale = set(mapObjScale[obj.name])
				if len(setScale) > 1:
					scaleIntDEF = "%s_ScaleInt" % objDEF
					flVRML.write("""\nDEF %s PositionInterpolator {
						key [ """ % scaleIntDEF)

					curFramePercentage = 0
					for iFrame in range(cFrames):
						flVRML.write(sPrecKEY % curFramePercentage)
						curFramePercentage += frameStep
					flVRML.write("]\n keyValue [ ") 

					for scale in mapObjScale[obj.name]:
						flVRML.write(sPrecXYZ % scale)
					flVRML.write("]\n}\n")

					# and now route the animation.
					flVRML.write("ROUTE %s.fraction_changed TO %s.set_fraction\n" % (timerDEF, scaleIntDEF))
					flVRML.write("ROUTE %s.value_changed TO %s.scale\n" % (scaleIntDEF, objDEF))



		# now remove duplicates we possibly made
		setObjNameNonDuplicates = set(
			[obj.name for obj in context.selected_objects]) and set(rgObjNamesOriginal)

		# traverse the selection and remove those we want to keep from it
		for objNameDuplicate in setObjNameNonDuplicates:
			bpy.data.objects[objNameDuplicate].select = False 

		# now only the extra copies are selected -> remove them
		bpy.ops.object.delete() # removes the selected object
		
		for objName in rgObjNamesOriginal:
			bpy.data.objects[objName].select = True # and select the original one again.
			# also make it active again.
		bpy.context.scene.objects.active = bpy.data.objects[objNameActive]

		flVRML.close()
		self.fnLast = fnVRML

		self.report({'INFO'},  "Export finished.")

		

		return {'FINISHED'}
	
	def invoke(self, context, event):
		# set some fields depending on the current scene:
		scene = context.scene

		cFramesExported = (scene.frame_end - scene.frame_start+1) / scene.frame_step
		secExported = cFramesExported / float(scene.render.fps)

		self.iAnimFrameStart = scene.frame_start
		self.iAnimFrameStop = scene.frame_end
		self.iAnimStep = scene.frame_step
		self.rAnimationDurationSec = secExported

		# how much precision do we need on the exporter?
		import math
		self.precisionKey = int(math.ceil(math.log10(cFramesExported)))


		if not context.selected_objects:
			# select everybody.
			bpy.ops.object.select_all(action="SELECT")

		# check that we could export everything:
		rgConvertableTypes = ['MESH', 'FONT', 'SURFACE', 'CURVE', 'META']
		rgRemoveObjectsFromSelection = []
		for obj in context.selected_objects:
			if obj.type not in rgConvertableTypes:
				rgRemoveObjectsFromSelection.append(obj.name)

		# remove objects from the selection we could not export
		# and notify the user about it
		for objName in rgRemoveObjectsFromSelection:
			bpy.data.objects[objName].select = False
			
		if rgRemoveObjectsFromSelection:
			self.report({'WARNING'},
					"Ignoring object(s) '%s' and removing them from the selection.\n\nOnly objects of types %s were exported." % 
						(",".join(rgRemoveObjectsFromSelection), "/".join(rgConvertableTypes)))
			#return {'CANCELLED'}
		
		# check again if there is something left...
		if not context.selected_objects:
			self.report({'ERROR'},  "No object to export left.")
			return {'CANCELLED'}

		# set first object as active object  (needed for convert and toggle)
		context.scene.objects.active = context.selected_objects[0]

		# reset the old filename for convenience.
		if self.fnLast:
			self.filepath = self.fnLast
		else:
			fnOut = context.selected_objects[0].name
			fnOut = fnOut.replace(" ", "_")
			self.filepath = fnOut + ".wrl"


		# then show the exporter.
		wm = context.window_manager.fileselect_add(self)
		return {'RUNNING_MODAL'}


def menuCB(self, context):
	self.layout.operator(Export_VRML.bl_idname, text="Export to VRML (.wrl)...")
 
def register():
	bpy.utils.register_module(__name__)
	bpy.types.INFO_MT_file_export.append(menuCB)
 
def unregister():
	bpy.utils.unregister_module(__name__)
	bpy.types.INFO_MT_file_export.remove(menuCB)
 
if __name__ == "__main__":
	register()
