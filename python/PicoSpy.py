import sys, re
import argparse
import logging
import serial
import TraceDecoder
import TraceCfg

parser = argparse.ArgumentParser(description='pictrace - trace decoder application')
parser.add_argument('-i', '--input', choices=['file', 'serial'], default='serial')
parser.add_argument('path', nargs='?', default='/dev/ttyUSB0:115200:8N1',
                   help='path to file or serial port identifier')
parser.add_argument('-b', '--block', default='10', type=int)
parser.add_argument('-d', '--debug', default=False, action='store_true')
args = parser.parse_args()

if args.debug:
    lv = logging.DEBUG
else:
    lv = logging.INFO

logging.basicConfig(level=lv,
                    format='%(asctime)s.%(msecs)03d %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M:%S',
                    filemode='w')

try:
    if args.input == 'serial':
        logging.info('Trying to open serial port: ' + args.path)
        rs = re.match('([^:]+):([0-9]+):([5678])([NOE])([12])', args.path)
        if rs:
            reader = serial.Serial(rs.group(1), rs.group(2), timeout=0, bytesize=int(rs.group(3)),
                                parity=rs.group(4), stopbits=int(rs.group(5)))
        else:
            raise ValueError('Wrong serial port format: ' + args.path)
    else:
        logging.info('Trying to open file: ' + args.path)
        reader = open(args.path, 'rb')

    try:
        writer = open(args.path + '.csv', 'wb')
        try:
            cfg = TraceCfg.TraceCfg.cfg
            decoder = TraceDecoder.TraceDecoder(reader, writer, cfg)
            decoder.decode(args.block)
        finally:
            writer.close()
    finally:
        reader.close()

except (ValueError, IOError, serial.SerialException):
    logging.error(sys.exc_info()[1])
