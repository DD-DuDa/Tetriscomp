# SDK Documentation (2.10.0)

- Source: https://sdk.cerebras.net/csl/code-examples/tutorial-pipeline-02-fifo
- Assigned Skill: cerebras-sdk-guides
- Scraped At: 2026-04-27T10:01:33.361199+00:00

## Content

.rst

.pdf

 Contents

Pipeline 2: Attach a FIFO to H2D

 Contents

Pipeline 2: Attach a FIFO to H2D
¶

The previous example stalls if the parameter
size
 exceeds the capacity of
the internal queues. The size of the queue is architecture-dependent. From the
software development point of view, a program should be independent of any
architecture. One solution is to add a FIFO between H2D and
@add16
. The FIFO
receives data from H2D and then forwards the data to
@add16
. The WSE
provides an efficient design for FIFO. The user just binds two microthreads to
the FIFO: one pushes data into the FIFO, and the other pops the data out. As
long as the parameter
size
 does not exceed the capacity of the FIFO, H2D can
always push all data into the FIFO even if
@add16
 cannot process any data.
Once H2D is done, D2H can continue to drain the data out such that
@add16

can progress.

To create a FIFO, we use a builtin
@allocate_fifo
 to bind a normal tensor.
We create two fabric DSDs: one pushes data from
MEMCPYH2D_DATA_1
 to the
FIFO and the other pops data from the FIFO to the color
C1
. Both DSDs must
use different microthreads.

The routing configuration of color
C1
 is RAMP to RAMP because
1) the FIFO pops data to the router via
C1
 and
2)
@add16
 receives data from the router via
C1

The disadvantage of this approach is the resource consumption. The FIFO
requires two microthreads and a scratch buffer.

The next example will fix this issue.

layout.csl
¶

// Color/ task ID map

//

//  ID var           ID var  ID var                ID var

//   0 MEMCPYH2D_1    9  C1  18                    27 reserved (memcpy)

//   1 MEMCPYD2H_1   10      19                    28 reserved (memcpy)

//   2               11      20                    29 reserved

//   3               12      21 reserved (memcpy)  30 reserved (memcpy)

//   4               13      22 reserved (memcpy)  31 reserved

//   5               14      23 reserved (memcpy)  32

//   6               15      24                    33

//   7               16      25                    34

//   8 main_task_id  17      26                    35

// Number of elements sent through core program rectangle

param
 size:
i16
;

param
 MEMCPYH2D_DATA_1_ID:
i16
;

param
 MEMCPYD2H_DATA_1_ID:
i16
;

const
 C1:
color

=

@get_color
(
9
);

const
 memcpy
=

@import_module
(
"<memcpy/get_params>"
, .{
  .width
=

1
,
  .height
=

1
,
  .MEMCPYH2D_1
=
 MEMCPYH2D_DATA_1_ID,
  .MEMCPYD2H_1
=
 MEMCPYD2H_DATA_1_ID
});

layout
 {

@set_rectangle
(
1
,
1
);

@set_tile_code
(
0
,
0
,
"pe_program.csl"
, .{
    .memcpy_params
=
 memcpy.get_params(
0
),
    .size
=
 size,
    .C1
=
 C1
  });

// fifo sends out the data via C1 --> tx = RAMP

// add16 receives data via C1 --> rx = RAMP

@set_color_config
(
0
,
0
, C1, .{ .routes
=
 .{ .rx
=
 .{
RAMP
 }, .tx
=
 .{
RAMP
 }}});
}

pe_program.csl
¶

// Introduce a fifo to buffer the data from H2D, so the H2D can

// finish as long as size does not exceed the capacity of the fifo

//

// H2D --> fifo --> C1 --> addh() --> D2H

param
 memcpy_params;

param
 size:
i16
;

param
 main:
u16
;

// Colors

param
 C1:
color
;

// Queue IDs

const
 h2d_1_iq: input_queue
=

@get_input_queue
(
2
);

const
 d2h_1_oq: output_queue
=

@get_output_queue
(
3
);

const
 C1_iq: input_queue
=

@get_input_queue
(
4
);

const
 C1_oq: output_queue
=

@get_output_queue
(
5
);

// Task IDs

const
 main_task_id: local_task_id
=

@get_local_task_id
(
8
);

const
 sys_mod
=

@import_module
(
"<memcpy/memcpy>"
, memcpy_params);

var
 fifo_buffer
=

@zeros
(
[
1024
]
i16
);

const
 fifo
=

@allocate_fifo
(fifo_buffer);

const
 INFINITE_DSD_LEN:
u16

=

0x7fff
;

const
 h2d_in_dsd
=

@get_dsd
(fabin_dsd, .{
  .extent
=
 INFINITE_DSD_LEN,
  .input_queue
=
 h2d_1_iq
});

const
 C1_out_dsd
=

@get_dsd
(fabout_dsd,
if
 (
@is_arch
(
"wse3"
)) .{
  .extent
=
 INFINITE_DSD_LEN,
  .output_queue
=
 C1_oq
}
else
 .{
  .extent
=
 INFINITE_DSD_LEN,
  .fabric_color
=
 C1,
  .output_queue
=
 C1_oq
});

const
 C1_in_dsd
=

@get_dsd
(fabin_dsd, .{
  .extent
=
 size,
  .input_queue
=
 C1_iq
});

const
 d2h_out_dsd
=
 sys_mod.get_streaming_fabout_dsd(
@get_color
(
@bitcast
(
u16
, sys_mod.MEMCPYD2H_1)), size, d2h_1_oq);

const
 buf
=

[
1
]
i16
{
1
 };

const
 one_dsd
=

@get_dsd
(mem1d_dsd, .{ .tensor_access
=
 |i|{size}
-
> buf
[
0
]
 });

task
 main_task()
void
 {

// Move from the fabric to the FIFO

@mov16
(fifo, h2d_in_dsd, .{ .async
=

true
 });

// Move from the FIFO to C1

@mov16
(C1_out_dsd, fifo, .{ .async
=

true
 });

@add16
(d2h_out_dsd, C1_in_dsd, one_dsd, .{ .async
=

true
 });
}

comptime
 {

// activate local task main_task_id at startup

@bind_local_task
(main_task, main_task_id);

@activate
(main_task_id);

@initialize_queue
(h2d_1_iq,  .{ .
color

=

@get_color
(
@bitcast
(
u16
, sys_mod.MEMCPYH2D_1)) });

@initialize_queue
(d2h_1_oq,
if
 (
@is_arch
(
"wse3"
)) .{ .
color

=

@get_color
(
@bitcast
(
u16
, sys_mod.MEMCPYD2H_1)) }
else
 .{});

@initialize_queue
(C1_iq, .{ .
color

=
 C1 });

@initialize_queue
(C1_oq,
if
 (
@is_arch
(
"wse3"
)) .{ .
color

=
 C1 }
else
 .{});
}

run.py
¶

#!/usr/bin/env cs_python

import

argparse

import

json

import

numpy

as

np

from

cerebras.sdk.sdk_utils

import

memcpy_view
,

input_array_to_u32

from

cerebras.sdk.runtime.sdkruntimepybind

import

SdkRuntime
,

MemcpyDataType

# pylint: disable=no-name-in-module

from

cerebras.sdk.runtime.sdkruntimepybind

import

MemcpyOrder

# pylint: disable=no-name-in-module

parser

=

argparse
.
ArgumentParser
()

parser
.
add_argument
(
'--name'
,

help
=
'the test name'
)

parser
.
add_argument
(
"--cmaddr"
,

help
=
"IP:port for CS system"
)

args

=

parser
.
parse_args
()

dirname

=

args
.
name

# Parse the compile metadata

with

open
(
f
"
{
dirname
}
/out.json"
,

encoding
=
"utf-8"
)

as

json_file
:

compile_data

=

json
.
load
(
json_file
)

params

=

compile_data
[
"params"
]

MEMCPYH2D_DATA_1

=

int
(
params
[
"MEMCPYH2D_DATA_1_ID"
])

MEMCPYD2H_DATA_1

=

int
(
params
[
"MEMCPYD2H_DATA_1_ID"
])

# Size of the input and output tensors; use this value when compiling the

# program, e.g. `cslc --params=size:12 --fabric-dims=8,3 --fabric-offsets=4,1`

size

=

int
(
params
[
"size"
])

print
(
f
"MEMCPYH2D_DATA_1 =
{
MEMCPYH2D_DATA_1
}
"
)

print
(
f
"MEMCPYD2H_DATA_1 =
{
MEMCPYD2H_DATA_1
}
"
)

print
(
f
"size =
{
size
}
"
)

memcpy_dtype

=

MemcpyDataType
.
MEMCPY_16BIT

runner

=

SdkRuntime
(
dirname
,

cmaddr
=
args
.
cmaddr
)

runner
.
load
()

runner
.
run
()

# Generate a random input tensor of the desired size

input_tensor

=

np
.
random
.
randint
(
256
,

size
=
size
,

dtype
=
np
.
int16
)

print
(
"step 1: streaming H2D"
)

# The type of input_tensor is int16, so we need to extend to 32-bit for memcpy H2D

input_tensor_u32

=

input_array_to_u32
(
input_tensor
,

1
,

size
)

runner
.
memcpy_h2d
(
MEMCPYH2D_DATA_1
,

input_tensor_u32
,

0
,

0
,

1
,

1
,

size
,
 \

streaming
=
True
,

data_type
=
memcpy_dtype
,

order
=
MemcpyOrder
.
COL_MAJOR
,

nonblock
=
True
)

print
(
"step 2: streaming D2H"
)

# The memcpy D2H buffer must be 32-bit

output_tensor_u32

=

np
.
zeros
(
size
,

np
.
uint32
)

runner
.
memcpy_d2h
(
output_tensor_u32
,

MEMCPYD2H_DATA_1
,

0
,

0
,

1
,

1
,

size
,
 \

streaming
=
True
,

data_type
=
memcpy_dtype
,

order
=
MemcpyOrder
.
COL_MAJOR
,

nonblock
=
False
)

# remove upper 16-bit of each u32

result_tensor

=

memcpy_view
(
output_tensor_u32
,

np
.
dtype
(
np
.
int16
))

runner
.
stop
()

np
.
testing
.
assert_equal
(
result_tensor
,

input_tensor

+

1
)

print
(
"SUCCESS!"
)

commands.sh
¶

#!/usr/bin/env bash

set
 -e

cslc --arch
=
wse3 ./layout.csl --fabric-dims
=
8
,3
\

--fabric-offsets
=
4
,1 --params
=
size:32 -o out
\

--params
=
MEMCPYH2D_DATA_1_ID:0
\

--params
=
MEMCPYD2H_DATA_1_ID:1
\

--memcpy --channels
=
1
 --width-west-buf
=
0
 --width-east-buf
=
0

cs_python run.py --name out
