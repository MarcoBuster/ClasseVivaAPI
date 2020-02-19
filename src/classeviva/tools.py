# This file is a part of Classe Viva Python API
#
# Copyright (c) 2017 The Classe Viva Python API Authors (see AUTHORS)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os


def download_didactics(session, root: str = "didactics", flatten: bool = False):
    """
    Download all didactics files in the following hierarchy: teacher/folder/file
    :param root: folder where to save the files
    :param flatten: If true will flatten the file hierarchy
    :type root: str
    :type flatten: bool
    """

    def _sanitize_filename(filename: str):
        return filename.replace('/', '-')

    format_string = '{}/{}/{}/{}' if not flatten else '{0}/{3}'

    os.makedirs(root)

    for teacher in session.didactics()['didacticts']:
        teacher_name = _sanitize_filename(teacher['teacherName'])
        for folder in teacher['folders']:
            folder_name = _sanitize_filename(folder['folderName'])
            if not flatten:
                os.makedirs('{}/{}/{}'.format(root, teacher_name, folder_name), exist_ok=True)
            for content in folder['contents']:
                if content['objectType'] == 'file':
                    content_name = _sanitize_filename(content['contentName'])
                    file_name = format_string.format(root, teacher_name, folder_name, content_name)
                    if not os.path.exists(file_name):
                        with open(file_name, 'wb') as f:
                            f.write(session._raw_request('didactics', 'item', content['contentId']).content)
