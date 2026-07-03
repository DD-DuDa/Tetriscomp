# SDK Documentation (2.10.0)

- Source: https://sdk.cerebras.net/csl/language_index
- Assigned Skill: cerebras-sdk-guides
- Scraped At: 2026-04-27T10:01:33.361199+00:00

## Content

.rst

.pdf

CSL Language Guide

CSL Language Guide
¶

Syntax of CSL

Type system overview

Variables

Pointers

Functions

Statements

Operators

Comments

Builtins

@activate

@allocate_fifo

@as

@assert

@bitcast

@bind_control_task

@bind_data_task

@bind_local_task

@block

@comptime_assert

@comptime_print

@constants

@dimensions

@element_count

@element_type

@export

@field

@fp16

@get_array

@get_color

@get_config

@get_config_unchecked

@get_control_task_id

@get_data_task_id

@get_dsd

@get_dsr

@get_filter_id

@get_input_queue

@get_int

@get_local_task_id

@get_output_queue

@get_rectangle

@get_string_from_byte

@has_field

@import_module

@increment_dsd_offset

@initialize_queue

@is_arch

@is_comptime

@is_same_type

@load_to_dsr

@map

@ptrcast

@random16

@range

@range_start, @range_stop, @range_step

@rank

@set_active_prng

@set_color_config, @set_local_color_config

@set_config

@set_config_unchecked

@set_dsd_base_addr

@set_dsd_length

@set_dsd_stride

@set_fifo_read_length

@set_fifo_write_length

@set_rectangle

@set_teardown_handler

@set_tile_code

@strcat

@strlen

@type_of

@unblock

@zeros

Builtins for Supporting Remote Procedure Calls (RPC)

Builtins for DSD Operations

Builtins for WSE-3

@get_ut_id

@queue_flush

@set_control_task_table

@set_empty_queue_handler

@bind_rotating_tasks

Microthread IDs

Constructor and Type

Usage and Semantics

Example

Blocking and Unblocking Microthreads

Comptime

Comptime Variables

Comptime-Known Values

Comptime Expressions

Types Whose Values are Required to be Comptime

Evaluation of Comptime-Known Control Flow

Typical Uses of the
comptime
 Keyword

Data Structure Descriptors

Basic Syntax

One-Dimensional Memory Vectors

Two-, Three-, or Four-Dimensional Memory Vectors

Pointers To Scalars As Destinations

Circular Buffers

Fabric Input Vectors

Fabric Output Vectors

FIFOs

Changing DSD Properties

Asynchronous DSD Operations

Explicit Index Offset

Advanced DSD Features

Data Structure Registers

Extended DSRs and Stride Registers

DSR, XDSR and SR Allocation

DSR Types

DSR Builtins

Libraries

<complex>

<control>

<data_utils>

<debug>

<directions>

<dsd_ops>

<empty>

<layout>

<malloc>

<math>

<random>

<simprint>

<string>

<tile_config>

<time>

<timer>

<types>

<kernels>

<collectives_2d>

Libraries for WSE-3

<message_passing>

<tile_config>

Modules

Builtin syntax

Semantics

Using a module

Example

Binary symbol names

Task Identifiers and Task Execution

Data Tasks

Local Tasks

Control Tasks

Type System in CSL

void
 type

Numeric Types

The
type
 Type

Function Types

Struct Types

Union Types

Enumeration Types

Array Types

Pointer Types

The
anyopaque
 Type

The
comptime_string
 Type

The
imported_module
 Type

The
direction
 Type

Type Coercions

Storage Classes

Overview

Object file symbols for
extern
 and
export
 declarations

Interaction with
linkname

Mixing
extern
 and
export
 declarations

Type restrictions

Generics

Overview

Constraining Type Parameters

Specializing Logic

Computing With Types

Advanced Hardware Features

Color Swapping

Compute Element (CE) Injection

Appendix

SIMD Mode
