from data_processing.processing import process_file


def test_process_file(tmp_path):
    in_file = tmp_path / 'in.txt'
    out_file = tmp_path / 'out.txt'
    in_file.write_text('hello world')

    result = process_file(str(in_file), str(out_file))

    assert result == 'HELLO WORLD'
    assert out_file.read_text() == 'HELLO WORLD'
