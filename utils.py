def get_qr_version(qr):
    n = len(qr)
    return ((n - 21) // 4) + 1 if n >= 21 else 1

def get_alignment_centers(version, n):
    if version == 1:
        return []
    # Number of alignment patterns: floor(version/7) + 2.
    num_align = version // 7 + 2
    if num_align == 2:
        return [6, n - 7]
    # Step between centers (calculated so that the first is at 6 and the last at n-7)
    step = (n - 13) // (num_align - 1)
    centers = [6]
    for i in range(1, num_align - 1):
        centers.append(6 + i * step)
    centers.append(n - 7)
    return centers

# reserved = None
def get_reserved_matrix(qr):
    # global reserved
    # if reserved is not None:
    #     return reserved
    
    n = len(qr)
    version = get_qr_version(qr)

    # Matrix 'reserved' will be True on reserved (function) positions, False on data positions.
    reserved = [[False for _ in range(n)] for _ in range(n)]

    def mark_rect(r1, r2, c1, c2):
        for i in range(r1, r2 + 1):
            for j in range(c1, c2 + 1):
                reserved[i][j] = True

    # === Mark function zones ===

    # 1. Finder patterns + separators
    # By standard, the modules in a 9x9 area are considered reserved at each corner
    # (except the bottom-right corner, where the separator is not repeated)
    mark_rect(0, 8, 0, 8)               # top-left
    mark_rect(0, 8, n - 8, n - 1)       # top-right
    mark_rect(n - 8, n - 1, 0, 8)       # bottom-left

    # 2. Timing patterns (horizontal and vertical lines)
    # The timing lines are on row 6 and column 6, outside the already reserved zones
    # (we use the limit: from 8 to n-9, if it exists)
    if n - 9 >= 8:
        mark_rect(6, 6, 8, n - 9)  # timing orizontal
        mark_rect(8, n - 9, 6, 6)  # timing vertical

    # 3. Format information
    # These are located near the finder patterns
    # – Vertical zone: column 8, rows 0..8 and rows n-8..n-1
    # – Horizontal zone: row 8, columns 0..8 and columns n-8..n-1
    for i in range(9):
        reserved[8][i] = True
        reserved[i][8] = True
    for j in range(n - 8, n):
        reserved[8][j] = True
    for i in range(n - 8, n):
        reserved[i][8] = True

    # 4. Alignment patterns (for versions >=2)
    if version >= 2:
        centers = get_alignment_centers(version, n)
        # For each pair (r, c) (alignment center), mark a 5x5 block (centered at (r, c)),
        # except when it overlaps with an eye.
        for r in centers:
            for c in centers:
                # If the center coincides with an eye, it is skipped.
                if (r, c) in ((6, 6), (6, n - 7), (n - 7, 6)):
                    continue
                r1, r2 = max(r - 2, 0), min(r + 2, n - 1)
                c1, c2 = max(c - 2, 0), min(c + 2, n - 1)
                mark_rect(r1, r2, c1, c2)

    # 5. Version information (for versions >=7)
    if version >= 7:
        # The version is encoded in two 3x6 areas:
        mark_rect(0, 5, n - 11, n - 9)  # top-right
        mark_rect(n - 11, n - 9, 0, 5)  # bottom-left

    # 6. Dark module
    dark_module_row = 4 * version + 9
    dark_module_col = 8
    if dark_module_row < n:
        reserved[dark_module_row][dark_module_col] = True

    return reserved

def matrix_timing_patterns(matrixQR):
    length_timing_patterns = len(matrixQR) - 16
    for i in range(8, len(matrixQR) - 8):
        matrixQR[i][6] = 1 if i%2 == 0 else 0
    for j in range(8, len(matrixQR) - 8):
        matrixQR[6][j] = 1 if j%2 == 0 else 0

def get_matrix_write(matrixQR):
    n = len(matrixQR)
    version = get_qr_version(matrixQR)
    matrixQR = [[0 for _ in range(n)] for _ in range(n)]
    
    matrix_EyE = [  [1, 1, 1, 1, 1, 1, 1],
                    [1, 0, 0, 0, 0, 0, 1],
                    [1, 0, 1, 1, 1, 0, 1],
                    [1, 0, 1, 1, 1, 0, 1],
                    [1, 0, 1, 1, 1, 0, 1],
                    [1, 0, 0, 0, 0, 0, 1],
                    [1, 1, 1, 1, 1, 1, 1]]
    matrix_Alignment = [ [1, 1, 1, 1, 1],
                         [1, 0, 0, 0, 1],
                         [1, 0, 1, 0, 1],
                         [1, 0, 0, 0, 1],
                         [1, 1, 1, 1, 1]]

    def mark_rect(matrix_Eye, matrixQR, points):
        n = len(matrixQR)
        
        def make_eye(ii, jj, matrixEye, matrixQR):
            for i in range(0, len(matrixEye)):
                jjj = jj
                for j in range(0, len(matrixEye)):
                    matrixQR[ii][jjj] = matrixEye[i][j]
                    jjj += 1
                ii += 1

        # top left
        for point in points:
            make_eye(point[0], point[1], matrix_Eye, matrixQR)

    # 1. Finder patterns    
    mark_rect(matrix_EyE,matrixQR, [(0, 0), (0, n-7), (n-7, 0)])
    
    centers = get_alignment_centers(version, n)
    for r in centers:
        for c in centers:
            # If the center coincides with an eye, it is skipped.
            if (r, c) in ((6, 6), (6, n - 7), (n - 7, 6)):
                continue
            r1 = max(r - 2, 0) 
            c1 = max(c - 2, 0)
            mark_rect(matrix_Alignment, matrixQR, [(r1, c1)])

    matrix_timing_patterns(matrixQR)

    #  Dark module
    dark_module_row = 4 * version + 9
    dark_module_col = 8
    if dark_module_row < n:
        matrixQR[dark_module_row][dark_module_col] = 1



    # print( "patterns:  ")
    # for line in matrixQR:
    #     print ("[", end = "")
    #     for elem in line:
    #         if elem == True:
    #             print(elem,"",end = "")
    #         else:
    #             print(elem,"",end = "")
    #     print ("]")
    #
    return matrixQR
