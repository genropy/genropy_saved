def roundToZero(v,precision=0.000000001):
    if abs(v)<precision:
        v=0.0
    return v