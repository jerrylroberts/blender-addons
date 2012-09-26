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

bl_info = {
    "name": "Export .md2",
    "description": "Export to Quake2 file format, applies modifiers (.md2)",
    "author": "Sebastian Lieberknecht, Dao Nguyen and Bernd Meyer metaio GmbH (based on Damien Thebault and Erwan Mathieu's Blender2.4x exporter)",
    "version": (1, 6),
    "blender": (2, 6, 3),
    "api": 46461,
    "location": "File > Export > md2",
    "warning": '', # used for warning icon and text in addons panel
    "wiki_url": "http://metaio.com", 
    "tracker_url": "http://metaio.com",
    "category": "Import-Export"}


import bpy
from bpy.props import *

from bpy_extras.io_utils import ExportHelper
from datetime import datetime

import math
from math import pi
import mathutils

import struct
import random
import os
import shutil


MD2_NORMALS=((-0.525731, 0.000000, 0.850651),
             (-0.442863, 0.238856, 0.864188),
             (-0.295242, 0.000000, 0.955423),
             (-0.309017, 0.500000, 0.809017),
             (-0.162460, 0.262866, 0.951056),
             ( 0.000000, 0.000000, 1.000000),
             ( 0.000000, 0.850651, 0.525731),
             (-0.147621, 0.716567, 0.681718),
             ( 0.147621, 0.716567, 0.681718),
             ( 0.000000, 0.525731, 0.850651),
             ( 0.309017, 0.500000, 0.809017),
             ( 0.525731, 0.000000, 0.850651),
             ( 0.295242, 0.000000, 0.955423),
             ( 0.442863, 0.238856, 0.864188),
             ( 0.162460, 0.262866, 0.951056),
             (-0.681718, 0.147621, 0.716567),
             (-0.809017, 0.309017, 0.500000),
             (-0.587785, 0.425325, 0.688191),
             (-0.850651, 0.525731, 0.000000),
             (-0.864188, 0.442863, 0.238856),
             (-0.716567, 0.681718, 0.147621),
             (-0.688191, 0.587785, 0.425325),
             (-0.500000, 0.809017, 0.309017),
             (-0.238856, 0.864188, 0.442863),
             (-0.425325, 0.688191, 0.587785),
             (-0.716567, 0.681718,-0.147621),
             (-0.500000, 0.809017,-0.309017),
             (-0.525731, 0.850651, 0.000000),
             ( 0.000000, 0.850651,-0.525731),
             (-0.238856, 0.864188,-0.442863),
             ( 0.000000, 0.955423,-0.295242),
             (-0.262866, 0.951056,-0.162460),
             ( 0.000000, 1.000000, 0.000000),
             ( 0.000000, 0.955423, 0.295242),
             (-0.262866, 0.951056, 0.162460),
             ( 0.238856, 0.864188, 0.442863),
             ( 0.262866, 0.951056, 0.162460),
             ( 0.500000, 0.809017, 0.309017),
             ( 0.238856, 0.864188,-0.442863),
             ( 0.262866, 0.951056,-0.162460),
             ( 0.500000, 0.809017,-0.309017),
             ( 0.850651, 0.525731, 0.000000),
             ( 0.716567, 0.681718, 0.147621),
             ( 0.716567, 0.681718,-0.147621),
             ( 0.525731, 0.850651, 0.000000),
             ( 0.425325, 0.688191, 0.587785),
             ( 0.864188, 0.442863, 0.238856),
             ( 0.688191, 0.587785, 0.425325),
             ( 0.809017, 0.309017, 0.500000),
             ( 0.681718, 0.147621, 0.716567),
             ( 0.587785, 0.425325, 0.688191),
             ( 0.955423, 0.295242, 0.000000),
             ( 1.000000, 0.000000, 0.000000),
             ( 0.951056, 0.162460, 0.262866),
             ( 0.850651,-0.525731, 0.000000),
             ( 0.955423,-0.295242, 0.000000),
             ( 0.864188,-0.442863, 0.238856),
             ( 0.951056,-0.162460, 0.262866),
             ( 0.809017,-0.309017, 0.500000),
             ( 0.681718,-0.147621, 0.716567),
             ( 0.850651, 0.000000, 0.525731),
             ( 0.864188, 0.442863,-0.238856),
             ( 0.809017, 0.309017,-0.500000),
             ( 0.951056, 0.162460,-0.262866),
             ( 0.525731, 0.000000,-0.850651),
             ( 0.681718, 0.147621,-0.716567),
             ( 0.681718,-0.147621,-0.716567),
             ( 0.850651, 0.000000,-0.525731),
             ( 0.809017,-0.309017,-0.500000),
             ( 0.864188,-0.442863,-0.238856),
             ( 0.951056,-0.162460,-0.262866),
             ( 0.147621, 0.716567,-0.681718),
             ( 0.309017, 0.500000,-0.809017),
             ( 0.425325, 0.688191,-0.587785),
             ( 0.442863, 0.238856,-0.864188),
             ( 0.587785, 0.425325,-0.688191),
             ( 0.688191, 0.587785,-0.425325),
             (-0.147621, 0.716567,-0.681718),
             (-0.309017, 0.500000,-0.809017),
             ( 0.000000, 0.525731,-0.850651),
             (-0.525731, 0.000000,-0.850651),
             (-0.442863, 0.238856,-0.864188),
             (-0.295242, 0.000000,-0.955423),
             (-0.162460, 0.262866,-0.951056),
             ( 0.000000, 0.000000,-1.000000),
             ( 0.295242, 0.000000,-0.955423),
             ( 0.162460, 0.262866,-0.951056),
             (-0.442863,-0.238856,-0.864188),
             (-0.309017,-0.500000,-0.809017),
             (-0.162460,-0.262866,-0.951056),
             ( 0.000000,-0.850651,-0.525731),
             (-0.147621,-0.716567,-0.681718),
             ( 0.147621,-0.716567,-0.681718),
             ( 0.000000,-0.525731,-0.850651),
             ( 0.309017,-0.500000,-0.809017),
             ( 0.442863,-0.238856,-0.864188),
             ( 0.162460,-0.262866,-0.951056),
             ( 0.238856,-0.864188,-0.442863),
             ( 0.500000,-0.809017,-0.309017),
             ( 0.425325,-0.688191,-0.587785),
             ( 0.716567,-0.681718,-0.147621),
             ( 0.688191,-0.587785,-0.425325),
             ( 0.587785,-0.425325,-0.688191),
             ( 0.000000,-0.955423,-0.295242),
             ( 0.000000,-1.000000, 0.000000),
             ( 0.262866,-0.951056,-0.162460),
             ( 0.000000,-0.850651, 0.525731),
             ( 0.000000,-0.955423, 0.295242),
             ( 0.238856,-0.864188, 0.442863),
             ( 0.262866,-0.951056, 0.162460),
             ( 0.500000,-0.809017, 0.309017),
             ( 0.716567,-0.681718, 0.147621),
             ( 0.525731,-0.850651, 0.000000),
             (-0.238856,-0.864188,-0.442863),
             (-0.500000,-0.809017,-0.309017),
             (-0.262866,-0.951056,-0.162460),
             (-0.850651,-0.525731, 0.000000),
             (-0.716567,-0.681718,-0.147621),
             (-0.716567,-0.681718, 0.147621),
             (-0.525731,-0.850651, 0.000000),
             (-0.500000,-0.809017, 0.309017),
             (-0.238856,-0.864188, 0.442863),
             (-0.262866,-0.951056, 0.162460),
             (-0.864188,-0.442863, 0.238856),
             (-0.809017,-0.309017, 0.500000),
             (-0.688191,-0.587785, 0.425325),
             (-0.681718,-0.147621, 0.716567),
             (-0.442863,-0.238856, 0.864188),
             (-0.587785,-0.425325, 0.688191),
             (-0.309017,-0.500000, 0.809017),
             (-0.147621,-0.716567, 0.681718),
             (-0.425325,-0.688191, 0.587785),
             (-0.162460,-0.262866, 0.951056),
             ( 0.442863,-0.238856, 0.864188),
             ( 0.162460,-0.262866, 0.951056),
             ( 0.309017,-0.500000, 0.809017),
             ( 0.147621,-0.716567, 0.681718),
             ( 0.000000,-0.525731, 0.850651),
             ( 0.425325,-0.688191, 0.587785),
             ( 0.587785,-0.425325, 0.688191),
             ( 0.688191,-0.587785, 0.425325),
             (-0.955423, 0.295242, 0.000000),
             (-0.951056, 0.162460, 0.262866),
             (-1.000000, 0.000000, 0.000000),
             (-0.850651, 0.000000, 0.525731),
             (-0.955423,-0.295242, 0.000000),
             (-0.951056,-0.162460, 0.262866),
             (-0.864188, 0.442863,-0.238856),
             (-0.951056, 0.162460,-0.262866),
             (-0.809017, 0.309017,-0.500000),
             (-0.864188,-0.442863,-0.238856),
             (-0.951056,-0.162460,-0.262866),
             (-0.809017,-0.309017,-0.500000),
             (-0.681718, 0.147621,-0.716567),
             (-0.681718,-0.147621,-0.716567),
             (-0.850651, 0.000000,-0.525731),
             (-0.688191, 0.587785,-0.425325),
             (-0.587785, 0.425325,-0.688191),
             (-0.425325, 0.688191,-0.587785),
             (-0.425325,-0.688191,-0.587785),
             (-0.587785,-0.425325,-0.688191),
             (-0.688191,-0.587785,-0.425325))

			 
class MD2:
	def __init__(self, options):
		self.options = options
		self.object = None
		self.progressBarDisplayed = -10
		return

	def setObject(self, object, scale=1.0):
		self.object = object
		self.scale = scale
		
	def write(self, filename):
		self.version = 8

		self.skinwidth = 2**10-1 #1023
		self.skinheight = 2**10-1 #1023

		# self.framesize : see below

		mesh = self.object.data

		skins = Util.getSkins(mesh)

		self.num_skins = len(skins)
		self.num_xyz = len(mesh.vertices)
		self.num_st = len(mesh.tessfaces)*3
		self.num_tris = len(mesh.tessfaces)
		self.num_glcmds = self.num_tris * (1+3*3) + 1

		self.num_frames = 1
		if self.options.fExportAnimation:
			self.num_frames = 1 + bpy.context.scene.frame_end - bpy.context.scene.frame_start

		self.framesize = 40+4*self.num_xyz

		self.ofs_skins = 68 # size of the header
		self.ofs_st = self.ofs_skins + 64*self.num_skins
		self.ofs_tris = self.ofs_st + 4*self.num_st
		self.ofs_frames = self.ofs_tris + 12*self.num_tris
		self.ofs_glcmds = self.ofs_frames + self.framesize*self.num_frames
		self.ofs_end = self.ofs_glcmds + 4*self.num_glcmds

		file = open(filename, 'wb')
		try:
			# write header
			bin = struct.pack('<4B16i', #bin = struct.pack('<4s16i',
			                  ord('I'),
			                  ord('D'),
			                  ord('P'),
			                  ord('2'),
			                  self.version,
			                  self.skinwidth,
			                  self.skinheight,
			                  self.framesize,
			                  self.num_skins,
			                  self.num_xyz,
			                  self.num_st, #  number of texture coordinates
			                  self.num_tris,
			                  self.num_glcmds,
			                  self.num_frames,
			                  self.ofs_skins,
			                  self.ofs_st,
			                  self.ofs_tris,
			                  self.ofs_frames,
			                  self.ofs_glcmds,
			                  self.ofs_end)
			file.write(bin)
			
			# write skin file names
			for iSkin, skin in enumerate(skins):

				fnImg = bpy.path.abspath(skin)

				if self.options.fCopyTextureSxS:
					fnSxS = os.path.join(os.path.dirname(filename), os.path.basename(fnImg))

					if iSkin == 0 and self.options.fNameTextureToMD2Filename:
						# rename first skin to basename
						fnSxS = os.path.splitext(filename)[0] + os.path.splitext(fnImg)[1]

					print("Copying texture %s to %s" % (fnImg, fnSxS))
					try:
						shutil.copy(fnImg, fnSxS)
					except:
						print("Copying texture %s to %s failed." % (fnImg, fnSxS))


					fnImg = fnSxS # for proper referencing in the MD2 file


				if len(fnImg) > 63 and not self.options.fExportOnlyTextureBasename:
					print("WARNING: The texture path '"+fnImg+"' is too long. It is automatically truncated to the file basename.")
					
				if len(fnImg) > 63 or self.options.fExportOnlyTextureBasename:
					fnImg = os.path.basename(fnImg)

				
				bin = struct.pack('<64s', bytes(fnImg[0:63], encoding='utf8'))
				file.write(bin) # skin name
			
			
			#define meshTextureFaces
			if len(mesh.tessface_uv_textures) != 0:
				meshTextureFaces = mesh.tessface_uv_textures[0].data
			else:
				meshTextureFaces = mesh.tessfaces # does this make sense?
				
			for meshTextureFace in meshTextureFaces: # for face in mesh.faces:
				try:
					uvs = meshTextureFace.uv
				except:
					uvs = ([0,0],[0,0],[0,0])
				
				# (u,v) in blender -> (u,1-v)
				bin = struct.pack('<6h',
								  int(uvs[0][0]*self.skinwidth),
								  int((1-uvs[0][1])*self.skinheight),
								  int(uvs[1][0]*self.skinwidth),
								  int((1-uvs[1][1])*self.skinheight),
								  int(uvs[2][0]*self.skinwidth),
								  int((1-uvs[2][1])*self.skinheight),
								  )
				file.write(bin) # uv
				# (uv index is : face.index*3+i)
			
			for face in mesh.tessfaces:
				# 0,2,1 for good cw/ccw
				bin = struct.pack('<3H',
				                  face.vertices[0],
				                  face.vertices[2],
				                  face.vertices[1]
				                )
				file.write(bin) # vert index
				bin = struct.pack('<3H',
				                  face.index*3 + 0,
				                  face.index*3 + 2,
				                  face.index*3 + 1,
				                  )
				
				file.write(bin) # uv index
			
			if self.options.fExportAnimation:
				min = None
				max = None
				
				timeLineMarkers =[]
				for marker in bpy.context.scene.timeline_markers:
					timeLineMarkers.append(marker)
					
				# sort the markers. The marker with the frame number closest to 0 will be the first marker in the list. 
				# The marker with the biggest frame number will be the last marker in the list
				timeLineMarkers.sort(key=lambda marker: marker.frame)
				markerIdx = 0
				
				# delete markers at same frame positions
				if len(timeLineMarkers) > 1:
					markerFrame = timeLineMarkers[len(timeLineMarkers)-1].frame
					for i in range(len(timeLineMarkers)-2, -1, -1):
						if timeLineMarkers[i].frame == markerFrame:
							del timeLineMarkers[i]
						else:
							markerFrame = timeLineMarkers[i].frame
				
				# BL: to fix: 1 is assumed to be the frame start (this is
				# hardcoded sometimes...)
				for frame in range(1, self.num_frames+1):
					percent = (frame - bpy.context.scene.frame_start) / ( 1. + self.num_frames)
					
					#Display the progress status of the export in the console
					progressStatus = math.floor(percent*100)
					if progressStatus - self.progressBarDisplayed >= 1:
						# only show major updates (>=1%)
						print("Export progress: %3i%%\r" % int(progressStatus), end=' ')
						self.progressBarDisplayed = progressStatus

					if frame == self.num_frames:
						print("Export progress: %3i%% - Model exported." % 100)

					bpy.context.scene.frame_set(frame)
				
					if len(timeLineMarkers) != 0:
						if markerIdx + 1 != len(timeLineMarkers):
							if frame >= timeLineMarkers[markerIdx + 1].frame:
								markerIdx += 1
						name = timeLineMarkers[markerIdx].name
					else:
						name = 'frame'
							
					self.outFrame(file, name + str(frame))
			else:
				self.outFrame(file)

			# gl commands
			for meshTextureFace in meshTextureFaces: 
				try:
					uvs = meshTextureFace.uv
				except:
					uvs = ([0,0],[0,0],[0,0])
				bin = struct.pack('<i', 3)
				file.write(bin)
				# 0,2,1 for good cw/ccw (also flips/inverts normal)
				for vert in [0,2,1]:
					# (u,v) in blender -> (u,1-v)
					bin = struct.pack('<ffI',
						uvs[vert][0],
						(1.0 - uvs[vert][1]),
						face.vertices[vert])
					
					file.write(bin)
			# NULL command
			bin = struct.pack('<I', 0)
			file.write(bin)
		finally:
			file.close()

	def outFrame(self, file, frameName = 'frame'):
		mesh = self.object.to_mesh(bpy.context.scene, True, 'PREVIEW')
		
		mesh.transform(self.object.matrix_world)
		mesh.transform(mathutils.Matrix.Rotation(pi/2, 4, 'X')) 
		mesh.transform(mathutils.Matrix.Rotation(pi, 4, 'Z')) 

		###### compute the bounding box ###############
		min = [mesh.vertices[0].co[0],
		       mesh.vertices[0].co[1],
		       mesh.vertices[0].co[2]]
		max = [mesh.vertices[0].co[0],
		       mesh.vertices[0].co[1],
		       mesh.vertices[0].co[2]]

		for vert in mesh.vertices:
			for i in range(3):
				if vert.co[i] < min[i]:
					min[i] = vert.co[i]
				if vert.co[i] > max[i]:
					max[i] = vert.co[i]
		########################################

		# BL: some caching to speed it up:
		# -> sd_ gets the vertices between [0 and 255]
		#    which is our important quantization.
		sdx = (max[0]-min[0]) / 255.0
		sdy = (max[1]-min[1]) / 255.0
		sdz = (max[2]-min[2]) / 255.0
		isdx = 255.0 / (max[0]-min[0])
		isdy = 255.0 / (max[1]-min[1])
		isdz = 255.0 / (max[2]-min[2])

		# note about the scale: self.object.scale is already applied via matrix_world
		bin = struct.pack('<6f16s', 
			# writing the scale of the model 
			self.scale * sdx,
			self.scale * sdy,
			self.scale * sdz,
			## now the initial offset [= min of bounding box (correctly scaled)]
			self.scale * min[0],
			self.scale * min[1],
			self.scale * min[2],
			# and finally the name.
			bytes(frameName, encoding='utf8'))
			
		file.write(bin) # frame header

		for vert in mesh.vertices:

			# find the closest normal for every vertex
			for iN in range(162):
			 	# BL: what's the magic here??
				dot =  vert.normal[1]*MD2_NORMALS[iN][0] + \
				      -vert.normal[0]*MD2_NORMALS[iN][1] + \
				       vert.normal[2]*MD2_NORMALS[iN][2]

				if iN==0 or dot > maxDot:
					maxDot = dot
					bestNormalIndex = iN

			# and now write the normal.
			bin = struct.pack('<4B',
			                  int((vert.co[0]-min[0])*isdx),
			                  int((vert.co[1]-min[1])*isdy),
			                  int((vert.co[2]-min[2])*isdz),
			                  bestNormalIndex)
			
			file.write(bin) # write vertex and normal

class Util:
	@staticmethod
	def pickName():
		name = '_MD2Obj_'+str(random.random())
		return name[0:20]

	# deletes an object from Blender (remove + unlink)
	@staticmethod
	def deleteObject(object):
		bpy.context.scene.objects.unlink(object)
		bpy.data.objects.remove(object)
		
	# duplicates the given object and returns it
	@staticmethod
	def duplicateObject(object, name):
		# backup the current object selection and current active object
		selObjects = bpy.context.selected_objects[:]
		actObject = bpy.context.active_object
		
		# deselect all selected objects
		bpy.ops.object.select_all(action='DESELECT')
		# select the object which we want to duplicate
		object.select = True
		
		# duplicate the selected object		
		bpy.ops.object.duplicate()
		
		# the duplicated object is automatically selected
		copyObj = bpy.context.selected_objects[0]
		
		# rename the object with the given name
		copyObj.name = name
		
		# select all objects which have been previously selected and make active the previous active object
		bpy.context.scene.objects.active = actObject
		for obj in selObjects:
			obj.select = True
		
		return copyObj

	@staticmethod
	def applyModifiers(object, possibleNewName):
		# backup the current object selection and current active object
		selObjects = bpy.context.selected_objects[:]
		actObject = bpy.context.active_object
		
		# deselect all selected objects
		bpy.ops.object.select_all(action='DESELECT')
		# select the object which we want to apply modifiers to
		object.select = True

		# duplicate the selected object		
		bpy.ops.object.duplicate()
		
		# the duplicated object is automatically selected
		modifiedObj = bpy.context.selected_objects[0]

		# now apply all modifiers except the Armature modifier...
		for modifier in modifiedObj.modifiers:
			if modifier.type == "ARMATURE":
				# these must stay for the animation
				continue 

			# all others can be applied.
			bpy.ops.object.modifier_apply(modifier=modifier.name)



		
		# select all objects which have been previously selected and make active the previous active object
		bpy.context.scene.objects.active = actObject
		for obj in selObjects:
			obj.select = True
		
		if modifiedObj.name == object.name:
			# no modifier applied.
			return object
		
		# modifiers were applied:
		modifiedObj.name = possibleNewName
		

		return modifiedObj



	# returns the mesh of the object and return object.data (mesh)
	@staticmethod
	def triangulateMesh(object):
		mesh = object.data
		
		# make the object the active object!
		bpy.context.scene.objects.active = object
		
		bpy.ops.object.mode_set( mode="EDIT" , toggle = False )
		bpy.ops.mesh.select_all(action="SELECT")
		
		bpy.ops.mesh.quads_convert_to_tris()
		bpy.ops.object.mode_set( mode="OBJECT" , toggle = False )

		mesh.update(calc_tessface=True)
		return mesh

	@staticmethod
	def getSkins(mesh):
		skins = []
		for material in mesh.materials:
			for texSlot in material.texture_slots:
				if not texSlot or texSlot.texture.type != "IMAGE": 
					continue

				skins.append(texSlot.texture.image.filepath)
		
		return skins
			
		
class ObjectInfo:
	def __init__(self, object):
		self.triang = True
		self.vertices = -1
		self.cTessfaces = 0
		self.status = ('','')

		self.ismesh = object and object.type == 'MESH'

		if self.ismesh:
			originalObject = object
			mesh = object.data

			self.skins = Util.getSkins(mesh)

			tmpObjectName = Util.pickName()
			try:
				# apply the modifiers
				object = Util.applyModifiers(object, tmpObjectName)
				
				if object.name != tmpObjectName: # not yet copied: do it now.
					object = Util.duplicateObject(object, tmpObjectName)
				mesh = Util.triangulateMesh(object)

				self.status = (str(len(mesh.vertices)) + ' vertices', str(len(mesh.tessfaces)) + ' faces')
				self.cTessFaces = len(mesh.tessfaces)
				self.vertices = len(mesh.vertices)
				
			finally:
				if object.name == tmpObjectName:
					originalObject.select = True
					bpy.context.scene.objects.active = originalObject
					Util.deleteObject(object)
		print(self.status)
		
		
class Export_MD2(bpy.types.Operator, ExportHelper):
	"""Export to Quake2 file format (.md2)"""
	bl_idname = "export_quake.md2"
	bl_label = "Export to Quake2 file format (.md2)"

	filename = StringProperty(name="File Path",
		description="Filepath used for processing the script",
		maxlen= 1024,default= "")	
	
	filename_ext = ".md2"

	rScaleFactor = FloatProperty(name="Scale for blenderUnits -> [mm]",
								 description="Defaults to 1000 (blender unit -> [mm])",
								 default=1000.0)

	fExportAnimation = BoolProperty(name="Export animation",
							description="default: False",
							default=False)

	fExportOnlyTextureBasename = BoolProperty(name="Export only basenames (skin)",
							description="default: True",
							default=True)

	fCopyTextureSxS = BoolProperty(name="Copy texture(s) next to .md2",
							description="default: True",
							default=True)

	fNameTextureToMD2Filename = BoolProperty(name="Name first texture similar to .md2",
							description="default: True",
							default=True)



	# id_export   = 1
	# id_cancel   = 2
	# id_anim     = 3
	# id_update   = 4
	# id_help     = 5
	# id_basename = 6

	def __init__(self):
		try:
			self.object = bpy.context.selected_objects[0]
		except:
			self.object = None

		# go into object mode before we start the actual export procedure
		bpy.ops.object.mode_set( mode="OBJECT" , toggle = False )
		
		self.info = ObjectInfo(self.object)
	
	def execute(self, context):
		
		props = self.properties
		filepath = self.filepath
		filepath = bpy.path.ensure_ext(filepath, self.filename_ext)

		object = self.object
		originalObject = object

		# different name each time or we can't unlink it later
		tmpObjectName = Util.pickName()

		object = Util.applyModifiers(object, tmpObjectName)

		mesh = object.data	
		
		if self.info.triang:
			if object.name != tmpObjectName: # not yet copied: do it now.
				object = Util.duplicateObject(object, tmpObjectName)
			mesh = Util.triangulateMesh(object)
		
		if object.type != 'MESH':
			raise NameError('Selected object must be a mesh!')

		# save the current frame to reset it after export
		if self.fExportAnimation:
			frame = bpy.context.scene.frame_current
		
		try:
			md2 = MD2(self)
			md2.setObject(object, self.rScaleFactor)
			md2.write(filepath) 
		finally:
			if object.name == tmpObjectName:
				originalObject.select = True
				bpy.context.scene.objects.active = originalObject
				Util.deleteObject(object)
			if self.fExportAnimation:
				bpy.context.scene.frame_set(frame)

			self.report({'INFO'},  "Model '"+originalObject.name+"' exported")
		return {'FINISHED'}
	
	def invoke(self, context, event):

		if not context.selected_objects:
			self.report({'ERROR'}, "Please, select an object to export!")
			return {'CANCELLED'}
		
		if len(bpy.context.selected_objects) > 1:
			self.report({'ERROR'}, "Please, select exactly one object to export!")
			return {'CANCELLED'}

		# check how many faces we have (there is a max..)
		obj = bpy.context.selected_objects[0]

		info = ObjectInfo(obj)
		cFinalTriangles = info.cTessFaces
		if cFinalTriangles*3 > 2**16:
			self.report({'ERROR'}, 
			   "Object has too many (triangulated) faces (%i), at most %i are supported in md2" % (cFinalTriangles, (2**16)/3))
			return {'CANCELLED'}

		wm = context.window_manager
		wm.fileselect_add(self)
		return {'RUNNING_MODAL'}


def menuCB(self, context):
	self.layout.operator(Export_MD2.bl_idname, text="MD2 (.md2)")
 
def register():
	bpy.utils.register_module(__name__)
	bpy.types.INFO_MT_file_export.append(menuCB)
 
def unregister():
	bpy.utils.unregister_module(__name__)
	bpy.types.INFO_MT_file_export.remove(menuCB)
 
if __name__ == "__main__":
	register()
