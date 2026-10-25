import bpy,sys,math
from pathlib import Path
from mathutils import Vector
root=Path(sys.argv[sys.argv.index('--')+1]).resolve();root.mkdir(exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
scene=bpy.context.scene
scene.render.engine='CYCLES';scene.cycles.samples=16;scene.cycles.use_denoising=True
scene.render.resolution_x=360;scene.render.resolution_y=500;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.film_transparent=False
scene.world.color=(.2,.2,.2)
scene.view_settings.view_transform='AgX'
labels=bpy.data.collections.new('Labels');scene.collection.children.link(labels)
def mat(name,col,trans=0):
 m=bpy.data.materials.new(name);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*col,1);p.inputs['Roughness'].default_value=.07 if trans else .32;p.inputs['Transmission Weight'].default_value=trans;p.inputs['IOR'].default_value=1.49;return m
clear=mat('clear acrylic',(.96,.98,1),1);floor=mat('neutral stage',(.06,.07,.09))
def cube(name,loc,scale,m):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.dimensions=scale;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(m);b=o.modifiers.new('edge bevel','BEVEL');b.width=.035;b.segments=3;o.modifiers.new('weighted normals','WEIGHTED_NORMAL');return o
for y in [-.18,.18]:cube('clear cover', (0,y,2.9),(3.25,.055,5.65),clear)
for x in [-1.6,1.6]:cube('clear rim',(x,0,2.9),(.09,.36,5.65),clear)
for z in [.12,5.68]:cube('clear rim',(0,0,z),(3.25,.36,.09),clear)
cube('stage',(0,0,-.02),(200,200,.1),floor)
def plane(slot,z,w,h,back=False,islabel=False):
 bpy.ops.mesh.primitive_plane_add(size=1,location=(0,.04 if back else -.04,z),rotation=(math.pi/2,0,math.pi if back else 0));o=bpy.context.object;o.name=slot;o.scale=(w,h,1);m=mat(slot,(1,1,1));tex=m.node_tree.nodes.new('ShaderNodeTexImage');tex.name='SOURCE_IMAGE';m.node_tree.links.new(tex.outputs['Color'],m.node_tree.nodes['Principled BSDF'].inputs['Base Color']);o.data.materials.append(m)
 if islabel:
  for c in list(o.users_collection):c.objects.unlink(o)
  labels.objects.link(o)
plane('cardfront_name',2.43,2.92,4.05);plane('cardback_name',2.43,2.92,4.05,True);plane('labelfront_name',5.1,2.92,.65,False,True);plane('labelback_name',5.1,2.92,.65,True,True)
for name,loc in {'front':(0,-10,4),'back':(0,10,4),'left45':(-7,-9,5),'right45':(7,-9,5),'top':(4,-8,8),'low':(-4,-9,2.9)}.items():
 bpy.ops.object.camera_add(location=loc);o=bpy.context.object;o.name='CAM_'+name;o.rotation_euler=(Vector((0,0,2.9))-o.location).to_track_quat('-Z','Y').to_euler();o.data.type='ORTHO';o.data.ortho_scale=7
for name,loc,power,size in [('key',(-4,-5,8),900,5),('rim',(4,3,7),1200,4),('fill',(4,-4,3),450,3)]:
 bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.name=name;o.data.energy=power;o.data.shape='DISK';o.data.size=size;o.rotation_euler=(Vector((0,0,2.9))-o.location).to_track_quat('-Z','Y').to_euler()
bpy.data.libraries.write(str(root/'LABEL.blend'),{labels})

for o in list(labels.objects):bpy.data.objects.remove(o,do_unlink=True)
scene.collection.children.unlink(labels);bpy.data.collections.remove(labels)
for n in ['labelfront_name','labelback_name']:
 m=bpy.data.materials.get(n)
 if m and m.users==0:bpy.data.materials.remove(m)
scene.camera=bpy.data.objects['CAM_front'];bpy.ops.wm.save_as_mainfile(filepath=str(root/'CASE.blend'))
