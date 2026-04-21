# coding: utf8

import os
from launch import LaunchDescription

from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(
            package ='example_agent',
            executable='example_agent',
            output='screen',
            parameters=[]
        )
    ])
