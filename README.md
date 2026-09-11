# Autonomous Robotics Development Studio (ROS 2 + Gazebo LLM Pipeline)

An end-to-end multi-agent robotics engineering system designed for autonomous robot synthesis, kinematic model generation (URDF/SDF), control algorithm code generation, automated ROS 2 workspace compilation, and real-time Gazebo physics simulation.

---

## 🛠 Architectural Overview

This framework bridges high-level natural language robot specifications with low-level ROS 2 execution pipelines and Gazebo physics simulation through an orchestrated multi-agent AI framework.

```
+-------------------------------------------------------------------------------+
|                             React Frontend UI                                 |
|          (Prompt Interface, System Telemetry, Step Tracker, Output Logs)       |
+-------------------------------------------------------------------------------+
                                      |
                                      v [REST API / Fast API]
+-------------------------------------------------------------------------------+
|                       Multi-Agent Robotics Pipeline                           |
|                                                                               |
|  +-------------------+      +-------------------+      +-------------------+  |
|  |  Planner Agent    | ---> | Robot Generator   | ---> | Behavior Agent    |  |
|  |  (Specs & DAG)    |      | (URDF/SDF Model)  |      | (ROS 2 Nodes)     |  |
|  +-------------------+      +-------------------+      +-------------------+  |
|                                                                  |            |
|  +-------------------+      +-------------------+                v            |
|  | Fixer / Debugger  | <--- | Validator Agent   | <---------------------------+  |
|  | (Auto-repair loop)|      | (colcon test)     |                             |
|  +-------------------+      +-------------------+                             |
+-------------------------------------------------------------------------------+
                                      |
                                      v
+-------------------------------------------------------------------------------+
|                           ROS 2 Workspace & Gazebo                            |
|      (Package generation, CMake/ament build, Gazebo Sim physics launch)        |
+-------------------------------------------------------------------------------+
```

---

## 🚀 Key Features

* **Kinematic & Dynamics Synthesis**: Generates valid URDF and SDF models with inertial matrices, joint limits, transmissions, link geometry, visual/collision meshes, and sensor plugins (IMU, LiDAR, Camera, Differential Drive).
* **ROS 2 Control & Node Generation**: Generates compliant Python (`rclpy`) and C++ (`rclcpp`) ROS 2 nodes, dynamic controllers, publisher/subscriber nodes, dynamic TF broadcasts, and custom msg/srv definitions.
* **Automated Build & Execution Pipeline**: Automatically scaffolds ROS 2 packages (`ament_python` / `ament_cmake`), updates `package.xml` and `setup.py`/`CMakeLists.txt`, triggers `colcon build`, and verifies package sourcing.
* **Closed-Loop Hardware-in-the-Loop (HIL) / Simulation Verification**: Launches Gazebo Sim instances, runs automated validator agents against ROS 2 topics and TF trees, and automatically feeds compilation or runtime errors back to the Fixer Agent for iterative code self-healing.
* **Full-Stack Robotics Command Dashboard**: Real-time telemetry monitoring, build status indicators, simulation lifecycle hooks, and interactive prompt interface for iterative robot prototyping.

---

## 📦 System Prerequisites

Ensure your system meets the following robotic development requirements:

* **Linux OS**: Ubuntu 22.04 LTS (Jammy Jellyfish) recommended
* **ROS 2 Environment**: ROS 2 Humble Hawksbill or newer (with `rclpy`, `xacro`, `robot_state_publisher`, `joint_state_publisher`, `ros2control`)
* **Simulator**: Gazebo Sim (Ignition / Fortress / Harmonic)
* **Python**: Python 3.10+
* **Node.js Runtime**: Bun v1.0+ or Node.js v18+

---

## ⚡ Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/your-org/robotics-studio.git
cd robotics-studio
```

### 2. Configure Backend Pipeline

```bash
# Sourcing ROS 2 Environment
source /opt/ros/humble/setup.bash

# Set up Python virtual environment
python3 -m venv venv
source venv/bin/activate

# Install backend dependencies
cd backend
pip install -r requirements.txt # or setup dependencies
```

Set up environment secrets in `backend/.env`:
```env
OPENAI_API_KEY=your_openai_api_key
ROS_DOMAIN_ID=0
```

Start the API Server:
```bash
python3 main.py
```

### 3. Launch Frontend Control Dashboard

In a new terminal window:
```bash
# Install dependencies & start dev server
bun install
bun run dev
```

Navigate to `http://localhost:8080` to access the Robotics Studio UI.

---

## 🔬 Multi-Agent Pipeline Execution Workflow

1. **System Prompting**: Enter robot requirements (e.g., *"Create a 4-wheeled mobile rover equipped with a 2-DOF robotic arm, top-mounted 3D LiDAR, and differential drive behavior node"*).
2. **Planner Agent**: Deconstructs requirements into a task DAG specifying URDF links, joints, sensors, controllers, and launch configurations.
3. **Robot Generator**: Synthesizes structured URDF/xacro and SDF files including visual/collision primitives and sensor macros.
4. **Behavior Agent**: Synthesizes ROS 2 control nodes handling joint state publishing, velocity commands (`geometry_msgs/msg/Twist`), and TF transforms.
5. **Validator & Auto-Fixer**: Runs `colcon build` inside `backend/ros2_ws/`. If missing dependencies or syntax errors occur, the Fixer Agent corrects `package.xml`, `setup.py`, or node logic until compilation succeeds.
6. **Gazebo Simulation Launch**: Spawns the synthesized robot model into Gazebo Sim, attaches control plugins, and establishes active ROS 2 communications.

---

## 📁 Repository Structure

```
.
├── backend/
│   ├── ros2_ws/              # Automated ROS 2 build workspace
│   ├── agents.py             # Agent definitions & system instructions
│   ├── planner.py            # High-level architecture planner
│   ├── robot_generator.py    # URDF/SDF kinematic synthesizer
│   ├── behavior_agent.py     # ROS 2 node generator
│   ├── validator_agent.py    # Build test runner & ROS 2 linter
│   ├── fix_agent.py          # Auto-repair loop agent
│   ├── pipeline_runner.py    # Orchestration engine
│   └── main.py               # FastAPI gateway server
├── src/                      # React Dashboard Frontend
│   ├── components/           # Telemetry panels, step progressors, terminal views
│   ├── pages/                # Workspace views
│   └── lib/                  # Web utilities & API client
├── README.md
└── package.json
```

---

## 🛡 License

Distributed under the MIT License. See `LICENSE` for more details.
