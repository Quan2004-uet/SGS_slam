#!/usr/bin/env python3
"""CPU-only offline ATE Mean and true ATE RMSE for a saved Phase 7 checkpoint."""
import argparse, hashlib, json
from pathlib import Path
import numpy as np

def sha256(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''): h.update(block)
    return h.hexdigest()
def quat_to_rot(q):
    q=np.asarray(q,dtype=np.float64); n=np.linalg.norm(q,axis=1,keepdims=True)
    if np.any(n<=0) or not np.isfinite(n).all(): raise ValueError('invalid quaternion')
    w,x,y,z=(q/n).T; R=np.empty((len(q),3,3))
    R[:,0,0]=1-2*(y*y+z*z); R[:,0,1]=2*(x*y-w*z); R[:,0,2]=2*(x*z+w*y)
    R[:,1,0]=2*(x*y+w*z); R[:,1,1]=1-2*(x*x+z*z); R[:,1,2]=2*(y*z-w*x)
    R[:,2,0]=2*(x*z-w*y); R[:,2,1]=2*(y*z+w*x); R[:,2,2]=1-2*(x*x+y*y)
    return R
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--checkpoint',required=True,type=Path)
    ap.add_argument('--json',required=True,type=Path); ap.add_argument('--markdown',required=True,type=Path)
    a=ap.parse_args(); cp=a.checkpoint.resolve(strict=True)
    if a.json.exists() or a.markdown.exists(): raise FileExistsError('refusing to overwrite ATE output')
    with np.load(cp,allow_pickle=False) as s:
        q=np.asarray(s['cam_unnorm_rots'],dtype=np.float64); t=np.asarray(s['cam_trans'],dtype=np.float64)
        gt=np.asarray(s['gt_w2c_all_frames'],dtype=np.float64); first=np.asarray(s['w2c'],dtype=np.float64)
    n=q.shape[-1]
    if q.shape!=(1,4,n) or t.shape!=(1,3,n) or gt.shape!=(n,4,4) or first.shape!=(4,4): raise ValueError('trajectory shapes mismatch')
    if not all(np.isfinite(v).all() for v in (q,t,gt,first)): raise ValueError('nonfinite pose data')
    est=np.empty((n,4,4),dtype=np.float64); est[0]=first; R=quat_to_rot(q[0].T)
    for i in range(1,n): est[i]=np.eye(4); est[i,:3,:3]=R[i]; est[i,:3,3]=t[0,:,i]
    x=est[:,:3,3].T; y=gt[:,:3,3].T; xc=x-x.mean(1,keepdims=True); yc=y-y.mean(1,keepdims=True)
    W=sum((np.outer(xc[:,i],yc[:,i]) for i in range(n)),np.zeros((3,3))); U,_,Vh=np.linalg.svd(W.T)
    S=np.eye(3)
    if np.linalg.det(U)*np.linalg.det(Vh)<0: S[2,2]=-1
    rot=U@S@Vh; trans=y.mean(1)-rot@x.mean(1); err=np.linalg.norm(rot@x+trans[:,None]-y,axis=0)
    data={'status':'PASS_OFFLINE_ATE_VALIDATION','run_id':'p7_bcgm_r1_full_room1_on_0_1999_r01','dataset':'Replica room1',
      'frame_ids_inclusive':[0,n-1],'pose_count':n,'alignment':'Horn rigid SE(3) on W2C translation columns; no scale fitting; all poses',
      'per_pose_error_m_definition':'e_i = ||R * t_est_i + t_align - t_gt_i||_2',
      'ate_mean_m':float(err.mean()),'ate_rmse_m':float(np.sqrt(np.mean(err**2))),
      'ate_median_m':float(np.median(err)),'ate_max_m':float(err.max()),'checkpoint':str(cp),
      'checkpoint_sha256':sha256(cp),'cpu_only':True,'cuda_used':False}
    a.json.parent.mkdir(parents=True,exist_ok=True); a.json.write_text(json.dumps(data,indent=2)+'\n')
    md='# Replica room1 — Offline ATE validation\n\n'
    md+=f"- Status: `{data['status']}`\n- Checkpoint SHA256: `{data['checkpoint_sha256']}`\n- Poses: {n}\n- Alignment: {data['alignment']}\n"
    md+=f"- ATE Mean: {data['ate_mean_m']:.12f} m\n- ATE RMSE: {data['ate_rmse_m']:.12f} m\n- ATE Median: {data['ate_median_m']:.12f} m\n- ATE Max: {data['ate_max_m']:.12f} m\n"
    md+='\nThe checkpoint is read-only. ATE Mean is the arithmetic mean of per-pose Euclidean errors; ATE RMSE is sqrt(mean(error²)). Neither uses scale alignment.\n'
    a.markdown.write_text(md)
    print(json.dumps({k:v for k,v in data.items() if k!='per_pose_translation_error_m'},indent=2))
if __name__=='__main__': main()
