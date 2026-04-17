from setuptools import find_packages, setup

package_name = "robot_pkg"

setup(
    name=package_name,
    version="0.0.1",
    packages=find_packages(exclude=["test"]),
    data_files=[
        ("share/ament_index/resource_index/packages", [f"resource/{package_name}"]),
        (f"share/{package_name}", ["package.xml"]),
        (f"share/{package_name}/launch", ["launch/simulation.launch.py"]),
        (f"share/{package_name}/urdf", ["urdf/robot.urdf", "urdf/human.urdf"]),
        (f"share/{package_name}/worlds", ["worlds/empty.world"]),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="dev",
    maintainer_email="dev@example.com",
    description="Generated ROS2 robot package",
    license="Apache-2.0",
)
