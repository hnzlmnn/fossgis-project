def normalize_temp(temp, height):
    # 0.65K per 100m less
    return temp + height / 100.0 * 0.65

