import os

from ex_installer.file_manager import FileManager


def test_dir_is_empty_returns_true_for_empty_directory(tmp_path):
    directory = os.path.join(str(tmp_path), "empty")
    os.mkdir(directory)

    assert FileManager.dir_is_empty(directory) is True


def test_dir_is_empty_returns_false_for_non_empty_directory(tmp_path):
    directory = os.path.join(str(tmp_path), "non-empty")
    os.mkdir(directory)
    with open(os.path.join(directory, "file.txt"), "w", encoding="utf-8") as file:
        file.write("content")

    assert FileManager.dir_is_empty(directory) is False
