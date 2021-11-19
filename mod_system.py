import pickle
from datetime import datetime
from pathlib import Path

class SystemManagement:
	def __init__(self):
		self.lastLoopTime = None # datetime object
		self.stop = False
		self.filename = "systemdata.pkl"
		filepath = Path(self.filename)
		if filepath.is_file():
			with open(self.filename, "rb") as f:
				self.lastLoopTime, self.stop = pickle.load(f)
		else:
			with open(self.filename, "wb") as f:
				pickle.dump((self.lastLoopTime, self.stop), f)

	def stop(self):
		self.stop = True

	def start(self):
		self.stop = False
	
	def load(self):
		with open(self.filename, "rb") as f:
			self.lastLoopTime, self.stop = pickle.load(f)
	
	def save(self):
		with open(self.filename, "wb") as f:
			pickle.dump((self.lastLoopTime, self.stop), f)



if __name__ == "__main__":
	system = SystemManagement()

