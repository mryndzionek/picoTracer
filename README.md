PicoSpy - lightweight tracing framework
=======================================

Introduction
------------
The main aim of this project is to create less intrusive alternative to traditional
software tracing/logging methods. It is achieved by decoupling data gathering from
data transmission. The trace messages are gathered in a RAM ring buffer. This buffer
can be drained bit-by-bit at times when processing power is available (idle state).

Structure of the project
------------------------

Protocol specification
----------------------

XML model format
----------------

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
  - [x] Add generated tests to CTest under CMake
  - [ ] Runtime trace level handling
  - [x] Implement integrity checking
  - [ ] Add different serialization strategies

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
