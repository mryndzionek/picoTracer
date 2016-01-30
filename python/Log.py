import struct

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
    def decode(cls, data):
        pos = 0
        log = [];

        while len(data[pos:]) >= 5:

            overflow = False

            uid = ord(data[pos])
            if uid == 0xFF:
                log.append((True,))
                return log, data[pos+1:]
                
            if uid in cls._log_map:
                pos = pos + 1

                timestamp = struct.unpack_from('I', data, pos)[0]
                pos = pos + 4

                s = cls._log_map.get(uid)
                if len(data[pos:]) >= s.size:
                    l = (timestamp,) + s.decode(data[pos:])
                    log.append(l)
                    pos = pos + s.size
                else:
                    pos = pos - 5
                    break
            else:
                raise Exception('Wrong key value: ' + str(uid))

        return log, data[pos:]
            
    @classmethod
    def decode_file(cls, in_file, out_file, block = 10):

        rest = ''
        i = 0

        data = in_file.read(block)
        while data:

            l, rest = cls.decode(rest + data)
            data = in_file.read(block)
            for msg in l:
                if len(msg) == 1:
                    out_file.write('--- Overflow !!! Missing data possible ---\n')
                else:
                    out_file.write('{0}, {1:#0{2}x}, {3}, {4}\n'.format(i, msg[0], 10, msg[1], msg[2]))
                    i = i + 1

