def total_pvc(pvc_list, time=30):
      pvcs = sum([pvc == 1 for pvc in pvc_list])
      return pvcs