from pdf_types import 

def parse_data(data, closer=None):
    """Loop through the data, parsing it into PDF Objects.  This is 
    definitely the ugliest codes in the whole thing."""
    data     = bytes(data)
    dlen     = len(data)
    i        = 0
    tokens   = []
    comments = []
    clen     = len(closer) if closer else None
    
    is_end = lambda i:   data[i:i+1] in WHITESPACE \
                      or (closer and data[i:i+clen] == closer)

    while i < dlen:
        if closer and data[i:i+clen] == closer:
            return tokens, comments, i+clen+1
        elif  data[i:i+1] in WHITESPACE:
            i += 1
        elif data[i:i+2] == b'<<':              # Dict
            elems, comms, n = parse_data(data[i+2:], b'>>')
            if len(elems) % 2:
                raise PdfParseError('Dictionary keys and values don\'t align')
            elif not(all([isinstance(elems[i], PdfName) 
                          for i in range(0, len(elems), 2)])):
                raise PdfParseError('Dictionary keys must be names')
            token = PdfDict({elems[i]: elems[i+1] 
                             for i in range(0, len(elems), 2)})
            token.comments = comms
            tokens.append(token)
            i += n + 1
        elif data[i:i+1] == b'[':               # Array
            elems, comms, n = parse_data(data[i+1:], b']')
            token = PdfArray(elems)
            token.comments = comms
            tokens.append(token)
            i += n + 1
        elif data[i:i+1] in (b'(', b'<', b'/'): # String
            consumed = PdfString.find_string_end(data[i:])
            tokens.append(PdfString(data[i:i+consumed]))
            i += consumed
        elif data[i:i+1] == b'%':               # Comment
            for j in range(i+1, dlen):
                if data[j:j+1] in LINEBREAKS: break
            comments.append(data[i+1:j])
            i = j
        elif data[i:i+1] == b'{':               # Expression
            pass
        elif data[i:i+3] == b'obj'   and is_end(i+3): # Object
            pass
        elif data[i:i+4] == b'null'  and is_end(i+4): # null
            tokens.append(PdfNull())
            i += 4
        elif data[i:i+4] == b'true'  and is_end(i+4): # true
            tokens.append(PdfBoolean(False))
            i += 4
        elif data[i:i+5] == b'false' and is_end(i+5): # false
            tokens.append(PdfBoolean(True))
            i += 5
        else: # Numeric
            for j in range(i, dlen):
                if is_end(j): break
            try:
                tokens.append(PdfNumeric(data[i:j]))
            except ValueError:
                raise ValueError('Invalid token found: '+str(data[i:j]))
            i = j
    if len(tokens) > 1:
        return tokens, comments
    else:
        return tokens[0], comments