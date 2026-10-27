#!/usr/bin/env python3
"""Offline Phase 7 Gate 3 observed-camera rendering and comparison packaging.

No dataset loading, SLAM, optimizer, or checkpoint writes. GPU rendering is
available only with --render-observed; --package is CPU/Pillow/OpenCV only.
"""
from __future__ import annotations
import argparse, hashlib, json, shutil, sys
from pathlib import Path

import numpy as np

REPO = Path('/home/robot/research/SGS_slam_phase7_bcgm')
if str(REPO) not in sys.path: sys.path.insert(0, str(REPO))
P4 = Path('/home/robot/research/SGS_slam')
RUN = 'p7_bcgm_g3_room0_on_0_1999_r01'
EVID = REPO / 'results/runtime_artifacts/phase7_gate3' / RUN
CHECKPOINT = REPO / 'experiments/Replica' / RUN / 'params.npz'
RGB_PLY = REPO / 'experiments/Replica' / RUN / 'params.ply'
SEM_PLY = REPO / 'experiments/Replica' / RUN / 'seg_params.ply'
P4_V1 = P4 / 'results/runtime_artifacts/phase4_vb001_visualization'
P4_V2 = P4 / 'results/runtime_artifacts/phase4_vb001_visualization_v2'
P4_V3 = P4 / 'results/runtime_artifacts/phase4_vb001_visualization_v3a'
P4_MAPPING = P4 / 'results/runtime_artifacts/phase4_vb001_visualization_audit/semantic_mapping.csv'
P4_V3_SCRIPT = P4 / 'scripts/visualization/visualize_full_scene_v3a.py'
P6 = P4 / 'results/runtime_artifacts/phase6_bam/p6_bam_006_comparison/visualization'
P6_V1 = P6 / 'va2_phase4_matched'
P6_EXT = P6 / 'va2_phase4_extended_matched'
P7_EXISTING = EVID / 'visualization'
ADV = EVID / 'advanced_visualization'
FRAMES = (0, 499, 999, 1499, 1999)
VIEWS = ('trajectory_observed', 'room_overview', 'top_oblique')
CLASSES = ('wall', 'floor', 'ceiling', 'sofa', 'chair', 'table', 'rug', 'blinds')

def sha(path: Path) -> str:
    h=hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(4*1024*1024),b''): h.update(b)
    return h.hexdigest()

def image(path: Path):
    from PIL import Image
    return Image.open(path).convert('RGB')

def triptych(paths, labels, out, title=None):
    from PIL import Image, ImageDraw
    if out.exists(): return  # resumable packaging: retain files from prior completed steps
    imgs=[image(p) for p in paths]
    w=max(i.width for i in imgs); h=max(i.height for i in imgs)
    top=54 if title else 36
    canvas=Image.new('RGB',(w*3,h+top),'white'); d=ImageDraw.Draw(canvas)
    for n,(im,label) in enumerate(zip(imgs,labels)):
        x=n*w; d.text((x+12,8),label,fill='black'); canvas.paste(im,(x,top))
    if title: d.text((12,top-18),title,fill='black')
    out.parent.mkdir(parents=True,exist_ok=True); canvas.save(out)

def preflight():
    expected='a02dd4b4ecfd9c982866cf4a4c38c187ef22c75049b8328e18eea20608944917'
    if not CHECKPOINT.is_file() or sha(CHECKPOINT)!=expected: raise SystemExit('checkpoint absent/hash mismatch')
    if ADV.exists(): raise SystemExit(f'refusing existing advanced output root: {ADV}')
    for f in FRAMES:
        meta=P4_V2/'frames'/f'frame_{f:04d}'/'frame_metadata.json'
        if not meta.is_file(): raise SystemExit(f'missing camera metadata {meta}')
        j=json.loads(meta.read_text())
        if j.get('image_dimensions_wh') != [1200,680]: raise SystemExit(f'unexpected dimensions {meta}')
        if np.asarray(j.get('estimated_w2c')).shape!=(4,4) or np.asarray(j.get('intrinsics')).shape!=(3,3): raise SystemExit(f'invalid camera {meta}')
    print(json.dumps({'checkpoint_sha256':expected,'frames':FRAMES,'advanced_root_absent':True,'camera_metadata':'PASS'},indent=2))

def render_observed():
    import cv2, torch
    import torch.nn.functional as F
    from PIL import Image
    from diff_gaussian_rasterization import GaussianRasterizer
    from utils.recon_helpers import setup_camera
    from utils.slam_helpers import get_depth_and_silhouette
    preflight()
    if not torch.cuda.is_available(): raise SystemExit('CUDA unavailable')
    free,total=torch.cuda.mem_get_info(0)
    if free < 8*1024**3: raise SystemExit(f'insufficient free VRAM: {free/1024**3:.2f} GiB')
    out=ADV/'phase7_only'/'observed_camera'
    (out/'rgb').mkdir(parents=True); (out/'semantic').mkdir(); (out/'depth').mkdir()
    cams=ADV/'cameras'/'observed_v2'; cams.mkdir(parents=True)
    before=sha(CHECKPOINT)
    with np.load(CHECKPOINT,allow_pickle=False) as z:
        p={k:np.asarray(z[k]).copy() for k in ('means3D','rgb_colors','unnorm_rotations','logit_opacities','log_scales','semantic_colors')}
    means=torch.from_numpy(p['means3D']).to('cuda:0')
    rotations=F.normalize(torch.from_numpy(p['unnorm_rotations']).to('cuda:0'),dim=-1)
    opacities=torch.sigmoid(torch.from_numpy(p['logit_opacities']).to('cuda:0'))
    scales=torch.exp(torch.tile(torch.from_numpy(p['log_scales']).to('cuda:0'),(1,3)))
    means2d=torch.zeros_like(means)
    records=[]
    for fid in FRAMES:
        src=P4_V2/'frames'/f'frame_{fid:04d}'
        md=src/'frame_metadata.json'; meta=json.loads(md.read_text())
        shutil.copyfile(md,cams/f'frame_{fid:04d}.json')
        w2c=np.asarray(meta['estimated_w2c'],dtype=np.float64); K=np.asarray(meta['intrinsics'],dtype=np.float64)
        settings=setup_camera(1200,680,K,w2c,0.01,100.0,device='cuda:0') # Phase 4 black background
        camera=torch.as_tensor(w2c,dtype=torch.float32,device='cuda:0')
        for modality,colors in [('rgb',torch.from_numpy(p['rgb_colors']).to('cuda:0')),('semantic',torch.from_numpy(p['semantic_colors']).to('cuda:0'))]:
            rendered,_,_=GaussianRasterizer(raster_settings=settings)(means3D=means,colors_precomp=colors,rotations=rotations,opacities=opacities,scales=scales,means2D=means2d)
            torch.cuda.synchronize(); arr=rendered.permute(1,2,0).clamp(0,1).mul(255).round().byte().cpu().numpy()
            dest=out/modality/f'frame_{fid:04d}.png'; Image.fromarray(arr,'RGB').save(dest)
        depth_colors=get_depth_and_silhouette(means,camera,device='cuda:0')
        depth,_,_=GaussianRasterizer(raster_settings=settings)(means3D=means,colors_precomp=depth_colors,rotations=rotations,opacities=opacities,scales=scales,means2D=means2d)
        torch.cuda.synchronize(); raw=depth[0].cpu().numpy().astype(np.float32,copy=False)
        np.save(out/'depth'/f'frame_{fid:04d}.npy',raw)
        valid=np.isfinite(raw)&(raw>0); scaled=np.zeros(raw.shape,dtype=np.uint8); scaled[valid]=np.rint(np.clip(raw[valid]/6.0,0,1)*255).astype(np.uint8)
        bgr=cv2.applyColorMap(scaled,cv2.COLORMAP_TURBO); bgr[~valid]=0
        cv2.imwrite(str(out/'depth'/f'frame_{fid:04d}.png'),bgr)
        records.append({'frame_id':fid,'camera_json':str(cams/f'frame_{fid:04d}.json'),'camera_sha256':sha(cams/f'frame_{fid:04d}.json'),'depth_units':'meters','depth_definition':'camera-z','depth_display':'Turbo fixed [0,6]m; invalid/nonpositive black'})
        del depth,depth_colors
    del means,rotations,opacities,scales,means2d
    torch.cuda.empty_cache()
    if sha(CHECKPOINT)!=before: raise SystemExit('checkpoint changed during rendering')
    (out/'render_metadata.json').write_text(json.dumps({'run_id':RUN,'checkpoint':str(CHECKPOINT),'checkpoint_sha256_before_after':before,'renderer':'Phase 7 native diff_gaussian_rasterization / setup_camera','background':'black (Phase 4 observed-camera convention)','frames':records,'cuda_device':torch.cuda.get_device_name(0),'peak_allocated_bytes':torch.cuda.max_memory_allocated(),'peak_reserved_bytes':torch.cuda.max_memory_reserved()},indent=2)+'\n')

def package():
    from PIL import Image, ImageDraw
    out=ADV/'phase7_only'; comp=ADV/'compare_phase4_phase6_phase7'
    if not (out/'observed_camera'/'render_metadata.json').is_file(): raise SystemExit('observed render missing; run --render-observed first')
    v3out=out/'v3a_diagnostics_r02'
    if not (v3out/'metadata'/'artifact_manifest.json').is_file(): raise SystemExit('V3A output missing')
    # Reuse, copy only, the already validated Phase 7 V1 free views.
    for family in ('reconstruction','semantic','paired','cameras'):
        src=P7_EXISTING/family; dst=out/'free_view'/family
        if not dst.exists(): shutil.copytree(src,dst)
    p4obs=P4_V2/'frames'; p6obs=P6_EXT/'reconstruction_fidelity'/'phase6_rendered'
    obs=out/'observed_camera'
    # Observed RGB, learned raw semantic and metric depth boards.
    for fid in FRAMES:
        n=f'frame_{fid:04d}'; p4f=p4obs/n
        triptych([p4f/'rendered_rgb.png',p6obs/'rgb/unfiltered'/f'{n}.png',obs/'rgb'/f'{n}.png'],['Phase 4','Phase 6','Phase 7'],comp/'A_observed_rgb'/f'{n}_triptych.png',f'Observed RGB — {n}')
        triptych([p4f/'rendered_semantic_raw.png',p6obs/'semantic/raw'/f'{n}.png',obs/'semantic'/f'{n}.png'],['Phase 4 raw learned color','Phase 6 raw learned color','Phase 7 raw learned color'],comp/'C_observed_semantic'/f'{n}_triptych.png',f'Observed learned semantic color — {n}')
        import cv2
        depths=[]
        for label,rawpath in [('phase4',p4f/'rendered_depth_raw.npy'),('phase6',p6obs/'depth'/f'{n}.npy'),('phase7',obs/'depth'/f'{n}.npy')]:
            raw=np.load(rawpath).astype(np.float32); valid=np.isfinite(raw)&(raw>0); gray=np.zeros(raw.shape,dtype=np.uint8); gray[valid]=np.rint(np.clip(raw[valid]/6,0,1)*255).astype(np.uint8); bgr=cv2.applyColorMap(gray,cv2.COLORMAP_TURBO); bgr[~valid]=0
            im=Image.fromarray(cv2.cvtColor(bgr,cv2.COLOR_BGR2RGB)); depths.append(im)
            rp=comp/'B_observed_depth'/'normalized_references'/label/f'{n}.png'; rp.parent.mkdir(parents=True,exist_ok=True); im.save(rp)
        triptych([comp/'B_observed_depth'/'normalized_references'/x/f'{n}.png' for x in ('phase4','phase6','phase7')],['Phase 4','Phase 6','Phase 7'],comp/'B_observed_depth'/f'{n}_triptych.png',f'Camera-z depth [0,6] m / Turbo — {n}')
    # Phase 4/6/7 full scene RGB at exact V1 views.
    for view in ('overview','oblique','top_oblique'):
        triptych([P4_V1/'reconstruction'/f'{view}.png',P6_V1/'reconstruction'/f'{view}.png',out/'free_view/reconstruction'/f'{view}.png'],['Phase 4','Phase 6','Phase 7'],comp/'D_full_scene_rgb'/f'{view}_triptych.png',f'Full-scene RGB — {view}')
        triptych([P4_V1/'semantic'/f'{view}.png',P6_V1/'semantic'/f'{view}.png',out/'free_view/semantic'/f'{view}.png'],['Phase 4 learned colors','Phase 6 learned colors','Phase 7 learned colors'],comp/'H_full_scene_semantic/learned_free_view'/f'{view}_triptych.png',f'Learned semantic color — free-view {view}')
    p4x=P4_V3; p6x=P6_EXT/'cross_modal_overview'; p7x=v3out
    for view in VIEWS:
        triptych([p4x/'rgb/unfiltered'/f'{view}.png',p6x/'rgb/unfiltered'/f'{view}.png',p7x/'rgb/unfiltered'/f'{view}.png'],['Phase 4','Phase 6','Phase 7'],comp/'D_full_scene_rgb'/f'{view}_triptych.png',f'Full-scene RGB — V3A {view}')
        triptych([p4x/'comparisons'/f'{view}_rgb_geometry_semantic.png',p6x/'comparisons'/f'{view}_rgb_geometry_semantic.png',p7x/'comparisons'/f'{view}_rgb_geometry_semantic.png'],['Phase 4: RGB | centers | fixed IDs','Phase 6: RGB | centers | fixed IDs','Phase 7: RGB | centers | fixed IDs'],comp/'E_cross_modal'/f'{view}_triptych.png',f'Cross-modal / fixed-ID structure — {view}')
        for repr_name, sub in [('learned_v3a_raw','raw'),('fixed_ids','categorical')]:
            triptych([p4x/'semantic'/sub/f'{view}.png',p6x/'semantic'/sub/f'{view}.png',p7x/'semantic'/sub/f'{view}.png'],['Phase 4','Phase 6','Phase 7'],comp/'H_full_scene_semantic'/repr_name/f'{view}_triptych.png',f'{repr_name} semantic map — {view}')
        triptych([p4x/'geometry'/f'{view}.png',p6x/'geometry'/f'{view}.png',p7x/'geometry'/f'{view}.png'],['Phase 4','Phase 6','Phase 7'],comp/'E_cross_modal'/f'{view}_geometry_triptych.png',f'Gaussian centers — {view}')
    # Exact selected class IDs and palette; per-class triptych and legend.
    for cls in CLASSES:
        fn=f'{cls}_top_oblique.png'
        triptych([p4x/'semantic/classwise'/fn,p6x/'semantic/classwise'/fn,p7x/'semantic/classwise'/fn],['Phase 4','Phase 6','Phase 7'],comp/'F_fixed_semantic_classes'/f'{cls}_id_triptych.png',f'Fixed semantic class: {cls} (Phase 4 verified ID/palette)')
    shutil.copy2(p7x/'semantic/categorical/legend_29_classes.png',comp/'F_fixed_semantic_classes/legend_29_classes.png')
    # Estimated path over geometry uses the same observed trajectory camera.
    triptych([p4x/'geometry/trajectory_observed.png',p6x/'geometry/trajectory_observed.png',p7x/'geometry/trajectory_observed.png'],['Phase 4','Phase 6','Phase 7'],comp/'G_estimated_trajectory/trajectory_on_geometry_triptych.png','Estimated camera path over reconstructed geometry (qualitative)')
    triptych([p4x/'trajectory/estimated_trajectory_3d.png',P6_EXT/'trajectory_in_geometry/estimated_trajectory_3d.png',p7x/'trajectory/estimated_trajectory_3d.png'],['Phase 4','Phase 6','Phase 7'],comp/'G_estimated_trajectory/trajectory_3d_triptych.png','Estimated trajectory diagnostic (not ATE)')
    (out/'fixed_semantic_classes').mkdir(parents=True,exist_ok=True)
    for source,dest in [(p7x/'semantic/classwise/selected_classes_overview_top_oblique.png',out/'fixed_semantic_classes/selected_classes_overview_top_oblique.png'),(p7x/'semantic/categorical/legend_29_classes.png',out/'fixed_semantic_classes/legend_29_classes.png')]:
        if not dest.exists(): shutil.copy2(source,dest)

    # Camera metadata and comparison manifest.
    md=ADV/'metadata'; md.mkdir(parents=True,exist_ok=True)
    camera_dir=ADV/'cameras'/'v3a'; camera_dir.mkdir(parents=True,exist_ok=True)
    for view in VIEWS:
        src=P4_V3/'cameras'/f'{view}.json'; dst=camera_dir/f'{view}.json'
        if not dst.exists(): shutil.copy2(src,dst)
    for fid in FRAMES:
        src=P4_V2/'frames'/f'frame_{fid:04d}'/'frame_metadata.json'; dst=ADV/'cameras'/f'frame_{fid:04d}.json'
        if not dst.exists(): shutil.copy2(src,dst)
    outputs=[]
    for p in sorted(ADV.rglob('*')):
        if p.is_file() and p.name!='advanced_visualization_manifest.json': outputs.append({'path':str(p.relative_to(ADV)),'size_bytes':p.stat().st_size,'sha256':sha(p)})
    reference_trees=[P4_V2/'frames',P4_V1/'reconstruction',P4_V1/'semantic',P4_V1/'paired',P4_V1/'cameras',P6_V1/'reconstruction',P6_V1/'semantic',P6_V1/'paired',P6_V1/'cameras',P4_V3/'comparisons',P4_V3/'geometry',P4_V3/'semantic',P4_V3/'trajectory',P4_V3/'cameras',P6_EXT/'reconstruction_fidelity/phase6_rendered',P6_EXT/'cross_modal_overview',P6_EXT/'semantic_id_structure',P6_EXT/'trajectory_in_geometry',P6_EXT/'cameras/v1',P6_EXT/'cameras/v3a']
    reference_hashes={}
    for tree in reference_trees:
        if tree.is_dir():
            for f in sorted(tree.rglob('*')):
                if f.is_file(): reference_hashes[str(f)] = sha(f)
    for f in [P4_MAPPING,P4_V3_SCRIPT,P4/'scripts/visualization/render_phase4_v2_cameras.py']:
        if f.is_file(): reference_hashes[str(f)] = sha(f)
    helper=REPO/'tools/phase7/gate3_advanced_visualization.py'
    manifest={'run_id':RUN,'checkpoint':str(CHECKPOINT),'checkpoint_sha256':sha(CHECKPOINT),'rgb_ply':str(RGB_PLY),'rgb_ply_sha256':sha(RGB_PLY),'semantic_ply':str(SEM_PLY),'semantic_ply_sha256':sha(SEM_PLY),'phase4_mapping_csv':str(P4_MAPPING),'phase4_observed_root':str(P4_V2),'phase4_v3a_cameras':str(P4_V3/'cameras'),'phase6_reference_root':str(P6_EXT),'observed_frame_ids':FRAMES,'observed_camera_convention':'Phase 4 estimated w2c/K, 1200x680, black background','depth':'camera-z float32 metres; fixed [0,6] m Turbo for all three board columns','semantic':'raw learned colors separate from categorical semantic_ids','v3a_camera_ids':VIEWS,'renderer_source':str(P4_V3_SCRIPT),'renderer_source_sha256':sha(P4_V3_SCRIPT),'phase7_helper':str(helper),'phase7_helper_sha256':sha(helper),'file_count':len(outputs),'reference_file_count':len(reference_hashes),'reference_file_sha256':reference_hashes,'files':outputs}
    (md/'advanced_visualization_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')

def main():
    ap=argparse.ArgumentParser(); g=ap.add_mutually_exclusive_group(required=True); g.add_argument('--preflight',action='store_true');g.add_argument('--render-observed',action='store_true');g.add_argument('--package',action='store_true')
    a=ap.parse_args()
    if a.preflight: preflight()
    elif a.render_observed: render_observed()
    else: package()
if __name__=='__main__': main()
