import sys
import struct
import logging
import binascii
import re
import datetime
import time

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

class TraceReader(object):
    def __init__(self, base_reader, block_size):
        self.reader = base_reader
        self.block_size = block_size

    def read(self):
        pass

class SerialTraceReader(TraceReader):

    def read(self):
        time.sleep(0.1)
        pending = self.reader.inWaiting()
        if pending < self.block_size:
            pending = self.block_size
        return self.reader.read(pending)

class FileTraceReader(TraceReader):

    def read(self):
        return self.reader.read(self.block_size)

class TraceDecoder(object):

    def __init__(self, reader, writer, cfg):
        self.reader = reader
        self.writer = writer
        self.cfg = cfg
        self.reset()

    def _format_hex(self, msg):
        m = binascii.hexlify(msg)
        return ' '.join(m[i:i+2] for i in range(0, len(m), 2))
   
    def _split(self, data):
        groups = data.split('\x7E')    
        return groups

    def _unescape_reducer(self, x, y):
        a, s = x

        if s:        
            a.append(y ^ 0x20)
            s = False
        else:
            if y == 0x7D:
                s = True
            else:
                a.append(y)

        return (a, s)
            
    def _unescape(self, data):
        v = reduce(lambda x,y: self._unescape_reducer(x,y), data, (bytearray(), False))
        return v[0]

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

    def _parse(self, data):
    
        frame = self._unescape(data)
        if len (frame) >= 6:
            cnt = frame[0]
            uid = frame[1]
            timestamp = struct.unpack_from('I', frame, 2)[0]

            if uid in self.cfg.cfg:
                decoder = self.cfg.cfg.get(uid)
                if len (frame[6:]) >= decoder.size+self.cfg.crc_decoder.size:
                    crc = self.cfg.crc_decoder.unpack_from(frame, 6+decoder.size)[0]
                    if self._crc_check(frame[:-self.cfg.crc_decoder.size], crc):
                        l = (cnt,) + (timestamp,) + decoder.decode(frame[6:]) + (frame,)
                        logging.info ("Recovered valid frame: " + self._format_hex(frame))
                        return l

            return None

    def reset(self):
        self.tmp_buf = bytearray()

    def _decode_data(self, data):
        log = []

        logging.debug ("Decoding data: " + self._format_hex(data))    

        #cumulate the last remainder
        self.tmp_buf.extend(bytearray(data))
        data = self.tmp_buf
        frames = self._split(self.tmp_buf)

        for frame in frames:
            if frame:
                logging.debug ("Processing frame: " + self._format_hex(frame))
                l = self._parse(frame)
                if l:
                    log.append(l)
                    self.reset()
                else:
                    self.tmp_buf = frame
                    if data[-1] == 0x7E:
                        self.tmp_buf.append(0x7E)

        return log
            
    def decode(self):
        i = -2
        
        # read data from file one block at a time
        data = bytearray(self.reader.read())
        while data:
            
            l = self._decode_data(data)

            for counter, timer, level, message, frame in l:

                    if (i == -2):
                        ts = datetime.datetime.now()
                        last_timer = timer
                    else:
                        ts +=  datetime.timedelta(milliseconds=timer-last_timer)
                        last_timer = timer

                    if i == 255:
                        i = -1
                    if (i > -2) and (counter - i) != 1:
                            logging.warn("Possible logs discontinuity detected. Missed at least " + str(abs(counter - i - 1)) + " message(s)")
                            ts = datetime.datetime.now()
                            last_timer = timer
                    i = counter

                    self.writer.write('{0}, {1}, {2}, {3}, {4}, {5}\n'.format(
                    ts.strftime('%Y-%m-%d %H:%M:%S.') + ts.strftime('%f')[:3], 
                    counter, 
                    timer, 
                    level, 
                    message, 
                    self._format_hex(frame)))
                    self.writer.flush()

            data = self.reader.read()
