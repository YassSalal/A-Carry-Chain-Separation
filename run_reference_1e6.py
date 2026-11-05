import sys, time
sys.path.insert(0, sys.argv[1])
import ccsa_ref as m
t=time.time()
for W in (32,64,128,256):
    m.random_vectors(W, 1_000_000, seed=0xCC5A)
    print(f'  elapsed {time.time()-t:.0f}s', flush=True)
