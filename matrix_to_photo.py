import matplotlib.pyplot as plt
import reedsolo
import math

from utils import *
from mask import *

def encode(message):

    encodedMessage = "0100"  # Byte mode indicator
    
    #Determine the length field size(8 bits versions 1-9/ 16 10-26/ 24 27-40)
    charCount = len(message)
    if charCount < 2**8: #8 bits
        charCountBits = format(charCount, '08b')
    elif charCount < 2**16: #16 bits
        charCountBits = format(charCount, '016b')
    else: #24 bits
        charCountBits = format(charCount, '024b')
    
    encodedMessage += charCountBits #Character count field
    
    #Encoded message
    for character in message:
        encodedMessage += format(ord(character), '08b')
    
    encodedMessage += '0000' #Terminator field
    
    #Ensure the length is a multiple of 8
    while len(encodedMessage) % 8 != 0:
        encodedMessage += '0'
    
    return encodedMessage

def encode_rs(encodedMessage):
    #Convert the binary string to a byte array
    byte_array = bytearray(int(encodedMessage[i:i+8], 2) for i in range(0, len(encodedMessage), 8))
    
    nrOctRS=int(input("Number of octets for reparation= "))
    rs = reedsolo.RSCodec(nrOctRS)  #symbols of error correction
    
    #Encode the message using Reed-Solomon encoding
    encodedMessageRS = rs.encode(byte_array)
    
    #Convert the encoded message to a binary string
    encodedMessageRS_str = ''.join(format(byte, '08b') for byte in encodedMessageRS)
    
    return encodedMessageRS_str

def make_matrix_before_mask(message):
    #Dimensions for the versions of QR(Byte,L)
    qrByteCapacity=[17, 32, 53, 78, 106, 134, 154, 192, 230, 271, 321, 367, 425, 458, 520, 586, 644, 718, 792, 858, 929, 1003, 1091, 1171, 1273, 1367, 1465, 1528, 1628, 1732, 1840, 1952, 2068, 2188, 2303, 2431, 2563, 2699, 2809, 2953]
    encodedMessage=encode(message)
    
    #Searches the version type
    version=None
    
    for i in range(len(qrByteCapacity)-1,-1,-1):
        if qrByteCapacity[i]>=len(message):
            version=i+1
            
    if version: #If we have a version we continue
        matrixLenght=21+4*(version-1)
        QRMatrix=[[0*matrixLenght] for i in range(matrixLenght)] #Create a matrix
        
        encodedMessageRS_str=encode_rs(encodedMessage) #version+lenght+message+end+reeds in binary
        QRMatrix=get_matrix_write(QRMatrix) #Prepares the matrix for the placement of the message
        reserved=get_reserved_matrix(QRMatrix) #The places where the message can be placed are marked as False
        
        # plt.imshow(reserved, cmap='gray_r')
        # plt.axis('off')
        # plt.show()
        
        version_info = [
            "000000000001011110101111",  #Version 7
            "000000000010011110110111",  #Version 8
            "000000000011001111111000",  #Version 9
            "000000000100000111111001",  #Version 10
            "000000000101000111111101",  #Version 11
            "000000000110000111111110",  #Version 12
            "000000000111000111111111",  #Version 13
            "000000001000001000000000",  #Version 14
            "000000001001001000000100",  #Version 15
            "000000001010001000000110",  #Version 16
            "000000001011001000000111",  #Version 17
            "000000001100001000001000",  #Version 18
            "000000001101001000001010",  #Version 19
            "000000001110001000001011",  #Version 20
            "000000001111001000001100",  #Version 21
            "000000010000001000001110",  #Version 22
            "000000010001001000001111",  #Version 23
            "000000010010001000010000",  #Version 24
            "000000010011001000010010",  #Version 25
            "000000010100001000010011",  #Version 26
            "000000010101001000010100",  #Version 27
            "000000010110001000010101",  #Version 28
            "000000010111001000010111",  #Version 29
            "000000011000001000011000",  #Version 30
            "000000011001001000011010",  #Version 31
            "000000011010001000011011",  #Version 32
            "000000011011001000011100",  #Version 33
            "000000011100001000011110",  #Version 34
            "000000011101001000011111",  #Version 35
            "000000011110001000100000",  #Version 36
            "000000011111001000100010",  #Version 37
            "000000100000001000100011",  #Version 38
            "000000100001001000100100",  #Version 39
            "000000100010001000100101",  #Version 40
        ]

        bit=0
        if version>=7:
            for j in range(matrixLenght-11,matrixLenght-8):
                for i in range(6):
                    QRMatrix[i][j]=version_info[version-7][bit]
                    bit+=1
                    
        bit=0
        if version>=7:
            for j in range(6):
                for i in range(matrixLenght-11,matrixLenght-8):
                    QRMatrix[i][j]=version_info[version-7][bit]
                    bit+=1
        
        bit = 0  # The bits of the message
        way = 1  # way=1=down->up, way=2=down->up
        for j in range(matrixLenght-1, 6, -2):
            if way == 1:
                for i in range(matrixLenght-1, -1, -1):
                    if reserved[i][j] == False:
                        if bit < len(encodedMessageRS_str) and encodedMessageRS_str[bit] == '1':
                            QRMatrix[i][j] = 1
                        bit += 1
                        if bit >= len(encodedMessageRS_str):
                            break
                    if reserved[i][j-1] == False:
                        if bit < len(encodedMessageRS_str) and encodedMessageRS_str[bit] == '1':
                            QRMatrix[i][j-1] = 1
                        bit += 1
                        if bit >= len(encodedMessageRS_str):
                            break
                way = 2
            else:
                for i in range(matrixLenght):
                    if reserved[i][j] == False:
                        if bit < len(encodedMessageRS_str) and encodedMessageRS_str[bit] == '1':
                            QRMatrix[i][j] = 1
                        bit += 1
                        if bit >= len(encodedMessageRS_str):
                            break
                    if reserved[i][j-1] == False:
                        if bit < len(encodedMessageRS_str) and encodedMessageRS_str[bit] == '1':
                            QRMatrix[i][j-1] = 1
                        bit += 1
                        if bit >= len(encodedMessageRS_str):
                            break
                way = 1

            if bit >= len(encodedMessageRS_str):
                break
        
        #Jump over the fixed patterns   
        for j in range(5,-1,-2):
            if way == 1:
                for i in range(matrixLenght-1, -1, -1):
                    if reserved[i][j] == False:
                        if bit < len(encodedMessageRS_str) and encodedMessageRS_str[bit] == '1':
                            QRMatrix[i][j] = 1
                        bit += 1
                        if bit >= len(encodedMessageRS_str):
                            break
                    if reserved[i][j-1] == False:
                        if bit < len(encodedMessageRS_str) and encodedMessageRS_str[bit] == '1':
                            QRMatrix[i][j-1] = 1
                        bit += 1
                        if bit >= len(encodedMessageRS_str):
                            break
                way = 2
            else:
                for i in range(matrixLenght):
                    if reserved[i][j] == False:
                        if bit < len(encodedMessageRS_str) and encodedMessageRS_str[bit] == '1':
                            QRMatrix[i][j] = 1
                        bit += 1
                        if bit >= len(encodedMessageRS_str):
                            break
                    if reserved[i][j-1] == False:
                        if bit < len(encodedMessageRS_str) and encodedMessageRS_str[bit] == '1':
                            QRMatrix[i][j-1] = 1
                        bit += 1
                        if bit >= len(encodedMessageRS_str):
                            break
                way = 1

            if bit >= len(encodedMessageRS_str):
                break
                
        _, QRMatrix = compute_QR_with_the_best_mask(QRMatrix)
        
        mask, _ = compute_QR_with_the_best_mask(QRMatrix)
        
        mask=[0,1]+mask
        xor_str=[1,0,1,0,1]
        
        for i in range(len(mask)):
            mask[i]=mask[i]^xor_str[i]
            
        # print(mask)
        for j in range(5):
            QRMatrix[8][j]=mask[j]
            
        for i in range(matrixLenght-1,matrixLenght-6,-1):
            QRMatrix[i][8]=mask[matrixLenght-i-1]
        
        plt.imshow(QRMatrix, cmap='gray_r')
        plt.axis('off')
        plt.show()
        
    else:
        print("The text is longer than the biggest version!")
        print("Reduce the characters of your text... =(")
        return
