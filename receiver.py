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
    tipe = ''
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
    fulldata = None
    
    def make_file(self,filename):
        self.fulldata = open(filename,'wb')
    def write_data(self,data):
        self.fulldata.write(base64.b64decode(data))
    def close_write(self):
        self.fulldata.close()

#class untuk melakukan koneksi ke sender
class receiver_connection():
    ip_receiver = None
    port_receiver = None
    socket_receiver = None
    address_receiver = None
    def __init__(self, ip_receiver = socket.gethostname(), port_receiver =8888):
        print('inisialisasi port dan ip receiver')
        self.ip_receiver = "127.0.0.1"
        self.port_receiver = port_receiver
        self.address_receiver = (self.ip_receiver,self.port_receiver)
    def connecting(self):
        print('try to connect')
        try:
            self.socket_receiver = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
            self.socket_receiver.bind(self.address_receiver)
        except socket.error as err:
            exception_handler(err)
            return False
        return True
    def close_connection(self):
        print('disconnecting to sender')
        self.socket_receiver.close()
    def send_packet_to_sender(self,tipe,msg,address):
        try:
            data = pickle.dumps([tipe,msg])
            #untuk mendapatkan sequence number
            self.socket_receiver.sendto(data,address)
            print('sending successfull to Seq_Number: {}'.format(packet.seq_no))
        except Exception as err:
            exception_handler(err)
    def get_packet_from_sender(self):
        succ = False
        file = file_handler()
        while(not succ):
            packet, address = self.socket_receiver.recvfrom(2048)
            packets = pickle.loads(packet)
            if(address):
                print(packets)
                self.send_packet_to_sender('ACK',"ACK",address)
                if (packets[0] == 'S'):
                    namafile = '{}_'.format(address)+'{}'.format(packets[1])
                    file.make_file(namafile)
                    print('kontol filename')
                    self.send_packet_to_sender('ACK',"ACK",address)
                if (packets[0] == 'D'):
                    file.write_data(packets[1])
                    self.send_packet_to_sender('ACK',"ACK",address)
                    print('kontol data')
                if (packets[0] == 'T'):
                    print('transfer success')
                    file.close_write()
                    self.send_packet_to_sender('ACK',"ACK",address)
                    self.close_connection()
                    succ = True
        return succ
        
            
            
            
        

if __name__ == "__main__":
        #meminta inputa prot receiver
        recvport = input('masukan port receiver: ')
        
        #membuat objek receiver
        receiver = receiver_connection(recvport)
        
        #membuat algoritma UDP send ant receiv
        receiver.connecting()
        if(receiver.get_packet_from_sender()):
            print('transfer data berhasil')
        else:
            print('transfer data gagal')
