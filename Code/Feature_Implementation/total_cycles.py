def count_consecutive_ones(pvc_list):
    count = 0
    seq_lengths = []
    i = 0
    while i < len(pvc_list):
        if pvc_list[i] == 1:
            # Count the length of the sequence
            seq_len = 1
            for j in range(i+1, len(pvc_list)):
                if pvc_list[j] == 1:
                    seq_len += 1
                else:
                    break
            
            # If the sequence is long enough, increment the count and store the length
            if seq_len >= 2:
                count += 1
                seq_lengths.append(seq_len)
            
            # Advance the index
            i += seq_len
        else:
            i += 1
    
    return count, seq_lengths