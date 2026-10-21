import bpy,math,random
from mathutils import Vector
def rebuild_eyes(centers,M):
 for o in list(bpy.data.objects):
  if o.name.startswith(('Eyeball_','Iris_','Cornea_')):bpy.data.objects.remove(o,do_unlink=True)
 right,up,fwd=[Vector(v) for v in M]
 def material(name,color,rough):
  m=bpy.data.materials.new(name);m.use_nodes=True;b=m.node_tree.nodes.get('Principled BSDF');b.inputs['Base Color'].default_value=(*color,1);b.inputs['Roughness'].default_value=rough;return m,b
 sclera,bs=material('R10B_sclera',(.23,.21,.186),.32);bs.inputs['Specular IOR Level'].default_value=.22
 iris,bs=material('R10B_iris_tissue',(.04,.055,.066),.65);bs.inputs['Specular IOR Level'].default_value=.05
 vc=iris.node_tree.nodes.new('ShaderNodeVertexColor');vc.layer_name='Iris_fibres';iris.node_tree.links.new(vc.outputs['Color'],bs.inputs['Base Color'])
 cornea,bs=material('R10B_cornea',(1,1,1),.035);bs.inputs['Transmission Weight'].default_value=1;bs.inputs['IOR'].default_value=1.376;bs.inputs['Specular IOR Level'].default_value=.5
 def meshobj(name,vs,fs,mat):
  me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update();o=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(o);me.materials.append(mat)
  for f in me.polygons:f.use_smooth=True
  return o
 rng=random.Random(727)
 for suffix,cc in zip(['L','R'],centers):
  c=Vector(cc);radius=11.7;rim=6.05;cut=math.asin(rim/radius);na=128;nt=56;vs=[];fs=[]
  for j in range(nt+1):
   t=cut+(math.pi-cut)*j/nt
   for k in range(na):
    a=k*math.tau/na;vs.append(tuple(c+(right*math.cos(a)+up*math.sin(a))*radius*math.sin(t)+fwd*radius*math.cos(t)))
  for j in range(nt):
   for k in range(na):
    a=j*na+k;b=j*na+(k+1)%na;fs.append((a,a+na,b+na,b))
  meshobj('Eyeball_'+suffix,vs,fs,sclera)
  depth=math.sqrt(radius*radius-rim*rim)-.08
  # A flat, recessed iris/pupil behind a separate transparent corneal dome.
  nr=42;vs=[tuple(c+fwd*depth)];cols=[(.001,.0013,.0015,1)];fib=[rng.uniform(.75,1.25) for _ in range(na)]
  for j in range(1,nr+1):
   r=rim*j/nr
   for k in range(na):
    a=k*math.tau/na;vs.append(tuple(c+(right*math.cos(a)+up*math.sin(a))*r+fwd*depth))
    if r<2.45:col=(.001,.0013,.0015,1)
    else:
     outer=max(0,min(1,(rim-r)/.48));inner=max(0,min(1,(r-2.45)/.7))
     f=fib[k]*(.9+.10*math.sin(r*11+k*.17))*(.38+.62*outer)*(.65+.35*inner)
     col=(.050*f,.066*f,.079*f,1)
    cols.append(col)
  fs=[(0,1+k,1+(k+1)%na) for k in range(na)]
  for j in range(nr-1):
   for k in range(na):
    a=1+j*na+k;b=1+j*na+(k+1)%na;fs.append((a,a+na,b+na,b))
  o=meshobj('Iris_'+suffix,vs,fs,iris);ca=o.data.color_attributes.new(name='Iris_fibres',type='FLOAT_COLOR',domain='POINT')
  for i,col in enumerate(cols):ca.data[i].color=col
  edge=math.sqrt(radius*radius-rim*rim);height=2.08;rad=(rim*rim+height*height)/(2*height);offset=edge+height-rad
  vs=[tuple(c+fwd*(edge+height))];nr=24
  for j in range(1,nr+1):
   r=rim*j/nr
   for k in range(na):
    a=k*math.tau/na;vs.append(tuple(c+(right*math.cos(a)+up*math.sin(a))*r+fwd*(offset+math.sqrt(rad*rad-r*r))))
  fs=[(0,1+k,1+(k+1)%na) for k in range(na)]
  for j in range(nr-1):
   for k in range(na):
    a=1+j*na+k;b=1+j*na+(k+1)%na;fs.append((a,a+na,b+na,b))
  ob=meshobj('Cornea_'+suffix,vs,fs,cornea);ob.visible_shadow=False
