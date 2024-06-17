#!/usr/bin/env python3
import time
import sys
import fasttext.util
from mlp_segmentation import mlp_preprocessor, mlp_preprocessor2

st = time.time()
ft = fasttext.load_model('cc.cs.300.bin')
mlp_preprocessor.preprocess_and_run(ft)
# mlp_preprocessor.preprocess_and_run_sigmorphon(ft)

sys.stderr.write("----%.2f s----" % (time.time() - st))
