import os

from absl import app
from absl import flags

import numpy as np

from robot.gripper import Suction
import pybullet as p
import pybullet_data

import time

from utility import check_convergence

UR5_URDF_PATH = 'ur5/ur5.urdf'
ASSET_ROOT = 'robot/assets/'

HOME_J = np.array([-1, -0.5, 0.5, -0.5, -0.5, 0]) * np.pi


class UR5:
    def __init__(self, base_pos):
        self.id = p.loadURDF(os.path.join(ASSET_ROOT, UR5_URDF_PATH), base_pos)

        ddict = {'fixed': [], 'rigid': [], 'deformable': []}
        self.ee_id = 10
        self.ee = Suction(ASSET_ROOT, self.id, self.ee_id-1, ddict)

        self.n_joints = p.getNumJoints(self.id)
        joints = [p.getJointInfo(self.id, i) for i in range(self.n_joints)]
        self.joints = [j[0] for j in joints if j[2] == p.JOINT_REVOLUTE]

        for i in range(len(self.joints)):
            p.resetJointState(self.id, self.joints[i], HOME_J[i])

        self.ee.release()
        self.move_timestep = 1/240

    def move_ee(self, pos, orn=None, error_thresh=0.01, max_iter=100, conv_eps=0.0001, break_cond=lambda: False):
        errors = []

        i = 0
        while True:
            q_tar = np.array(p.calculateInverseKinematics(self.id, self.ee_id, pos, targetOrientation=orn))
            q_cur = np.array([q_state[0] for q_state in p .getJointStates(self.id, self.joints)])
            err = np.linalg.norm(q_tar - q_cur)

            errors.append(err)
            if break_cond() or err < error_thresh or (i > max_iter and check_convergence(errors[-5:], eps=conv_eps)):
                print(err, 'break_cond:', break_cond())
                break

            p.setJointMotorControlArray(bodyUniqueId=self.id,
                                        jointIndices=self.joints,
                                        controlMode=p.POSITION_CONTROL,
                                        targetPositions=q_tar)

            p.stepSimulation()
            time.sleep(self.move_timestep)
            i += 1

        return q_tar, q_cur

    def move_ee_down(self, pos, orn=(0, 0, 0, 1)):
        """
        moves down from `pos` to z=0 until it detects object
        returns: pose=(pos, orn) at which it detected contact"""
        pos = [*pos[:2], 0]
        # ee_tip dynamics = (0.0, 0.5, (0.0, 0.0, 0.0), (0.0, 0.0, 0.0), (0.7071067811882787, -0.7071067811848163, 7.31230107716731e-14, -7.312301077203115e-14), 0.0, 0.0, 0.0, -1.0, -1.0, 2, 0.001)
        # my ee tip dynamics = (0.0, 0.5, (0.0, 0.0, 0.0), (0.0, 0.0, 0.0), (0.7071067811882787, -0.7071067811848163, 7.31230107716731e-14, -7.312301077203115e-14), 0.0, 0.0, 0.0, -1.0, -1.0, 2, 0.001)

        self.move_ee(pos, orn=orn, break_cond=lambda: self.ee.detect_contact())
        return self.ee_pose

    def move_ee_above(self, pos, orn=(0, 0, 0, 1), above_offt=(0, 0, 0.2)):
        a_pos = np.add(pos, above_offt)
        self.move_ee(a_pos, orn=orn)

    def suction(self, on):
        if on:
            self.ee.activate()
        else:
            self.ee.release()

    def set_joints(self, q):
        for ji, qi in zip(self.joints, q):
            p.resetJointState(self.id, ji, qi)

    @property
    def ee_pose(self):
        return p.getLinkState(self.id, self.ee_id)[:2]

    @property
    def ee_offset(self):
        return p.getLinkState(self.id, self.ee_id)[2:4]

    @property
    def ee_frame(self):
        return p.getLinkState(self.id, self.ee_id)[4:6]


def setup():
    ur5 = UR5([-0.5, 0, 0])

    for _ in range(100):
        p.stepSimulation()

    time.sleep(10)


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

    setup()


if __name__ == '__main__':
    main()
