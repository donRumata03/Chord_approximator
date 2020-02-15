import math

import numpy as np
from matplotlib import pyplot as plt
from fft_test import get_fft, get_file_fft
from cleaner import delete_rubbish, zero_split
from graphic_smoother import *

INF = 2 << 30


class peek_detect_params:
    noise_edge : float = None
    sigma : float = None
    big_amp_diff : float
    neigh_value : float
    peek_edge : float
    frame_width : float
    very_little_neigh_value : float

    def __init__(self, noise_edge, sigma, big_amp_diff = 1.5, neigh_value = 1.3, peek_edge = 1., frame_width = 1., very_little_neigh_value = 1.1):
        self.noise_edge = noise_edge
        self.sigma = sigma
        self.big_amp_diff = big_amp_diff
        self.neigh_value = neigh_value
        self.peek_edge = peek_edge
        self.frame_width = frame_width
        self.very_little_neigh_value = very_little_neigh_value


def detect_peek_candidates(spectrum, percent_noise_edge = 0.001, percent_sigma = 0.005,
                           percent_frame_width = 1, edge_peek_k = 1.5,
                           very_little_neigh_value = None, neigh_value = None, debug = False):
    log_clear_spectrum = delete_rubbish(spectrum, percent_noise_edge)

    log_res = []
    # smoothed = smooth_graph(clear_spectrum, 1, 1)
    splitted = zero_split(log_clear_spectrum)

    nonzeros = []
    for i in splitted:
        nonzeros.extend(i)

    log_nonzero_smoothed = smooth_graph_as_exp(nonzeros, percent_sigma, percent_frame_width)
    log_little_smoothed = smooth_graph_as_exp(nonzeros, percent_sigma * 2, percent_frame_width)

    corresponding_index = 0

    for index, sample in enumerate(log_clear_spectrum):
        while log_nonzero_smoothed[corresponding_index][0] < sample[0]:
            if corresponding_index != len(log_nonzero_smoothed) - 1:
                corresponding_index += 1
            else:
                break

        if index != 0 and sample[1] > log_clear_spectrum[index - 1][1] \
                and index != len(log_clear_spectrum) - 1 and sample[1] > log_clear_spectrum[index + 1][1] \
                and sample[1] > log_nonzero_smoothed[corresponding_index][1] * edge_peek_k:
            log_res.append((index, sample[0], sample[1]))

    res, integral = filter_possible_peeks(spectrum, [(np.exp(s1), s2) for index, s1, s2 in log_res],
                                very_little_neigh_value=very_little_neigh_value, neigh_value=neigh_value,
                                islands=[get_exponentated_graph_x(s) for s in splitted], debug=True)



    if debug:
        nonzero_smoothed = get_exponentated_graph_x(log_nonzero_smoothed)
        little_smoothed = get_exponentated_graph_x(log_little_smoothed)
        clear_spectrum = get_exponentated_graph_x(log_clear_spectrum)
        # nonzero_smoothed = log_nonzero_smoothed
        # clear_spectrum = log_clear_spectrum

        peeks_xs = []
        peeks_ys = []


        i_peeks_xs = []
        i_peeks_ys = []


        for s in res:
            peeks_xs.append(s[0])
            peeks_ys.append(s[1])



        for s in integral:
            i_peeks_xs.append(s[0])
            i_peeks_ys.append(s[1])


        """
        for s in splitted:
            this_splitted_xs = []
            this_splitted_ys = []
            for i in s:
                this_splitted_xs.append(i[0])
                this_splitted_ys.append(i[1])

            plt.plot(this_splitted_xs, this_splitted_ys)
        """

        plot_tuple_graph(nonzero_smoothed)
        plt.scatter(peeks_xs, peeks_ys, edgecolors="red")
        plt.scatter(i_peeks_xs, i_peeks_ys, edgecolors="red")
        plot_tuple_graph(clear_spectrum)
        plot_tuple_graph(little_smoothed)

        plt.show()

    return res


test_samples = [
    (0, 0.5),
    (1, 2),
    (3, 3),
    (3.5, 2),
    (5, 2.7),
    (6, 0.5),
    (7, 1.5),
    (8, 0),

]


def filter_possible_peeks(spectrum : list, peeks : list, neigh_value = 1.3, big_apm_diff = 2.5, very_little_neigh_value = 1.1, integral_mode_on = True, islands = None, debug = False):
    if islands is None and integral_mode_on:
        islands = zero_split(spectrum)



    for index, (freq, amp) in enumerate(peeks):
        neighbors = enumerate(peeks) # TODO : add only some items to neighbors
        for n_index, (fn, amp_n) in neighbors:
            if n_index != index and max(fn, freq) / min(fn, freq) < very_little_neigh_value or \
                    (max(fn, freq) / min(fn, freq) < neigh_value and max(amp_n, amp) / min(amp_n, amp) > big_apm_diff):
                if amp_n > amp:
                    if not integral_mode_on:
                        peeks[n_index] = peeks[n_index][0], peeks[n_index][1] + peeks[index][1]
                    del peeks[index]
                else:
                    if not integral_mode_on:
                        peeks[index] = peeks[index][0], peeks[n_index][1] + peeks[index][1]
                    del peeks[n_index]

    simple_peek_sum = sum(np.array(peeks).T[1])

    integral_peeks = []
    for isl_index, island in enumerate(islands):
        isl_beg = island[0][0]
        isl_end = island[-1][0]

        isl_points = [p for p in peeks if isl_beg <= p[0] <= isl_end]
        isl_point_peek_indexes = [i for i in range(len(peeks)) if isl_beg <= peeks[i][0] <= isl_end]
        isl_point_indexes = [island.index(p) for p in isl_points]

        if not isl_points:
            continue
        elif len(isl_points) == 1:
            integral_peeks.append((isl_points[0][0], sum(np.array(island).T[1])))
        else:
            # Splitting spectrum for the points!!!
            this_isl_sum = sum(np.array(island).T[1])
            this_peek_sum = sum(np.array(isl_points).T[1])
            last_interval_min_index = 0

            prev_point_iceland_index = -1
            s_sqrt = 0
            sum0 = 0
            for index, point in enumerate(isl_points):
                this_iceland_index = isl_point_indexes[index]
                # this_point_sum = this_isl_sum * point[1] / this_peek_sum
                if index == len(isl_points) - 1:
                    this_min_index = len(island)
                else:
                    this_min_index = -1
                    for sample_index in range(this_iceland_index, isl_point_indexes[index + 1] + 1):
                        if this_min_index == -1 or island[this_min_index][1] > island[sample_index][1]:
                            this_min_index = sample_index

                s_sqrt += (point[1]) ** 0.2
                sum0 += sum(np.array(island[last_interval_min_index:this_min_index]).T[1])
                integral_peeks.append((point[0], sum(np.array(island[last_interval_min_index:this_min_index]).T[1]) * (point[1]) ** 0.2))
                last_interval_min_index = this_min_index
                prev_point_iceland_index = this_iceland_index

            new_s = 0
            for index, point in enumerate(isl_points):
                integral_peeks[isl_point_peek_indexes[index]] = integral_peeks[isl_point_peek_indexes[index]][0], integral_peeks[isl_point_peek_indexes[index]][1] / s_sqrt
                new_s += integral_peeks[isl_point_peek_indexes[index]][1]

            for index, point in enumerate(isl_points):
                integral_peeks[isl_point_peek_indexes[index]] = integral_peeks[isl_point_peek_indexes[index]][0], integral_peeks[isl_point_peek_indexes[index]][1] * sum0 / new_s



    # Normalizing peeks:
    integral_peek_sum = sum(np.array(integral_peeks).T[1])
    new_coeff = simple_peek_sum / integral_peek_sum
    for index, p in enumerate(integral_peeks):
        integral_peeks[index] = p[0], p[1] * new_coeff

    return peeks if not debug else (peeks, integral_peeks)


def detect_peeks(raw_spectrum : list, params : peek_detect_params, debug = False):
    return detect_peek_candidates(raw_spectrum, percent_noise_edge=params.noise_edge, percent_sigma=params.sigma,
                                        edge_peek_k=params.peek_edge, very_little_neigh_value=params.very_little_neigh_value, neigh_value=params.neigh_value, debug=debug)


def detect_file_peaks(filename, sample_size, sample_start, params : peek_detect_params, debug = False):
    fft_res = get_file_fft(filename, sample_size, sample_start)
    return detect_peeks(fft_res, params=params, debug=debug)

if __name__ == "__main__":
    # detect_peaks("music/guitar_test.wav", 2**13, 74000, debug=True)
    params = peek_detect_params(noise_edge=0.0005, sigma=0.3)
    detect_file_peaks("music/guitar_test.wav", 2 ** 14, 0, params, debug=True)