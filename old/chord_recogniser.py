from instrument import *

def is_pretty_int(num : float, precision) -> bool:
    return abs(num - round(num)) <= precision

def count_median(instruments : list) -> list:
    res = {}
    count = {}
    for index, instrument in enumerate(instruments):
        old_harms = instrument.harmonics[:]
        instrument.revise_harmonics()
        if instrument.harmonics != old_harms:
            print(old_harms, instrument.harmonics)
        for peak in instrument.harmonics:
            if is_pretty_int(peak[0], 0.1) and peak[1] >= 0.01 and round(peak[0]) < 10:
                if round(peak[0]) in res:
                    res[round(peak[0])] += peak[1]
                    count[round(peak[0])] += 1
                else:
                    res[round(peak[0])] = peak[1]
                    count[round(peak[0])] = 1
    print(res, "\n", count)
    res_instr = Instrument(_harmonics = [(i, res[i]) for i in res])
    print(res_instr.harmonics)
    res_instr.to_file("Instruments\\piano_median.instrument")
    res_instr.play_to_file("Music_res\\Piano_res.wav")


def dummy_detect_chord(chord_instr : Instrument, base_instrument : Instrument, num_notes : int) -> list:
    res = [None for _ in range(num_notes)]
    coeffs = [
        (None, None) for _ in range(num_notes) # (Scaling factor; offset)
    ]



if __name__ == "__main__":
    count_median(get_folder_instruments("Instruments\\Piano"))
