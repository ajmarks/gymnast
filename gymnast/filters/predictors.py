"""
Compression predictors for LZW and Flate.

See:
    Basic PDF information - Reference pp. 75-77
    PDF Predictors - http://www.w3.org/TR/PNG-Filters.html
    TIFF Predictor - <TODO>

IDEA: Consider replacing this with something like pypng
"""

from __future__ import division
from ..misc import int_to_bytes
import io
import math

__all__ = ['predictor_decode', 'predictor_encode']

def predictor_decode(data, predictor_id, params):
    """Decode the data using the appropriate predictor filter"""
    if predictor_id == 1:
        return data
    elif predictor_id == 2:
        raise NotImplementedError('TIFF predictor not yet implemented')
    elif 10 <= predictor_id <= 15:
        # PNG predictors.  Subtracting 10 to turn it into a W3C standard PNG
        # predictor number
        return png_predictor_decode(data, params, predictor_id - 10)
    else:
        raise ValueError('Invalid predictor number')

def png_predictor_decode(data, params, predictor=None):
    """Decode the entire data string with the specified PNG predictor.
    See http://www.w3.org/TR/PNG-Filters.html"""
    if predictor is None:
        predictor = params.get('Predictor', 11) - 10
    if not (1 <= predictor <= 5):
        raise ValueError('Invalid PNG predictor')

    columns   = params.get('Columns', 1)
    early_change = bool(params.get('EarlyChange', 1))

    # Break up the data into samples
    bpp = math.ceil(params.get('BitsPerComponent',8)*params.get('Colors', 1)/8)
    rec_size = bpp*columns+1
    samples = [(n, data[i], bytearray(data[i+1:i+rec_size]))
               for n, i in enumerate(range(0, len(data), rec_size))]
    prev_sample = None
    results = [None]*len(samples)
    for n, pred, sample in samples:
        if predictor == 5:
            predictor = pred
        prev_sample = png_decode_sample(pred, sample, bpp, prev_sample)
        results[n] = prev_sample
    return [bytes(s) for s in results]

def png_decode_sample(pred, sample, bpp, prev_sample=None):
    """Decode an individual sample using the specified PNG predictor.

    Arguments:
        pred: The PNG predictor number
        sample: bytearray with the sample data
        bpp: The number of bytes per pixel
        prev_sample: The previous sample, if applicable"""
    # Variable name conventions for bytes in the comprehensions:
    #   r  - Raw
    #   l  - Corresponding byte in pixel to the left
    #   u  - Corresponding byte in pixel above (up)
    #   ul - Corresponding byte in pixel up and to the left
    if prev_sample is None:
        prev_sample = bytearray(len(sample))
    lefts = bytearray(bpp)+sample[bpp:]
    if   pred == 0: # PNG None
        return sample
    elif pred == 1: # PNG Sub
        return bytearray((r + l) % 256 for r, l in zip(sample, lefts))
    elif pred == 2: # PNG Up
        return bytearray((r + u) % 256 for r, u in zip(prev_sample, sample))
    elif pred == 3: # PNG Average
        return bytearray((r + (l + u)//2) % 256
                         for r, l, u in zip(sample, lefts, prev_sample))
    elif pred == 4: # PNG Paeth
        up_lefts = bytearray(b'\x00'*bpp)+prev_sample[bpp:]
        return bytearray((r + paeth_decode(l, u, ul)) % 256
                         for r, l, u, ul in zip(sample, lefts, prev_sample, up_lefts))
    raise ValueError('Invalid PNG predictor')

def paeth_decode(left, up, up_left):
    """Paeth predictor decoding.  Returns whichever argument is closest to
    left + up - up_left, prefering left over up and up over up_left in ties."""
    est = left + up - up_left
    e_left = abs(est - left)
    e_up   = abs(est - up)
    e_ul   = abs(est - up_left)
    min_err = min((e_left, e_up, e_ul))
    if e_left == min_err:
        return left
    elif e_up == min_err:
        return up
    return up_left

def predictor_encode(samples, predictor_id, params):
    """Encode the data using the appropriate predictor filter"""
    if predictor_id == 1:
        return samples
    elif predictor_id == 2:
        raise NotImplementedError('TIFF predictor not yet implemented')
    elif 10 <= predictor_id <= 15:
        # PNG predictors
        return png_predictor_encode(samples, params, predictor_id)
    else:
        raise ValueError('Invalid predictor number')

def png_predictor_encode(samples, params, predictor=None, sample_predictors=None):
    """Decode the entire data string with the specified PNG predictor."""
    results = io.BytesIO()
    if predictor is None:
        predictor = params.get('Predictor', 11) - 10
    if not (1 <= predictor <= 5):
        raise ValueError('Invalid PNG predictor')
    colors    = params.get('Colors', 1)
    comp_bits = params.get('BitsPerComponent', 8)
    columns   = params.get('Columns', 1)
    early_change = bool(params.get('EarlyChange', 1))

    bpp = round(colors*comp_bits*columns/8 + .5)

    results = [None]*len(samples)
    if predictor == 5:
        if len(sample_predictors) != len(samples):
            raise ValueError('PNG Optimal requires a filter for each sample')
    elif sample_predictors is not None:
        raise ValueError('Sample filters can only be specified with the PNG Optimal filter')
    else:
        sample_predictors = (predictor for s in samples)
    results = [None]*len(samples)
    prev_sample = None
    rows = ((p, s) for p, s in zip(sample_predictors, samples))
    for pred, sample in rows:
        prev_sample = png_encode_sample(pred, sample, bpp, prev_sample)
        results.write(int_to_bytes(pred, 1)+bytes(prev_sample))
    return results.getvalue()

def png_encode_sample(pred, sample, bpp, prev_sample=None):
    """Encode an individual sample using the specified PNG predictor

    Arguments:
        pred: The PNG predictor number
        sample: bytearray with the sample data
        bpp: The number of bytes per pixel
        prev_sample: The previous sample, if applicable"""
    # Variable name conventions for bytes in the comprehensions:
    #   r  - Raw
    #   l  - Corresponding byte in pixel to the left
    #   u  - Corresponding byte in pixel above (up)
    #   ul - Corresponding byte in pixel up and to the left
    if prev_sample is None:
        prev_sample = bytearray(len(sample))
    lefts = bytearray(bpp)+sample[bpp:]
    if   pred == 0: # PNG None
        return sample
    elif pred == 1: # PNG Sub
        return bytearray((r - l) % 256 for r, l in zip(sample, lefts))
    elif pred == 2: # PNG Up
        return bytearray((r - u) % 256 for r, u in zip(prev_sample, sample))
    elif pred == 3: # PNG Average
        return bytearray((r - (l + u)//2) % 256
                         for r, l, u in zip(sample, lefts, prev_sample))
    elif pred == 4: # PNG Paeth
        up_lefts = bytearray(b'\x00'*bpp)+prev_sample[bpp:]
        return bytearray((r - paeth_decode(l, u, ul)) % 256
                         for r, l, u, ul in zip(sample, lefts, prev_sample, up_lefts))
    raise ValueError('Invalid PNG predictor')
