def duration_score(user_start, user_end, ref_start, ref_end):
    user_dur = user_end - user_start
    ref_dur = ref_end - ref_start

    if user_dur <= 0 or ref_dur <= 0:
        return 0

    ratio = min(user_dur, ref_dur) / max(user_dur, ref_dur)
    return int(ratio * 100)
