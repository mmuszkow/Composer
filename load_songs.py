import midi
import os
import traceback
import util
import numpy as np

patterns = {}
dirs = ['samples/nes', 'samples/gb']
all_samples = []
all_lens = []
print("Loading Songs...")
for dir in dirs:
	for root, subdirs, files in os.walk(dir):
		for f in files:
			path = os.path.join(root, f)
			if not (path.endswith('.mid') or path.endswith('.midi')):
				continue
			try:
				samples = midi.midi_to_samples(path)
			except Exception as e:
				print("ERROR ", path, e, traceback.format_exc())
				continue
			if len(samples) < 8:
				continue
				
			samples, lens = util.generate_add_centered_transpose(samples)
			all_samples += samples
			all_lens += lens
			print('SUCCESS', f)
	
assert(sum(all_lens) == len(all_samples))
print("Saving " + str(len(all_samples)) + " samples...")
all_samples = np.array(all_samples, dtype=np.uint8)
all_lens = np.array(all_lens, dtype=np.uint32)
np.save('samples.npy', all_samples)
np.save('lengths.npy', all_lens)
print("Done")
