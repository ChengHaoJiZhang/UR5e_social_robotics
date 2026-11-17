# Face and Voice HRI Demo with ROS 2

## Objective

Execute a social motion using face verification and voice control:

1. verify that the person is authorised;
2. listen to a voice command;
3. accept only commands that start with `robot`;
4. execute the requested motion with ROS 2.

The face is checked once when the HRI system starts. After authorisation, voice requests are enabled.

## Architecture

```text
Teacher PC - HRI client and robot server

camera -> face verification ---------------------------+
                                                       |
microphone -> speech recognition -> keyword "robot"   |
                              -> /social_behavior/request
                                                       |
                                                       v
                                              authorised request
                                              -> /social_behavior
                                                       |
                                                       v
                                              Behavior Manager
                                                       |
                                      ROS 2 /ur5e/run_sequence
                                                       |
                                                       v
                              sequence server -> MoveIt 2 -> UR5e
```

All nodes run on the Teacher PC because its camera, microphone and speakers are next to the robot. The person stands in front of the robot and interacts directly with this equipment. No Student PC is used in this demo.

Face and voice recognition are interaction tools. They are not robot safety systems.

## Before starting

Everything is already installed and built. Do not install packages or rebuild the workspace.

The `.venv-humble` environment must already be prepared as explained in [UR5e ROS 2 setup](1_UR5e_ROS2_setup.md). All Teacher terminals must use the same `ROS_DOMAIN_ID`.

Check these items:

- the Teacher PC has a camera, microphone, speakers and Internet connection;
- the authorised reference image is correct;
- `handshake.yaml` and `give5.yaml` are installed on the Teacher PC;
- the motions were already approved with fake hardware;
- no Python socket server is running.

The example reference image is:

```text
~/UR5e_social_robotics/Python_sockets_Robotic_project/resources/Pictures/authorised_user.png
```

## 1. Prepare every terminal

Run this in every Teacher container terminal:

```bash
cd /root/UR5e_social_robotics
source /opt/ros/humble/setup.bash
source .venv-humble/bin/activate
source install/setup.bash
```

Verify that every terminal uses the same domain:

```bash
echo "$ROS_DOMAIN_ID"
```

## 2. Test with fake hardware

Teacher terminal 1:

```bash
ros2 launch ur_robot_driver ur_control.launch.py \
  ur_type:=ur5e robot_ip:=192.168.0.20 \
  use_fake_hardware:=true launch_rviz:=false
```

Teacher terminal 2:

```bash
ros2 launch ur_moveit_config ur_moveit.launch.py \
  ur_type:=ur5e launch_rviz:=true
```

Teacher terminal 3:

```bash
ros2 run ur5e_motion_server ur5e_sequence_server
```

Teacher terminal 4:

```bash
ros2 launch social_robot_behaviors social_behavior.launch.py
```

Teacher terminal 5:

```bash
ros2 topic echo /social_behavior
```

Teacher terminal 6:

```bash
ros2 launch social_robot_hri face_voice_hri.launch.py \
  reference_image:=$HOME/UR5e_social_robotics/Python_sockets_Robotic_project/resources/Pictures/authorised_user.png \
  camera_index:=0
```

## 3. Verify the face gate

1. First show a non-authorised person to the camera.
2. Check that the window shows `UNKNOWN` and no motion request reaches `/social_behavior`.
3. Show the authorised person to the camera.
4. Check that the window shows `AUTHORISED`.
5. Check that the terminal reports `User authorised. HRI requests are enabled.`

Press `Q` to cancel if the wrong camera is open. Change `camera_index` only if the Teacher PC uses another camera.

## 4. Verify voice control

The activation word must be the first word. Say:

```text
handshake
```

Nothing must move because the word `robot` is missing.

Now say:

```text
robot handshake
```

Check that:

- `/voice/text` receives the sentence;
- `/social_behavior` receives `handshake`;
- the Teacher server accepts the sequence;
- the complete motion is visible in RViz.

Then test:

```text
robot give me five
```

The expected behavior is `give5`.

## 5. Execute on the real UR5e

Stop all fake-hardware nodes. Continue only with instructor approval.

Teacher terminal 1:

```bash
ros2 launch ur_robot_driver ur_control.launch.py \
  ur_type:=ur5e robot_ip:=192.168.0.20 \
  use_fake_hardware:=false launch_rviz:=false
```

On the teach pendant, load the program containing **External Control** and press **Play**.

Teacher terminal 2:

```bash
ros2 launch ur_moveit_config ur_moveit.launch.py \
  ur_type:=ur5e launch_rviz:=true
```

Teacher terminal 3:

```bash
ros2 run ur5e_motion_server ur5e_sequence_server
```

Teacher terminal 4 - restart the Behavior Manager:

```bash
ros2 launch social_robot_behaviors social_behavior.launch.py
```

Teacher terminal 5 - restart face and voice control:

```bash
ros2 launch social_robot_hri face_voice_hri.launch.py \
  reference_image:=$HOME/UR5e_social_robotics/Python_sockets_Robotic_project/resources/Pictures/authorised_user.png \
  camera_index:=0
```

After the authorised face is accepted, say one command at a time:

```text
robot handshake
robot give me five
```

Wait until one motion finishes before saying the next command. Stop the experiment immediately if the real movement differs from the fake-hardware test.

## Future extension

This demo can be extended with AI-based gesture identification using YOLO Pose and a 3D camera. A person could offer a hand instead of speaking.

The next guide, [Gesture HRI with YOLO Pose and a 3D Camera](7_Gesture_HRI_with_YOLO_Pose_and_3D_Camera.md), describes the current experimental design and launch commands. The complete gesture nodes are not finished or validated yet.
