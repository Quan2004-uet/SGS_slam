import os
import zipfile

import numpy as np
import random
import torch
from utils.convert_ply import convert


def seed_everything(seed=42):
    """
        Set the `seed` value for torch and numpy seeds. Also turns on
        deterministic execution for cudnn.
        
        Parameters:
        - seed:     A hashable seed value
    """
    random.seed(seed)
    os.environ["PYTHONHASHSEED"] = str(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False
    print(f"Seed set to: {seed} (type: {type(seed)})")


def params2cpu(params):
    res = {}
    for k, v in params.items():
        if isinstance(v, torch.Tensor):
            res[k] = v.detach().cpu().contiguous().numpy()
        else:
            res[k] = v
    return res


def save_params(output_params, output_dir, save_ply=True):
    # Convert to CPU Numpy Arrays
    to_save = params2cpu(output_params)
    # Save the Parameters containing the Gaussian Trajectories
    os.makedirs(output_dir, exist_ok=True)
    print(f"Saving parameters to: {output_dir}")
    save_path = os.path.join(output_dir, "params.npz")
    np.savez(save_path, **to_save)
    if save_ply:
        convert(to_save, os.path.join(output_dir, "params.ply"), is_semantic=False)
        convert(to_save, os.path.join(output_dir, "seg_params.ply"), is_semantic=True)        


def validate_final_checkpoint(path, expected_frames, require_semantics=True):
    """Validate the saved NPZ container/schema before downstream evaluation."""
    if not os.path.isfile(path):
        raise FileNotFoundError(f"Final checkpoint is missing: {path}")
    if require_semantics:
        for export_name in ("params.ply", "seg_params.ply"):
            export_path = os.path.join(os.path.dirname(path), export_name)
            if not os.path.isfile(export_path) or os.path.getsize(export_path) == 0:
                raise ValueError(f"Required final Gaussian export is missing or empty: {export_path}")
    with zipfile.ZipFile(path) as archive:
        corrupt_member = archive.testzip()
        if corrupt_member is not None:
            raise ValueError(f"Corrupt checkpoint member: {corrupt_member}")
    with np.load(path, allow_pickle=False) as params:
        required = {
            "means3D", "rgb_colors", "unnorm_rotations", "logit_opacities",
            "log_scales", "cam_unnorm_rots", "cam_trans", "intrinsics", "w2c",
            "gt_w2c_all_frames", "keyframe_time_indices", "timestep", "org_width", "org_height",
        }
        if require_semantics:
            required.update({"semantic_ids", "semantic_colors"})
        missing = sorted(required.difference(params.files))
        if missing:
            raise ValueError(f"Final checkpoint missing fields: {missing}")
        if params["cam_unnorm_rots"].shape != (1, 4, expected_frames):
            raise ValueError("Final checkpoint camera-rotation horizon mismatch")
        if params["cam_trans"].shape != (1, 3, expected_frames):
            raise ValueError("Final checkpoint camera-translation horizon mismatch")
        if params["gt_w2c_all_frames"].shape != (expected_frames, 4, 4):
            raise ValueError("Final checkpoint ground-truth trajectory horizon mismatch")
        if params["means3D"].ndim != 2 or params["means3D"].shape[1] != 3:
            raise ValueError("Final checkpoint Gaussian means shape is invalid")
        gaussian_count = params["means3D"].shape[0]
        expected_shapes = {
            "rgb_colors": (gaussian_count, 3),
            "unnorm_rotations": (gaussian_count, 4),
            "logit_opacities": (gaussian_count, 1),
            "log_scales": (gaussian_count, 1),
        }
        if require_semantics:
            expected_shapes["semantic_colors"] = (gaussian_count, 3)
            expected_shapes["semantic_ids"] = (gaussian_count,)
        for key, shape in expected_shapes.items():
            if params[key].shape != shape:
                raise ValueError(f"Final checkpoint {key} shape mismatch")
        keyframes = params["keyframe_time_indices"]
        if keyframes.ndim != 1 or keyframes.size == 0 or int(keyframes[-1]) != expected_frames - 1:
            raise ValueError("Final checkpoint keyframe metadata is incomplete")
    return True


def save_params_ckpt(output_params, output_dir, time_idx):
    # Convert to CPU Numpy Arrays
    to_save = params2cpu(output_params)
    # Save the Parameters containing the Gaussian Trajectories
    os.makedirs(output_dir, exist_ok=True)
    print(f"Saving parameters to: {output_dir}")
    save_path = os.path.join(output_dir, "params"+str(time_idx)+".npz")
    np.savez(save_path, **to_save)


def save_seq_params(all_params, output_dir):
    params_to_save = {}
    for frame_idx, params in enumerate(all_params):
        params_to_save[f"frame_{frame_idx}"] = params2cpu(params)
    # Save the Parameters containing the Sequence of Gaussians
    os.makedirs(output_dir, exist_ok=True)
    print(f"Saving parameters to: {output_dir}")
    save_path = os.path.join(output_dir, "params.npz")
    np.savez(save_path, **params_to_save)


def save_seq_params_ckpt(all_params, output_dir,time_idx):
    params_to_save = {}
    for frame_idx, params in enumerate(all_params):
        params_to_save[f"frame_{frame_idx}"] = params2cpu(params)
    # Save the Parameters containing the Sequence of Gaussians
    os.makedirs(output_dir, exist_ok=True)
    print(f"Saving parameters to: {output_dir}")
    save_path = os.path.join(output_dir, "params"+str(time_idx)+".npz")
    np.savez(save_path, **params_to_save)
