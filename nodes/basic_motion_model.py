#!/usr/bin/env python
# CONTROLLER NODE ___ THE MOTION MODEL OF THE LOCALISATION ALGORITHM

import sys
import rospy
from geometry_msgs.msg import Twist, Vector3
from my_tutorial.srv import * #import all custom package srv
from my_tutorial.msg import * #import all custom package msg
from math import sqrt

# global variable FIND A BETTER WAY TO DO THIS!
# x_estimated = 0
# y_estimated = 0
# yaw_estimated = 0

#Subscribed to Topic state_estimate that is being published
#by the prediction node (executable file name: data_processing)
def get_state_belief():

	#Initiate motion model node for the Bayes Filter.
	rospy.init_node('motion_model', anonymous=True)

	#(x_estimated, y_estimated, yaw_estimated) = get_state_belief()
	rospy.Subscriber('state_estimate', Config, send_vel_command)

	rospy.spin()


def get_desired_state_client(t):

	rospy.wait_for_service('get_desired_state')
	try: 

		new_config = rospy.ServiceProxy('get_desired_state', DesiredState)
		x_desired = new_config(t).q.x
		y_desired = new_config(t).q.y
		yaw_desired = new_config(t).q.th
		print "response from request at t=%s is: [%s %s %s]"%(t, x_desired, y_desired, yaw_desired)
		return (x_desired, y_desired, yaw_desired)
		#return (new_config)
	except rospy.ServiceException, e: 
		print "Service call failed: %s"%e


def send_vel_command(data):

	#Define publiser to send the calculated velocity to the turtlebot
	pub = rospy.Publisher('/cmd_vel_mux/input/teleop',Twist, queue_size = 10)

	r = rospy.Rate(62.5) #62.5hz

	x_estimated = data.x
	y_estimated = data.y
	yaw_estimated = data.th
	print "x_estimated:%s, y_estimated:%s, yaw_estimated: %s"%(x_estimated, y_estimated, yaw_estimated)
	# spin() simply keeps python from exiting until this node is stopped
	#rospy.spin()
	

	while not rospy.is_shutdown():

		t = rospy.get_time()
		(x_desired, y_desired, yaw_desired) = get_desired_state_client(t)

		new_time = rospy.get_time()
		dt = new_time - t
		v_x = (x_desired - x_estimated)
		v_y = (y_desired - y_estimated)
		velocity_linear = sqrt(v_x**2 + v_y**2)
		velocity_angular= (yaw_desired - yaw_estimated)/dt
		#print "velocities linear=$s, angular=%s"%(velocity_linear, velocity_angular)
		#velocities = Twist(Vector3((velocity_linear),0,0), Vector3(0,0,(velocity_angular)))
		velocities = Twist(Vector3((0),0,0), Vector3(0,0,(0)))
		rospy.loginfo(velocities)
		pub.publish(velocities)
		#past_time = new_time

		r.sleep()

	rospy.spin()

#Main section of code that will continuously run unless rospy receives interuption (ie CTRL+C)
if __name__ == '__main__':

	try: get_state_belief()
	except rospy.ROSInterruptException: pass


