PicoTracer - lightweight tracing framework
==========================================

Introduction
------------
The main aim of this project is to create less intrusive alternative to traditional
software tracing/logging methods. It is achieved by decoupling data gathering from
data transmission. The trace messages are gathered in a RAM ring buffer. This buffer
can be drained bit-by-bit at times when processing power is available (idle state).

Structure of the project
------------------------

![fig1](../blob/master/images/fig1.png)

Protocol specification
----------------------

![fig2](../blob/master/images/fig2.png)

Syntax in ABNF format:
```
pico-frame      = counter uid timestamp payload crc FLAG
counter         = HDLC
uid             = HDLC
timestamp       = 4HDLC
payload         = *256HDLC
crc             = HDLC

HDLC            = *1%x7D (%x00-7D / %x7F-FF)
FLAG            = %x7E
```

The protocol uses HDLC 'octet stuffing'.
This is reflected in the HDLC rule - the FLAG octet is escaped.

XML model format
----------------
The basic description can be found [here](../blob/master/models/fsm.xml).

Dependencies
------------
Code generator is implemented in [GSL](https://github.com/imatix/gsl).
The ASCII figures are converted to graphics using [ASCIIToSVG](https://bitbucket.org/dhobsd/asciitosvg) 
(see the `tools/gen_images.sh` script).

Build instructions
------------------
Standard CMake routine:
```sh
mkdir build
cd build
cmake ..
make
make test
```

TODO
----
  - [ ] Add more info to this README
  - [ ] Add more examples
  - [x] Fully support generated tests in CTest under CMake
  - [x] Runtime trace level handling
  - [x] Implement integrity checking
  - [ ] Add different serialization strategies
  - [x] Limit temporary buffers size

License
-------
  - MPLv2

Acknowledgments
---------------
  - (MpicoSys)[http://www.mpicosys.com/] for letting me implement this project as my 10% time activity

Contact
-------
If you have questions, contact Mariusz Ryndzionek at:

<mryndzionek@gmail.com>
