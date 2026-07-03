# SDK Documentation (2.10.0)

- Source: https://sdk.cerebras.net/csl/language/appendix
- Assigned Skill: cerebras-sdk-guides
- Scraped At: 2026-04-27T10:01:33.361199+00:00

## Content

.rst

.pdf

 Contents

Appendix

 Contents

Appendix
¶

SIMD Mode
¶

Many of the

builtins for DSD operations

have a SIMD (single instruction, multiple data) mode, in which multiple
operations can be performed in a single cycle.
Under appropriate conditions, these builtins will automatically
execute in SIMD mode when operating on DSDs, if possible.

In particular, builtins can only operate at their full SIMD width
if no bank conflicts occur when fetching the operands from memory.
The 48 KB of memory in a PE are laid out into 8 banks of 6 KB each.
Each successive 16 bits are located in successive banks.
In a single cycle, the PE can perform two 32-bit reads and one 32-bit write.
However, the reads must occur from separate banks. More specifically,
if the 8 banks are numbered 0 to 7, then the bank IDs
bank_1
 and

bank_2
 of the two reads must be such that
bank_1

%

4

!=

bank_2

%

4
.

For best results in avoiding bank conflicts with SIMD operations, the operand
addresses should be 32-bit aligned, and

(src0_addr

%

8)

==

((src1_addr

+

4)

%

8)
, where
src0_addr
 and

src1_addr
 are the addresses of the operands.
Dumping the ELF file’s symbol table with the
--sym
 option of

cs_readelf
 provides addresses and banking information for all symbols
in a compiled CSL program, and can be useful for determining if bank conflicts
may occur.

Additionally, if the DSD operands have non-contiguous strided accesses,
the SIMD width may be limited:

Strides of 0 and 1 can operate at full SIMD width.

Strides such that
stride

%

8
 is 2, 3, 5, or 6 can operate at full
SIMD width.

Unless stride is 1, strides such that
stride

%

8
 is 1 or 7 is limited
to two operations per cycle, or a SIMD width of 2.

Unless stride is 0, strides such that
stride

%

8
 is 0 is limited to
one operation per cycle, or a SIMD width of 1.

Strides such that
stride

%

8
 is 4 are limited to two operations per
cycle, or a SIMD width of 4.

The maximum width of builtins which can operate in SIMD mode are given
in the table below.

Builtin

WSE-2 SIMD Width

WSE-3 SIMD Width

@add16

4

8

@addc16

1

8

@and16

4

8

@fabsh

4

8

@fabss

2

4

@faddh

4

8

@faddhs

2

4

@fadds

2

4

@fnormh

4

8

@fnorms

2

4

@fh2s

1

4

@fh2xp16

1

8

@fmach

4

8

@fmachs

2

4

@fmaxh

1

8

@fmaxs

1

4

@fmovh

4

8

@fmovs

2

4

@fmulh

4

8

@fnegh

4

8

@fnegs

2

4

@fs2h

1

4

@fs2xp16

1

4

@fscaleh

4

8

@fscales

2

4

@fsubh

4

8

@fsubs

2

4

@mov16

4

8

@mov32

2

4

@or16

4

8

@sar16

1

4

@sll16

1

4

@slr16

1

4

@sub16

4

8

@xor16

4

8

@xp162fh

1

8

@xp162fs

1

4
