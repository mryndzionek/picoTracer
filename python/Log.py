import sys
import struct
import logging
import binascii
import re

class MsgDecoder(object):
    def __init__(self, level, format, structure, enums = {}):
        self.f = format
        self.s = struct.Struct(structure)
        self.size = self.s.size
        self.e = enums
        self.l = level

    def decode(self, data):
        values = list(self.s.unpack_from(data, 0))
        for i,v in enumerate(values):
            if i in self.e:
                values[i] = self.e.get(i).get(v, 'Unknown enum: ' + str(v))
            
        return (self.l, self.f.format(*values))

class Log(object):


    @classmethod
    def _format_hex(cls, msg):
        m = binascii.hexlify(msg)
        return ' '.join(m[i:i+2] for i in range(0, len(m), 2))
   
    @classmethod
    def _split(cls, data):
    
        groups = data.split('\x7E')    
        escaped = []
        for group in groups:
            s = re.split('[\x7d](.)', group)
            if len(s) > 1:
                print [s]
                for i,j,k in zip(s[0::3], s[1::3], s[2::3]):
                    g = bytearray(i)
                    g.append(ord(j[0])^0x20)
                    g.extend(k)
                    escaped = escaped + [g]
                    logging.debug ("Escaping seq. form group: " + cls._format_hex(group))
            else:
                escaped = escaped + [group]

        return escaped


    @classmethod
    def _parse(cls, frame):

        if len (frame) >= 6:
            cnt = frame[0]
            uid = frame[1]
            timestamp = struct.unpack_from('I', frame, 2)[0]

            if cnt == 0:
                print [frame]

            if uid in cls._log_map:
                decoder = cls._log_map.get(uid)
                if len (frame[6:]) >= decoder.size:
                    l = (cnt,) + (timestamp,) + decoder.decode(frame[6:])
                    return True, l, frame[6+decoder.size:]
                else:
                    return False, None, frame
            else:
                return False, None, bytearray(())

        else:
            return False, None, frame
        

    @classmethod
    def decode(cls, rest, data):
        log = []

        logging.debug ("Decoding data: " + str([data]))    

        frames = cls._split(data)
        logging.debug("After splitting: " + str(frames))

        rest.extend(frames[0])
        frames[0] = rest

        for frame in frames:
            logging.debug ("Processing frame: " + cls._format_hex(frame))

            s, l, rest = cls._parse(bytearray(frame))
            if s:
                log.append(l)

        return log, rest
            
    @classmethod
    def decode_file(cls, in_file, out_file, block = 10):

        rest = bytearray(())
        i = 0

        data = bytearray(in_file.read(block))
        while data:
            
            l, rest = cls.decode(rest, data)
            data = in_file.read(block)
            for msg in l:
                    out_file.write('{0}, {1:#0{2}x}, {3}, {4}\n'.format(msg[0], msg[1], 10, msg[2], msg[3]))
                    if (msg[0] - i) > 1:
                        logging.warn("Possible logs discontinuity detected")
                    i = msg[0]
