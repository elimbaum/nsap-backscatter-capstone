#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Not titled yet
# Author: ebaum
# GNU Radio version: 3.8.3.1

from distutils.version import StrictVersion

if __name__ == '__main__':
    import ctypes
    import sys
    if sys.platform.startswith('linux'):
        try:
            x11 = ctypes.cdll.LoadLibrary('libX11.so')
            x11.XInitThreads()
        except:
            print("Warning: failed to XInitThreads()")

from PyQt5 import Qt
from gnuradio import eng_notation
from gnuradio import analog
import math
from gnuradio import blocks
from gnuradio import digital
from gnuradio import filter
from gnuradio.filter import firdes
from gnuradio import gr
import sys
import signal
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import uhd
import time
from gnuradio.qtgui import Range, RangeWidget

from gnuradio import qtgui

class top_block(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "Not titled yet")
        Qt.QWidget.__init__(self)
        self.setWindowTitle("Not titled yet")
        qtgui.util.check_set_qss()
        try:
            self.setWindowIcon(Qt.QIcon.fromTheme('gnuradio-grc'))
        except:
            pass
        self.top_scroll_layout = Qt.QVBoxLayout()
        self.setLayout(self.top_scroll_layout)
        self.top_scroll = Qt.QScrollArea()
        self.top_scroll.setFrameStyle(Qt.QFrame.NoFrame)
        self.top_scroll_layout.addWidget(self.top_scroll)
        self.top_scroll.setWidgetResizable(True)
        self.top_widget = Qt.QWidget()
        self.top_scroll.setWidget(self.top_widget)
        self.top_layout = Qt.QVBoxLayout(self.top_widget)
        self.top_grid_layout = Qt.QGridLayout()
        self.top_layout.addLayout(self.top_grid_layout)

        self.settings = Qt.QSettings("GNU Radio", "top_block")

        try:
            if StrictVersion(Qt.qVersion()) < StrictVersion("5.0.0"):
                self.restoreGeometry(self.settings.value("geometry").toByteArray())
            else:
                self.restoreGeometry(self.settings.value("geometry"))
        except:
            pass

        ##################################################
        # Variables
        ##################################################
        self.symbol_rate = symbol_rate = 1e3
        self.filter_samp_rate = filter_samp_rate = 15e3
        self.sps = sps = int(filter_samp_rate/symbol_rate)
        self.signal_freq_khz = signal_freq_khz = 100
        self.scatter_freq_khz = scatter_freq_khz = 200.125
        self.fsk_deviation_hz = fsk_deviation_hz = 5.003e3
        self.tx_samp_rate = tx_samp_rate = 1e6
        self.tx_gain = tx_gain = 0
        self.signal_freq = signal_freq = signal_freq_khz * 1e3
        self.scatter_center_freq = scatter_center_freq = scatter_freq_khz * 1e3
        self.samp_rate = samp_rate = 1e6
        self.rx_gain = rx_gain = 35
        self.rrc_taps = rrc_taps = firdes.root_raised_cosine(1.0, filter_samp_rate,symbol_rate, 0.35, 11*sps)
        self.nfilts = nfilts = 32
        self.fsk_width_hz = fsk_width_hz = fsk_deviation_hz / 5
        self.enable_rx = enable_rx = 1
        self.center_freq = center_freq = 915e6

        ##################################################
        # Blocks
        ##################################################
        self._tx_gain_range = Range(0, 50, 1, 0, 200)
        self._tx_gain_win = RangeWidget(self._tx_gain_range, self.set_tx_gain, 'TX gain (dB)', "counter_slider", float)
        self.top_grid_layout.addWidget(self._tx_gain_win, 2, 1, 1, 1)
        for r in range(2, 3):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(1, 2):
            self.top_grid_layout.setColumnStretch(c, 1)
        self._rx_gain_range = Range(0, 70, 1, 35, 200)
        self._rx_gain_win = RangeWidget(self._rx_gain_range, self.set_rx_gain, 'RX gain (dB)', "counter_slider", float)
        self.top_grid_layout.addWidget(self._rx_gain_win, 2, 2, 1, 1)
        for r in range(2, 3):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(2, 3):
            self.top_grid_layout.setColumnStretch(c, 1)
        self._fsk_deviation_hz_tool_bar = Qt.QToolBar(self)
        self._fsk_deviation_hz_tool_bar.addWidget(Qt.QLabel('fsk_deviation_hz' + ": "))
        self._fsk_deviation_hz_line_edit = Qt.QLineEdit(str(self.fsk_deviation_hz))
        self._fsk_deviation_hz_tool_bar.addWidget(self._fsk_deviation_hz_line_edit)
        self._fsk_deviation_hz_line_edit.returnPressed.connect(
            lambda: self.set_fsk_deviation_hz(eng_notation.str_to_num(str(self._fsk_deviation_hz_line_edit.text()))))
        self.top_grid_layout.addWidget(self._fsk_deviation_hz_tool_bar, 1, 3, 1, 1)
        for r in range(1, 2):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(3, 4):
            self.top_grid_layout.setColumnStretch(c, 1)
        _enable_rx_check_box = Qt.QCheckBox('enable_rx')
        self._enable_rx_choices = {True: 1, False: 0}
        self._enable_rx_choices_inv = dict((v,k) for k,v in self._enable_rx_choices.items())
        self._enable_rx_callback = lambda i: Qt.QMetaObject.invokeMethod(_enable_rx_check_box, "setChecked", Qt.Q_ARG("bool", self._enable_rx_choices_inv[i]))
        self._enable_rx_callback(self.enable_rx)
        _enable_rx_check_box.stateChanged.connect(lambda i: self.set_enable_rx(self._enable_rx_choices[bool(i)]))
        self.top_grid_layout.addWidget(_enable_rx_check_box, 1, 4, 1, 1)
        for r in range(1, 2):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(4, 5):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.uhd_usrp_source_0 = uhd.usrp_source(
            ",".join(("", "")),
            uhd.stream_args(
                cpu_format="fc32",
                args='',
                channels=list(range(0,1)),
            ),
        )
        self.uhd_usrp_source_0.set_center_freq(center_freq, 0)
        self.uhd_usrp_source_0.set_gain(rx_gain, 0)
        self.uhd_usrp_source_0.set_antenna('RX2', 0)
        self.uhd_usrp_source_0.set_samp_rate(samp_rate)
        self.uhd_usrp_source_0.set_time_unknown_pps(uhd.time_spec())
        self.uhd_usrp_sink_0 = uhd.usrp_sink(
            ",".join(("", "")),
            uhd.stream_args(
                cpu_format="fc32",
                args='',
                channels=list(range(0,1)),
            ),
            '',
        )
        self.uhd_usrp_sink_0.set_center_freq(center_freq, 0)
        self.uhd_usrp_sink_0.set_gain(tx_gain, 0)
        self.uhd_usrp_sink_0.set_antenna('TX/RX', 0)
        self.uhd_usrp_sink_0.set_samp_rate(tx_samp_rate)
        self.uhd_usrp_sink_0.set_time_unknown_pps(uhd.time_spec())
        self._signal_freq_khz_tool_bar = Qt.QToolBar(self)
        self._signal_freq_khz_tool_bar.addWidget(Qt.QLabel('Signal Freq (kHz)' + ": "))
        self._signal_freq_khz_line_edit = Qt.QLineEdit(str(self.signal_freq_khz))
        self._signal_freq_khz_tool_bar.addWidget(self._signal_freq_khz_line_edit)
        self._signal_freq_khz_line_edit.returnPressed.connect(
            lambda: self.set_signal_freq_khz(int(str(self._signal_freq_khz_line_edit.text()))))
        self.top_grid_layout.addWidget(self._signal_freq_khz_tool_bar, 1, 1, 1, 1)
        for r in range(1, 2):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(1, 2):
            self.top_grid_layout.setColumnStretch(c, 1)
        self._scatter_freq_khz_tool_bar = Qt.QToolBar(self)
        self._scatter_freq_khz_tool_bar.addWidget(Qt.QLabel('Scatter Freq (kHz)' + ": "))
        self._scatter_freq_khz_line_edit = Qt.QLineEdit(str(self.scatter_freq_khz))
        self._scatter_freq_khz_tool_bar.addWidget(self._scatter_freq_khz_line_edit)
        self._scatter_freq_khz_line_edit.returnPressed.connect(
            lambda: self.set_scatter_freq_khz(eng_notation.str_to_num(str(self._scatter_freq_khz_line_edit.text()))))
        self.top_grid_layout.addWidget(self._scatter_freq_khz_tool_bar, 1, 2, 1, 1)
        for r in range(1, 2):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(2, 3):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.low_pass_filter_0 = filter.fir_filter_ccf(
            int(samp_rate/filter_samp_rate),
            firdes.low_pass(
                1,
                samp_rate,
                fsk_deviation_hz + fsk_width_hz,
                fsk_width_hz,
                firdes.WIN_HAMMING,
                6.76))
        self.digital_pfb_clock_sync_xxx_0 = digital.pfb_clock_sync_fff(sps, 6.28/100, rrc_taps, nfilts, 16, 1.5, 1)
        self.digital_binary_slicer_fb_0 = digital.binary_slicer_fb()
        self.blocks_udp_sink_0 = blocks.udp_sink(gr.sizeof_char*1, 'localhost', 7890, 1472, True)
        self.blocks_multiply_xx_0 = blocks.multiply_vcc(1)
        self.blocks_multiply_const_vxx_0 = blocks.multiply_const_cc(enable_rx)
        self.blocks_copy_0 = blocks.copy(gr.sizeof_gr_complex*1)
        self.blocks_copy_0.set_enabled(True)
        self.blocks_add_const_vxx_0 = blocks.add_const_bb(ord('0'))
        self.analog_sig_source_x_1 = analog.sig_source_c(samp_rate, analog.GR_COS_WAVE, -(signal_freq + scatter_center_freq), 1, 0, 0)
        self.analog_sig_source_x_0 = analog.sig_source_c(tx_samp_rate, analog.GR_COS_WAVE, signal_freq, 1, 0, 0)
        self.analog_quadrature_demod_cf_0 = analog.quadrature_demod_cf(1)


        ##################################################
        # Connections
        ##################################################
        self.connect((self.analog_quadrature_demod_cf_0, 0), (self.digital_pfb_clock_sync_xxx_0, 0))
        self.connect((self.analog_sig_source_x_0, 0), (self.uhd_usrp_sink_0, 0))
        self.connect((self.analog_sig_source_x_1, 0), (self.blocks_multiply_xx_0, 1))
        self.connect((self.blocks_add_const_vxx_0, 0), (self.blocks_udp_sink_0, 0))
        self.connect((self.blocks_copy_0, 0), (self.analog_quadrature_demod_cf_0, 0))
        self.connect((self.blocks_multiply_const_vxx_0, 0), (self.blocks_multiply_xx_0, 0))
        self.connect((self.blocks_multiply_xx_0, 0), (self.low_pass_filter_0, 0))
        self.connect((self.digital_binary_slicer_fb_0, 0), (self.blocks_add_const_vxx_0, 0))
        self.connect((self.digital_pfb_clock_sync_xxx_0, 0), (self.digital_binary_slicer_fb_0, 0))
        self.connect((self.low_pass_filter_0, 0), (self.blocks_copy_0, 0))
        self.connect((self.uhd_usrp_source_0, 0), (self.blocks_multiply_const_vxx_0, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "top_block")
        self.settings.setValue("geometry", self.saveGeometry())
        event.accept()

    def get_symbol_rate(self):
        return self.symbol_rate

    def set_symbol_rate(self, symbol_rate):
        self.symbol_rate = symbol_rate
        self.set_rrc_taps(firdes.root_raised_cosine(1.0, self.filter_samp_rate, self.symbol_rate, 0.35, 11*self.sps))
        self.set_sps(int(self.filter_samp_rate/self.symbol_rate))

    def get_filter_samp_rate(self):
        return self.filter_samp_rate

    def set_filter_samp_rate(self, filter_samp_rate):
        self.filter_samp_rate = filter_samp_rate
        self.set_rrc_taps(firdes.root_raised_cosine(1.0, self.filter_samp_rate, self.symbol_rate, 0.35, 11*self.sps))
        self.set_sps(int(self.filter_samp_rate/self.symbol_rate))

    def get_sps(self):
        return self.sps

    def set_sps(self, sps):
        self.sps = sps
        self.set_rrc_taps(firdes.root_raised_cosine(1.0, self.filter_samp_rate, self.symbol_rate, 0.35, 11*self.sps))

    def get_signal_freq_khz(self):
        return self.signal_freq_khz

    def set_signal_freq_khz(self, signal_freq_khz):
        self.signal_freq_khz = signal_freq_khz
        self.set_signal_freq(self.signal_freq_khz * 1e3)
        Qt.QMetaObject.invokeMethod(self._signal_freq_khz_line_edit, "setText", Qt.Q_ARG("QString", str(self.signal_freq_khz)))

    def get_scatter_freq_khz(self):
        return self.scatter_freq_khz

    def set_scatter_freq_khz(self, scatter_freq_khz):
        self.scatter_freq_khz = scatter_freq_khz
        self.set_scatter_center_freq(self.scatter_freq_khz * 1e3)
        Qt.QMetaObject.invokeMethod(self._scatter_freq_khz_line_edit, "setText", Qt.Q_ARG("QString", eng_notation.num_to_str(self.scatter_freq_khz)))

    def get_fsk_deviation_hz(self):
        return self.fsk_deviation_hz

    def set_fsk_deviation_hz(self, fsk_deviation_hz):
        self.fsk_deviation_hz = fsk_deviation_hz
        Qt.QMetaObject.invokeMethod(self._fsk_deviation_hz_line_edit, "setText", Qt.Q_ARG("QString", eng_notation.num_to_str(self.fsk_deviation_hz)))
        self.set_fsk_width_hz(self.fsk_deviation_hz / 5)
        self.low_pass_filter_0.set_taps(firdes.low_pass(1, self.samp_rate, self.fsk_deviation_hz + self.fsk_width_hz, self.fsk_width_hz, firdes.WIN_HAMMING, 6.76))

    def get_tx_samp_rate(self):
        return self.tx_samp_rate

    def set_tx_samp_rate(self, tx_samp_rate):
        self.tx_samp_rate = tx_samp_rate
        self.analog_sig_source_x_0.set_sampling_freq(self.tx_samp_rate)
        self.uhd_usrp_sink_0.set_samp_rate(self.tx_samp_rate)

    def get_tx_gain(self):
        return self.tx_gain

    def set_tx_gain(self, tx_gain):
        self.tx_gain = tx_gain
        self.uhd_usrp_sink_0.set_gain(self.tx_gain, 0)

    def get_signal_freq(self):
        return self.signal_freq

    def set_signal_freq(self, signal_freq):
        self.signal_freq = signal_freq
        self.analog_sig_source_x_0.set_frequency(self.signal_freq)
        self.analog_sig_source_x_1.set_frequency(-(self.signal_freq + self.scatter_center_freq))

    def get_scatter_center_freq(self):
        return self.scatter_center_freq

    def set_scatter_center_freq(self, scatter_center_freq):
        self.scatter_center_freq = scatter_center_freq
        self.analog_sig_source_x_1.set_frequency(-(self.signal_freq + self.scatter_center_freq))

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.analog_sig_source_x_1.set_sampling_freq(self.samp_rate)
        self.low_pass_filter_0.set_taps(firdes.low_pass(1, self.samp_rate, self.fsk_deviation_hz + self.fsk_width_hz, self.fsk_width_hz, firdes.WIN_HAMMING, 6.76))
        self.uhd_usrp_source_0.set_samp_rate(self.samp_rate)

    def get_rx_gain(self):
        return self.rx_gain

    def set_rx_gain(self, rx_gain):
        self.rx_gain = rx_gain
        self.uhd_usrp_source_0.set_gain(self.rx_gain, 0)

    def get_rrc_taps(self):
        return self.rrc_taps

    def set_rrc_taps(self, rrc_taps):
        self.rrc_taps = rrc_taps
        self.digital_pfb_clock_sync_xxx_0.update_taps(self.rrc_taps)

    def get_nfilts(self):
        return self.nfilts

    def set_nfilts(self, nfilts):
        self.nfilts = nfilts

    def get_fsk_width_hz(self):
        return self.fsk_width_hz

    def set_fsk_width_hz(self, fsk_width_hz):
        self.fsk_width_hz = fsk_width_hz
        self.low_pass_filter_0.set_taps(firdes.low_pass(1, self.samp_rate, self.fsk_deviation_hz + self.fsk_width_hz, self.fsk_width_hz, firdes.WIN_HAMMING, 6.76))

    def get_enable_rx(self):
        return self.enable_rx

    def set_enable_rx(self, enable_rx):
        self.enable_rx = enable_rx
        self._enable_rx_callback(self.enable_rx)
        self.blocks_multiply_const_vxx_0.set_k(self.enable_rx)

    def get_center_freq(self):
        return self.center_freq

    def set_center_freq(self, center_freq):
        self.center_freq = center_freq
        self.uhd_usrp_sink_0.set_center_freq(self.center_freq, 0)
        self.uhd_usrp_source_0.set_center_freq(self.center_freq, 0)





def main(top_block_cls=top_block, options=None):

    if StrictVersion("4.5.0") <= StrictVersion(Qt.qVersion()) < StrictVersion("5.0.0"):
        style = gr.prefs().get_string('qtgui', 'style', 'raster')
        Qt.QApplication.setGraphicsSystem(style)
    qapp = Qt.QApplication(sys.argv)

    tb = top_block_cls()

    tb.start()

    tb.show()

    def sig_handler(sig=None, frame=None):
        Qt.QApplication.quit()

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    timer = Qt.QTimer()
    timer.start(500)
    timer.timeout.connect(lambda: None)

    def quitting():
        tb.stop()
        tb.wait()

    qapp.aboutToQuit.connect(quitting)
    qapp.exec_()

if __name__ == '__main__':
    main()
