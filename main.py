from include.server_manager import ServerManger

#app main class
class AppEntry():
	def __init__(self):
		ServerManger()

if __name__ == '__main__':
	AppEntry()