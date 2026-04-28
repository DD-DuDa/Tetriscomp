import io
from parse_simlog import parse


SAMPLE = """\
@0 GITREV=abc, GITCLEAN=1
@0 Create from elfs
@100 PE(0,0): op_start:rmsnorm_x
@250 PE(0,0): comm_start:all_reduce_bsz
@380 PE(0,0): comm_end:all_reduce_bsz
@500 PE(0,0): op_end:rmsnorm_x
@510 PE(1,0): op_start:rmsnorm_x
@900 PE(1,0): op_end:rmsnorm_x
"""


def test_parse_extracts_op_region():
    df = parse(io.StringIO(SAMPLE))
    row = df[(df.pe_x == 0) & (df.pe_y == 0) & (df.region == 'op:rmsnorm_x')].iloc[0]
    assert row.cycles == 400  # 500 - 100


def test_parse_extracts_comm_region():
    df = parse(io.StringIO(SAMPLE))
    row = df[(df.pe_x == 0) & (df.pe_y == 0) & (df.region == 'comm:all_reduce_bsz')].iloc[0]
    assert row.cycles == 130  # 380 - 250


def test_parse_handles_multiple_pes():
    df = parse(io.StringIO(SAMPLE))
    row = df[(df.pe_x == 1) & (df.pe_y == 0) & (df.region == 'op:rmsnorm_x')].iloc[0]
    assert row.cycles == 390  # 900 - 510


def test_parse_skips_non_marker_lines():
    df = parse(io.StringIO(SAMPLE))
    # Only valid op_*/comm_* markers should produce rows
    assert len(df) == 3  # rmsnorm_x@(0,0), all_reduce_bsz@(0,0), rmsnorm_x@(1,0)


def test_parse_handles_uppercase_in_tag():
    """all_reduceMax_bsz contains an uppercase M — regex must handle it."""
    sample = """\
@10 PE(0,0): comm_start:all_reduceMax_bsz
@30 PE(0,0): comm_end:all_reduceMax_bsz
"""
    df = parse(io.StringIO(sample))
    row = df.iloc[0]
    assert row.region == 'comm:all_reduceMax_bsz'
    assert row.cycles == 20


EXPECTED_COLS = ['pe_x', 'pe_y', 'region', 'occurrence', 'cycles']


def test_parse_handles_end_without_start():
    df = parse(io.StringIO('@10 PE(0,0): op_end:foo\n'))
    assert len(df) == 0
    assert list(df.columns) == EXPECTED_COLS


def test_parse_handles_start_without_end():
    df = parse(io.StringIO('@10 PE(0,0): op_start:foo\n'))
    assert len(df) == 0
    assert list(df.columns) == EXPECTED_COLS


def test_parse_handles_empty_input():
    df = parse(io.StringIO(''))
    assert len(df) == 0
    assert list(df.columns) == EXPECTED_COLS
