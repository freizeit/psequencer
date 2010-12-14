import os
import shutil
import tempfile
import unittest

from sequencer import (
    get_audio_files, get_unsequenced_files, next_seqnum, sequence_files)


class GetAudioFilesTest(unittest.TestCase):
    """Tests for the L{get_audio_files} function."""

    def setUp(self):
       self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_only_plain_files(self):
        """Only plain files will be considered."""
        path = "%s%sfile" % (self.test_dir, os.sep)
        open(path, "w+").close()

        os.symlink(path, "%s%s" % (path, ".mp3"))
        os.mkdir("%s%s" % (path, ".ogg"))
        self.assertEqual([], get_audio_files(self.test_dir))

    def test_only_files_with_audio_extensions(self):
        """Only plain files with an audio file extension will be considered."""
        path = "%s%sfile" % (self.test_dir, os.sep)
        audio_file1 = "%s%s" % (path, ".mp3")
        audio_file2 = "%s%s" % (path, ".ogg")
        open(path, "w+").close()
        open(audio_file1, "w+").close()
        open(audio_file2, "w+").close()
        open("%s%s" % (path, ".txt"), "w+").close()

        self.assertEqual(
            [os.path.basename(audio_file1), os.path.basename(audio_file2)],
            get_audio_files(self.test_dir))


class GetUnsequencedFilesTest(unittest.TestCase):
    """Tests for the L{get_unsequenced_files} function."""

    def test_get_unsequenced_files(self):
        """Only files without a (\d+) prefix are returned."""
        files = [
            'TM-0079.mp3', '02 31-ITC.TN.mp3', '034-Web-.mp3',
            '999- Web.mp3', '  035- Web.mp3',
            ]
        self.assertEqual(
            ['  035- Web.mp3', '02 31-ITC.TN.mp3', 'TM-0079.mp3'],
            sorted(get_unsequenced_files(files)))


class NextSeqnumTest(unittest.TestCase):
    """Tests for the L{next_seqnum} function."""

    def test_next_seqnum(self):
        """The next unused sequence number is returned."""
        files = ['999- Web.mp3', '  035- Web.mp3']
        self.assertEqual(1000, next_seqnum(files))

    def test_next_seqnum_with_no_values_so_far(self):
        """
        If there are no sequenced files so far the sequence number returned
        should be "00001".
        """
        files = ['Web.mp3', 'Xen.mp3']
        self.assertEqual(1, next_seqnum(files))

    def test_next_seqnum_with_negative_prefix(self):
        """
        For files with negative numeric prefixes the returned value
        should be "00001".
        """
        files = ['-001-Web.mp3', '-112 Xen.mp3']
        self.assertEqual(1, next_seqnum(files))


class SequenceFilesTest(unittest.TestCase):
    """Tests for the L{sequence_files} function."""

    def setUp(self):
       self.test_dir = tempfile.mkdtemp(prefix="with space")

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_sequence_file(self):
        """L{sequence_files} works correctly."""
        sequence_number = 200
        old_name = "audio.mp3"
        new_name = "%05d-%s" % (sequence_number, old_name)
        path_prefix = "%s%s" % (self.test_dir, os.sep)
        old_path = "%s%s" % (path_prefix, old_name)
        new_path = "%s%s" % (path_prefix, new_name)
        open(old_path, "w+").close()
        sequence_files(200, self.test_dir, [old_name])
        self.assertTrue(os.path.islink(old_path))
        self.assertFalse(os.path.islink(new_path))
        self.assertTrue(os.path.isfile(new_path))

    def test_sequence_file_with_empty_file_name_list(self):
        """
        L{sequence_files} ignores files that were not passed via the
        C{unsequenced_files} parameter.
        """
        sequence_number = 200
        old_name = "audio.mp3"
        new_name = "%05d-%s" % (sequence_number, old_name)
        path_prefix = "%s%s" % (self.test_dir, os.sep)
        old_path = "%s%s" % (path_prefix, old_name)
        new_path = "%s%s" % (path_prefix, new_name)
        open(old_path, "w+").close()
        sequence_files(200, self.test_dir, [])
        self.assertTrue(os.path.isfile(old_path))
        self.assertFalse(os.path.islink(old_path))
        self.assertFalse(os.access(new_path, os.F_OK))

    def test_sequence_file_with_width_too_small(self):
        """
        L{sequence_files} raises a C{RuntimeError} if the prefix width is
        too small.
        """
        sequence_number = 200
        old_name = "audio.mp3"
        new_name = "%05d-%s" % (sequence_number, old_name)
        path_prefix = "%s%s" % (self.test_dir, os.sep)
        old_path = "%s%s" % (path_prefix, old_name)
        new_path = "%s%s" % (path_prefix, new_name)
        open(old_path, "w+").close()
        self.assertRaises(
            RuntimeError, sequence_files, 200, self.test_dir, [old_name], 1)

    def test_sequence_file_with_whitespace_in_name(self):
        """
        L{sequence_files} works correctly even if the file name contains
        whitespace.
        """
        sequence_number = 200
        old_name = "au d	io.mp3"
        new_name = "%05d-%s" % (sequence_number, old_name)
        path_prefix = "%s%s" % (self.test_dir, os.sep)
        old_path = "%s%s" % (path_prefix, old_name)
        new_path = "%s%s" % (path_prefix, new_name)
        open(old_path, "w+").close()
        sequence_files(200, self.test_dir, [old_name])
        self.assertTrue(os.path.islink(old_path))
        self.assertFalse(os.path.islink(new_path))
        self.assertTrue(os.path.isfile(new_path))


if __name__ == '__main__':
    unittest.main()
