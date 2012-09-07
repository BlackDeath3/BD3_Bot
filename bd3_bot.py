import socket
import threading

def listenThreadRun(bot):
    with open("log.txt", mode = "w", encoding = "utf-8") as writeLogFile, open("log.txt", mode = "r", encoding = "utf-8") as readLogFile, open("chatLog.txt", mode = "w", encoding = "utf-8") as writeChatLogFile:
        writeChatLogFile.write("Channel | Client | Message\n\n")
        while True:
            data = bot.receiveData()
            if data:
                if data.find(b"PING :") != -1:                 
                    bot.sendData("PONG :pingis\n")
                for line in readLogFile:
                    if "PRIVMSG " in line:
                        line = line.partition(" ")
                        client = line[0][1:]
                        line = line[2].partition(" ")
                        line = line[2].partition(" ")
                        channel = line[0]
                        message = line[2][1:]
                        writeChatLogFile.write(channel + " | " + client + " | " + message)
                        writeChatLogFile.flush()
                writeLogFile.write(data.decode("latin-1"))
                writeLogFile.flush()

class Bot:
    def __init__(self, server, port, channel, nick, name, password):
        self.mServer = server
        self.mPort = port
        self.mChannel = channel
        self.mNick = nick
        self.mName = name
        self.mPass = password
        self.mCommands = {"message" : self.sendMessage,
                          "receive" : self.receiveData,
                          "join" : self.joinChannel,
                          "leave" : self.leaveChannel,
                          "ping" : self.ping,
                          "kill" : self.kill}
    def setSocket(self, socket):
        self.mSocket = socket
    def connect(self):
        print("Connecting to %s:%d as %s(%s)..." % (self.mServer, self.mPort, self.mNick, self.mName))
        self.setSocket(socket.socket(socket.AF_INET, socket.SOCK_STREAM))
        self.mSocket.connect((self.mServer, self.mPort))
        print("Connected!")
        self.sendData(("USER %s %s bla :%s\r\n" % (self.mNick, self.mNick, self.mName)))
        self.sendData(("NICK %s\r\n" % (self.mNick)))
        self.sendData(("NickServ identify %s\r\n" % (self.mPass)))
        self.joinChannel(self.mChannnel)
        print("Joined channel %s." % (self.mChannel))
    def sendData(self, string):
        self.mSocket.send(string.encode())
    def receiveData(self, extraParameter = None):
        try:
            return self.mSocket.recv(4096)
        except:
            return
    def sendMessage(self, parameter):
        parameter = parameter.partition(" ")
        channel = parameter[0]
        string = parameter[2]
        if "#" == channel[0]:
            message = ("PRIVMSG %s :%s\n" % (channel, string))
            self.sendData(message)
        else:
            print("ERROR: Usage - #channel message...")
    def receiveMessage(self, extraParameter = None):
        data = self.receiveData()
        data = message.strip("\n\r")
        if data.find(":BD3_Bot!") != -1:
            self.mSocket.send(("PRIVMSG %s :Hi!\n" % (self.mChannel)).encode())
    def joinChannel(self, channel):
        if "#" == channel[0]:
            self.sendData(("JOIN %s\n" % (channel)))
        else:
            self.sendData(("JOIN #%s\n" % (channel)))
    def leaveChannel(self, channel):
        if "#" == channel[0]:
            self.sendData(("PART %s\n" % (channel)))
        else:
            self.sendData(("PART #%s\n" % (channel)))
    def ping(self, target):
        self.sendData("PING %s\n" %(target))    # TO DO: Work on ping functionality.
    def kill(self):
        print("\nKilling connection!")
        self.mSocket.shutdown(socket.SHUT_RDWR)
        self.mSocket.close()

def main():
    default_server = "irc.freenode.net"
    default_port = 6667
    default_channel = ""
    default_nick = ""
    default_name = ""
    default_password = ""
    buffer = ""

    try:
        print("====================== START BD3 BOT =======================")
        bot = Bot(default_server, default_port, default_channel, default_nick, default_name, default_password)
        connect = input("> Connect to (server:port): ")
        if 0 < len(connect):
            connect = connect.partition(":")
            bot.mServer = connect[0]
            bot.mPort = connect[2]
        channel = input("> Join (#channel) upon startup: ")
        if 0 < len(channel):
            bot.mChannel = channel
        nick = input("> Bot nickname: ")
        if 0 < len(nick):
            bot.mNick = nick
        password = input("> Bot password: ")
        if 0 < len(password):
            bot.mPass = default_password
        name = input("> Bot realname: ")
        if 0 < len(name):
            bot.mName = name
        print("")
        bot.connect()
        print("")
        listenThread = threading.Thread(target=listenThreadRun, args=(bot,))
        listenThread.daemon = True
        listenThread.start()
        while True:
            commandInput = input("> BD3 Command: ")
            commandInput = commandInput.partition(" ")
            command = commandInput[0]
            parameter = commandInput[2]
            try:
                commandFunc = bot.mCommands[command]
                commandFunc(parameter)
            except KeyError:
                print("ERROR: Invalid command.")
            if "kill" == command:
                break
    except:
        bot.kill()
    print("======================= END BD3 BOT ========================")

main()
