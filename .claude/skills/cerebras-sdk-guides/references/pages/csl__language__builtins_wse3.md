# SDK Documentation (2.10.0)

- Source: https://sdk.cerebras.net/csl/language/builtins_wse3
- Assigned Skill: cerebras-sdk-guides
- Scraped At: 2026-04-27T10:01:33.361199+00:00

## Content

.rst

.pdf

 Contents

Builtins for WSE-3

 Contents

Builtins for WSE-3
¶

This section documents CSL builtins that are only supported for WSE-3.

@get_ut_id
¶

Create a value of type
ut_id
 from the provided integer identifier.

Syntax
¶

@get_ut_id
(id);

Where:

id
 is a comptime-known expression of any unsigned integer type,
or a runtime expression of type
u16
.

Semantics
¶

If
id
 is comptime-known, the builtin will only accept integers
in the target architecture’s valid range for microthread IDs.

If
id
 is not comptime-known, its type must be
u16
.
In this case no runtime checks are performed to ensure that
id
 is
within the range of valid microthread IDs.

@queue_flush
¶

Activates the teardown task ID (see

teardown
) once the given queue becomes
empty.

Syntax
¶

@queue_flush
(queue_id);

Where:

queue_id
 is an expression of type
input_queue
 or
output_queue
.

Example
¶

const
 out_q
=

@get_output_queue
(
2
);

const
 fabout
=

@get_dsd
(fabout_dsd, .{..., .output_queue
=
 out_q});

task
 foo()
void
 {

@mov16
(fabout, ..., .{.async
=

true
});

// Will activate the teardown task once 'out_q' is empty.

// Note that 'out_q' may not be empty when the microthread

// above is done.

@queue_flush
(out_q);
}

Semantics
¶

The builtin can only be evaluated at runtime, and therefore it cannot appear
during comptime evaluation or during the evaluation of a top-level comptime
or layout block.

The builtin’s return type is
void
.

Calling the builtin will cause the teardown task to be activated once the
input (or output) queue associated with
queue_id
 becomes empty or is
already empty.

It is guaranteed that if the teardown task is activated because of a call
to
@queue_flush
 then the respective queue will be empty.

From within the teardown task the
queue_flush
 library
(see
queue_flush
)
can be used to check whether the teardown task was activated due to
a call to
queue_flush
 for a given queue or not.

@set_control_task_table
¶

Create a separate control task table.

Syntax
¶

@set_control_task_table
();

@set_control_task_table
(config);

Where:

config
 is a comptime-known (anonymous) struct with the following
optional fields:

instructions

stride

Example
¶

task
 foo()
void
 {}

task
 bar()
void
 {}

comptime
 {

@bind_control_task
(foo,
@get_control_task_id
(
10
));

@bind_local_task
(bar,
@get_local_task_id
(
10
));

// Even though 'foo' and 'bar' have the same IDs they do not

// clash because this call to @set_control_task_table will

// decouple control tasks from data and local tasks. Control

// tasks now have their own separate task table.

@set_control_task_table
(.{.instructions
=

8
, .stride
=

4
});
}

Semantics
¶

The
@set_control_task_table
 builtin will decouple control tasks
from data and local tasks by creating a separate task table that is
dedicated to control tasks.

The builtin can only be called at most once during the evaluation of a
top-level comptime block.

It can have an optional argument that must be a comptime-known struct
with two optional fields:
instructions
 and
stride
.

If
@set_control_task_table
 is called without an argument then the
default values for
instructions
 and
stride
 will be used (see
below).

The
instructions
 field can be used to specify the number of instructions
for each entry point in the new control task table. The number of instructions
must be a comptime-known integer value within the valid set of options which are

2
,
4
 and
8
. The default value is
4
.

The
stride
 field requires a comptime-known integer value that represents the
stride - in number of entry points - per input queue’s local control table index
(see
@initialize_queue
). Its value should be in the
range
[1,

7]
 and the default value is
1
.

@set_empty_queue_handler
¶

Set a function to be the empty queue handler for a given queue.

Syntax
¶

@set_empty_queue_handler
(func, queue_id);

Where:

func
 is the name of a function with no input parameters
and
void
 return type.

queue_id
 is a comptime-known expression of type
input_queue

or
output_queue
.

Example
¶

const
 tile_config
=

@import_module
(
"<tile_config>"
);

fn
 foo()
void
 {

// Reconfiguration of empty queue takes place here.

  ...

// At the end, ensure that the queue flush status register is reset

// to prevent re-entrancy.

  tile_config.queue_flush.exit();
}

const
 in_q
=

@get_input_queue
(
4
);

comptime
 {

// Specifies function 'foo' to be executed when 'in_q' is flushed

// (i.e., becomes empty) after calling '@queue_flush(in_q)'.

@set_empty_queue_handler
(foo, in_q);
}

Semantics
¶

The
@set_empty_queue_handler
 builtin must appear in a top-level

comptime
 block. When
@queue_flush

(see
@queue_flush
) has been called for a qiven
queue (input or output) and the teardown task is activated due to that
queue becoming empty, then the function associated with that queue,
through a call to
@set_empty_queue_handler
, will be executed.

The user is responsible for resetting the status of the queue flush status
register through the
queue_flush
 submodule of the
<tile_config>

library (see
queue_flush
).

Calling
@set_empty_queue_handler
 for the same queue more than once
is not allowed and will result in an error.

If there is at least 1 call to
@set_empty_queue_handler
 in the program
then no task is allowed to be bound to the
teardown task ID
 and vice-versa.
The teardown task ID is the value returned by the CSL standard library through
the teardown API (see
teardown
).

@bind_rotating_tasks
¶

Bind a pair of tasks - a data task
(see
Data Tasks
) and a control task
(see
Control Tasks
) - and enable rotation between those tasks.

Syntax
¶

@bind_rotating_tasks
(main, alt, task_id, config);

Where:

main
 is a data task handler (see
Data Tasks
).

alt
 is a control task handler (see
Control Tasks
).

task_id
 is a comptime-known expression of type
data_task_id
.

config
 is a comptime-known (anonymous) struct with the following
fields:

init
 (optional) is a comptime-known non-negative integer that
may not exceed
limit
.

limit
 (required) is a comptime-known non-negative integer.

Example
¶

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

// Task 'alt' will start after '10' starts of task 'main'.

// Task 'alt' is bound to control task id '0' (see 'semantics' for

// more details).

@bind_rotating_tasks
(main, alt, main_id, .{.limit
=

10
});

// Input queue must be initialized to allow us to bind 'main'

// to 'main_id'.

@initialize_queue
(iq, .{.
color

=
 c});

// Must be called to prevent 'main' and 'alt' from clashing.

@set_control_task_table
();
}

const
 iq1
=

@get_input_queue
(
0
);

const
 main_id1
=

@get_data_task_id
(iq);

task
 main1(data:
u32
)
void
 {}

task
 alt1()
void
 {}

const
 iq2
=

@get_input_queue
(
0
);

const
 main_id2
=

@get_data_task_id
(iq);

task
 main2(data:
u32
)
void
 {}

task
 alt2()
void
 {}

comptime
 {

// Task 'alt1' will start after '4' starts of task 'main'.

// After that, 'alt1' will start after '10' starts of task 'main'.

// Task 'alt' is bound to control task id '0' that is associated with

// input queue 'iq1'.

@bind_rotating_tasks
(main1, alt1, main_id1, .{.init
=

5
, .limit
=

10
});

// Task 'alt' is bound to control task id '0' that is associated with

// input queue 'iq2'.

@bind_rotating_tasks
(main2, alt2, main_id2, .{.limit
=

10
});

// 'iq1' and 'iq2' must have separate control task tables to allow the

// two pairs of rotating tasks to function correctly.

@initialize_queue
(iq1, .{.
color

=
 c1, .ctrl_table_id
=

0
});

@initialize_queue
(iq2, .{.
color

=
 c2, .ctrl_table_id
=

1
});

// This separates the control task table from the data task table

// which will guarantee that alternate tasks will not overlap

// with data tasks.

@set_control_task_table
();
}

Semantics
¶

The
@bind_rotating_tasks
 builtin enables task rotation for a pair of
tasks. Task rotation is a WSE3 hardware feature that allows us to execute
a different task every Nth data task start.

Task
main
 must be a data task (see
Data Tasks
) which means
that it must have input parameters corresponding to input wavelet(s) while
task
alt
 must be a control task (see
Control Tasks
).

WSE3 can only support two concurrent pairs of rotating tasks. Therefore,
the builtin can only be called at most twice during the evaluation of a
top-level comptime block.

When
@bind_rotating_tasks
 is called, then task
main
 gets bound to

task_id
, which must be of type
data_task_id
, while task
alt
 gets
bound to control task id zero. In other words, a call to

@bind_rotating_tasks
 is equivalent to
@bind_data_task(main,

task_id)

(see
@bind_data_task
) and

@bind_control_task(alt,

@get_control_task_id(0))

(see
@bind_control_task
).

Task
alt
 is the same task that would be started if a control wavelet with
control task id zero arrived from the input queue that is associated with

task_id
.

This means that if
@bind_rotating_tasks
 is called more than once, then
the input queue associated with the
task_id
 of each call, must have
its own dedicated control task table
(see
@set_control_task_table
) in order to prevent
multiple control tasks bound to control task id zero from clashing.

Every time task
main
 starts, a counter is compared against

limit
. If the counter equals
limit
 then task
alt
 starts instead
of
main
 and the counter resets to zero.

The initial value of the counter can be optionally specified through the

init
 field. If it is not specified then it defaults to zero.
