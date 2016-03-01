cmake_minimum_required(VERSION 2.8)
project(pico_spy)

enable_testing()

set(VERSION_MAJOR 0)
set(VERSION_MINOR 0)
set(VERSION_PATCH 1)
set(VERSION_STRING "${VERSION_MAJOR}.${VERSION_MINOR}.${VERSION_PATCH}")

set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -std=gnu99 -Wall -Wextra -pedantic -Wno-unused -DTRACE_FSM_ENABLE")

link_libraries(m)

configure_file (
  "${CMAKE_CURRENT_SOURCE_DIR}/include/config.h.in"
  "${CMAKE_CURRENT_BINARY_DIR}/include/config.h"
  )

find_program(GSLGEN "generate.sh" HINTS ${CMAKE_CURRENT_SOURCE_DIR}/models)

include_directories("${CMAKE_CURRENT_SOURCE_DIR}/include")
include_directories("${CMAKE_CURRENT_SOURCE_DIR}/gen/include")
include_directories("${CMAKE_CURRENT_SOURCE_DIR}/example/include")
include_directories("${CMAKE_CURRENT_BINARY_DIR}/include")

set(COMMON_SRCS ${CMAKE_CURRENT_SOURCE_DIR}/gen/src/trace_fsm.c
                ${CMAKE_CURRENT_SOURCE_DIR}/src/rb.c)

function(gsl_gen in_model)
  add_custom_command(OUTPUT ${CMAKE_CURRENT_SOURCE_DIR}/gen/src/trace_${in_model}.c 
                            ${CMAKE_CURRENT_SOURCE_DIR}/gen/tests/trace_${in_model}_test.c
                            ${CMAKE_CURRENT_SOURCE_DIR}/gen/include/trace_${in_model}.h
                            ${CMAKE_CURRENT_SOURCE_DIR}/gen/trace_${in_model}.py
    COMMAND ${GSLGEN} ${CMAKE_CURRENT_SOURCE_DIR}/models/${in_model}.xml ${ARGN}
    DEPENDS ${CMAKE_CURRENT_SOURCE_DIR}/models/${in_model}.xml
    )
  add_custom_target(gsl_${in_model} DEPENDS ${CMAKE_CURRENT_SOURCE_DIR}/gen/src/trace_${in_model}.c)
  add_executable(trace_${in_model}_test ${CMAKE_CURRENT_SOURCE_DIR}/gen/tests/trace_${in_model}_test.c ${COMMON_SRCS})
  add_test(trace_${in_model}_test trace_${in_model}_test)
endfunction(gsl_gen)

gsl_gen(fsm)
