# SDK Documentation (2.10.0)

- Source: https://sdk.cerebras.net/csl/code-examples/tutorial-topic-16-queue-flush
- Assigned Skill: cerebras-sdk-guides
- Scraped At: 2026-04-27T10:01:33.361199+00:00

## Content

.rst

.pdf

 Contents

Topic 16: Reusing Output Queues on WSE-3

 Contents

Topic 16: Reusing Output Queues on WSE-3
¶

On WSE-3, each output queue can only bind to a single color. Applications
which, on WSE-2, shared multiple colors on an output queue must be
modified to avoid running out of output queues on WSE-3.

WSE-3 allows the user to repurpose input/output queues with a
different color using
@queue_flush
. This new feature allows reuse of
queues with a reasonable cost.

This example demonstrates how to reuse an output queue in the sender and
an input queue in the receiver on the WSE-3 architecture.

There are two PEs in this example, a sender (queue_flush_sender.csl) on
the left and a receiver (queue_flush_receiver.csl) on the right.
The sender sends two data sets to the receiver via the colors C10 and C12
. Both data sets are handled by the output queue 2.

The output queue must be drained before it can be reused. However, the
termination of a microthread only confirms that it pushed all of its data
into the output queue; the queue may not be empty yet. WSE-3 provides an
event handling mechanism to notify the user when an output queue becomes
empty.

Here is how it works:
The user calls
@queue_flush(oq)
 after the microthread operation, for
example,
@mov32
 which sends the data to an output queue
oq
. When

oq
 becomes empty, WSE-3 will trigger the special teardown task 29,
the same way a teardown wavelet does. The user has to register a handler,

foo
, which can repurpose the output queue.

@set_empty_queue_handler(foo,

oq)
 binds the handler
foo
 to the
output queue
oq
. The handler
foo
 does three things:
1. Reconfigure the color field of the output queue
oq
 by
output_queue_config.encode_output_queue(oq, new color).
2. Execute logic that should follow reconfiguration of the output queue.
In the example, this is
@activate(transmit2_id)
, which allows the
next data to be processed.
3. Clear the state of queue flush.

queue_flush.exit(oq)
 is necessary, otherwise subsequent invocations
of the special teardown task 29 will call
foo
 again.

The sender has the following sequence:
1. Send data1 to output queue
oq
 which binds to color
out_color1
.
2.
done_transmit1
 is triggered when data1 has been sent to
oq
.
3.
done_transmit1
 reconfigures the color field of
oq
 and calls

@queue_flush(oq)
.
4. Whole data1 has been moved to the router, i.e.
oq
 becomes empty.
5. The special teardown task 29 is triggered because
oq
 is empty.
6. The special teardown task 29 calls the handler foo().
7.
foo()
 binds
oq
 with
out_color2
.
8.
foo()
 activates
transmit2_id
 to send data2.
9.
foo()
 calls
queue_flush.exit()
 to clear the queue flush state.
10.
transmit2_id
 is triggered to send out data2.
11.
transmit2_id
 send data2 to output queue
oq
 which binds to
color
out_color2
.
12.
exit()
 is triggered when data2 has been pushed into
oq
.

Be careful not to issue
@queue_flush(oq)
 before
@mov32
, otherwise
it is possible that WSE-3 immediately triggers the special teardown task
29 when
oq
 is empty because
@mov32
 is not started yet to push
data into
oq
.

The receiver receives two data sets from C10 and C12 sequentially. It is
safe to reuse the input queue. We just reconfigure input queue
iq

after data1 is received into
result1
. Then we can continue receiving
data2 on the same
iq
. This example does not need to use

@queue_flush(iq)
 because
iq
 is already empty at the time

done_receive1
 is triggered.
done_receive1
 can reconfigure
iq

safely.

The receiver introduces a dummy loop to increase the delay between

@queue_flush(oq)
 and the special teardown task 29 so we can confirm
if the teardown task was triggered by emptiness of
oq
 easily.

On WSE-2, multiple colors can share the same output queue without needing
to call the
@queue_flush
 builtin (unlike on WSE-3). This is because,
on WSE-2, an output queue is not bound to a specific color, so data from
multiple colors can be sent to the same queue. Accordingly,
queue_flush_sender.csl omits
@queue_flush(oq)
 when targeting WSE-2.
Likewise, queue_flush_receiver.csl does not call
@queue_flush
: it
relies on the fact that the input queue is empty when the microthread
finishes, making it safe to reconfigure the input queue.

The filter enabled on color C12 accepts only the first two wavelets of
each 15-wavelet sequence. This behavior is enabled by passing the

filter_enable
 parameter to encode_input_queue. As a result,
queue_flush_receiver.csl modifies only the first two entries of
result2
.

queue_flush_layout.csl
¶

const
 memcpy
=

@import_module
(
"<memcpy/get_params>"
, .{
  .width
=

2
,
  .height
=

1
,
});

layout
 {

@set_rectangle
(
2
,
1
);

const
 memcpy_params_0
=
 memcpy.get_params(
0
);

const
 memcpy_params_1
=
 memcpy.get_params(
1
);

@set_tile_code
(
0
,
0
,
"queue_flush_sender.csl"
, .{ .memcpy_params
=
 memcpy_params_0 });

@set_tile_code
(
1
,
0
,
"queue_flush_receiver.csl"
, .{ .memcpy_params
=
 memcpy_params_1 });

@export_name
(
"launch"
,
fn
()
void
);

@export_name
(
"result1"
,
[*]
u32
,
true
);

@export_name
(
"result2"
,
[*]
u32
,
true
);
}

queue_flush_receiver.csl
¶

param
 memcpy_params;

// memcpy reserves input/output queue 0 and 1

const
 sys_mod
=

@import_module
(
"<memcpy/memcpy>"
, memcpy_params);

const
 tile_config
=

@import_module
(
"<tile_config>"
);

const
 input_queue_config
=
 tile_config.input_queue_config;

const
 size
=

15
;

const
 filter_size
=

2
;
export
var
 result1:
[
size
]
u32
;
export
var
 result2:
[
size
]
u32
;

var
 result1_ptr:
[*]
u32

=

&
result1;

var
 result2_ptr:
[*]
u32

=

&
result2;

const
 delay_size
=

500
;
export
var
 dummy:
[
delay_size
]
u16
;

const
 memDSD
=

@get_dsd
(mem1d_dsd, .{.tensor_access
=
 |i|{size}
-
> result1
[
i
]
});

const
 input_queue_id:
i16

=

2
;

const
 in_color1
=

@get_color
(
10
);

const
 iq
=

@get_input_queue
(input_queue_id);

const
 fabin1
=

@get_dsd
(fabin_dsd, .{.extent
=
 size, .input_queue
=
 iq});

const
 in_color2
=

@get_color
(
12
);

const
 fabin2
=

@get_dsd
(fabin_dsd, .{.extent
=
 filter_size, .input_queue
=
 iq});

const
 main_id
=

@get_local_task_id
(
8
);

const
 exit_id
=

@get_local_task_id
(
9
);

// avoid using C10 and C12 for local task because they are used in routing colors

const
 receive1_id
=

@get_local_task_id
(
13
);

const
 receive2_id
=

@get_local_task_id
(
14
);

const
 done_receive1_id
=

@get_local_task_id
(
15
);

const
 task_id
=

if
 (
@is_arch
(
"wse3"
))
@get_data_task_id
(iq)
else

@get_data_task_id
(in_color1);

task
 main()
void
 {

// dummy loop to increase the delay between @queue_flush(oq) and T29

// in queue_flush_sender.csl

var
 idx:
u16

=

0
;

while
 (idx < delay_size) : (idx
+=

1
) {
    dummy
[
idx
]

=
 idx;
  }

@activate
(receive1_id);
}

task
 receive1()
void
 {

// activate done_receive1 to repurpose `iq` after data1 is received.

@mov32
(memDSD, fabin1, .{.async
=

true
, .activate
=
 done_receive1});
}

// The task `receive1` has finished the microthread so the `iq` is empty.

// It is safe to repurpose `iq` with `in_color2`.

task
 done_receive1()
void
 {

// bind the color `in_color2` to the input queue `iq`.

// `in_color2` binds to a filter, so filter_enable = true.

  input_queue_config.encode_input_queue(input_queue_id,
@get_int
(in_color2),
true
);

// process next data in `in_color2`.

@activate
(receive2_id);
}

task
 receive2()
void
 {

const
 dest
=

@set_dsd_base_addr
(memDSD, result2);

@mov32
(dest, fabin2, .{.async
=

true
, .activate
=
 exit});
}

// RPC: receive two data sets from the sender via different colors

// 1. data1 from in_color1(C10)

// 2. data2 from in_color2(C12)

// The input queue `iq` is reconfigured after data1 has been received via in_color1.

// After that, data2 is received on `iq` with in_color2.

fn
 launch()
void
 {

@activate
(main_id);
}

task
 exit()
void
 {

// the user must unblock cmd color for every PE

  sys_mod.unblock_cmd_stream();
}

comptime
 {

// input queue 2 is shared by in_color1 and in_color2.

// A microthread is used to read input queue 2, so

// the initial state of input queue 2 is blocked.

@block
(task_id);

@bind_local_task
(main, main_id);

@bind_local_task
(exit, exit_id);

@bind_local_task
(receive1, receive1_id);

@bind_local_task
(done_receive1, done_receive1_id);

@bind_local_task
(receive2, receive2_id);

@initialize_queue
(iq, .{.
color

=
 in_color1});

@set_local_color_config
(in_color1, .{.routes
=
 .{.rx
=
 .{
WEST
}, .tx
=
 .{
RAMP
}}});

// only accept [0,1] wavelets among `size` wavelets

@set_local_color_config
(in_color2, .{
    .routes
=
 .{.rx
=
 .{
WEST
}, .tx
=
 .{
RAMP
}},
    .filter
=
 .{
            .kind
=
 .{ .counter
=

true
 },
            .count_data
=

true
,
            .count_control
=

false
,
            .init_counter
=

0
,
            .max_counter
=
 filter_size
-
1
,
            .limit1
=
 (size
-

1
)
        }
  });
}

comptime
 {

@export_symbol
(launch);

@export_symbol
(result1_ptr,
"result1"
);

@export_symbol
(result2_ptr,
"result2"
);
}

queue_flush_sender.csl
¶

param
 memcpy_params;

// memcpy reserves input/output queue 0 and 1

const
 sys_mod
=

@import_module
(
"<memcpy/memcpy>"
, memcpy_params);

const
 tile_config
=

@import_module
(
"<tile_config>"
);

const
 queue_flush
=
 tile_config.queue_flush;

const
 output_queue_config
=
 tile_config.output_queue_config;

const
 size
=

15
;

var
 data1
=

@constants
(
[
size
]
u32
,
42
);

var
 data2
=

@constants
(
[
size
]
u32
,
43
);

const
 memDSD
=

@get_dsd
(mem1d_dsd, .{.tensor_access
=
 |i|{size}
-
> data1
[
i
]
});

export
var
 result1:
[
size
]
u32
;
export
var
 result2:
[
size
]
u32
;

var
 result1_ptr:
[*]
u32

=

&
result1;

var
 result2_ptr:
[*]
u32

=

&
result2;

const
 output_queue_id:
i16

=

2
;

const
 oq
=

@get_output_queue
(output_queue_id);

const
 out_color1
=

@get_color
(
10
);

const
 out_color2
=

@get_color
(
12
);

// WSE-2 does not bind a color to an output queue.

// Instead, DSD determines the color.

// On the contrary, WSE-3 binds a color to an output queue, so

// fabout_1 and fabout_2 are the same.

// When fabout_2 is used, oq has reset its color field to out_color2.

const
 fabout_1
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
 size, .output_queue
=
 oq
                     }
else
 .{
                       .fabric_color
=
 out_color1,
                       .extent
=
 size, .output_queue
=
 oq
                     });

const
 fabout_2
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
 size, .output_queue
=
 oq
                     }
else
 .{
                       .fabric_color
=
 out_color2,
                       .extent
=
 size, .output_queue
=
 oq
                     });

// the runtime color binding to oq

var
 switch_color:
i16

=

0
;

// `foo` is the teardown handler of output queue `oq`.

// The purpose of `foo` is to reconfigure the color field of `oq`.

fn
 foo()
void
 {

// WSE-2 does not support qflush

if
 (
@is_arch
(
"wse3"
)) {

// The encoding offset of the queue's color is 4.

// @set_config(0x7b82, @get_int(out_color2) << 4);

    output_queue_config.encode_output_queue(output_queue_id, switch_color);

@activate
(transmit2_id);

// WARNING: necessary, otherwise subsequent T29 can still see it.

    queue_flush.exit(oq);
  }
}

// Normally, we could use the '.activate' field to synchronize

// the re-configuration of the output queue 'oq'. However, this

// will trigger a simulator assertion because 'oq' will not be

// empty when the DSD operation is done. The only way to

// re-configure 'oq' in this case is with '@queue_flush'.

const
 transmit1_id
=

@get_local_task_id
(
8
);

task
 transmit1()
void
 {

if
 (
@is_arch
(
"wse3"
)) {

@mov32
(fabout_1, memDSD, .{.async
=

true
, .activate
=
 done_transmit1});
  }
else
{

// WSE-2 does not need to reconfigure the output queue.

// It can trigger transmit2 to send `data2`.

@mov32
(fabout_1, memDSD, .{.async
=

true
, .activate
=
 transmit2});
  }
}

const
 done_transmit1_id
=

@get_local_task_id
(
9
);

// transmit1 has pushed data1 into `oq` so we can repurpose oq.

// `oq` is usually non-empty at the time the microthread terminates.

task
 done_transmit1()
void
 {

// WSE-2 does not support qflush

if
 (
@is_arch
(
"wse3"
)) {

// bind out_color2 to oq

    switch_color
=

@get_int
(out_color2);

// queue_flush() triggers T29 when oq becomes empty, i.e. data1 has been sent out.

// T29 calls the handler, foo(), to activate transmit2_id.

@queue_flush
(oq);
  }
}

const
 transmit2_id
=

@get_local_task_id
(
11
);

task
 transmit2()
void
 {

const
 newMemDSD
=

@set_dsd_base_addr
(memDSD, data2);

@mov32
(fabout_2, newMemDSD, .{.async
=

true
, .activate
=
 exit});
}

// RPC: send two data sets, data1 and data2, via different colors but with the same output queue.

// Here is the sequence on WSE-3:

// 1. send data1 to output queue `oq` which binds to color `out_color1`.

// 2. `done_transmit1` is triggered when data1 has been sent to `oq`.

// 3. `done_transmit1` reconfigures the color field of `oq` and calls `@queue_flush(oq)`.

// 4. whole data1 has been moved out to the router, i.e. `oq` becomes empty.

// 5. T29 is triggered because `oq` is empty.

// 6. T29 calls the handler `foo()`.

// 7. foo() binds `oq` with `out_color2`.

// 8. foo() activates transmit2_id to send data2.

// 9. foo() calls queue_flush.exit() to clear the queue flush state.

// 10. transmit2_id is triggered to send out data2.

// 11. transmit2_id send data2 to output queue `oq` which binds to color `out_color2`.

// 12. exit() is triggered when data2 has been pushed into `oq`.

//

// WARNING: now `oq` binds to `out_color2`.

// If the user wants to switch it back to `out_color1`, queue_flush(oq) must be called again.

// In addition, the user needs to set `switch_color` back to `out_color1` before calling to

// queue_flush(oq).

//

// WARNING: if the user wants to switch the color back to `out_color1`, it has to be done

// before calling to sys_mod.unblock_cmd_stream(). Otherwise it is possible that next RPC

// command could start before `oq` switches the color back to `out_color1`.

//

// WSE-2 can map multiple colors to the same output queue, so no need to reconfigure

// the output queue.

// Here is the sequence on WSE-2:

// 1. send data1 to output queue oq via out_color1.

// 2. transmit2 is triggered when data1 has been sent to oq.

// 3. transmit2_id is triggered to send out data2.

// 4. transmit2_id send data2 to output queue oq via color out_color2.

// 5. exit() is triggered when data2 has been pushed into oq.

fn
 launch()
void
 {

@activate
(transmit1_id);
}

const
 exit_id
=

@get_local_task_id
(
17
);

task
 exit()
void
 {

// the user must unblock cmd color for every PE

  sys_mod.unblock_cmd_stream();
}

comptime
 {

@bind_local_task
(transmit1, transmit1_id);

@bind_local_task
(done_transmit1, done_transmit1_id);

@bind_local_task
(transmit2, transmit2_id);

@bind_local_task
(exit, exit_id);

// WSE-2 does not bind an output queue to a color

@initialize_queue
(oq,
if
 (
@is_arch
(
"wse3"
)) .{ .
color

=
 out_color1 }
else
 .{});

// WSE-2 does not support qflush

if
 (
@is_arch
(
"wse3"
)) {

@set_empty_queue_handler
(foo, oq);
  }

const
 R_to_E
=
 .{.rx
=
 .{
RAMP
}, .tx
=
 .{
EAST
}};

@set_local_color_config
(out_color1, .{.routes
=
 R_to_E});

@set_local_color_config
(out_color2, .{.routes
=
 R_to_E});
}

comptime
 {

@export_symbol
(launch);

@export_symbol
(result1_ptr,
"result1"
);

@export_symbol
(result2_ptr,
"result2"
);
}

run.py
¶

#!/usr/bin/env cs_python

import

argparse

import

numpy

as

np

from

cerebras.sdk.runtime.sdkruntimepybind

import

SdkRuntime
,

MemcpyDataType
,

MemcpyOrder

# pylint: disable=no-name-in-module

# Read arguments

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
"the test compile output dir"
)

parser
.
add_argument
(
'--cmaddr'
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

# Construct a runner using SdkRuntime

runner

=

SdkRuntime
(
args
.
name
,

cmaddr
=
args
.
cmaddr
)

sym_launch

=

runner
.
get_id
(
'launch'
)

sym_result1

=

runner
.
get_id
(
'result1'
)

sym_result2

=

runner
.
get_id
(
'result2'
)

print
(
f
"sym_launch =
{
sym_launch
}
"
)

print
(
f
"sym_result1 =
{
sym_result1
}
"
)

print
(
f
"sym_result2 =
{
sym_result2
}
"
)

# Load and run the program

runner
.
load
()

runner
.
run
()

runner
.
launch
(
"launch"
,

nonblock
=
True
)

# Copy result1 and result2 back from PE (1, 0)

# If `queue_flush.exit(oq)` is not called, T29 of mempcy_d2h will trigger `foo`

# and the kernel will stall.

size

=

15

filter_size

=

2

result1

=

np
.
zeros
([
size
],

dtype
=
np
.
uint32
)

runner
.
memcpy_d2h
(
result1
,

sym_result1
,

1
,

0
,

1
,

1
,

size
,

streaming
=
False
,

order
=
MemcpyOrder
.
ROW_MAJOR
,

data_type
=
MemcpyDataType
.
MEMCPY_32BIT
,

nonblock
=
False
)

result2

=

np
.
zeros
([
size
],

dtype
=
np
.
uint32
)

runner
.
memcpy_d2h
(
result2
,

sym_result2
,

1
,

0
,

1
,

1
,

size
,

streaming
=
False
,

order
=
MemcpyOrder
.
ROW_MAJOR
,

data_type
=
MemcpyDataType
.
MEMCPY_32BIT
,

nonblock
=
False
)

# Stop the program

runner
.
stop
()

result1_expected

=

np
.
ones
(
size
,

dtype
=
np
.
uint32
)

*

42

result2_expected

=

np
.
ones
(
size
,

dtype
=
np
.
uint32
)

*

0

result2_expected
[
0
:
filter_size
]

=

43

print
(
f
"result1 =
{
result1
}
"
)

print
(
f
"result2 =
{
result2
}
"
)

np
.
testing
.
assert_allclose
(
result1
,

result1_expected
,

atol
=
0.0
,

rtol
=
0
)

np
.
testing
.
assert_allclose
(
result2
,

result2_expected
,

atol
=
0.0
,

rtol
=
0
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
wse3 ./queue_flush_layout.csl --fabric-dims
=
9
,3
\

--fabric-offsets
=
4
,1 -o out --memcpy --channels
1

cs_python run.py --name out
