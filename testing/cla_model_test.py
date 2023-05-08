import numpy as np
import os.path as osp
# import open3d as o3d
import torch
from torch_geometric.data import Data, InMemoryDataset

from Network import ObjectNet
from utility import normalize

RP_ROOT = osp.abspath('/home/mk/rp/')
DDPATH = osp.join(RP_ROOT, 'data/dep_data/')
PDPATH = osp.join(RP_ROOT, 'data/pcd_data/')
MODELS_PATH = osp.join(RP_ROOT, 'models/')


def sample_exact(pcd, n):
    idx = np.random.choice(len(pcd), n, replace=len(pcd) < n)
    return pcd[idx]


def tid_colors(typeidx):
    return np.array([
        [0, 0, 0],
        [0.4160655362053999, 0.13895618220307226, 0.05400398384796701],
        [0.45815538934366873, 0.5622777225161942, 0.12222557471515583],
        [0.5285494304846649, 0.8052616853729326, 0.47328724440755865],
        [0.520059254934221, 0.4733167572634138, 0.5049641813650521],
        [0.2448837131753191, 0.5174992612426157, 0.8959927219176224],
        [0.0859375, 0.9921875, 1.3359375],
        [0.8728815094572616, 0.11715588167789504, 0.9012921785976408],
        [0.8708585184367256, 0.13537291463132384, 0.2942509320637464]
    ])[typeidx]


# def make_pcd(xyz, colors=None):
#     pcd = o3d.geometry.PointCloud()
#     pcd.points = o3d.utility.Vector3dVector(xyz)
#
#     if colors is not None:
#         if len(colors) == 3:
#             colors = np.tile(colors, (len(xyz), 1))
#         pcd.colors = o3d.utility.Vector3dVector(colors)
#
#     return pcd


# def visualize(pcd):
#     o3d.visualization.draw_geometries([pcd])


def main():
    cla_net = ObjectNet().cuda()
    mp = osp.join(MODELS_PATH, 'cn_model-200.pt')
    # mp = '/home/mk/rp/models/cn_test_model-20.pt'
    cla_net.load_state_dict(torch.load(mp))
    cla_net.cuda()
    cla_net.eval()

    rp_root = osp.abspath('/home/mk/rp')

    pcd_root = osp.join(rp_root, 'data/pcd_data/')
    dep_root = osp.join(rp_root, 'data/dep_data/')

    i = 1000

    file_name = f'{i // 1000}_{i % 1000}.npz'
    pcd_file = np.load(osp.join(pcd_root, file_name))
    dep_file = np.load(osp.join(dep_root, file_name))
    pcds, o_ids, t_ids = [pcd_file[x] for x in ['pc', 'oid', 'tid']]
    node_ids, dep_g = [dep_file[x] for x in ['node_ids', 'depg']]

    types = ['cube', 'cylinder', 'ccuboid', 'scuboid', 'tcuboid', 'roof', 'pyramid', 'cuboid']
    oid_tid = dict(zip(o_ids, t_ids))
    tid_name = dict(enumerate(types, start=1))
    name = lambda oid: tid_name[oid_tid[oid]]

    for nid in np.unique(o_ids).astype(int):
        obj_pcd = pcds[o_ids == nid]

        # pos = torch.tensor(sample_exact(normalize(obj_pcd), 512)).cuda().float()
        # model_input = Data(pos=pos)

        # outs = cla_net(model_input, nobatch=True)
        # pred_tid = outs.max(1)[1].item() + 1
        pred_tid = cla_net.predict(obj_pcd)
        print(f'{nid} is a {name(nid)}, predicted: {tid_name[pred_tid]}')
    # visualize(make_pcd(pcds, colors=tid_colors(t_ids)))

if __name__ == '__main__':
    main()
