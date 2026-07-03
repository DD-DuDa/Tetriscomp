# SDK Documentation (2.10.0)

- Source: https://sdk.cerebras.net/csl/language/types
- Assigned Skill: cerebras-sdk-guides
- Scraped At: 2026-04-27T10:01:33.361199+00:00

## Content

.rst

.pdf

 Contents

Type System in CSL

 Contents

Type System in CSL
¶

void
 type
¶

Expressions of type
void
 have a single possible value. It describes
constructs that do not produce a result. For example, blocks which do not break
values have type
void
 and
void
 is the return type of functions and
builtins that do not return anything. Using a block as an expression, the void
value can be expressed with
{}
:

const
 void_val
=
 {};
// type is void.

const
 also_void_val :
void

=
 foo();

fn
 foo()
void
 {}

void
 is allowed at runtime as a function return type. All other uses of

void
 values must be comptime-known; see
Comptime
 for more
information on comptime.

Numeric Types
¶

These types describe numbers:

signed integers (
iN
 for arbitrary bit width
N
)

unsigned integers (
uN
 for arbitrary bit width
N
)

arbitrary precision integers (
comptime_int
)

floating point numbers (
f16
,
f32
,
bf16
,
cb16
,

comptime_float
)

Arbitrary-Width Integer Types
¶

CSL supports integer types with any bit width from 0 to 16777215. These are
specified using
uN
 for unsigned types and
iN
 for signed types,
where
N
 is the bit width:

var
 small: u3
=

7
;
// 3-bit unsigned (range: 0 to 7)

var
 tiny: i4
=

-
8
;
// 4-bit signed (range: -8 to 7)

var
 flags: u1
=

1
;
// 1-bit unsigned (0 or 1)

var
 byte:
u8

=

255
;
// 8-bit unsigned

var
 word:
i16

=

-
100
;
// 16-bit signed

var
 dword:
u32

=

1000
;
// 32-bit unsigned

Integer types support arithmetic, comparisons, and bitwise operations:

var
 a: u5
=

10
;

var
 b: u5
=

5
;

var
 sum: u5
=
 a
+
 b;
// OK: result is 15, fits in u5

var
 product: u5
=

3

*

4
;
// OK: result is 12, fits in u5

Arithmetic operations on integer literals produce
comptime_int

results at compile time, which are then coerced to the target type. An
error occurs if the result cannot be represented in the target type:

var
 overflow: u5
=

31

+

1
;
// Error: 32 exceeds u5 max (31)

var
 underflow: i4
=

-
8

-

1
;
// Error: -9 exceeds i4 min (-8)

Note

Only integer types with bit widths of 16 or 32 are ABI-sized.
Non-ABI-sized integer types cannot be used in
export
 or
extern

declarations or as task parameters, and certain hardware-specific
operations (such as DSD builtins) may require ABI-sized types.
Non-ABI-sized types are primarily intended for compact data structures
such as packed structs and unions.

The
comptime_int
 Type
¶

Values of
comptime_int
 type can hold arbitrarily large (or small) integers.
Integer literals have type
comptime_int
:

const
 ten
=

10
;
// type is comptime_int.

const
 also_ten :
comptime_int

=

10
;

Character literals also have type
comptime_int
:

const
 some_char
=
 'a';
// type is comptime_int, value is 97

// (ASCII value of 'a')

const
 some_other_char
=
 '\x0a';
// type is comptime_int, value is 10

// (i.e., 0x0a, in hexadecimal)

const
 yet_another_char
=
 '\n';
// type is comptime_int, value is 10

// (ASCII value of newline character)

Arithmetic between
comptime_int
 values happen at compile time, produce
another
comptime_int
 value, and never underflow or overflow:

const
 thousand
=

1000
;

const
 trillion
=
 thousand
*
 thousand
*
 thousand
*
 thousand;

const
 one
=
 trillion
/
 trillion;

Operations between a value of type
comptime_int
 and a value of
fixed-precision integer type cause the
comptime_int
 value to be converted
to the fixed-precision type. An error is emitted upon overflow or underflow:

const
 thousand
=

1000
;
// comptime_int.

const
 ten :
i16

=

10
;
// 10 is converted from comptime_int to i16.

const
 hundred :
i16

=
 thousand
/

10
;
// thousand is converted to i16.

const
 overflow :
i16

=

10000000000000
;
// error.

The builtin
@as
 can be used to force literals to have a specific width, for
example
@as(u16,

1)

|

0xbeef
.

All values of type
comptime_int
 must be comptime-known, see

Comptime
 for more information on comptime.

The
comptime_float
 Type
¶

Values of
comptime_float
 type can hold any IEEE double precision floating
point number. Float literals have type
comptime_float
:

const
 ten
=

10.0
;
// type is comptime_float.

const
 also_ten : comptime_float
=

10.0
;

Arithmetic between
comptime_float
 values happen at compile time and produce
another
comptime_float
 value. If an operation performs division by zero or
generates a
NaN
 value, an error is emitted.

Operations between a value of type
comptime_float
 and a value of different
float type cause the
comptime_float
 value to be converted to other float
type. An error is emitted if this is not possible.

All values of type
comptime_float
 must be comptime-known, see

Comptime
 for more information on comptime.

FP16 Types
¶

f16
,
cb16
, and
bf16
 are 16-bit floating point (“FP16”) types of
different formats:

Type

Description

Exponent

Mantissa

f16

IEEE half-precision

5 bits

10 bits

cb16

Cerebras float16

6 bits, customized bias

9 bits

bf16

Brain float16

8 bits

7 bits

const
 ieee_six:
f16

=

6.0
;

const
 cb_six: cb16
=

6.0
;

const
 bf_six: bf16
=

6.0
;

comptime
 {

@comptime_assert
(
@bitcast
(
u16
, ieee_six)
==
 0b0100011000000000);

@comptime_assert
(
@bitcast
(
u16
, cb_six)
==
 0b0101100100000000);

@comptime_assert
(
@bitcast
(
u16
, bf_six)
==
 0b0100000011000000);
}

CSL supports use of
a single FP16 type
 within the runtime code of a program.
This type is chosen by the value of the
--fp16-format
 command line option,
with a default of
f16
. All values of the other FP16 types must be
comptime-known:

// With --fp16-format=f16 or --fp16-format absent, OK

// Otherwise, error: variable of type 'f16' must be comptime-known

var
 ieee_one:
f16

=

1.0
;

// With --fp16-format=cb16, OK

// Otherwise, error: variable of type 'cb16' must be comptime-known

var
 cb_one: cb16
=

1.0
;

// With --fp16-format=bf16, OK

// Otherwise, error: variable of type 'bf16' must be comptime-known

var
 bf_one: bf16
=

1.0
;

The
@fp16()
 builtin (see
@fp16
) facilitates
programming with respect to the selected FP16 format.

The
type
 Type
¶

In CSL, the type
type
 can be used to describe values that are themselves
types:

const
 my_type
=

i16
;

const
 same_type :
type

=

i16
;

These values can be used anywhere a type is expected.

const
 my_type
=

i16
;

const
 array
=

@zeros
(
[
10
]
my_type);

fn
 foo() my_type { ... }

All values of type
type
 must be comptime-known, see

Comptime
 for more information on comptime.

Function Types
¶

Values of function type contain the name of a function and may be used anywhere
a function is expected. The type is written as

fn(<arg

types>)

<return_type>
.

fn
 foo(arg1 :
i16
, arg2 :
f16
)
void
 {...}

const
 also_foo1
=
 foo;

const
 also_foo2 :
fn
(
i16
,
f16
)
void

=
 foo;

also_foo1(
10
,
10.0
);
also_foo2(
20
,
20.0
);

Copying a function value does not create a new function, it copies the name of
the function.

All values of function type must be comptime-known, see

Comptime
 for more information on comptime.

Struct Types
¶

There are two kinds of struct types in CSL: anonymous structs and named structs.

The Anonymous Struct Types
¶

Anonymous struct types are defined by an optional
list
 of field names and a

list
 of types. Two anonymous struct types are the same if they have the same
list of field names (or both lack field names) and the same list of types.

A value of an anonymous struct type with named fields is created with the
syntax:
.{.field1

=

value1,

.field2

=

value2,

...}
. A value of an anonymous
struct type with unnamed fields is created with the syntax:

.{value1,

value2,

...}
.

Anonymous struct types with nameless fields are also known as
tuple
 types.
The elements of tuples may be accessed with the
[]
 operator, as long as
the index is known at compile time.

// Type: {a : comptime_int, b : comptime_float}

var
 struct1
=
 .{.a
=

10
, .b
=

1.0
};

var
 struct2
=
 .{.a
=

20
, .b
=

2.0
};

var
 struct1
=
 struct2;
// ok, same type!

// Type: {a : comptime_float, b : comptime_float}

var
 struct3
=
 .{.a
=

10.0
, .b
=

1.0
};
struct3
=
 struct1;
// error: different types!

var
 some_float
=
 struct3
[
1
]
;
// error: struct3 is not a tuple type!

// Type: {comptime_float, comptime_float}

var
 struct4
=
 .{
10.0
,
1.0
};

var
 some_float
=
 struct4
[
0
]
;
// ok!

var
 some_other_float
=
 struct4
[
2
]
;
// error: index 2 is out of bounds!

task
 t(i:
u16
)
void
 {

var
 yet_another_float
=
 struct4
[
i
]
;
// error: i is not known

// at comptime!

}

Currently, it is not possible to spell out anonymous struct types using CSL
syntax.

The Named Struct Types
¶

Named struct types are similar to anonymous struct types, except that two
named struct types defined at different places in the source code are
considered to be different types, even if their field names and types are the
same.

A named struct type is expressed with the form

struct

{

field1:

type1,

field2:

type2,

...

}
. Once a named struct type has
been defined, a value of that type can be created by giving the name of the
type, followed by a field initializer list of the form

{

.field1

=

value1,

.field2

=

value2,

...

}
.

const
 complex
=
 struct {
  real_part:
f16
,
  imag_part:
f16

};

const
 one
=
 complex { .real_part
=

1.0
, .imag_part
=

0.0
 };

const
 zero
=
 complex { .real_part
=

0.0
, .imag_part
=

0.0
 };

As mentioned above, two named struct types are considered equal if and only if
they have identical field names and types
and
 they were both defined at the
same point in the program (i.e., by the same
struct
 expression).

const
 some_struct
=
 struct {
  x:
i16
,
  y:
i16

};

const
 some_other_struct
=
 struct {
  x:
i16
,
  y:
i16

};

comptime
 {

@comptime_assert
(some_struct
==
 some_struct);

@comptime_assert
(some_other_struct
==
 some_other_struct);

// Although some_struct and some_other_struct have the same field names and

// types, they are *not* the same type, because they were defined at

// different source locations.

@comptime_assert
(some_struct
!=
 some_other_struct);
}

Named struct types can also be returned from functions. When combined with
comptime
type
 arguments, this can be used to define parameterized struct
types, whose field types can be customized by the user.

fn
 pair(
comptime
 T1:
type
,
comptime
 T2:
type
)
type
 {

return
 struct {
    first: T1,
    second: T2
  };
}

const
 my_pair
=
 pair(
i32
, comptime_string) {
  .first
=

42
,
  .second
=

"this is a struct"

};

comptime
 {

@comptime_assert
(
@type_of
(my_pair)
==
 pair(
i32
, comptime_string));

@comptime_assert
(
@type_of
(my_pair.first)
==

i32
);

@comptime_assert
(
@type_of
(my_pair.second)
==
 comptime_string);
}

The fields of a struct can be mutated by assigning to them via
.
 syntax.

const
 s
=
 struct {
   x:
i32
,
   y:
i32

};

comptime
 {

var
 my_s
=
 s {
    .x
=

15
,
    .y
=

99

  };

@comptime_assert
(my_s.x
==

15
);

@comptime_assert
(my_s.y
==

99
);

  my_s.x
=

0
;
  my_s.y
=

33
;

@comptime_assert
(my_s.x
==

0
);

@comptime_assert
(my_s.y
==

33
);
}

extern

struct
¶

By default, the memory layout of structs is not defined. Fields are guaranteed
to be ABI-aligned, but no guarantees are provided about the ordering of fields
or size of the struct. If a well-defined memory layout is required, a named
struct type can be qualified with
extern
. This gives the struct in-memory
layout matching the C ABI for the target, enabling
extern

struct
 types to be
used in
export
 and
extern
 declarations. All fields of
extern

struct

types must have an export-compatible type. See

Storage Classes
 for details.

const
 s
=
 extern struct {
   x:
i16
,
   y:
f32
,
};

export
var
 shared_s
=
 s {
   .x
=

-
1
,
   .y
=

-
1.1
,
};

packed

struct
¶

packed
 structs have a different kind of well-defined memory layout. All
packed structs have a
backing integer
. The type of this integer is implicitly
determined by the total bit count of fields, and the ABI of this integer is
exactly the ABI of the
packed

struct
 type. This enables ABI-sized

packed

struct
 types to be used in
export
 and
extern
 declarations
(see
Storage Classes
 for details).

Each field of a packed struct is interpreted as a logical sequence of bits,
arranged from least to most significant. The following field types are allowed,
with bit counts defined as follows:

A field of fixed-width integer or float type uses as many bits as its
width. For example, a
u8
 will use 8 bits of the backing integer.

A
bool
 field uses exactly 1 bit.

An
enum
 field uses exactly the bit width of its underlying integer
type.

A
packed

struct
 field uses the bits of its backing integer.

A
packed

union
 field uses the bits of its backing integer.

A field of pointer type uses as many bits as the target architecture’s
word size.

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

var
 s0
=
 some_struct {
   .x
=

2
,
   .y
=

0.0
,
};

const
 some_other_struct
=
 packed struct {
   x:
i8
,
   y:
i8
,
   p:
[*]
u16
,
};

// Size of some_other_struct is 32 bits, which is ABI-sized

extern
var
 s1: some_other_struct;

It is illegal to take the address of a
packed

struct
 field, since the field
may be unaligned:

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

var
 s0
=
 some_struct {
   .x
=

2
,
   .y
=

0.0
,
};

// error: address of packed struct field is unsupported

const
 ptr
=

&
s0.y;

Union Types
¶

An untagged union type is similar to a named struct type,
except that it represents a choice among the field types
rather than a collection of field types.

Only untagged union types are currently supported in CSL.

An untagged union type is expressed with the form

union

{

field1:

type1,

field2:

type2,

...

}
.
Once a union type has
been defined, a value of that type can be created by giving the name of the
type, followed by a field initializer of the form

{

.field

=

value

}
.

const
 value
=
 union {
  i:
i16
,
  f:
f16

};

const
 i_value
=
 value { .i
=

57
 };

const
 f_value
=
 value { .f
=

57.0
 };

The fields of a union type are also called its variants.
The field that has been initialized is called the active variant.
By default, only accesses to the active variant are allowed.
Note that this is currently only enforced for comptime accesses and
not for runtime accesses.
At run time, it is therefore the programmer’s responsibility to ensure
only the active variant of a bare union is accessed.  Otherwise,
behavior is undefined.
In extern and packed unions, accesses to the other variants are also allowed,
in which case the memory is reinterpreted.
See
extern union
 and
packed union
.

Similarly to named struct types,
two union types are considered equal if and only if
they have identical field names and types
and
 they were both defined at the
same point in the program (i.e., by the same
union
 expression).

const
 some_union
=
 union {
  i:
i16
,
  f:
f16

};

const
 some_other_union
=
 union {
  i:
i16
,
  f:
f16

};

comptime
 {

@comptime_assert
(some_union
==
 some_union);

@comptime_assert
(some_other_union
==
 some_other_union);

// Although some_union and some_other_union

// have the same field names and types,

// they are *not* the same type, because they were defined at

// different source locations.

@comptime_assert
(some_union
!=
 some_other_union);
}

Just like named struct types in

the parameterized struct types example
,
it is possible to define parameterized union
types, with field types that can be customized by the user.

The active variant of a union can be mutated by assignment via
.
 syntax.
A new active variant can only be established by assigning
a new value to the entire union object.

const
 u
=
 union {
  i:
i32
,
  f:
f32

};

comptime
 {

var
 my_u
=
 u {
    .i
=

15

  };

@comptime_assert
(my_u.i
==

15
);

  my_u.i
=

0
;

@comptime_assert
(my_u.i
==

0
);

  my_u
=
 u { .f
=

33.0
 };

@comptime_assert
(my_u.f
==

33.0
);
}

extern

union
¶

Similarly to an
extern struct
,
a union type qualified with
extern
 has an in-memory
layout matching the C ABI for the target, enabling
extern

union
 types to be
used in
export
 and
extern
 declarations. All fields of
extern

union

types must have an export-compatible type. See

Storage Classes
 for details.

const
 u
=
 extern union {
    i:
i32
,
    f:
f32

};

 export
var
 shared_u
=
 u {
    .i
=

-
1
,
 };

Note that even though accessing a variant of an extern union
other than the active variant is allowed,
this is not yet fully supported at comptime.

packed

union
¶

Similarly to a
packed struct
,
a union type qualified with
packed
 has a
backing integer
.
All fields of a packed union must have the same bit width,
and the ABI of this integer is exactly the ABI of the
packed

union
 type.
This enables ABI-sized
packed

union
 types to be used in

export
 and
extern
 declarations
(see
Storage Classes
 for details).

The valid field types are the same as those
that are valid for a
packed struct
.

const
 some_struct
=
 packed struct {
   x:
i8
,
   y:
i8
,
};

const
 some_union
=
 packed union {
   s: some_struct,
   i:
i16
,
};

// The size of some_union is 16 bits, which is ABI-sized.

extern
var
 u: some_union;

Note that even though accessing a variant of a packed union
other than the active variant is allowed,
this is not yet fully supported at comptime.

Enumeration Types
¶

An enumeration type is a set of named elements, each of which is represented
by a unique integer value:

const
 colors
=
 enum(
u16
) { red, white, blue };

const
 favorite
=
 colors.red;

The underlying integer type is specified by the type argument (
u16
 in the
example above) and it can be any fixed-precision integer type (e.g.
i16
 or

u32
).

Any element can be assigned a comptime-known integer value:

const
 colors
=
 enum(
u16
) { red, white
=

1
, blue };

The values assigned must be unique within the type. Any element not assigned a
value will be assigned a value by the compiler. The compiler assigns values from
left to right, using  consecutive integers starting with zero. In the example
above, the compiler will assign the value
0
 to
red
 and the value
2

to
blue
. If
white
 is instead assigned the value
4
, then the compiler
will assign the value
0
 to
red
 and
1
 to
blue
.

Enumeration type values can be cast to and from their underlying numeric values
using the
@as()
 builtin, as the following assertions demonstrate:

@comptime_assert
(
@as
(
i16
, colors.red)
==

0
);

@comptime_assert
(
@as
(
u16
, colors.white)
==

1
);

@comptime_assert
(
@as
(
f32
, colors.blue)
==

2.0
);

@comptime_assert
(
@as
(colors,
1
)
==
 colors.white);

An enumeration type can be cast to and from any numeric type
regardless of its underlying integer type, subject only to the general
compatibility rules of type casts.

An enumeration value cannot be cast directly to a value of another enumeration
type, but the same effect can be achieved by casting via a numeric type:

const
 game
=
 enum(
i16
) {rock, paper
=

-
3
, scissors};

// @as(color, game.rock)  <= Error!

const
 myred
=

@as
(colors,
@as
(
u16
, game.rock));
// OK

@comptime_assert
(
@as
(colors, as(
i16
, colors.white)
+

1
))
==
 colors.blue);

Two expressions of the same enumeration type can be compared using the
==

and
!=
 operators.

Enumeration Type Equality
¶

Two enumeration types are the same if and only if both of the following
conditions are true:

they have the same structure, i.e., the same underlying integer type, and the
same set of element values, each of which is assigned the same numeric value.

their definitions originate at the same source code location.

const
 e1
=
 enum(
i16
) {red, white};

const
 e2
=
 enum(
i16
) {red, white};

fn
 enum_type(base_type:
type
)
type
 {

return
 enum(base_type) {red, white};
};

const
 e3
=
 enum_type(
i16
);

const
 e4
=
 enum_type(
i32
);

const
 e5
=
 e1;

const
 myred
=
 e1.red;

// different types, not originating from the same location:

@comptime_assert
(e1
!=
 e2);

// different types, same originating location, but not same structure

@comptime_assert
(e3
!=
 e4);

@comptime_assert
(e5
==
 e1);
// same type

@comptime_assert
(
@type_of
(myred)
==
 e5);
// same type

Array Types
¶

An array type is parameterized by an element type, describing a
collection of elements of the base type. An array type whose element type is

T
 can be written as
[size]T
.

The element type must not be another array type. Multidimensional
arrays are specified with a sequence of dimensions:
[size1,

size2,

size3]T
.

var
 1d_array
=

@zeros
(
[
10
]
u16
);

var
 2d_array
=

@zeros
(
[
10
,
10
]
u16
);

var
 another_array
=

[
2
]
i16
 {
1
,
2
}

Pointer Types
¶

A value of pointer type contains the memory address where a variable is
located.

Pointer types are described by an element type and an optional
const

qualifier.

In CSL, pointers are
only
 created by taking the address of a variable. This
provides the property that pointers always point to valid data when they are
created.

There are two kinds of pointers in CSL: pointers to a single element and
pointers to an unknown number of elements.

Pointers to a Single Element
¶

A pointer to a single value of type
T
 is written as
*T
. For example:

a pointer to a single
i16
 is written as
*i16

a pointer to a single array of ten integers is written as
*[10]i16
.

Pointers to a single element are created with the address-of operator (
&
):

var
 array
=

@zeros
(
[
10
]
u16
);

const
 ptr
=

&
array;

const
 same_ptr:
*[
10
]
u16

=

&
array;

The only operation allowed on pointers to a single element is to dereference
them with the dereference
.*
 operator:

var
 array
=

@zeros
(
[
10
]
i32
);

const
 ptr
=

&
array;
ptr.
*

=

@constants
(
[
10
]
i32
,
42
);
ptr.
*[
2
]

=

1
;

Pointer types may be
const
 qualified, indicating that this pointer may not
be used to modify the underlying memory:

var
 array
=

@zeros
(
[
10
]
i32
);

var
 ptr:
*
const
[
10
]
i32

=

&
array;
ptr.
*

=

@constants
(
[
10
]
i32
,
42
);
// Error: pointer type is const qualified.

ptr.
*[
2
]

=

1
;
// Error: pointer type is const qualified.

const
 array
=

@zeros
(
[
10
]
i32
);

var
 ptr
=

&
array;
// Type of ptr is *const[10]i32

ptr.
*

=

@constants
(
[
10
]
i32
,
42
);
// Error: pointer type is const qualified.

ptr.
*[
2
]

=

1
;
// Error: pointer type is const qualified.

In the example above,
ptr
 itself is mutable, but the memory it points to is
not.

Pointers to Unknown Number of Elements
¶

A pointer to an unknown number of elements of type
T
 is written as

[*]T
.  For example, a pointer to an unknown number of
f16
 elements is
written as
[*]f16
.

Pointers to an unknown number of elements are created through coercion from
pointers to a single element of array type (e.g.
*[2]i16
):

fn
 foo(ptr :
[*]
i32
)
void
 {

// ...

}

var
 array10
=

@zeros
(
[
10
]
i32
);

var
 array20
=

@zeros
(
[
20
]
i32
);
foo(
&
array10);
// ok!

foo(
&
array20);
// ok!

var
 array_float
=

@zeros
(
[
20
]
f16
);
foo(
&
array_float);
// Error: base type mismatch.

var
 ptr :
[*]
i32

=

&
array10;
ptr
=

&
array20;

The original array must have rank one:

var
 array
=

@zeros
(
[
3
,
3
,
3
]
i32
);

var
 ptr :
[*]
i32

=

&
array;
// Error.

Dereferencing a pointer to an unknown number of elements is not allowed. The
access operator
[]
 must be used instead:

fn
 foo(ptr :
[*]
i32
)
void
 {
  ptr.
*

=

10
;
// Error: dereferencing is not allowed.

  ptr
[
0
]

=

10
;
}

It is illegal to access an element whose index is out-of-bounds on the original
array:

fn
 foo(ptr :
[*]
i32
)
void
 {
  ptr
[
1000
]

=

10
;
}

var
 array10
=

@zeros
(
[
10
]
i32
);
foo(
&
array10);
// Bad: will create out-of-bounds access.

An error is emitted if the compiler is able to detect an out-of-bounds access.

Pointers and Configuration Memory
¶

It is illegal to dereference or use the access operator
[]
 on pointers
occurring in the selected target’s configuration address range. An error is
emitted if the compiler is able to detect such an access. Configuration memory
should be accessed using the builtins
@get_config
 and
@set_config

instead (see
@get_config
,

@set_config
).

The
anyopaque
 Type
¶

The
anyopaque
 type represents an opaque type whose size and alignment are
unknown.  It is primarily useful as the element type of a pointer
(
*anyopaque
) to create type-erased pointers that can point to values of
any type.

The
anyopaque
 type itself cannot be used directly as a value, as a function
parameter, as a function return type, or in container types (structs, unions,
arrays) because its size is not known.  It can only be used behind a pointer.

Pointers to any type can be implicitly coerced to
*anyopaque
:

var
 x:
i32

=

42
;

var
 y:
f16

=

3.14
;

var
 ptr_x:
*
anyopaque
=

&
x;
// Implicit coercion from *i32

var
 ptr_y:
*
anyopaque
=

&
y;
// Implicit coercion from *f16

To recover the original type, use
@ptrcast
:

var
 x:
i32

=

42
;

var
 opaque_ptr:
*
anyopaque
=

&
x;

var
 ptr_i32:
*
i32

=

@ptrcast
(
*
i32
, opaque_ptr);
ptr_i32.
*

=

100
;
// Modifies x

Warning

Casting a pointer to
*anyopaque
 and then casting it back to an incorrect
type results in undefined behavior.  The programmer must ensure type safety
when using
@ptrcast
.

The
comptime_string
 Type
¶

Warning

Support for compile-time strings is still experimental, and the set of
operations available on the type
comptime_string
 is very limited.

Values of
comptime_string
 type hold immutable strings that can be
manipulated at compile time. All values of type
comptime_string
 must be
comptime-known. See ref:
language-comptime
 for more information on
comptime.

const
 hello
=

"abc"
;
// type is comptime_string

fn
 bool_to_str(b:
bool
) comptime_string {

if
 (b) {

return

"true"
;
   }
else
 {

return

"false"
;
   }
}

comptime
 {

const
 true_str
=
 bool_to_str(
true
);

@comptime_assert
(true_str
==

"true"
);

var
 s
=

"hello"
;

@comptime_assert
(s
==

"hello"
);
  s
=

"goodbye"
;

@comptime_assert
(s
!=

"hello"
);

@comptime_assert
(s
==

"goodbye"
);
}

As in C and C++, strings in CSL are sequences of bytes. A Unicode character
may correspond to a sequence of more than one byte, and CSL does not have a
“wide character” type.

Like
std::string
 in C++, but
unlike

char

*
 strings in C, strings in
CSL are
not
 null-terminated. This means that the NUL character can occur
anywhere in a string. For example, the following
@comptime_assert
s will
succeed:

@comptime_assert
(
"abc\x00xyz"

!=

"abc"
)

@comptime_assert
(
"abc\x00xyz"

==

"abc\x00xyz"
)

@comptime_assert
(
@strlen
(
"abc\x00xyz"
)
!=

3
)

@comptime_assert
(
@strlen
(
"abc\x00xyz"
)
==

7
)

UTF-8 encoded text is allowed in string literals, but if the text contains
non-ASCII characters, the length of the string (as returned by
@strlen
)
will not necessarily match the number of characters in the string. For
example, the
@comptime_assert
s in the following code will succeed:

// Note: The UTF-8 encoding of the "thumbs up" emoji is F0 9F 91 8D.

const
 thumbs_up
=

"👍"
;

@comptime_assert
(
@strlen
(thumbs_up)
==

4
);

var
 as_array:
[
4
]
u8

=

@get_array
(thumbs_up);

@comptime_assert
(as_array
[
0
]

==

0xf0
);

@comptime_assert
(as_array
[
1
]

==

0x9f
);

@comptime_assert
(as_array
[
2
]

==

0x91
);

@comptime_assert
(as_array
[
3
]

==

0x8d
);

The
imported_module
 Type
¶

TODO.

The
direction
 Type
¶

TODO.

Type Coercions
¶

Numeric Coercions
¶

CSL supports implicit numeric coercions that widen values to larger, compatible
types. These coercions preserve all possible values from the source type.

Integer Widening
¶

Integer types can be implicitly coerced to wider integer types when the
destination type can represent all values that the source type can represent:

Same signedness with wider width
:
i8
 →
i16
 →
i32
 →
i64
,
and
u8
 →
u16
 →
u32
 →
u64

Unsigned to wider signed
:
u8
 →
i16
,
u16
 →
i32
,

u32
 →
i64

var
 small:
i8

=

42
;

var
 large:
i32

=
 small;
// OK: i8 can be widened to i32

var
 unsigned_val:
u16

=

1000
;

var
 signed_val:
i32

=
 unsigned_val;
// OK: i32 can represent all u16 values

The following integer coercions are
not
 allowed:

Narrowing
 (loses precision): This applies to any coercion where the
destination integer type has a smaller bit width than the source integer type,
such as
i32
 →
i16
.

Signed to unsigned
 (unsigned types cannot represent negative values):
This applies to all coercions from signed to unsigned types, regardless of
bit width, such as
i8
 →
u8
 or
i32
 →
u64
.

Float Widening
¶

Float types can be implicitly coerced to wider float types:

FP16 to f32
:
f16
 →
f32
,
bf16
 →
f32
,
cb16
 →
f32

var
 half:
f16

=

3.14
;

var
 single:
f32

=
 half;
// OK: f16 can be widened to f32

The following float coercions are
not
 allowed:

Narrowing
:
f32
 →
f16
 (loses precision). This applies to any
coercion where the destination float type has a smaller bit width than the
source float type.

Cross-format
:
f16
 →
bf16
 (different representations, not pure
widening)

Comptime Coercions
¶

Values of
comptime_int
 and
comptime_float
 can be coerced to compatible
fixed-precision types as long as the target type can represent the source value.
Specifically,
comptime_int
 can be coerced to any integer type, and

comptime_float
 can be coerced to any floating point type:

const
 int_val
=

42
;
// comptime_int

var
 x:
i32

=
 int_val;
// OK: 42 fits in i32

const
 big_val
=

100000
;
// comptime_int

var
 y:
i16

=
 big_val;
// Error: 100000 doesn't fit in i16

const
 float_val
=

3.14
;
// comptime_float

var
 z:
f32

=
 float_val;
// OK: comptime_float to f32

Pointer Coercions
¶

CSL supports implicit coercions between certain pointer types. The following
pointer coercions are supported (where
T
 represents any specific element
type, e.g.
f16
,
i32
, etc., and
N
 represents a specific array size):

Const qualification
¶

*T
 →
*const

T

[*]T
 →
[*]const

T

*[N]T
 →
*const

[N]T

var
 x:
i32

=

42
;

var
 ptr:
*
i32

=

&
x;

// OK: can add const qualifier

var
 const_ptr:
*
const

i32

=
 ptr;

var
 arr:
[
10
]
i32
;

var
 arr_ptr:
*[
10
]
i32

=

&
arr;

// OK: can add const qualifier

var
 const_arr_ptr:
*
const

[
10
]
i32

=
 arr_ptr;

// Cannot remove const qualifier

// Error: cannot coerce '*const i32' to '*i32'

var
 bad_ptr:
*
i32

=
 const_ptr;

// Error: cannot coerce '*const [10]i32' to '*[10]i32'

var
 bad_arr_ptr:
*[
10
]
i32

=
 const_arr_ptr;

Array pointer to many-item pointer
¶

*[N]T
 →
[*]T

*[N]T
 →
[*]const

T

*const

[N]T
 →
[*]const

T

var
 arr:
[
10
]
i32
;

var
 arr_ptr:
*[
10
]
i32

=

&
arr;
// array pointer

// OK: coerce to many-item pointer

var
 many_ptr:
[*]
i32

=
 arr_ptr;

// Cannot coerce many-item pointer back to array pointer

// Error: cannot coerce '[*]i32' to '*[10]i32'

var
 bad_arr_ptr:
*[
10
]
i32

=
 many_ptr;

Single-element pointer to single-element array pointer
¶

*T
 →
*[1]T

*T
 →
*const

[1]T

*const

T
 →
*const

[1]T

var
 x:
i32

=

42
;

var
 ptr:
*
i32

=

&
x;
// single-element pointer

// OK: coerce to single-element array pointer

var
 arr_ptr:
*[
1
]
i32

=
 ptr;

// Cannot coerce array pointer back to single-element pointer

// Error: cannot coerce '*[1]i32' to '*i32'

var
 bad_ptr:
*
i32

=
 arr_ptr;

Note that the base element type must match for coercions to be valid.

Struct Coercions
¶

Anonymous structs may be coerced to other struct types. For a coercion to be
valid:

The destination struct type must have the same field names as the source
value, but the order of the field names does not need to match.

Each source field value must be coercible to the corresponding destination
field type.

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

// OK: anonymous struct coerced to named struct

var
 p0: Point
=
 .{ .x
=

10
, .y
=

20
 };

// OK: anonymous struct coerced to anonymous struct

var
 p1: struct { x:
i32
, y:
i32
 }
=
 .{ .x
=

10
, .y
=

20
 };

// OK: field order does not need to match

var
 p2: Point
=
 .{ .y
=

20
, .x
=

10
 };

// Error: expected 2 fields, got 1

var
 p3: Point
=
 .{ .x
=

1
 };

// Error: expected 2 fields, got 3

var
 p4: Point
=
 .{ .x
=

1
, .y
=

2
, .z
=

3
 };

// Error: field 'y' not present in source

var
 p5: Point
=
 .{ .x
=

1
, .z
=

2
 };

// Error: cannot coerce field 'y' from type 'comptime_string' to type 'i32'

var
 p6: Point
=
 .{ .x
=

1
, .y
=

"str"
 };

Peer Type Resolution
¶

Peer type resolution is used when CSL needs to find a common type for multiple
expressions. CSL attempts to find a common type that all expressions can be
coerced to.

Peer type resolution occurs in the following contexts:

Conditional expressions (
if
/
else
), when the if and else branches have
different but compatible types

Switch expressions, when different cases return different but compatible types

Block expressions, when multiple
break
 statements with values have
different but compatible types

Binary operations between compatible types (addition, subtraction, comparison,
etc.)

The following coercions are supported in peer type resolution:

Numeric coercions
¶

All numeric coercions described in
Numeric Coercions
 are supported in
peer type resolution. For example,
i16
 can be widened to
i32
, and

f16
 can be widened to
f32
.

fn
 choose_int_or_comptime_int(condition:
bool
)
i32
 {

var
 x:
i32

=

10
;

// OK: 20 is comptime_int, coerced to i32; result has type i32

return

if
 (condition) x
else

20
;
}

fn
 choose_float_or_comptime_float(condition:
bool
)
f32
 {

var
 y:
f32

=

1.0
;

// OK: 2.0 is comptime_float, coerced to f32; result has type f32

return

if
 (condition) y
else

2.0
;
}

fn
 choose_narrow_or_wide_int(condition:
bool
)
i32
 {

var
 small:
i16

=

100
;

var
 large:
i32

=

200
;

// OK: i16 widened to i32; result has type i32

return

if
 (condition) small
else
 large;
}

fn
 choose_narrow_or_wide_float(condition:
bool
)
f32
 {

var
 half:
f16

=

1.5
;

var
 single:
f32

=

2.5
;

// OK: f16 widened to f32; result has type f32

return

if
 (condition) half
else
 single;
}

Pointer coercions
¶

All pointer coercions described in
Pointer Coercions
 are supported in
peer type resolution.

fn
 choose_ptr(condition:
bool
)
*
const

i32
 {

var
 x:
i32

=

1
;

const
 y:
i32

=

2
;

// OK: both coerced to *const i32

return

if
 (condition)
&
x
else

&
y;
}

fn
 choose_array_ptr(condition:
bool
)
[*]
i32
 {

var
 arr1:
[
10
]
i32
;

var
 arr2:
[
20
]
i32
;

// OK: both coerced to [*]i32

return

if
 (condition)
&
arr1
else

&
arr2;
}

fn
 choose_ptr_or_array_ptr(condition:
bool
)
*
const

[
1
]
i32
 {

var
 x:
i32

=

1
;

var
 arr:
[
1
]
i32
;

// OK: &x coerced to *[1]i32, then both to *const [1]i32

return

if
 (condition)
&
x
else

&
arr;
}
