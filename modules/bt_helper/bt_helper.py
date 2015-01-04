# Version:	1.0
# Author:	Vincent Diener - diener@teco.edu

import logging as log
import time as t
import bluetooth

# Helper class for Bluetooth.
# Also does logging.
class BTHelper:
	# Initialize with matrix and window.
	# Matrix represents the 576 LEDs on the Connection Machine.
	def __init__(self, matrix, max_fps, window):
		self.matrix = matrix
		self.window = window
		self.max_fps = max_fps
		self.running = False
		
	# This gets started as a thread.
	def btreader(self, arg) :
		# Start logging.
		log.basicConfig(filename='logs/events.log',
						format='%(asctime)s %(message)s',
						datefmt='%d/%m/%Y %H:%M:%S',
						level=log.INFO)
						
		log.info("- Starting the server.\n")
		
		# Bluetooth reading loop.
		while(True):

			# No connection yet.
			self.running = False

			# Set up server socket and start listening.
			server_sock = bluetooth.BluetoothSocket( bluetooth.RFCOMM )

			port = 16
			server_sock.bind(("", port))
			server_sock.listen(1)
			
			# Print Bluetooth address and RFCOMM port to window title.
			addr = str(server_sock.getsockname()[0])
			port = str(server_sock.getsockname()[1])
			self.window.set_caption("Connection Machine Emulator (" + addr + " Port: " + port + ")")
			
			# Connection established.
			client_sock, address = server_sock.accept()
			self.running = True
			 
			# Log time of connection.
			time_connect = t.time()
			log.info("- Accepted connection from device " + str(address) + ".")
			
			# Start counting received frames.
			frames_received = 0
			
			# Receive handshake packet. More info: see http://www.teco.kit.edu/cm/dev/
			try:
				version = ""
				xSize = ""
				ySize = ""
				colorMode = ""
				nameLength = ""
				name = ""
				
				version = client_sock.recv(1)
				xSize = client_sock.recv(1)
				ySize = client_sock.recv(1)
				colorMode = client_sock.recv(1)
				nameLength = client_sock.recv(1)
				name = client_sock.recv(ord(nameLength))
			except:
				# Malformed handshake packet.
				# Close connection and go back to listening.
				self.running = False

			# Log received handshake info.
			log.info("- Received handshake. Version: \"" + str(ord(version)) + "\", Name: \"" + str(name) + "\", X-Size: \"" + str(ord(xSize)) + "\", Y-Size: \"" + str(ord(ySize)) + "\", ColorMode: \"" + str(ord(colorMode)) + "\".")
			
			# Send back response code 0 ("No error, connection OK.").
			rsp_code = 0
			client_sock.send(chr(rsp_code))
			
			# Set FPS supported by emulator.
			client_sock.send(chr(self.max_fps))
			
			# Log sent response.
			log.info("- Sent response. Code: " + str(rsp_code) +  ", Max. FPS: " + str(self.max_fps) + ".")
			
			# Loop while connection is open.
			while(self.running == True) :
				# Receive 576 bytes.
				# If no data is received, close connection.
				try:
					data = ""
					data = client_sock.recv(576)
				except:
					self.running = False

				# Broken connection might result in empty buffer getting read over and over again.
				# To counter this infinite loop, we have to check if received data is empty and stop if it is.
				if (not data) :
					self.running = False
				
				# Make sure the data was received and the connection is still open.
				if (self.running == True and len(data) >= 576) :
					# Debugging: Print out data.
					# print "Received [%s]" % data
					
					# Map received bytes to integers between 0 and 255.
					numbers = map(ord, data)
					
					# Increase frame counter.
					frames_received += 1

					# Put received integers in the float array of red values that is used by the shaders.
					count = 0
					for x in range (0,24) :
						for y in range (0,24) :
								self.matrix[24 * (23 - y) + x] = numbers[576 - 1 - count] / 255.0
								count += 1

			# Close connection.
			client_sock.close()
			server_sock.close()
			
			# Log disconnect time.
			time_disconnect = t.time()
			log.info("- Connection to " + str(address) + " closed. Connection lasted " +
					str((int(time_disconnect - time_connect) + 1)) + " seconds. Received " +
					str(frames_received) + " frames.\n") 
