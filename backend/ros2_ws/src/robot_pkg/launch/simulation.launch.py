from launch import LaunchDescription
from launch.actions import ExecuteProcess


def generate_launch_description():
	gazebo = ExecuteProcess(
		cmd=["gazebo", "--verbose", "empty.world"],
		output="screen",
	)

	spawn_placeholder = ExecuteProcess(
		cmd=["bash", "-c", "echo Spawning robot placeholder"],
		output="screen",
	)

	return LaunchDescription([
		gazebo,
		spawn_placeholder,
	])
