import midi
import os
import os.path
import traceback
import util
import numpy as np

# input directories
dirs = ['samples/']

patterns = {}
all_samples = []
all_lens = []
succ = 0
failed = 0
ignored = 0
for dir in dirs:
    for root, subdirs, files in os.walk(dir):
        for f in files:
            path = os.path.join(root, f)
            if not (path.lower().endswith('.mid') or path.lower().endswith('.midi')):
                continue
            try:
                samples = midi.midi_to_samples(path)
            except Exception as e:
                print('ERROR', f, e, traceback.format_exc())
                failed += 1
                continue
            if len(samples) < 16:
                print('WARN', f, 'Sample too short, unused')
                ignored += 1
                continue
            samples, lens = util.generate_add_centered_transpose(samples)
            all_samples += samples
            all_lens += lens
            print('SUCCESS', f, len(samples), 'samples')
            succ += 1
    
print('Saving', len(all_samples), 'samples')
assert(sum(all_lens) == len(all_samples))
all_samples = np.array(all_samples, dtype=np.uint8)
all_lens = np.array(all_lens, dtype=np.uint32)
if not os.path.exists('input'):
    os.makedirs('input')
np.save('input/samples.npy', all_samples)
np.save('input/lengths.npy', all_lens)
print('Done', succ, 'succeded', ignored, 'ignored', failed, 'failed of', succ+ignored+failed, 'in total')

