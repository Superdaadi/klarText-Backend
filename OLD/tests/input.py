from pronunce_score.adapters.mfa import load_ctm

user_segments = load_ctm("example.ctm")
ref_segments = load_ctm("example.ctm")

aligned = list(zip(user_segments, ref_segments))
