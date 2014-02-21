#-*-coding:utf-8-*-

"""
Copyright (c) 2012 wong2 <wonderfuly@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the
'Software'), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED 'AS IS', WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

CHUNK_SIZE = 30

def enctypt(e, m, c):
    return pow(c, e, m)

def enctyptChunk(e, m, chunk):
    chunk = map(ord, chunk)

    if not len(chunk) % 2 == 0:
        chunk.append(0)

    nums = [chunk[i] + (chunk[i + 1] << 8) for i in range(0, len(chunk), 2)]

    c = sum([n << i * 16 for i, n in enumerate(nums)])

    encypted = enctypt(e, m, c)

    return hex(encypted)[2:]

def encryptString(e, m, s):
    e, m = int(e, 16), int(m, 16)

    chunks = [s[:CHUNK_SIZE], s[CHUNK_SIZE:]] if len(s) > CHUNK_SIZE else [s]

    result = [enctyptChunk(e, m, chunk) for chunk in chunks]
    return ' '.join(result)[:-1]

if __name__ == '__main__':
    print encryptString('10001', '856381005a1659cb02d13f3837ae6bb0fab86012effb3a41c8b84badce287759', 'abcdef')
