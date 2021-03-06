from mido import MidiFile, MidiTrack, Message
import numpy as np
import os
import util

num_notes = 96
samples_per_measure = 96

def midi_to_samples(fname):
    has_time_sig = False
    mid = MidiFile(fname)

    ticks_per_beat = mid.ticks_per_beat
    ticks_per_measure = 4 * ticks_per_beat

    for track in mid.tracks:
        for msg in track:
            if msg.type == 'time_signature':
                new_tpm = msg.numerator * ticks_per_beat * 4 / msg.denominator
                if has_time_sig and new_tpm != ticks_per_measure:
                    raise NotImplementedError('Multiple time signatures not supported')
                ticks_per_measure = new_tpm
                has_time_sig = True

    all_notes = {}
    for track in mid.tracks:
        abs_time = 0
        for msg in track:
            abs_time += msg.time

            # programs 0x70-0x7F are percurssion and sound effects
            # we ignore them
            if msg.type == 'program_change' and msg.program >= 0x70:
                break

            if msg.type == 'note_on':
                if msg.velocity == 0:
                    continue
                note = msg.note - (128 - num_notes)/2
                if note < 0 or note >= num_notes:
                    print('Ignoring', fname, 'note is outside 0-%d range' % (num_notes - 1))
                    return []
                    
                if note not in all_notes:
                    all_notes[note] = []
                else:
                    single_note = all_notes[note][-1]
                    if len(single_note) == 1:
                        single_note.append(single_note[0] + 1)
                all_notes[note].append([abs_time * samples_per_measure / ticks_per_measure])
            elif msg.type == 'note_off':
                if len(all_notes[note][-1]) != 1:
                    continue
                all_notes[note][-1].append(abs_time * samples_per_measure / ticks_per_measure)
    for note in all_notes:
        for start_end in all_notes[note]:
            if len(start_end) == 1:
                start_end.append(start_end[0] + 1)
    samples = []
    for note in all_notes:
        for start, end in all_notes[note]:
            sample_ix = int(start / samples_per_measure)
            assert(sample_ix < 1024*1024)
            while len(samples) <= sample_ix:
                samples.append(np.zeros((samples_per_measure, num_notes), dtype=np.uint8))
            sample = samples[sample_ix]
            start_ix = int(start - sample_ix * samples_per_measure)
            if False:
                end_ix = min(end - sample_ix * samples_per_measure, samples_per_measure)
                while start_ix < end_ix:
                    sample[start_ix, note] = 1
                    start_ix += 1
            else:
                sample[start_ix, int(note)] = 1
    return samples

def samples_to_midi(samples, fname, ticks_per_sample, thresh=0.5):
    mid = MidiFile()
    track = MidiTrack()
    mid.tracks.append(track)
    ticks_per_beat = mid.ticks_per_beat
    ticks_per_measure = 4 * ticks_per_beat
    ticks_per_sample = ticks_per_measure / samples_per_measure
    abs_time = 0
    last_time = 0
    for sample in samples:
        for y in range(sample.shape[0]):
            abs_time += ticks_per_sample
            for x in range(sample.shape[1]):
                note = x + (128 - num_notes)/2
                if sample[y,x] >= thresh and (y == 0 or sample[y-1,x] < thresh):
                    delta_time = abs_time - last_time
                    track.append(Message('note_on', note=int(note), velocity=127, time=int(delta_time)))
                    last_time = abs_time
                if sample[y,x] >= thresh and (y == sample.shape[0]-1 or sample[y+1,x] < thresh):
                    delta_time = abs_time - last_time
                    track.append(Message('note_off', note=int(note), velocity=127, time=int(delta_time)))
                    last_time = abs_time
    mid.save(fname)

