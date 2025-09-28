import reedsolo

def get_correction_level(qr):
    bytes = str(qr[0][8]) + str(qr[1][8])

    if bytes == "01":
        return "L"
    elif bytes == "00":
        return "M"
    elif bytes == "10":
        return "Q"
    elif bytes == "11":
        return "H"
    
    return "Unknown"

def get_ecc_codewords_count(version, ecc_level):
    lookup = {
        1: {'L': 7,  'M': 10, 'Q': 13, 'H': 17},
        2: {'L': 10, 'M': 16, 'Q': 22, 'H': 28},
        3: {'L': 15, 'M': 26, 'Q': 36, 'H': 44},
        4: {'L': 20, 'M': 36, 'Q': 52, 'H': 68},
    }
    return lookup[version][ecc_level]
    
def correct_bitstream(bitstream, version, ecc_level):
    # Add pad bits (0s) until it reaches a multiple of 8
    if len(bitstream) % 8 != 0:
        pad_length = 8 - (len(bitstream) % 8)
        # print(f"Add {pad_length} bits (0) as padding.")
        bitstream += "0" * pad_length

    # Convert the bitstream into codewords (groups of 8 bits)
    codewords = [int(bitstream[i:i+8], 2) for i in range(0, len(bitstream), 8)]
    nsym = get_ecc_codewords_count(version, ecc_level)
    try:
        rsc = reedsolo.RSCodec(nsym)
        corrected = rsc.decode(bytearray(codewords))
        corrected_bitstream = "".join(f"{byte:08b}" for byte in corrected)
        return corrected_bitstream
    except reedsolo.ReedSolomonError as e:
        print("Error at Reed–Solomon correction:", e)
        return None