import time
from typing import Iterable

import numpy as np

from robot.robot import UR5

import pybullet as p
import pybullet_data


def draw_sphere_marker(position, radius=0.02, color=(0, 0, 1, 1)):
    vs_id = p.createVisualShape(p.GEOM_SPHERE, radius=radius, rgbaColor=color)
    marker_id = p.createMultiBody(basePosition=position, baseCollisionShapeIndex=-1, baseVisualShapeIndex=vs_id)
    return marker_id


def mean(lst: Iterable, axis: int = 0) -> float:
    return np.array(lst).mean(axis=axis)


def main():
    physics_client = p.connect(p.GUI)
    p.setGravity(0, 0, -9.81)

    target = (-0.07796166092157364, 0.005451506469398737, -0.06238798052072525)
    dist = 1.0
    yaw = 89.6000747680664
    pitch = -17.800016403198242
    p.resetDebugVisualizerCamera(dist, yaw, pitch, target)

    p.setAdditionalSearchPath(pybullet_data.getDataPath())
    plane_id = p.loadURDF("plane.urdf")

    robot_offt_z = -mean(
        [-0.1867676817112838,
         -0.18596259913093333,
         -0.1902045026366347,
         -0.19100720846428204,
         -0.191706796360579]
    )
    ur5 = UR5([-0.5, 0, robot_offt_z + 0.034])
    ur5.set_q(ur5.home_q)
    for _ in range(100):
        p.stepSimulation()

    # sim home table
    # ((-0.008222591285089068, 0.10945360117595199, 0.006515842374053449),
    # (-1.5159749908267316e-05, 0.0005101967058123463, 1.8056975931157737e-07, 0.999999869734727))

    # ur5.set_q(ur5.home_q)
    # sim_home_table = np.array(ur5.move_ee_down(ur5.ee_pose[0])[0])
    # real_home_table = np.array([0.4919385612010956, 0.13330744206905365, -0.18895940482616425])
    #
    # # draw_sphere_marker(sim_home_table-real_home_table)
    # draw_sphere_marker(p.getBasePositionAndOrientation(ur5.id)[0])

    p0 = [-3.1416080633746546, -0.7186852258494874, 2.1041701475726526, -2.956341405908102, -1.5708392302142542,
          3.109525277977809e-05]
    x0 = [0.49186625307348386, 0.13328192619420318, -0.1877609601159873, -2.221381184249495, 2.2214844953975756,
          -0.00011447118359276727]
    i01 = [-3.141599957142965, -0.9831872147372742, 2.1431077162372034, -2.7307244739928187, -1.5708311239825647,
           3.8635731471003965e-05]
    i02 = [-3.1415961424456995, -0.7127751272967835, 1.5218456427203577, -2.3797036610045375, -1.570798699055807,
           3.4585951652843505e-05]
    p1 = [-3.141592089329855, -0.5305090707591553, 1.4884045759784144, -2.528691907922262, -1.5708068052874964,
          5.460591273731552e-05]
    x1 = [0.691893712664788, 0.13329782727636674, -0.18787452182426512, 2.2213762416152023, -2.2214962921720494,
          1.1723235090357444e-05]
    i11 = [-3.14158803621401, -0.7126355332187195, 1.5215500036822718, -2.3795110187926234, -1.570803467427389,
           8.688084199093282e-05]
    i12 = [-3.4306326548205774, -0.7284988325885315, 1.55591327348818, -2.3982817135252894, -1.5708592573748987,
           -0.28900224367250615]
    p2 = [-3.4305806795703333, -0.5385233920863648, 1.5208080450641077, -2.552784582177633, -1.5708830992328089,
          -0.2889187971698206]
    x2 = [0.6918887910463184, -0.06666159823827206, -0.1903795720345819, 2.221210803557936, -2.221364552552534,
          -0.00034443148547808126]

    q = [p0, p1, p2]
    rx = [x0[:3], x1[:3], x2[:3]]

    s0 = [-0.010150188246474658, 0.10913780113131626, 0.008155820746643228]
    s1 = [0.1872985578980705, 0.10915033057458054, 0.011853772508362753]
    s2 = [0.1804238344673205, -0.08996453240191944, 0.010479755950644945]
    sx = [s0, s1, s2]

    ur5.move_timestep = 0
    i = 0
    for ppon in [p0, i01, i02, p1, i11, i12, p2]:
        ur5.move_q(ppon)
        if ppon in [p0, p1, p2]:
            sx[i] = ur5.ee_pose[0]
            print(f'p{i} =', sx[i])
            i += 1

    print(np.linalg.norm(np.array(s0)-np.array(s2)))
    print(np.linalg.norm(np.array(x0[:3])-np.array(x2[:3])))

    # p0 = (-0.009702441790120406, 0.10913248665426761, 0.007850393252120932)
    # p1 = (0.1873634383892793, 0.10915401010402465, 0.011117038198546952)
    # p2 = (0.18058300759558982, -0.08996500752827487, 0.010548185249060496)

    m = [-0.13761184, -0.23431528,  0.00310984]
    draw_sphere_marker(m)

    time.sleep(500)


if __name__ == '__main__':
    main()
