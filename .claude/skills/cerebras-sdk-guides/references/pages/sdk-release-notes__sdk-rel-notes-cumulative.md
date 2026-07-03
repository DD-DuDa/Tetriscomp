# SDK Documentation (2.10.0)

- Source: https://sdk.cerebras.net/sdk-release-notes/sdk-rel-notes-cumulative
- Assigned Skill: cerebras-sdk-guides
- Scraped At: 2026-04-27T10:01:33.361199+00:00

## Content

.rst

.pdf

 Contents

SDK Release Notes

 Contents

SDK Release Notes
¶

The following are the release notes for the Cerebras SDK.

Version 2.10.0
¶

Released 15 March 2026

Note

The SDK version numbering scheme has been updated to match the Cerebras ML Software release
numbering scheme. SDK 2.10 is the SDK version following 1.4.0, and has been tested for
functionality with the Cerebras Wafer-Scale Cluster appliance running Cerebras ML Software
2.10.

New features and enhancements
¶

CSL language and compiler enhancements:

Introduces
anyopaque
 type, representing a value whose size and representation is unknown.
Mostly useful to describe type-erased pointers:
*anyopaque
 is analogous to C’s

void*
.

Introduces arbitrary-width integers.
iN
 and
uN
 describe a signed or unsigned integer
of
N
 bits, where
N
 is any nonnegative integer: e.g.,
u3
,
i4
,
u1
,
i0
,

u128
.
Only integer types with bit widths of 16 or 32 are ABI-sized.
Non-ABI-sized integer types cannot be used as task parameters, and certain hardware-specific
operations (such as DSD builtins) may require ABI-sized types.

Introduces
packed

struct
. Fields are arranged as a sequence of bits with no gaps in
between. All fields must have defined bit width. For example:

const
 some_struct
=
 packed struct {
  x:
i16
,
  y:
f32
,
};

Introduces union types. Untagged unions (analogous to
union
 in C) are supported. Unions
may be
packed
, analogous to structs. For example:

const
 my_union
=
 packed union {
  full :
u16
,
  bits: packed struct {
    low:
u8
,
    high:
u8
,
  }
};

Introduces integer and float widening coercions. Coercions among fixed-width integer types
are now supported if the destination type can represent all possible values of the source
type. Likewise for fixed-width float types. For example:

var
 medium:
i16

=

42
;

var
 large:
i32

=
 small;
// OK: i16 can be widened to i32

var
 small:
i8

=
 medium;
// ERROR: i8 is smaller than i16

Introduces coercion of anonymous structs to named struct types. For example:

const
 Point
=
 struct {
  x:
i32
,
  y:
i32
,
};

var
 p: Point
=
 .{.x
=

0
, .y
=

0
};

Introduces
*T
 to
*[1]T
 coercion and
*[N]T
 to
[*]T
 in peer type resolution.
The type
*T
 will now automatically coerce to
*[1]T
, and the type
*[N]T

will now automatically coerce to
[*]T
.

Introduces
sr
 type representing stride registers, and the
@get_sr
 builtin.

Introduces
@load_to_dsr_xdsr_sr
 builtin, used to load
mem4d_dsd
 values to explicit
DSRs, XDSRs, and SRs.
@load_to_dsr
 with just a
mem4d_dsd
 is no longer allowed;
an XDSR and SR must also be allocated using
@load_to_dsr_xdsr_sr
. For example:

const
 dsr
=

@get_dsr
(dsr_dest,
0
);

const
 xdsr
=

@get_xdsr
(
1
);

const
 sr1
=

@get_sr
(
0
);

const
 sr2
=

@get_sr
(
1
);

const
 sr3
=

@get_sr
(
2
);

var
 dsd: mem4d_dsd;

task
 foo()
void
 {

@load_to_dsr_xdsr_sr
(dsr, xdsr, .{sr1, sr2, sr3}, dsd);
}

Introduces FIFO full and empty actions via new
.full_action
 (WSE-3 only) and

.empty_action
 fields of the
@allocate_fifo
 config struct. These are actions taken
when a push occurs on a full FIFO or a pop occurs from an empty FIFO, respectively.
Accepts options
test_or_suspend
,
terminate
,
suspend
 (WSE-3 only), and
fault

(WSE-3 only). If omitted,
test_or_suspend
 is the default. For example:

var
 fifo_buffer
=

@zeros
(
[
32
]
i16
);

const
 fifo
=

@allocate_fifo
(
  fifo_buffer,
  .{ .empty_action
=
 .{ .terminate
=

true
 },
     .full_action
=
 .{ .fault
=

true
 } }
);

Introduces task rotation via
@bind_rotating_tasks
. For example:

const
 iq
=

@get_input_queue
(
0
);

const
 main_id
=

@get_data_task_id
(iq);

task
 main(data:
u32
)
void
 {}

task
 alt()
void
 {}

comptime
 {

@bind_rotating_tasks
(main, alt, main_id, .{.limit
=

10
});

@initialize_queue
(iq, .{.
color

=
 c});

@set_control_task_table
();
}

Introduces
src0
 DSRs as operands of 1-source builtins on WSE-3.

Introduces support for additional DSD builtin operand combinations on WSE-3, including

dsr_src0,

scalar,

dsr_src0
. Additionally, removes the restriction that
dsr_dest
 and

dsr_src0
 operands must have the same number.

DSR, XDSR, and SR values now support
==
 /
!=
 comparison.

@get_int
 now supports DSR, XDSR, and SR values.

==
 and
!=
 can now compare
type
. The
@is_same_type
 builtin is now deprecated.

DSD builtins are now restricted to no more than one
fabin_dsd
 operand on WSE-3,
properly reflecting the WSE-3 architectural restriction.

Introduces dense mode support for queues on WSE-3.
See
@initialize_queue
.

Introduces support for
circbuf_dsd
. Currently only supported at comptime and must be
manually loaded to DSR+XDSR using
@load_to_dsr_xdsr
.

const
 circbuf
=

@get_dsd
(circbuf_dsd, .{.base_address
=

&
B,
                                        .extent
=
 A_size,
                                        .wraparound
=

5
});

const
 src1
=

@get_dsr
(dsr_src1,
2
);

const
 xdsr_id
=

@get_xdsr
(
3
);

comptime
 {

@load_to_dsr_xdsr
(src1, xdsr_id, circbuf);
}

Wraparound can be inferred from size of
base_address
 if it is an array.

Introduces support for
linksection
 on functions. For example:

export
fn
 has_special_section() linksection(
"dcache_sect"
)
void
 {
  gv
=

42
;
}

Changed default SIMD setting on WSE-2 to
simd_32
. Changed behavior of SIMD settings on
WSE-3: the valid options are now
simd_off
 and
simd_max
 (default).

Trailing comma is now allowed in enum members.

Change to export compatibility of integers and enums: only export compatible when ABI-sized
(16 or 32 bits). Removes export compatibility for
i8
,
u8
,
i64
,
u64
.

Default
--max-inlined-iterations
 limit is increased.

Improved pointer representation consistency: values of pointer type are now always encoded
as byte addresses.

CSL library enhancements:

Introduces
<data_utils>
 library, providing utility functions
lo16
,
hi16
,

lo32
, and
hi32
.

Introduces
<string>
 library, providing
comptime_int_to_string
 and
fmt
 functions.

Introduces
<types>
 library, providing type introspection functions such as

is_unsigned_int
,
is_signed_int
,
is_float
,
is_numeric
,
word_size_of
,

byte_size_of
,
bit_size_of
,
is_dsd
,
is_dsr
, and more.

Introduces
math.subsat
 for saturating subtraction, with
f16
,
f32
, and generic
variants.

Introduces
tile_config.filters
 functions for half-wavelets. Only supported on WSE-3.

SdkRuntime
 host runtime enhancements:

Introduces
cslc_prefix
 option in
SdkLayout
.

Introduces
f16_type
 option in
SdkLayout.compile
 to specify the 16-bit floating point
format (
F16
,
BF16
, or
CB16
).

Introduces
libs
 option in
SdkLayout.compile
 to specify additional library search
paths for the compiler.

Example programs:

Introduces a new tutorial example to demonstrate reusing output queues on WSE-3 with

@queue_flush
. See
Topic 16: Reusing Output Queues on WSE-3
.

Resolved issues
¶

Instruction traces in the SDK GUI are now supported on WSE-3.

Fixes possible read-after-write hazard in
tile_config.teardown.exit()
.

Fixes bug in which a runtime call to a function could cause incorrect evaluation of comptime
calls to the same function.

Fixes bug where a dereference expression passed to
@set_dsd_base_address
 could crash the
compiler.

Fixes bug where DSDs could not be passed as comptime function parameters.

Fixes
SdkLayout
 crash with
simprint
 library.

Fixes exception propagation in
SdkRuntime
 when a simulator failure occurs.

Fixes potential segfault in
SdkLayout
 caused by stale reference to
CodeRegion
.

Known issues
¶

The
25-pt-stencil
 and
histogram-torus

benchmark examples are not supported on WSE-3.

The bandwidth of memory transfers saturates at around 8 IO channels.

Deprecations
¶

fabric_color
 in
@get_dsd
 is no longer required, and emits a deprecation warning
for all
fabin_dsd
 and
fabout_dsd
 on WSE-3, and for
fabin_dsd
 that specify

input_queue
 on WSE-2.

Automatic input queue initialization for
fabin_dsd
 operands of DSD/DSR builtins has been
removed.

The
comptime_struct
 type has been removed.
See
Migrating from comptime_struct and @concat_structs
 for a migration guide.

The
@concat_structs
 builtin has been removed.
See
Migrating from comptime_struct and @concat_structs
 for a migration guide.

Version 1.4.0
¶

Released 26 May 2025

Note

The Cerebras Wafer-Scale Cluster appliance running Cerebras ML Software 2.4 supports SDK 1.3.

See here for SDK 1.3 documentation
.

The Cerebras Wafer-Scale Cluster appliance running Cerebras ML Software 2.5 supports SDK 1.4,
the current version of SDK software.

New features and enhancements
¶

(beta) New
SdkLayout
 program layout specification API:

Introduces a new
SdkLayout
 Python API for specifying program layout. This API
allows the user to define retangular code regions, define color routing and switching,
automatically allocate colors, and automatically route between code regions.

Introduces several example programs demonstrating the use of the
SdkLayout
 API. See the
list of new example programs below.

Introduces new documentation for this API. See
SdkLayout API Reference
.

This API is in
beta
. The
memcpy
 API for data transfers and remote kernel
launches is not currently supported. CSL libraries with their own internal color routing
are not currently supported.

CSL language and compiler enhancements:

@map
 now supports explicit DSR arguments. DSR input arguments must be
dsr_src1
 and
DSR output arguments must be
dsr_dest
. All DSR arguments should be loaded with the

single_step
 property set. For example:

param
 inDSR: dsr_src1;

param
 outDSR: dsr_dest;

task
 foo()
void
 {

// Compute the square-root of each element of `memDSD` and

// send it out to `faboutDSD`.

@load_to_dsr
(inDSR, memDSD, .{.single_step
=

true
});

@load_to_dsr
(outDSR, faboutDSD, .{.single_step
=

true
});

@map
(math_lib.sqrt_f16, inDSR, outDSR);
}

Introduces support for
cb16
 (
cbfloat16
) and
bfloat16
 (bfloat) 16-bit floating
point types, and the associated
@fp16()
 builtin. See
@fp16
 and

Type System in CSL
.
cbfloat16
 is a Cerebras-specific 16-bit floating point format with
a 6-bit exponent and 9-bit explicit mantissa.

On WSE-3, introduces support for microthread priority via the
.priority
 field in

@get_dsd
 for
fabin_dsd
 and
fabout_dsd
, and in
@allocate_fifo
. See

Data Structure Descriptors
.

CSL library enhancements:

Introduces 3D FFT kernel library. See
<fft>
.

Introduces
tile_config.input_queue_status
 and
tile_config.output_queue_status

to query input and output queue full/ empty status registers. See

input_queue_status
 and

output_queue_status
.

SdkRuntime
 host runtime enhancements:

Introduces the
SdkRuntime
 direct link API functions
send
 and
receive
, which are
used to stream data into or out of the wafer via program input and output ports. This API
can be used with
SdkLayout
 as demonstrated in
SdkLayout 4: Host-to-device and device-to-host data streaming
.
See
SdkRuntime API Reference
.

Example programs:

Introduces a series of example programs demonstrating the new
SdkLayout
 API:

SdkLayout 1: Introduction
 introduces the
SdkLayout
 API with a
single-PE program.

SdkLayout 2: Basic routing
 demonstrates color routing with the
SdkLayout

API and automatic color allocation.

SdkLayout 3: Ports and connections
 demonstrates automatic routing between
code regions.

SdkLayout 4: Host-to-device and device-to-host data streaming
 demonstrates the use of the
SdkRuntime

direct link API with
SdkLayout
 to create host-to-device and device-to-host streams.

SdkLayout 5: Generalized matrix-vector multiplication (GEMV)
 implements a full GEMV program with the
SdkLayout

API.

Introduces an example using the 3D FFT kernel library. See
3D FFT
.

Resolved issues
¶

Fixes incorrect parsing of CSL if statements whose body is an assignment without braces
(e.g.
if

(cond)

lhs

=

rhs;
)

On WSE-2, fixes bug in which
@set_color_config
 did not support all 6 available filters.
Previously, only the first four were available.

Fixes potential stall caused by sending many small data transfers via
SdkRuntime
.

Appliance mode compilation via
SdkCompiler
 no longer allocates a system while compiling.

Appliance mode SDK jobs launched via
SdkCompiler
,
SdkLauncher
, or
SdkRuntime
 now
exit gracefully.

Known issues
¶

The
25-pt-stencil
,
histogram-torus
, and
spmv-hypersparse

benchmark examples are not supported on WSE-3.

Instruction traces in the SDK GUI are not supported on WSE-3.

The bandwidth of memory transfers saturates at around 8 IO channels.

Deprecations
¶

In CSL, calling a task is now an error. Only functions may be called. Tasks must
be activated.

In CSL, dereference or access of pointers into config space is now illegal.
The
@get_config
 and
@set_config
 builtins should be used instead.

WSE-1 is no longer supported.

Version 1.3.0
¶

Released 13 December 2024

New features and enhancements
¶

CSL language and compiler enhancements:

For DSD definitions, a tensor access expression is now shorthand for a
comptime_struct

with
extent
,
stride
, and
base_address
 fields. DSDs can now also be specified
using these fields directly, for example:

// These two definitions are equivalent:

var
 my_dsd
=

@get_dsd
(mem1d_dsd, .{ .extent
=

10
, .stride
=

2
, .base_address
=

&
my_arr });

var
 my_dsd
=

@get_dsd
(mem1d_dsd, .{ .tensor_access
=
 |i|{
10
}
-
> my_arr
[
2
*
i
]
 });

stride
 is an optional parameter with default value 1.
See
tensor_access
 for more information.

Memory DSD properties can now take runtime values when using the individual field
specification format. However,
mem4d_dsd
 extent and stride must still be comptime known.

Introduces inline functions, which are expanded during semantic analysis.
See
Syntax of CSL
 for more information.

Introduces labeled
break
 and the ability to break values from blocks.
See
Syntax of CSL
 for more information.

Improves performance of CSL’s parser, potentially improving program compile times.

Improves DSR allocation diagnostics when using DSDs. Upon failure to allocate, diagnostics now
contain information about operations that prevent a DSR from being allocated.

CSL library enhancements:

Introduces a
<dsd_ops>
 library which provides wrappers around DSD op builtins that select
an appropriate builtin depending on the underlying data types, enabling more concise and
flexible code when supporting multiple data types.
See
<dsd_ops>
 for more information.

SdkRuntime
 host runtime enhancements:

Introduces a strided version of
memcpy_h2d
 for strided host-to-device data transfers.
See
memcpy_h2d_stride
 in
SdkRuntime API Reference
.

Introduces row and column broadcast variants of
memcpy_h2d
 for host-to-device row and
column broadcasts. See
memcpy_h2d_colbcast
 and
memcpy_h2d_rowbcast
 in

SdkRuntime API Reference
.
Also see the example program
Host-to-Device Broadcast Test
.

Example programs:

Introduces a new example program
Host-to-Device Broadcast Test
 to demonstrate row and
column broadcasts for host-to-device data transfers.

Resolved issues
¶

Fixes an issue in the
<message_passing>
 library where messages were limited to only 16
wavelets. The maximum message size is 32 wavelets.

Fixes bugs in the
<control>
 library in which
encode_payload()
 could index out of bounds,
and not set
NOCE
 bit on unused commands.

Fixes a bug in which sequential
@map
 operations within a function would not be able to reuse
DSRs.

Known issues
¶

The
25-pt-stencil
,
histogram-torus
, and
spmv-hypersparse

benchmark examples are not yet supported on WSE-3.

Instruction traces in the SDK GUI are not yet supported on WSE-3.

The bandwidth of memory transfers saturates at around 8 IO channels.

Version 1.2.0
¶

Released 28 June 2024

Note

The Cerebras Wafer-Scale Cluster appliance running Cerebras ML Software 2.2 supports SDK 1.1.

See here for SDK 1.1 documentation
.

The Cerebras Wafer-Scale Cluster appliance running Cerebras ML Software 2.3 supports SDK 1.2,
the current version of SDK software.

New features and enhancements
¶

CSL language and compiler enhancements:

Introduces
inline

for
-loops, which are unrolled at compile time.
The body of an
inline

for
-loop may assign to a
comptime

variable. For example:

fn
 length(
comptime
 array: anytype)
comptime_int
 {

comptime

var
 result
=

0
;

// This loop will be inlined.

  inline
for
 (array) |v| {
    result
+=

1
;
  }

return
 result;
}

Introduces the
@queue_flush
 and
@set_empty_queue_handler
 builtin
for WSE-3. See
@queue_flush
.

Runtime
on_control
 values in DSD operations are now supported.
For example:

fn
 f(out: fabout_dsd, in: fabin_dsd, act_id: local_task_id)
void
 {

@fmovh
(out, in, .{
         .async
=

true
, .on_control
=
 .{ .activate
=
 act_id }});
}

Improves
void
 type semantics, enabling optionally specified module
parameters and function arguments.

Significantly improves compile times for large programs. Compilation time
for full-wafer programs may be improved as much as 10x.

CSL library enhancements:

Introduces a
<simprint>
 library for runtime debug printing to the
simulator log. See
<simprint>
.

Introduces a
<control>
 library for creating control wavelet payloads.
See
<control>
.

Introduces a
<message_passing>
 library for WSE-3 point-to-point
communication. See
<message_passing>
.

Introduces the
queue_flush
 module within the
<tile_config>
 library
for WSE-3, which can be used for querying when a queue is flushed and to
exit the flushed state.
See
queue_flush
.

Adds WSE-3 support to the
collectives_2d
 library.

SdkRuntime
 host runtime enhancements:

Adds WSE-3 support for
memcpy
 streaming mode.

Example programs:

Reorganizes and updates all tutorial example programs with WSE-3 support.

Introduces two new tutorial examples for switches, demonstrating use of
the
<control>
 library. See
Topic 6: Switches
 and

Topic 7: Switches and Control Entrypoints
.

Introduces a new tutorial example to demonstrate the
<simprint>

library. See
Topic 13: Simprint Library
.

Introduces a new tutorial example to demonstrate color swapping on WSE-2.
See
Topic 14: Color Swap
.

Adds WSE-3 support to the
wide-multiplication
,
residual
,

mandelbrot
,
gemv-collectives_2d
,
gemv-checkerboard-pattern
,

gemm-collectives_2d
,
7pt-stencil-spmv
,
bicgstab
,

conjugateGradient
,
preconditionedConjugateGradient
, and

powerMethod
 benchmark example programs.

Resolved issues
¶

Adds
memcpy
 streaming support for WSE-3.

Adds WSE-3 support for the
<collectives_2d>
 library.

Fixes potential bug in the
<collectives_2d>
 library related to
reconfiguring the library’s colors.

Fixes potential bug in the
<memcpy>
 library related to reconfiguring
the library’s colors.

Known issues
¶

The
25-pt-stencil
,
histogram-torus
, and
spmv-hypersparse

benchmark examples are not yet supported on WSE-3.

The SDK GUI is not yet supported on WSE-3.

The bandwidth of memory transfers saturates at around 8 IO channels.

Deprecations
¶

The deprecated
@get_color_id
 builtin to get the numerical value of a
color is now removed. Use
@get_int
 instead.

Use of
@get_color
 on any ID other than a routable color ID is no longer
supported.

tile_config.reg_ptr
 has been removed. Use
@get_config
 and

@set_config
 for direct manipulation of config space addresses.

Version 1.1.0
¶

Released 10 April 2024

This version of the Cerebras SDK is the first with experimental support
for the WSE-3, the third generation Cerebras architecture.
The WSE-3 is the wafer-scale processor powering the CS-3 Cerebras system.

Note

The Cerebras Wafer-Scale Cluster appliance running Cerebras ML Software 2.0 supports SDK 0.9.

See here for SDK 0.9 documentation
.

The Cerebras Wafer-Scale Cluster appliance running Cerebras ML Software 2.1 supports SDK 1.0.

See here for SDK 1.0 documentation
.

The Cerebras Wafer-Scale Cluster appliance running Cerebras ML Software 2.2 supports SDK 1.1,
the current version of SDK software.

New features and enhancements
¶

CSL language and compiler enhancements:

Introduces initial support for WSE-3.

Introduces
ut_id
 type and
@get_ut_id
 builtin for representing
microthread IDs. This feature is WSE-3 only.

Introduces runtime
@get_config
 and
@set_config
 support.

Introduces
i64
 and
u64
 types, and support in
<math>
,

<debug>
, and
<malloc>
 libraries.
Like
i8
 and
u8
, these types are not allowed in memory DSD tensors
or
@map
, nor as arguments to tasks.

CSL
memcpy
 library enhancements:

memcpy/get_params
 no longer requires specifying a
LAUNCH
 color
for host kernel launch support.

The
@rpc
 builtin is no longer necessary for host kernel launch support.
The RPC server is now created internally.

Other CSL library enhancements:

Introduces
reset_tsc_counter()
 function in
<time>
 library
to clear timestamp counter.

enable_tsc()
 function in
<time>
 library now automatically
clears timestamp counter.

Introduces
color_config
 and
switch_config
 modules within

<tile_config>
 library for target-independent runtime manipulation
of color and switch configurations.

The
<tally>
 library has been updated to support WSE-3.
The library API has been updated to require specification of both
input and output queues. On WSE-2, the two input queus can be the
same as the output queues, but on WSE-3, they must be different.
See
<tally>
.

Example programs:

GEMV tutorials 1 through 8 have been updated to support WSE-2 and WSE-3.

cholesky
,
FFT
,
bandwidth-test
, and
single-tile-matvec

programs have been updated to support WSE-2 and WSE-3.

Introduces example program to demonstrate WSE-3 features for
separation of queue IDs from microthread IDs for asynchronous
operations.
See
Topic 13: WSE-3 Microthreads
.

Documentation improvements:

Introduces documentation on WSE-3-specific builtins
(see
Builtins for WSE-3
).

Introduces documentation on microthread semantics for WSE-3
(see
Microthread IDs
).

Appliance mode enhancements:

Introduces a new
SdkLauncher
 class which allows users to stage data
onto the appliance before running, and run with the same host code
Python script used when running with the Singularity container.
This class is particularly useful when transferring large amounts of
data onto and off of the CS system.
See
Running SDK on a Wafer-Scale Cluster
.

Separates SDK appliance mode functionality into a
cerebras.sdk

Python module.

Deprecations
¶

Deprecated function
teardown.get_color()
 in
<tile_config>
 library
has been removed. Use
teardown.get_task_id()
 instead.

Deprecated
@bind_task
 builtin has been removed.
Use
@bind_control_task
,
@bind_data_task
, or
@bind_local_task

instead.

Deprecated use of color in
@activate
,
.activate
, on-control

.activate
, FIFO
.activate_push
, and FIFO
.activate_pop

is now an error. Use
local_task_id
 instead.

Use of integers as queue IDs is now an error. Use
input_queue_id
 and

output_queue_id
 types instead.

Resolved issues
¶

Fixed bug in which  an
if
 expression assigned to a variable where both
branches’ values are comptime known, but the condition is not,
would crash the compiler.

Fixed bug where
<time>
 library would occasionally incorrectly read
the timestamp counter.

Fixed bug where DSD operations in which the first operand is a 32-bit
scalar could crash at runtime.

Fixed bug where runtime-determined
color
,
input_queue
, or

output_queue
 in
@get_dsd
 config would crash the compiler.

Fixed bug where
.input_queue
 DSD config field would allow

output_queue
 values and vice versa.

The 1D FFT example program now compiles for
Nz

>=

256
.

Known issues
¶

WSE-3 support is currently experimental. Users may encounter bugs while
running WSE-3 programs.

memcpy
 streaming mode is not yet supported on WSE-3.

The
<collectives_2d>
 library is not yet supported on WSE-3.

Only GEMV tutorials 1 through 8 are currently supported on WSE-3.

The SDK GUI is not yet supported on WSE-3.

The bandwidth of memory transfers saturates at around 8 IO channels.

Notes for future releases
¶

Use of
@get_color
 on any ID other than a routable color ID will be
removed in a future release.

Version 1.0.0
¶

Released 13 November 2023

Note

The Cerebras Wafer-Scale Cluster appliance running Cerebras ML Software 2.0 supports SDK 0.9.
For SDK 0.9 documentation,
see here
.

New features and enhancements
¶

CSL language and compiler enhancements:

Introduces the
data_task_id
,
local_task_id
,
and
control_task_id
 types, to explicitly differentiate the three
types of tasks.
Values of these types are created via the new
@get_data_task_id
,

@get_local_task_id
, and
@get_control_task_id
 builtins,
respectively.

@get_data_task_id
 generates a task ID from a routable
color
,
while
@get_local_task_id
 and
@get_control_task_id
 generate
task IDs from an integer within the range of allowed IDs.
See
Task Identifiers and Task Execution
 for more information on the new
task type system.

Introduces the
@bind_data_task
,
@bind_local_task
, and

@bind_control_task
 builtins for binding tasks to the corresponding
task ID type.
Data tasks must take either one or two arguments (corresponding to the
contents of a wavelet’s payload),
and local tasks must take no arguments.

Colors which are used by a
fabin_dsd
 to receive data and are not
explicitly bound to a task no longer need to be blocked at compile time.
The initial state of a
data_task_id
 not explicitly bound to a task
is now blocked.

Introduces the
@get_int
 builtin to return the numerical value of
values of type
data_task_id
,
control_task_id
,
local_task_id
,

color
,
input_queue
, and
output_queue
, as well as values of any

enum
 or integer type.

@get_color_id
 is now deprecated.

@activate
 builtin and
.activate
 field of builtins on DSDs
now take values of type
local_task_id
 as an argument.
Using
@activate
 or the
.activate
 field on a value of type

color
 is now deprecated.

.activate_pop
 and
.activate_push
 fields of FIFOs now take
values of type
local_task_id
 as an argument.
Using these fields on a value of type
color
 is now deprecated.

@block
 and
@unblock
 builtins and
.unblock
 field of builtins
on DSDs now take values of type
local_task_id
 or
data_task_id

as arguments.

The
@rpc
 builtin now takes values of type
data_task_id
.
It no longer accepts values of type
color
.

Introduces the
cslc
 compiler flag
--warnings-as-errors
, to treat
compiler warnings as errors.

cslc
 compiler script which launches container to run
the compiler now reads
CSL_IMPORT_PATH
 environment
variable to search additional paths for
@import_module
.

CSL
memcpy
 library enhancements:

The
memcpy
 library has been rewritten to use the new task ID types.

Other CSL library enhancements:

collectives_2d
 library has been rewritten to use the new task ID
types.

SdkRuntime
 host runtime enhancements:

Introduces new functionality in the
sdk_utils
 module to simplify data
type transformations for
memcpy_h2d()
 and
memcpy_d2h()
 calls.

Introduces new functionality in the
sdk_utils
 module to process
elapsed timestamp data.

Introduces
suppress_simfab_trace
 option in the
SdkRuntime

constructor to suppress generation of
simfab_traces
 files when running.

Example programs:

Example programs have been reorganized, renumbered, and updated.

Introduces three new example programs in the GEMV series, demonstrating
more complex communication patterns.

Introduces a series of pipelining example programs to demonstrate the use
of
memcpy

streaming
 mode to create a computation pipeline on
the WSE.

Documentation improvements:

Introduces new documentation on debugging CSL programs.
See
Debugging Guide
.

Expands installation documentation to include Apptainer for running
the SDK container.
See
Installation and Setup
.

Appliance mode enhancements:

For Cerebras Wafer-Scale Clusters running Cerebras ML Software 2.1, the

SdkCompiler::compile
 function now expects an artifact output path, and
the function returns a compile artifact path instead of an artifact ID.
The compile artifacts are now by default copied back to the user node
when compilation finishes.

Deprecations
¶

Support for
CSELFRunner
 has now been fully removed.
All programs should use the
SdkRuntime
 host runtime.

The
call()
 function in the
SdkRuntime
 Python host API has been
deprecated.
Use
launch()
 instead, which includes argument type checking.

cslc
 no longer accepts
--channels=0
 when compiling, as this
setting corresponded to
CSELFRunner

memcpy
 support.

The
@get_color_id
 and
@bind_task
 builtins have been deprecated.

Using values of type
color
 with the
@activate
 builtin or the

.activate
,
.activate_pop
, and
.activate_push
 fields
has been deprecated.

The
@rpc
 builtin no longer accepts values of type
color
.
Values of type
data_task_id
 must be used instead.

Known issues
¶

The bandwidth of memory transfers saturates at around 8 IO channels.

When a DSD operation uses an explicit
fabin
 DSR, the compiler does not
bind the color to the associated input queue at runtime. Instead, the user
has to bind the color to the input queue explicitly via
@initialize_queue
.
See
pe.csl
 in
3D 7-Point Stencil SpMV
 for an example.

The 1D FFT example program may fail to compile if
Nz

>=

256
,
triggering an internal compiler exception.

Notes for future releases
¶

Using the
@bind_task
 builtin to bind a task to a
color
 is now
deprecated.
This builtin will be removed in a future release.
Use
@bind_data_task
 for wavelet-triggered data tasks,

@bind_local_task
 for self-activated tasks, and

@bind_control_task
 for control wavelet-triggered tasks.

Using the
@get_color_id
 builtin to get the numerical value of a color
is now deprecated.
This builtin will be removed in a future release.
Use
@get_int
 instead.

Using the
@activate
 builtin on a
color
 is now deprecated.
The ability to do this will be removed in a future release.

Version 0.9.0
¶

Released 2 October 2023

New features and enhancements
¶

CSL language and compiler enhancements:

@get_tensor_ptr
 is now legal in code that contains no exported
symbols, and will compile. If
@get_tensor_ptr
 is executed at runtime
when no symbols have been exported, then an
assert(false)
 will be hit.

Introduces
@has_exported_tensors
 builtin, which evaluates to
true

at comptime if the program contains any exported tensors.

Introduces
extern
 keyword. The
extern
 storage class declares that
a symbol for a variable or function is expected to be defined in an

export
 declaration elsewhere.
See
Storage Classes
.

Introduces
export
 keyword. The
export
 storage class defines a
variable or function with a certain name and type, and makes that variable
or function available to other object files that are linked with the
object being compiled.
See
Storage Classes
.

Introduces
linkname
 keyword, which can be used to specify the name of
the ELF symbol corresponding to the variable.
See
Syntax of CSL
.

Introduces support for function pointers. See
Syntax of CSL
.

Introduces new FIFO DSR types
dsr_fifo_dest
 and
dsr_fifo_src
,
which allow FIFOs to be used with explicit DSRs.
See
Data Structure Registers
.

The
bool
 type is no longer allowed with the
@zeros
 builtin.

@constants
 should be used instead to initialize an array with

false
.

Bitwise not operator
~
 is no longer allowed on the
bool
 type.

Logical not operator
!
 is no longer allowed on integer types.

Compiler diagnostics for circular dependencies have been improved.

CSL
memcpy
 library enhancements:

The
memcpy
 framework reserves two DSRs,
dsr_dest

0
 and

dsr_src1

0
, to enable improved performance and reduce resource usage.
The user should avoid using these explicit DSRs.

The
.data_type
 field is no longer needed when importing
memcpy

to support copy mode.

Other CSL library enhancements:

The
collectives_2d
 library has been rewritten to use explicit DSRs,
enabling improved performance and reducing resource usage.
By default, the library uses
dsr_dest
,
dsr_src0
, and
dsr_src1

IDs 1 and 2, for the X and Y dimensions, respectively, but can be
configured to use other IDs when imported.

The input and output queue IDs of
collectives_2d
 are also now
configurable when imported. By default, the X dimension uses queues

2
 and
4
, and the Y dimension uses queues
3
 and
5
.

The
tile_config
 library contains a new
exceptions
 submodule,
which can be used to unmask exceptions.
See
<tile_config>
.

SdkRuntime
 host runtime additions:

Introduces an
sdk_utils
 library which includes utility functions to
prepare data sent with
memcpy_h2d

and process data received from
memcpy_d2h
.
See
SdkRuntime API Reference
.

Example programs additions:

Adds
SdkRuntime
 versions of
gemv-checkerboard-pattern
 and

gemv-collectives
, which implement two different approaches for
computing GEMV. See
GEMV with Checkerboard Pattern
 and

GEMV with Collective Communications
.

Adds
SdkRuntime
 version of
cholesky
, which computes the Cholesky
decomposition of a symmetric positive-definite matrix.
See
Cholesky
.

Adds additional
SdkRuntime
 tutorial example programs, including demos
of sparse tensor operations, switches, filters, FIFOs, and the
@map

builtin.

See the
csl-examples

GitHub repository

for more example programs, including a 1D and 2D FFT,
histogram-torus
,

mandelbrot
, and
wide-multiplication
.

Documentation improvements:

Introduces additional documentation on the
SdkRuntime
 Python
host API, including the new
sdk_utils
 library.
See
SdkRuntime API Reference
.

Resolved issues
¶

Fixes crash when compiling pointer to array of non-scalars.

Fixes crash when compiling pointer coercion from multidimensional array to
1D pointer of unknown size.

Fixes LLVM backend bug which previously produced incorrect addresses in
certain circumstances,
resulting in “Invalid address” errors in the simulator.
This in particular could cause issues with the
collectives_2d
 library.

Fixes behavior of CSL
math
 library’s
isSignaling(x)

for checking if
x
 is a signaling NaN.

Fixes a bug where programs using
collectives_2d
 stall if the width or
height of the core rectangle is greater than 160 PEs.

The simulator can now support programs with height greater than 256 PEs.

csdb
 has been fixed to correctly read core dumps from SDK programs.

Known issues
¶

The Singularity image may fail to work on Debian-based Linux distributions.
The image works best with a Fedora-based distribution such as Red Hat or Rocky.

The bandwidth of memory transfers saturates at around 8 IO channels.

When a DSD operation uses an explicit
fabin
 DSR, the compiler does not
bind the color to the associated input queue at runtime. Instead, the user
has to bind the color to the input queue explicitly via
@initialize_queue
.
See
pe.csl
 in
3D 7-Point Stencil SpMV
 for an example.

Notes for future releases
¶

The
CSELFRunner
 host runtime has been deprecated. It will be completely
removed in a future release.

Version 0.8.0
¶

Released 21 June 2023

New features and enhancements
¶

Introduces support for Cerebras Wafer-Scale Clusters
running in appliance mode.
This support is limited to Python host code using the
SdkRuntime

host runtime, and only one SDK compile or execute job can be
launched at a time, using no more than one Cerebras system.
See
Running SDK on a Wafer-Scale Cluster
.

CSL language and compiler enhancements:

Introduces
@get_output_queue
 builtin for creating output queue
types. Using integers for output queue IDs is now deprecated and
produces a warning.

Introduces additional improvements and enhancements to internal
builtins for supporting remote procedure calls (RPCs).

Introduces improved error handling for type casts using the

@as
 builtin.

@load_to_dsr
 now allow runtime determined colors in the

@activate
 and
@unblock
 fields.

The grammar of
inititialize_queue
 has been updated.
Previously, inititializing a queue with ID
queue_id
 on color

color_id
 took the form
@initialize_queue(queue_id,

color_id);
.
The new syntax is
@initialize_queue(queue_id,

.{.color

=

color_id});
.

CSL
memcpy
 library enhancements:

The
memcpy
 library can now support multiple types in the same kernel.
The user still needs to import
memcpy.csl
 with the
.data_type

=

field.
The semantic meaning of
.data_type
 is to enable copy mode for the
host runtime.

SdkRuntime
 host runtime enhancements:

Introduces a
debug_utils
 library which includes
get_symbol
,

get_symbol_rect
, and
read_trace
, providing parity with

CSELFRunner
’s debug support.
Note that this library is available for simulator runs only.

Introduces a
launch
 function, which features type checking
and a variable number of arguments for kernel launches with the
RPC mechanism.
The legacy
memcpy_launch
 function has been deprecated, and
users should use
launch
 instead.

memcpy_d2h
 and
memcpy_h2d
 now feature dimension and data
type checking for the host tensor.

The bandwidth of D2H transfers is greatly improved for systems running
in weight streaming mode.

Benchmark programs additions:

Adds
spmv-hypersparse
 to demonstrate a hypersparse matrix-vector
multiplication.

Adds
7pt-stencil-spmv
 to demonstrate a sparse matrix-vector product
using a matrix generated by a finite difference seven-point stencil.
See
3D 7-Point Stencil SpMV
.

Adds
bicgstab
,
powerMethod
,
conjugateGradient
, and

preconditionedConjugateGradient
 to demonstrate iterative methods
on a seven-point stencil. See
BiCGSTAB
,

Power Method
,
Conjugate Gradient
,
and
Preconditioned Conjugate Gradient
.

Adds
single-tile-matvec
, which benchmarks the performance of
single-PE matrix-vector products in terms of aggregate wafer
memory bandwidth and FLOPS. See
Single Tile Matvec
.

Documentation improvements:

Introduces new tutorials for
SdkRuntime
 built around computing
a GEMV.

Introduces additional documentation on the
SdkRuntime
 Python
host API. See
SdkRuntime API Reference
.

Resolved issues
¶

When using
SdkRuntime
, a  nonblocking
memcpy_d2h
 before

stop()
 no longer triggers a segmentation fault.

Programs using
SdkRuntime
 now load correctly in the SDK GUI.

Known issues
¶

The bandwidth of memory transfers saturates at around 8 IO channels.

When a DSD operation uses an explicit
fabin
 DSR, the compiler does not
bind the color to the associated input queue at runtime. Instead, the user
has to bind the color to the input queue explicitly via
@initialize_queue
.

Notes for future releases
¶

The
CSELFRunner
 host runtime has been deprecated. It will be completely
removed in a future release.

Version 0.7.0
¶

Released 17 April 2023

New features and enhancements
¶

CSL language and compiler enhancements:

Introduces
@set_teardown_handler
 builtin which virtualizes the
teardown task and allows for separate definitions of teardown
operations for different colors.

Introduces
@rpc
 builtin which automatically generates RPC
interpreter for exported functions. Used with the
call
 host
function added to
SdkRuntime
. Note that exported symbols
may not have struct or enum types, and exported function may
have at most 15 parameters.

Introduces
@get_input_queue
 builtin for creating input queue
types. Using integers for input queue IDs is now deprecated and
produces a warning.

Variables now have a
linksection
 attribute. With the

--link-section-address-bytes
 flag, this allows global variables
to be placed at a specific address.

Introduces
control_transform
 field for DSDs to transform the index
portion of control wavelets.

Introduces
@dfilt
 builtin which instructs an input queue to drop
all data wavelets until a certain number of control wavelets are
encountered.

DSD
.activate
 field now allows a runtime-determined color value.

Deprecated color config syntax has been removed.

Compiler task table packing optimization increases performance
of small tasks.

CSL library enhancements:

tile_config
 library introduces
control_transform
 submodule
to set mask when transforming index portion of control wavelets.

collectives_2d
 library  now uses the virtualized teardown task,
allowing for interoperability with programs that use
memcpy
 and
the
SdkRuntime
 host runtime.

SdkRuntime
 host runtime enhancements:

SdkRuntime
 introduces a
call
 function to greatly simplify
kernel launches with the RPC mechanism. Functions exported in device
code with the
@rpc
 builtin are now directly host-callable.

memcpy
 library now supports 16-bit for copy mode.

memcpy
 library now reserves color 27 to deliver better performance.

Both
copy
 and
streaming
 mode now support 16-bit data. Note that
in
streaming
 mode, the
MemcpyDataType
 parameter in
memcpy_h2d

and
memcpy_d2h
 host calls has no effect, and the user must handle the
data appropriately in the receiving wavelet-triggered task.

The
memcpy_h2d
 and
memcpy_d2h
 host functions take an argument to
specify the packing of the 3D input/output tensor into a 1D array, either
row-major or column-major. The column-major option improves bandwidth of
data transfers when the host data is packed in that order.

The
memcpy_h2d
 and
memcpy_d2h
 host functions have new function
signatures to better handle the increased number of transfer type
arguments. These are passed in a
struct
 in the C++ interface,
or as required
kwargs
 in the Python interface. This
release supports the following options:

DataType
: (new option) 16-bit or 32-bit

Order
: (new option) row-major or column-major

streaming
: true or false

nonblock
: true or false

The runtime can seamlessly aggregate consecutive nonblocking

memcpy_h2d
 calls, improving the bandwidth of bursts of small
transfers.

Benchmark programs additions and enhancements:

Adds
bandwidth-test
 to benchmark data transfer performance
between host and device. See
Bandwidth Test
.

Adds a version of
gemm-collectives_2d
 using
SdkRuntime
,
which showcases the interoperability of the
collectives_2d

library with
memcpy
. See
GEMM with Collective Operations
.

Benchmark programs written with
SdkRuntime
 and using the RPC
mechanism to launch device kernels have been rewritten to use
call

in the host code and the
@rpc
 builtin in the device code, greatly
reducing the complexity of the programs.

Documentation improvements:

Example programs have been reorganized into
CSELFRunner
 and

SdkRuntime
 sections, to clearly differentiate programs by their
host runtime.

Adds appendix to describe SIMD operations on DSDs.
See
SIMD Mode
.

Adds five tutorial example programs using
SdkRuntime
, mirroring
those written to use
CSELFRunner
.

Adds improved documentation on
SdkRuntime
 and its host API.

Resolved issues
¶

Runtime expressions with
comptime
-only types in comparisons no longer
crash the compiler.

comptime
 switch expressions can now switch on
comptime_int
.

Binding more than one task to the same color now produces a compiler error.

Compiler now checks that dimensionality of a tensor access expression
does not exceed max dimensionality of type.

Known issues
¶

Programs using the
SdkRuntime
 host runtime may fail to load in the

sdk-gui
 when invoked with
sdk_debug_shell

visualize
.

The bandwidth of D2H (device to host) memory transfers using
memcpy

are about 7x to 8x slower than H2D (host to device).

The bandwidth of memory transfers saturates at around 8 IO channels.

When a DSD operation uses an explicit
fabin
 DSR, the compiler does not
bind the color to the associated input queue at runtime. Instead, the user
has to bind the color to the input queue explicitly via
@initialize_queue
.

When using
SdkRuntime
, if the last call before
stop()
 is a nonblocking

memcpy_d2h
, then
stop()
 may trigger a segmentation fault.

Notes for future releases
¶

The
CSELFRunner
 runtime will be deprecated in a future release.
Code should be ported to the
SdkRuntime
 runtime.

Using integers for input queue IDs is now deprecated and will be
removed in a future release.

Version 0.6.0
¶

Released 22 December 2022

New features and enhancements
¶

Compile times are improved due to enhanced caching support.

Introduces a new host-side runtime,
SdkRuntime
, with greatly improved
host-to-device and device-to-host data transfer performance.

Supports host-to-device (H2D) copy to a device CSL variable address
(
memcpy_h2d
), device-to-host (D2H) copy from a device CSL variable
address (
memcpy_d2h
), and launch of CSL device kernels
(
memcpy_launch
).

See
Host Runtime and Tensor Streaming
 for more details. For examples using the
new API, see
Residual
 and
25-Point Stencil
.

The legacy runtime,
CSELFRunner
, now supports host-to-device and
device-to-host copy using the memcpy API.

CSL language enhancements:

Support for normal-mode FIFOs.

Introduces explicit DSRs, providing a more efficient way to execute
DSD operations.

Initial RPC (remote procedure call) support, with a mechanism for
host-device communication using shared symbols.

Additional support for DSD-to-scalar operations.

Support for setting task and microthread priority at comptime and runtime.

Improved assertion failure messages in
@comptime_assert
.

The
.unblock
 DSD field can now be used at runtime and comptime.

CSL library enhancements:

Introduces
collectives_2d
 library, which implements MPI-like
communication primitives over rows or columns of PEs.

New generic API for math libraries.

Introduces
directions
 library, which provides utility functions for
manipulating directions.

Adds efficient implementations of
sin_f16
 and
cos_f16
.

Adds
issignaling_f16
 and
issignaling_f32
, which check for
signalling NaN.

A new version of the
memcpy
 library supports copies to/from address,
and updates to support new runtime. See
Residual
 and

25-Point Stencil
 examples.

cs_readelf
 improvements:

Adds
--visualize
 command line option for drawing ASCII art
representation of PE populations. See
--help
 information for details.

All addresses (both command line option inputs and printed outputs) are
now in byte (8-bit) units instead of word (16-bit) units.

New benchmark programs:

Dense Cholesky decomposition.

Hadamard product, demonstrating selective batched execution mode.

GEMV with collective communications, demonstrating the

collectives_2d
 library.

Documentation improvements:

Adds a new introductory tutorials section to provide step-by-step
instruction for learning CSL. See
Tutorials
.

Adds new example demonstrating the use of the
debug
 library for
tracing values at runtime.

Adds sections on generics and DSRs. See
Generics

and
Data Structure Registers
.

Resolved issues
¶

Relative paths are now handled correctly when importing code files as
modules.

Known issues
¶

The copy mode of
memcpy
 only supports 32-bit data. To copy 16-bit data
to the device, streaming mode must be used instead.

If there are two device-to-host (D2H)
memcpy
 calls in a non-blocking
sequence, and the first D2H is non-blocking, then the run can stall,
especially when using back-to-back D2H calls. To avoid this risk, the user
must use blocking D2H calls instead.

Notes for future releases
¶

The
CSELFRunner
 runtime will be deprecated in a future release.
Code should be ported to the
SdkRuntime
 runtime.

Version 0.5.1
¶

Released 27 September 2022

New features and enhancements
¶

An optional new implementation for tensor streaming is available.
The new implementation is described in
Host Runtime and Tensor Streaming
,
along with instructions for porting kernels to use the new implementation.
Two new CSL code examples,
Residual
 and
25-Point Stencil
,
are provided for reference.

The SDK GUI has introduced new features, detailed in
SDK GUI
.
Major new features include:

Updated display of routing.

Addition of instruction tracing in the timeline.

CSL language enhancements:

Runtime support for named struct types.

switch
 support.

comptime
 and
anytype
 function argument support.

comptime_string
 support.

Either color or task can now be used for DSD config operations.

CSL library enhancements:

Initial complex number support.

Runtime support for finding the position of the running PE within the
rectangle.

Version 0.4.0
¶

Released 29 April 2022

New features and enhancements
¶

New CLI tool
csdb
 introduced.
csdb
 currently supports debugging on
hardware and will eventually support simulation debugging.

New CLI tool
cs_readelf
 introduced.

As of 0.3.1, the numbers in the ELF binary names do NOT correspond to PE
coordinates.

To access prior versions of SDK documentation, please email

developer@cerebras.net
.

Known issues
¶

In the SDK GUI timeline view, clicking multiple PEs on the grid in quick
succession may result in a JSON error. To avoid this error, please wait for
the timeline to load before clicking the next PE. If you see this error for
a PE, click a different PE, allow the timeline to load, and then click the
original PE again.

If you launch
csdb
 and type
ctrl+x
, the container will lock up and
prevent further action. If this happens, you must exit and re-launch your
terminal session.

cslc

--help
 returns options for
cslc-driver
, which are very similar
tools, but not exactly the same. Please note that some options listed may not
be available in
cslc
.

Notes for future releases
¶

csdb
 CLIs will replace
sdk_debug_shell
 CLIs in a future release.

sdk_debug_shell
 will be deprecated.

Content under
CSL

Code

Examples
 will be move to the
csl-examples

GitHub repository in a future release. Please let us know if you need access
to this repository by emailing
developer@cerebras.net
.

Version 0.3.1
¶

Released 25 February 2022

New features and enhancements
¶

Compile time is faster now due to caching improvements.

Support for FIFOs is added. See
Data Structure Descriptors
 for documentation and

@allocate_fifo
 in
Builtins
.

See
Topic 9: FIFOs
 for an example showing how to use

@allocate_fifo
.

Support for switching and filtering is added. With this feature, you can
specify the routing configuration for a specific color at a specific
processing element (PE). This can be done in a layout block
(
@set_color_config
) or in a processing element’s top-level
comptime

block (
@set_local_color_config
). See
Builtins
 for
documentation.

See
Topic 6: Switches
 and
Topic 8: Filters

for examples.

Support for microthreads is added. See
Data Structure Descriptors
 for documentation.

Library support is added. See
Libraries
 for a full list of
supported library functions.

Added the following built-ins. See
Builtins
 for a full list
of supported built-ins.

@set_dsd_base_addr

@random16

@is_same_type

@is_comptime

Compile time floating point constants are now automatically type-casted as
needed. So, instead of
@as(f32,

1.0)
 (see
Builtins
) or

@as(f16,

1.0)
, simply write
1.0
.

Runtime floating point constants no longer default to type
f16
 but to

comptime_float
. If you want a runtime variable, you now need to explicitly
specify the desired type of that variable. For example, instead of

var

x

=

0.0;
 (wrong), write
var

x:

f16

=

0.0;
.

Adds support for setting the state of the pseudo-random number generator
(PRNG).

Adds support for using general purpose registers (GPRs) as destination for
DSD operations:

var
 result:
f16

=

1.0
;

const
 buffer
=

[
3
]
f16
 {
100.0
,
250.0
,
349.0
};

task
 fooTask()
void
 {

const
 dsd
=

@get_dsd
(mem1d_dsd, .{ .tensor_access
=
 |i|{
3
}
-
> buffer
[
i
]
 });

@faddh
(
&
result, result, dsd);
}

Asynchronous DSD operations must have at least one fabric DSD operand.
Non-compliant code will now trigger an error message.

Adds support for the dot operator to access members of structs.
Implemented for compile time only.

Colors can now be compared using
==
 and
!=
 operators.

DSD operations, for example,
add16
, now support unsigned integer operands.

A new
--verbose
 compiler flag shows progress.

Requirements and unsupported features
¶

The SDK requires that the

overlay filesystem

functionality is available on your Linux system.

This SDK is supported only on Linux systems.

There are no guarantees for forward- or backward-compatibility for this
release.

The SDK does not support running external Python scripts in the
Singularity container.

The SDK only supports running the versions of packages provided in the
Singularity container.

Resolved issues
¶

Fixes a bug that prevented unit innermost dimension loops in
mem4d_dsds
.

Fixes a bug so that
mem4d_dsds
 is now allowed to set the

wavelet_index_offset
 bit.

Compile time and runtime semantics of
set_dsd_base_addr
 (see

Builtins
) were different. This is fixed and now
they are the same.

Known issues
¶

When using the SDK GUI, via
sdk_debug_shell

visualize

--artifact_dir

command, if the artifacts in the artifact directory change, then the SDK GUI
will continue to show the old artifact data in a cache. To view the new
artifacts, restart the SDK GUI by running the command

sdk_debug_shell

visualize

--artifact_dir
.

When you run the command
sdk_debug_shell

visualize

--artifact_dir
 to
invoke the SDK GUI, you will see the following error message. This message
can be safely ignored.

$ sdk_debug_shell visualize --artifact_dir /cb/cold/user1/sandbox/sdk_tool_rel-0.3.1/residual
WARNING:cerebras.common.decorators:Call to deprecated
function
 EnumFiles
WARNING:root: . is not a valid workdir.
ERROR:root:plan.meta not found
in
 current directory or subdirectories.
ERROR:root:No entries will be displayed.
Click this link to open URL:  http://user1:8000/?session_id
=
12b77f285e
Click this link to open URL:  http://172.xx.51.216:8000/?session_id
=
12b77f285e
Press Ctrl-C to
exit

ERROR:root:Error reading A_1_1.elf
ERROR:root:Error reading A_0_1.elf
ERROR:root:Error reading A_1_0.elf
ERROR:root:Error reading A_0_0.elf

The SDK GUI currently displays the color values only in the range of 0-14
inclusive.

Version 0.2.1
¶

Released 5 November 2021

This release adds usability improvements and fixes bugs encountered in the
0.2.0 debug tool CLIs. This release also adds compatibility with the Cerebras
R0.9 Software Release, so the CS system hardware does not require re-imaging
in order to use the SDK.

This SDK is supported only on Linux systems.

There are no guarantees for forward- or backward-compatibility for this
release.

The SDK requires that the

overlay filesystem

functionality is available on your Linux system.

The SDK only supports running the versions of packages provided in the
Singularity container.

If the CSL compiler aborts with the LLVM error message
"PLEASE

submit

a

bug

report

to

https://bugs.llvm.org/

and

include

the

crash

backtrace,

preprocessed

source,

and

associated

run

script."
 then do not report to llvm.org but
instead report the problem to Cerebras.

The visualizer tool will not display single-ended routes, i.e., routes where
PE A transmits to PE B, but PE B is missing a receiving route, and vice-versa.

CSELFRunner
 supports single-node host only.

We are no longer actively supporting or maintaining the CASM and Spoke
workflow of version 0.1.x. Migration of code to CSL is needed.

The following examples in the
cslang/benchmarks
 directory of the SDK can
be run only in simulation, and not on the CS system:

cslang/benchmarks/FFT

cslang/benchmarks/wide-multiplication

The
cslang/benchmarks/FFT
 example incorrectly states “SUCCESS” on test
completion.

To run the CSL examples on the CS-1 you must manually emit wavelet to
terminate the runtime.

Version 0.2.0
¶

Released 12 October 2021

This SDK is supported only on Linux systems.

There are no guarantees for forward- or backward-compatibility for this
release.

The SDK 0.2.0 requires that the

overlay filesystem

functionality is available on your Linux system.

Hardware support for SDK 0.2.0 is limited to the CS-1.

The SDK does not support running external Python scripts in the
Singularity container.

The SDK only supports running the versions of packages provided in the
Singularity container.

The SDK 0.2.0 image for the CS-1 is incompatible with the Cerebras Graph
Compiler (CGC) 0.9.0 image. Hence, the SDK system image must be loaded in
order to run CSL programs on the CS-1 system.

The visualizer tool will not display single-ended routes, i.e., routes where
PE A transmits to PE B, but PE B is missing a receiving route, and vice-versa.

CSELFRunner supports single-node host only.

The following examples in the
cslang/benchmarks
 directory of the
SDK can be run only in simulation, and not on the CS system:

cslang/benchmarks/FFT
.

cslang/benchmarks/wide-multiplication
.

Pre-release Version 0.2.0
¶

Released 27 August 2021

Initial availability of the Pre-release 0.2.0 of the SDK documentation.
