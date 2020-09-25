import socket
import os, sys
import pickle
import hashlib
import copy
import base64


# untuk melakukan handle ketika ada exception
def exception_handler(e):
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    print('Type: %s' % (exc_type), 'On file: %s' % (fname), exc_tb.tb_lineno, 'Error: %s' % (e))

# class untuk membuat objek packet

class packet():
    tipe =''
    length = 0
    seq_no = 0
    checksum = 0
    data = 0
    
    def increase_seqNo(self):
        self.seq_no +=1
        return self.seq_no

    def create_packet(self,tipe,message=None):
        self.tipe = tipe
        self.data = message
        if(message):
            self.length = str(len(message))
        self.checksum = hashlib.sha1(message.encode('utf-8')).hexdigest()
        return [self.length,self.increase_seqNo(),self.data]
        
#class untuk melakukan file handler
class file_handler():
    readdata = None
    filename = None
    
    def __init__(self,filename):
        self.readdata = open(filename,'rb')
        self.filename = filename
    def read_data(self):
        data = []
        totsize = os.stat(filename).st_size
        currsize = 0
        if(totsize>800):
            while True:
                if(currsize > totsize):
                    break
                data.append(base64.b64encode(self.readdata.read(800)))
                currsize += 800
        data.append(base64.b64encode(self.readdata.read(800)))
        return data

#class untuk melakukan koneksi ke sender
class sender_connection():
    ip_sender = None
    port_sender = None
    socket_sender = None
    address_sender = None
    def __init__(self, port_sender = 8888):
        print('inisialisasi port dan ip receiver')
        self.ip_sender ="127.0.0.1"
        self.port_sender = port_sender
        self.address_sender = (self.ip_sender,self.port_sender)
    def connecting(self):
        print('try to connect')
        try:
            self.socket_sender = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
            self.socket_sender.bind(self.address_sender)
        except socket.error as err:
            exception_handler(err)
            return False
        return True
    def close_connection(self):
        print('disconnecting to sender')
        self.socket_sender.close()
    def send_packet_to_sender(self,tipe,msg,address):
        try:
            data = pickle.dumps([tipe,msg])
            #untuk mendapatkan sequence number
            self.socket_sender.sendto(data,address)
            print('sending successfull to Seq_Number: {}'.format(packet.seq_no))
        except Exception as err:
            exception_handler(err)

    def get_packet_from_receiver(self): #melakukan cek apakah sender mendapat ack dari receiver
        packet, address = self.socket_sender.recvfrom(1024)
        data = pickle.loads(packet)
        if(data[0] == 'ACK'):
            return True
        else:
            return False
    
if __name__ == "__main__":
        dataReceiver = [] #untuk menyimpan data receiver
        #meminta inputan port sender
        senport = input('masukan port sender: ')
        #membuat objek file handler
        filename = input('masukan filename yang akan dikirim: ')
        file = file_handler(filename)
        #meminta
        print('kosongi jika untuk mengakhiri pengisian')
        recv = None
        while True:
            recv = input('masukan daftar port receiver: ')
            if(recv):
                dataReceiver.append(recv)
            if(not recv):
                break
        
        #membuat objek sender dan mengkoneksikan ke server
        sender = sender_connection(int(senport))
        sender.connecting()
        
        
        #membuat algoritma transfer keseluruh receiver
        for receiver in dataReceiver:
            address = ("127.0.0.1",int(receiver))
            #mengirim filename
            sender.send_packet_to_sender('S',str(filename),address)
            if(sender.get_packet_from_receiver()):
                for data in file.read_data():
                    if(sender.get_packet_from_receiver()):
                        sender.send_packet_to_sender('D',data,address)
            sender.send_packet_to_sender('T',None,address)
                        
        