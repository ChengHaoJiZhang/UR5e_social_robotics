# Social Robotics with the UR5e:

# Guided practical activity: previous simulation before real development

### Session 2 - Ubuntu 22.04, VS Code and ROS 2 Humble

### Goal and requirements

Before Session 2, simulate the same `handshake, give5 and custom_motion` movement locally with ROS 2, the fake UR5e driver, MoveIt 2, and RViz. All five ROS 2 processes run on the same Ubuntu computer.

### 1. Create a new ROSject on theConstruct environment

You need Ubuntu 22.04 and **ROS 2 Humble**. Work in TheConstruct environment for this activity. Each time you enter its environment, run:

```bash
sudo apt update
sudo apt install ros-humble-ur
```

### 2. Clone and open the project

In a terminal, run:

```bash
cd /home/user
git clone https://github.com/GITHUB_USERNAME/UR5e_social_robotics.git
cd /home/user/UR5e_social_robotics
```

### 2. Review `~/.bashrc`

Open it with `code ~/.bashrc` and add these lines at the end. Do not add duplicates if they already exist:

```bash
# ROS 2 Humble and this local workspace
source /opt/ros/humble/setup.bash
source /home/user/UR5e_social_robotics/install/setup.bash
cd /home/user/UR5e_social_robotics
# Local, one-computer simulation
export ROS_DOMAIN_ID=0
export ROS_LOCALHOST_ONLY=0
export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
```

For this local activity, `ROS_LOCALHOST_ONLY=0` enables ROS 2 communication on this computer and others in the network.

### 3. Build the workspace

In the VS Code integrated terminal:

```bash
cd /home/user/UR5e_social_robotics
colcon build
```

### 4. Verify the examples and create your motion

Open **five VS Code terminals**. Then start one process in each terminal.

**Terminal 1 - fake UR5e driver**

```bash
ros2 launch ur_robot_driver ur_control.launch.py \
  ur_type:=ur5e robot_ip:=192.168.0.20 \
  use_fake_hardware:=true launch_rviz:=false
```

**Terminal 2 - MoveIt 2 and RViz**

```bash
ros2 launch ur_moveit_config ur_moveit.launch.py \
  ur_type:=ur5e launch_rviz:=true
```

Wait until RViz displays the robot and MoveIt 2 is ready.

![](./Images/ROS2Activity/moveit2.png)

**Terminal 3 - sequence server**

```bash
ros2 run ur5e_motion_server ur5e_sequence_server
```

**Terminal 4 - behaviour manager client**

```bash
ros2 launch social_robot_behaviors social_behavior.launch.py
```

**Terminal 5 - example requests**

```bash
ros2 topic pub --once /social_behavior std_msgs/msg/String "{data: 'handshake'}"
ros2 topic pub --once /social_behavior std_msgs/msg/String "{data: 'give5'}"
```

![](./Images/ROS2Activity/init_pose.png)

Both supplied motions must run in RViz.

Finally, send your motion:

```bash
ros2 topic pub --once /social_behavior std_msgs/msg/String "{data: 'wave'}"
```

Replace `wave` with your own name.

Insert the video of simulated motion here!

### 5. Delivery

Update the Director's group GitHub repository with:

- `UR5e_social_robotics\src\social_robot_behaviors\motions\custom_motion.yaml`;
- Inserted video of simulated motion.
