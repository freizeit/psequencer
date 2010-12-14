#!/usr/bin/env python
# encoding: utf-8

"""
Copyright (c) 2010, Muharem Hrnjadovic

All rights reserved.

Redistribution and use in source and binary forms, with or without 
modification, are permitted provided that the following conditions
are met:

    * Redistributions of source code must retain the above copyright notice,
      this list of conditions and the following disclaimer.
    * Redistributions in binary form must reproduce the above copyright
      notice, this list of conditions and the following disclaimer in the
      documentation and/or other materials provided with the distribution.
    * Neither the name of Muharem Hrnjadovic nor the names of other
      contributors may be used to endorse or promote products derived from
      this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR
CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

---------------------------------------------------------------------------

File name sequencer. Usage:

    sequencer [path]
"""

# Copyright: (c) 2010 Muharem Hrnjadovic
# created: Sun, 17 Oct 2010 21:04:19 +0200

import logging
logging.basicConfig(level=logging.INFO)
import os
import re
import scriptutil


sequenced_file_regex = re.compile("^(\d+)-")


def next_seqnum(file_names):
    """
    Return the minimum unused sequence number given a list of files.

    @param file_names: a list of file names in the directory of interest.
    @return: the maximum sequence number found in the C{file_names} list
        plus one.
    """
    matches = filter(
        None, [sequenced_file_regex.search(name) for name in file_names])
    numbers = [int(match.group(1)) for match in matches]
    number = max(numbers) + 1 if numbers else 1
    return number


def get_unsequenced_files(file_names):
    """
    Return the file names that need a numeric sequence prepended to them.
    """
    return filter(
        lambda s: not sequenced_file_regex.search(s), file_names)


audio_file_regex = re.compile("\.(flac|ogg|mp3|mpa)$")


def get_audio_files(path):
    """
    Return a list of plain file with audio extensions.
    """

    def file_filter(s):
        """True for plain files with an audio extension."""
        return (
            os.path.isfile(s) and not os.path.islink(s) and
            audio_file_regex.search(s))

    audio_files = scriptutil.ffind(path, namefs=(file_filter,))
    return [os.path.basename(audio_file) for audio_file in audio_files]


def sequence_files(sequence_number, path, unsequenced_files, width=5):
    """
    Prepends a numeric sequence number to the file names given.

    @param path: the next available sequence number.
    @param path: the path to the files in question.
    @param unsequenced_files: a list of unsequenced file names.
    @param width: the width of the numeric prefix
    @raises RuntimeError: when the prefix width is too small to hold the
        sequence number.
    """
    template = "%%0%sd-%%s" % width
    os.chdir(path)
    for old_name in unsequenced_files:
        if len(str(sequence_number)) > width:
            raise RuntimeError("Prefix width too small for sequence number.")
        new_name = template % (sequence_number, old_name)
        logging.info("  -> %s" % new_name)
        os.rename(old_name, new_name)
        os.symlink(new_name, old_name)
        sequence_number += 1


def run(path):
    """
    Find plain audio files in the given directory and prepend them with a
    numeric sequence ("NNNNN-") if needed.

    Also, create a symbolic link with the old name to the newly sequenced
    files.
    """
    files = get_audio_files(path)
    unsequenced = get_unsequenced_files(files)
    if not unsequenced:
        logging.info("No unsequenced files. Done.")
        return
    sequence_number = next_seqnum(files)
    sequence_files(sequence_number, path, sorted(unsequenced))


if __name__ == '__main__':
    import sys
    cwd = os.path.abspath(os.path.curdir)
    for path in sys.argv[1:]:
        if not os.path.isdir(path):
            logging.error("\"%s\" does not exist or is not a directory" % path)
            continue
        logging.info("+> %s" % path)
        run(path)
        os.chdir(cwd)
