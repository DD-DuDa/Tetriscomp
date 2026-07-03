# SDK Documentation (2.10.0)

- Source: https://sdk.cerebras.net/csl/comptime-struct-migration
- Assigned Skill: cerebras-sdk-guides
- Scraped At: 2026-04-27T10:01:33.361199+00:00

## Content

.rst

.pdf

 Contents

Migrating from comptime_struct and @concat_structs

 Contents

Migrating from
comptime_struct
 and
@concat_structs
¶

Note

The
comptime_struct
 type and the
@concat_structs
 builtin were removed in
SDK 2.10.0 (see
Version 2.10.0
). This guide explains how to migrate existing code
to use named
struct
 types instead.

For a full reference on struct types in CSL, see
Type System in CSL
.

Replacing
comptime_struct
 with
struct
¶

As a consequence of the removal of
comptime_struct
,
@concat_structs
 can
no longer be used.

Before (removed):

// Error: `comptime_struct` is no longer supported in CSL

const
 structA: comptime_struct;

const
 structB: comptime_struct;

const
 structC
=

@concat_structs
(structA, structB);

After:

CSL now requires
struct
 types to be declared explicitly. These can be used at both
compile time and runtime. The following code serves the equivalent function to the
above example:

const
 structA
=
 struct {...};

const
 structB
=
 struct {...};

const
 structC
=
 struct {
   a: structA,
   b: structB,
};

Partial initialization
¶

Another key difference between
comptime_struct
 and
struct
 is that
all fields must be declared and set. No partial initialization can be done,
sometimes requiring the use of temporary placeholders.

Before (removed):

var
 mystruct: comptime_struct
=
 .{ .foo
=

true
 };
mystruct
=

@concat_struct
(mystruct, .{ .bar
=

42
 });

After:

const
 mystruct_t
=
 struct {
    foo:
bool
,
    bar:
u16
,
};

var
 mystruct: mystruct_t
=
 .{
    .foo
=

true
,
    .bar
=

0
,
// Temporary placeholder value

};
mystruct.bar
=

42
;

Parameterized structs
¶

Sometimes, the members of a given
struct
 need to vary based on compile-time
parameters or constants. This can be achieved by writing a comptime function that
returns a
type
. The returned type is a
struct
 whose fields depend on the
arguments passed to the function.

For example, a function that returns a point type whose coordinate type depends
on the scale type requested:

// Functions returning a type must have comptime arguments only.

fn
 point_type(
comptime
 scalar_type:
type
)
type
 {

return
 struct {
        x: scalar_type,
        y: scalar_type,
    };
}

fn
 make_point(x_val: anytype) point_type(
@type_of
(x_val)) {

return
 .{ .x
=
 x_val, .y
=

0
 };
}

See also the
parameterized struct types example

in the Language Guide for additional patterns.
