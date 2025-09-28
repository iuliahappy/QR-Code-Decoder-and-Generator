from utils import *

def get_mask_id(qr):
    length_black = 0
    stop = 0
    for row_index in range(0, len(qr)):
        for column_index in range(0, len(qr[row_index])):
            if qr[row_index][column_index] != 1:
                stop = 1
                break
            length_black += 1
        if stop == 1:
            break

    # jump over the white line
    length_black = length_black + 1

    primitive_mask = [1, 0, 1, 0, 1]
    coded_mask_id = []
    decoded_mask_id = []

    for column_index in range(0, 5):
        coded_mask_id.append(qr[length_black][column_index])

    for i in range(len(coded_mask_id) ):
        decoded_mask_id.append( coded_mask_id[i] ^ primitive_mask[i] )

    # first two bits are for error correction, so we drop them
    decoded_mask_id.pop(0)
    decoded_mask_id.pop(0)

    return decoded_mask_id

def is_bit_flipped(mask_code, row_index, column_index):
    if mask_code == [0, 0, 0]:
        return (row_index + column_index) % 2 == 0
    elif mask_code == [0, 0, 1]:
        return row_index % 2 == 0
    elif mask_code == [0, 1, 0]:
        return column_index % 3 == 0
    elif mask_code == [0, 1, 1]:
        return (row_index + column_index) % 3 == 0
    elif mask_code == [1, 0, 0]:
        return (row_index // 2 + column_index // 3) % 2 == 0
    elif mask_code == [1, 0, 1]:
        return ((row_index * column_index) % 2 + (row_index * column_index) % 3) == 0
    elif mask_code == [1, 1, 0]:
        return (((row_index * column_index) % 2 + (row_index * column_index) % 3) % 2) == 0
    elif mask_code == [1, 1, 1]:
        return (((row_index + column_index) % 2 + (row_index * column_index) % 3) % 2) == 0

def remove_mask(qr, mask):
    reserved = get_reserved_matrix(qr)
    unmasked_qr = [row[:] for row in qr]
    for i in range(len(qr)):
        for j in range(len(qr[0])):
            if not reserved[i][j] and is_bit_flipped(mask, i, j):
                unmasked_qr[i][j] = 0 if qr[i][j] == 1 else 1
    return unmasked_qr

def apply_mask_with_given_pattern(where_to_apply_matrix, qr, mask):
    # print("where_to_apply_matrix matrix:")
    
    # for line in where_to_apply_matrix:
    #     print ("[", end = "")
    #     for elem in line:
    #         if elem == True:
    #             print(1," ", end = "")
    #         else:
    #             print(0," ", end = "") 
    #     print ("]")
    unmasked_qr = [row[:] for row in qr]
    for i in range(len(qr)):
        for j in range(len(qr[0])):
            if not where_to_apply_matrix[i][j] and is_bit_flipped(mask, i, j):
                unmasked_qr[i][j] = 0 if qr[i][j] == 1 else 1
    return unmasked_qr

# Mask For writing part.
# Part for computing the best mask that is applied before writing the QR code!

def compute_QR_with_the_best_mask(qr):
    allMasks = [ [0, 0, 0], [0, 0, 1], [0, 1, 0], [0, 1, 1], [1, 0, 0], [1, 0, 1], [1, 1, 0], [1, 1, 1] ]
    lowestScore = 9999999999999999999999999
    
    whereToApplyMatrix = []
    for i in range(0, len(qr)):
        whereToApplyMatrix.append([])
        for j in range(0, len(qr[0])):
            whereToApplyMatrix[i].append(False)  # False means that the element will be processed    



    indexMask = -1
    for k in range(0, len(allMasks)):
        matrixToProcess = [row[:] for row in qr]
        currentMatrixComputed = apply_mask_with_given_pattern(whereToApplyMatrix, matrixToProcess, allMasks[k])
        currentScoreM1 = compute_score_for_evaluation1(currentMatrixComputed)
        #print ( "Score method1 = ", currentScoreM1, " for mask  ", allMasks[k] )
        
        currentScoreM2 = compute_score_for_evaluation2(currentMatrixComputed)
        #print ( "Score method2 = ", currentScoreM2, " for mask  ", allMasks[k] )

        currentScoreM3 = compute_score_for_evaluation3(currentMatrixComputed)
        #print ( "Score method3 = ", currentScoreM3, " for mask  ", allMasks[k] )

        currentScoreM4 = compute_score_for_evaluation4(currentMatrixComputed)
        #print ( "Score method4 = ", currentScoreM4, " for mask  ", allMasks[k] )

        currentScore = currentScoreM1 + currentScoreM2 + currentScoreM3 + currentScoreM4
        # print ( "Score TOTAL = ", currentScore, " for mask  ", allMasks[k] )
        # Todo add the other 3 methods
        if currentScore < lowestScore:
            lowestScore = currentScore
            indexMask = k

    if k < 0:
        print("Error indexMask is ", k)


    whereToApplyMatrix = get_reserved_matrix(qr)
    return (allMasks[indexMask], apply_mask_with_given_pattern(whereToApplyMatrix, qr, allMasks[indexMask]))

def compute_score_for_evaluation1(matrix_to_process):
    height = len(matrix_to_process)
    penalty = 0

    currentColor = -1
    nrConsecutive = 0
    # iterating each line
    for i in range(0, len(matrix_to_process)):
        for j in range(0, len(matrix_to_process[0])):
            if matrix_to_process[i][j] == 1:
                if currentColor == 1:    
                    nrConsecutive += 1
                    if nrConsecutive == 5:
                        penalty += 3
                    elif nrConsecutive > 5:
                        penalty += 1
                else:
                    nrConsecutive = 0
                    currentColor = 1
            elif matrix_to_process[i][j] == 0:
                if currentColor == 0:    
                    nrConsecutive += 1
                    if nrConsecutive == 5:
                        penalty += 3
                    elif nrConsecutive > 5:
                        penalty += 1
                else:
                    nrConsecutive = 0
                    currentColor = 0

    # for each column
    for i in range(0, len(matrix_to_process)):
        for j in range(0, len(matrix_to_process[0])):
            if matrix_to_process[j][i] == 1:
                if currentColor == 1:    
                    nrConsecutive += 1
                    if nrConsecutive == 5:
                        penalty += 3
                    elif nrConsecutive > 5:
                        penalty += 1
                else:
                    nrConsecutive = 0
                    currentColor = 1
            elif matrix_to_process[j][i] == 0:
                if currentColor == 0:    
                    nrConsecutive += 1
                    if nrConsecutive == 5:
                        penalty += 3
                    elif nrConsecutive > 5:
                        penalty += 1
                else:
                    nrConsecutive = 0
                    currentColor = 0

    return penalty

def compute_score_for_evaluation2(matrix_to_process):
    penalty = 0
        
    for i in range(0, len(matrix_to_process)-1):
        for j in range(0, len(matrix_to_process[0])-1):
            if matrix_to_process[i][j] == 0 and matrix_to_process[i][j+1] == 0 and matrix_to_process[i+1][j] == 0 and matrix_to_process[i+1][j+1] == 0:
                penalty += 3
            elif matrix_to_process[i][j] == 1 and matrix_to_process[i][j+1] == 1 and matrix_to_process[i+1][j] == 1 and matrix_to_process[i+1][j+1] == 1:
                penalty += 3
    
    return penalty            

def compute_score_for_evaluation3(matrix_to_process):
    penalty = 0
    # dark-light-dark-dark-dark-light-dark-light-light-light-light
    firstPattern = [1, 0, 1, 1, 1, 0, 1, 0, 0, 0, 0]
    # light-light-light-light-dark-light-dark-dark-dark-light-dark
    secondPattern = [0, 0, 0, 0, 1, 0, 1, 1, 1, 0, 1]
    # 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 

    for i in range(0, len(matrix_to_process)):
        for j in range(0, len(matrix_to_process[0])):
            nrCharacters = 0
            jj = j
            for k in range(0, len(firstPattern)):
                if jj < len(matrix_to_process[0]):
                    if firstPattern[k] == matrix_to_process[i][jj]:
                        nrCharacters += 1
                    jj += 1
            if nrCharacters == len(firstPattern):
                penalty += 40
            

    for i in range(0, len(matrix_to_process)):
        for j in range(0, len(matrix_to_process[0])):
            nrCharacters = 0
            jj = j
            for k in range(0, len(secondPattern)):
                if jj < len(matrix_to_process[0]):
                    if secondPattern[k] == matrix_to_process[jj][i]:
                        nrCharacters += 1
                    jj += 1
            if nrCharacters == len(secondPattern):
                penalty += 40
            
    return penalty
                    
def compute_score_for_evaluation4(matrix_to_process):
    
    totalNumberOfModules = len(matrix_to_process) * len( matrix_to_process)
    
    countDarkModule = 0
    for i in range(0, len(matrix_to_process)):
        for j in range(0, len(matrix_to_process[0])):
            if matrix_to_process[i][j] == 1:
                countDarkModule += 1
    
    percentage = (countDarkModule / totalNumberOfModules) * 100
    
    prevMultipleOfFive = -1
    nextMultipleOfFive = -1
    if percentage % 5 == 0:
        prevMultipleOfFive = percentage - 5
        nextMultipleOfFive = percentage + 5
    else:
        prevMultipleOfFive = (percentage // 5) * 5 
        nextMultipleOfFive = ((percentage // 5) * 5) + 5
    
    prevMod = abs(prevMultipleOfFive - 50)
    nextMod = abs(nextMultipleOfFive - 50)
    
    prevMod = prevMod / 5
    nextMod = nextMod / 5
    
    penalty = int(prevMod * 10 if prevMod < nextMod else nextMod * 10)
    
    return penalty