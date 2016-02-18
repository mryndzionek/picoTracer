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

    def __init__(self):
        logging.basicConfig(level=logging.DEBUG,
            format='%(asctime)s.%(msecs)d %(levelname)-8s %(message)s',
            datefmt='%m-%d %H:%M:%S',
            filemode='w')

        self.reset()

    def _format_hex(self, msg):
        m = binascii.hexlify(msg)
        return ' '.join(m[i:i+2] for i in range(0, len(m), 2))
   
    def _split(self, data):
    
        groups = data.split('\x7E')    
        escaped = []
        for group in groups:
            s = re.split('[\x7d](.)', group)
            if len(s) > 1:
                for i,j,k in zip(s[0::3], s[1::3], s[2::3]):
                    g = bytearray(i)
                    g.append(ord(j[0])^0x20)
                    g.extend(k)
                    escaped = escaped + [g]
                    logging.debug ("Escaping seq. form group: " + self._format_hex(group) + " -> " + self._format_hex(g))
            else:
                escaped = escaped + [group]

        return escaped

    def _default_crc(self, data):
        crc = reduce(lambda x, y: x+y, data)        
        return (~crc) & 0xFF

    def _crc_check(self, data, expected_crc):
        logging.debug ("Computing CRC on: " + self._format_hex(data))

        crc = self._default_crc(data)

        if crc == expected_crc:
            return True
        else:
            logging.warn("CRC error: " + hex(crc) + " expected : " + hex(expected_crc))
            return False

    def _parse(self, frame):

        if len (frame) >= 6:
            cnt = frame[0]
            uid = frame[1]
            timestamp = struct.unpack_from('I', frame, 2)[0]

            if uid in self._log_map:
                decoder = self._log_map.get(uid)
                if len (frame[6:]) >= decoder.size+1:
                    crc = frame[6+decoder.size]
                    if self._crc_check(frame[1:-1], crc):
                        l = (cnt,) + (timestamp,) + decoder.decode(frame[6:]) + (frame,)
                        return True, l, frame[7+decoder.size:]
                    else:
                        return False, None, bytearray(())
                else:
                    return False, None, frame
            else:
                return False, None, bytearray(())

        else:
            return False, None, frame
        

    def reset(self):
        self.tmp_buf = bytearray()

    def decode(self, data):
        log = []

        logging.debug ("Decoding data: " + self._format_hex(data))    

        frames = self._split(data)
        #logging.debug("After splitting: " + str(frames))

        self.tmp_buf.extend(frames[0])
        frames[0] = self.tmp_buf

        for frame in frames:
            if frame:
                logging.debug ("Processing frame: " + self._format_hex(frame))

            s, l, self.tmp_buf = self._parse(bytearray(frame))
            if s:
                log.append(l)

        return log
            
    def decode_file(self, in_file, out_file, block = 10):
        i = -1
        
        # read data from file one block at a time
        data = bytearray(in_file.read(block))
        while data:
            
            l = self.decode(data)
            data = in_file.read(block)
            for msg in l:
                    out_file.write('{0}, {1:#0{2}x}, {3}, {4}, {5}\n'.format(msg[0], msg[1], 10, msg[2], msg[3], self._format_hex(msg[4])))
                    if (i > -1) and (msg[0] - i) > 1:
                            logging.warn("Possible logs discontinuity detected. Missed " + str(msg[0] - i - 1) + " message(s)")
                    i = msg[0]
