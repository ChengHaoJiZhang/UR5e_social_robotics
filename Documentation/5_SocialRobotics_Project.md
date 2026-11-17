# Social Robotics Project with the UR5e

## Objective

Verify these motions in this order:

1. `handshake`;
2. `give5`;
3. the new motion prepared at home (`<motion_name>`).

First run the three motions in simulation. Then run them on the real UR5e in the same order.

## Safety

- Real tests require instructor approval.
- Keep the workspace clear and the emergency stop accessible.
- Use low robot speed and check the TCP and payload.
- Stop immediately if the real movement differs from the simulation.

## Session 1 - Python sockets

### Network

```text
Student PC 1  192.168.1.15 --\
Student PC 2  192.168.1.25 ---\
Student PC 3  192.168.1.35 ----+-- TCP 5000 --> Teacher PC 192.168.1.5
Student PC 4  192.168.1.45 ---/                    |
                                                    | URScript, TCP 30002
                                                    v
Teacher robot interface 192.168.0.10 ----------> UR5e 192.168.0.20
```

The Student PC sends the complete YAML file to `192.168.1.5:5000`. The Teacher server replies with `OK` or `ERROR`. Only the Teacher PC connects to the UR5e.

### 1. Prepare the Student PC

Copy the new file to:

```text
Python_sockets_Robotic_project/motions/<motion_name>.yaml
```

Register it in `MOTIONS` in `behavior_manager_client.py`:

```python
MOTIONS = {
    "init": "motions/init.yaml",
    "handshake": "motions/handshake.yaml",
    "give5": "motions/give5.yaml",
    "<motion_name>": "motions/<motion_name>.yaml",
}
```

In the Student PC `config.py`, always use:

```python
SERVER_IP = "192.168.1.5"
SERVER_PORT = 5000
```

### 2. Simulation

#### Teacher PC - start first

In the Teacher PC `config.py`, set:

```python
EXECUTION_MODE = "simulation_only"
```

Start the server:

```powershell
cd UR5e_social_robotics\Python_sockets_Robotic_project
python ur5e_motion_server.py
```

Keep this terminal running. RoboDK must open and the server must listen on `0.0.0.0:5000`.

#### Student PC - start second

Check the connection and the registered motions:

```powershell
Test-NetConnection 192.168.1.5 -Port 5000
cd UR5e_social_robotics\Python_sockets_Robotic_project
python motion_client.py --list
```

Send one motion at a time and wait for `OK: sequence executed`:

```powershell
python motion_client.py handshake
python motion_client.py give5
python motion_client.py <motion_name>
```

Check every movement in RoboDK. Stop the Teacher server after the three tests.

### 3. Real UR5e

#### Teacher PC - start first

Check the robot connection:

```powershell
Test-NetConnection 192.168.0.20 -Port 30002
```

In the Teacher PC `config.py`, set:

```python
EXECUTION_MODE = "simulation_and_real"
```

Start the server again:

```powershell
cd UR5e_social_robotics\Python_sockets_Robotic_project
python ur5e_motion_server.py
```

#### Student PC - start second

With instructor approval, send one motion at a time:

```powershell
python motion_client.py handshake
python motion_client.py give5
python motion_client.py <motion_name>
```

## Session 2 - ROS 2

### Network

```text
Student PC 1  192.168.1.15, ROS_DOMAIN_ID=1 --\
Student PC 2  192.168.1.25, ROS_DOMAIN_ID=2 ---\
Student PC 3  192.168.1.35, ROS_DOMAIN_ID=3 ----+-- ROS 2 DDS/RTPS over UDP
Student PC 4  192.168.1.45, ROS_DOMAIN_ID=4 ---/    port 7400 base + domain offsets
                                                        |
                                                        v
                                         Teacher PC 192.168.1.5
                                         selected ROS_DOMAIN_ID=1, 2, 3 or 4
                                                        |
                                                        | UR driver / RTDE
                                                        v
Teacher robot interface 192.168.0.10 ----------> UR5e 192.168.0.20
```

ROS 2 DDS uses UDP multicast and domain-dependent RTPS ports starting from base port `7400`; it does not use one fixed application port. The Student publishes `/social_behavior` and calls `/ur5e/run_sequence` through the Behavior Manager. The Teacher runs the driver, MoveIt 2 and the sequence server.

### 1. Configure ROS 2 multicast

Use the domain that matches the selected group:

| Student PC | Classroom IP | `ROS_DOMAIN_ID` |
|---|---|---|
| Student 1 | `192.168.1.15` | `1` |
| Student 2 | `192.168.1.25` | `2` |
| Student 3 | `192.168.1.35` | `3` |
| Student 4 | `192.168.1.45` | `4` |

#### Student PC `~/.bashrc`

Add this block. Change `1` to `2`, `3` or `4` for the other groups:

```bash
source /opt/ros/humble/setup.bash
if [ -f "$HOME/UR5e_social_robotics/install/setup.bash" ]; then
    source "$HOME/UR5e_social_robotics/install/setup.bash"
fi
export ROS_DOMAIN_ID=1
export ROS_LOCALHOST_ONLY=0
export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
unset CYCLONEDDS_URI
```

#### Teacher container `~/.bashrc`

The Teacher runs ROS 2 inside the Humble container. Add this block and use the same group number as the selected Student:

```bash
source /opt/ros/humble/setup.bash
if [ -f "$HOME/UR5e_social_robotics/install/setup.bash" ]; then
    source "$HOME/UR5e_social_robotics/install/setup.bash"
fi
export ROS_DOMAIN_ID=1
export ROS_LOCALHOST_ONLY=0
export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
export CYCLONEDDS_URI=file:///root/UR5e_social_robotics/Documentation/Files/Docker/cyclonedds_teacher_multicast.xml
```

The Teacher XML must bind Cyclone DDS to `192.168.1.5`.

Reload and verify on both computers:

```bash
source ~/.bashrc
ros2 daemon stop
echo "$ROS_DOMAIN_ID"
echo "$ROS_LOCALHOST_ONLY"
echo "$RMW_IMPLEMENTATION"
echo "$CYCLONEDDS_URI"
```

### 2. Send `<motion_name>.yaml` to the Teacher PC

On the Student PC, open:

```bash
nano ~/UR5e_social_robotics/Documentation/Files/Send_motion/send_social_motion.py
```

The default parameters are prepared for the laboratory. Check `PROFESSOR_IP`, `PROFESSOR_USER`, `LOCAL_FOLDER` and `REMOTE_FOLDER` before running it. `REMOTE_FOLDER` must point to the Teacher `install/social_robot_behaviors/share/social_robot_behaviors/motions/` directory.

Run the copy tool:

```bash
cd ~/UR5e_social_robotics/Documentation/Files/Send_motion
python3 send_social_motion.py
```

When asked for the filename, enter:

```text
<motion_name>.yaml
```

The script copies the YAML directly to the Teacher `install` directory. No build is required. Continue only after it prints `Fitxer copiat correctament.`

### 3. Simulation with fake hardware

#### Teacher PC - start first

Open three terminals inside the Teacher container. Check that all use the selected group domain.

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

Check that the server shows the installed directory containing `<motion_name>.yaml`.

#### Student PC - start second

Student terminal 1:

```bash
ros2 launch social_robot_behaviors social_behavior.launch.py
```

Student terminal 2: send one motion at a time:

```bash
ros2 topic pub --once /social_behavior std_msgs/msg/String \
  "{data: 'handshake'}"
ros2 topic pub --once /social_behavior std_msgs/msg/String \
  "{data: 'give5'}"
ros2 topic pub --once /social_behavior std_msgs/msg/String \
  "{data: '<motion_name>'}"
```

Check that every IK request and trajectory succeeds in RViz. Stop all fake-hardware nodes before the real test.

### 4. Real UR5e

#### Teacher PC - start first

Check the robot connection:

```bash
ping -c 4 192.168.0.20
```

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

#### Student PC - start second

Student terminal 1:

```bash
ros2 launch social_robot_behaviors social_behavior.launch.py
```

Student terminal 2: with instructor approval, send one motion at a time:

```bash
ros2 topic pub --once /social_behavior std_msgs/msg/String \
  "{data: 'handshake'}"
ros2 topic pub --once /social_behavior std_msgs/msg/String \
  "{data: 'give5'}"
ros2 topic pub --once /social_behavior std_msgs/msg/String \
  "{data: '<motion_name>'}"
```

## Next session

In the next session, we will create a more social HRI demonstration using face recognition and voice commands. See [Face and Voice HRI Demo with ROS 2](6_Face_and_Voice_HRI_ROS2_Demo.md). The following guide adds the experimental [Gesture HRI with YOLO Pose and a 3D Camera](7_Gesture_HRI_with_YOLO_Pose_and_3D_Camera.md).

## Results

For each motion, record the simulation result, the real-robot result, any error or protective stop, and the main difference between both executions.
