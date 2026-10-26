from setuptools import find_packages, setup
from glob import glob
import os

package_name = 'mobile_robot'

setup(
    name=package_name,
    version='0.0.0',

    packages=find_packages(exclude=['test']),

    data_files=[
        (
            'share/ament_index/resource_index/packages',
            ['resource/' + package_name]
        ),

        (
            'share/' + package_name,
            ['package.xml']
        ),

        (
            os.path.join('share', package_name, 'launch'),
            glob('launch/*.py')
        ),

        (
            os.path.join('share', package_name, 'description'),
            glob('description/*.xacro')
        ),

        (
            os.path.join('share', package_name, 'worlds'),
            glob('worlds/*.sdf')
        ),

        (
            os.path.join('share', package_name, 'config'),
            glob('config/*.rviz') + glob('config/*.yaml')
        ),
    ],

    install_requires=['setuptools'],

    zip_safe=True,

    maintainer='akashakhade',

    maintainer_email='akashakhade@todo.todo',

    description='Mobile robot simulation using ROS 2 Jazzy and Gazebo Harmonic',

    license='Apache-2.0',

    extras_require={
        'test': [
            'pytest',
        ],
    },

    entry_points={
        'console_scripts': [
            'depth_colorizer = mobile_robot.depth_colorizer:main',
        ],
    },
)