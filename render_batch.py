"""Run with Blender background mode and --disable-autoexec; never save source files."""
import bpy,sys,json,time,hashlib
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from batch_plan import build_plan,digest,SLOTS
args=sys.argv[sys.argv.index('--')+1:];csv,assets,out,labelblend=args
jobs=build_plan(csv,assets,out);out=Path(out);out.mkdir(parents=True,exist_ok=True)
source=Path(bpy.data.filepath);before={'case':digest(source),'label':digest(labelblend)}
if bpy.data.collections.get('Labels'):raise RuntimeError('Labels already present: refusing duplicate append')
with bpy.data.libraries.load(labelblend,link=False) as (src,dst):
    if 'Labels' not in src.collections:raise ValueError('Missing Labels collection')
    dst.collections=['Labels']
for c in dst.collections:bpy.context.scene.collection.children.link(c)
scene=bpy.context.scene;scene.render.threads_mode='FIXED';scene.render.threads=2
lights={o.name:{'matrix':[list(row) for row in o.matrix_world],'energy':o.data.energy} for o in scene.objects if o.type=='LIGHT'}
# Validate all scene bindings before the first render.
for slot in SLOTS:
    obj=scene.objects.get(slot)
    mat=obj.active_material if obj else None
    if mat is None or not mat.use_nodes or mat.node_tree.nodes.get('SOURCE_IMAGE') is None:raise ValueError('Missing material/image binding '+slot)
for j in jobs:
    if bpy.data.objects.get('CAM_'+j['style']) is None:raise ValueError('Camera preset missing')
receipts=[]
for job in jobs:
    started=time.monotonic()
    for slot,item in job['images'].items():
        if digest(item['path'])!=item['sha256']:raise ValueError('Image changed since preflight')
        image=bpy.data.images.load(item['path'],check_existing=True);image.reload()
        scene.objects[slot].active_material.node_tree.nodes['SOURCE_IMAGE'].image=image
    scene.camera=bpy.data.objects['CAM_'+job['style']];scene.render.filepath=job['output']
    bpy.ops.render.render(write_still=True)
    if lights!={o.name:{'matrix':[list(row) for row in o.matrix_world],'energy':o.data.energy} for o in scene.objects if o.type=='LIGHT'}:raise RuntimeError('Lighting unexpectedly changed')
    receipts.append({**job,'sha256':digest(job['output']),'seconds':round(time.monotonic()-started,3),'loaded_images':{s:str(Path(scene.objects[s].active_material.node_tree.nodes['SOURCE_IMAGE'].image.filepath).resolve()) for s in SLOTS}})
    (out/'render_receipts.json').write_text(json.dumps({'blender':bpy.app.version_string,'render_engine':scene.render.engine,'resolution':[scene.render.resolution_x,scene.render.resolution_y],'lights_unchanged':True,'source_hashes':before,'renders':receipts},indent=2))
assert before=={'case':digest(source),'label':digest(labelblend)}
print('BATCH_PASS',len(receipts),flush=True)
