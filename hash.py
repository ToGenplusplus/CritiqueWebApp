
import hashlib, binascii, os

import struct

def protect_pass(data):
    value = (data)
    packinstruct = struct.Struct('32s')
    packedpassword = packinstruct.pack(value)
    chksum =  bytes(hashlib.md5(packedpassword).hexdigest(), encoding="UTF-8")     
    return chksum

def verify_Password(storedPass, inputpass):
    return storedPass == inputpass

