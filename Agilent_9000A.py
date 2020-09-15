
from instrument import Instrument
import numpy
import visa
import types
import logging
import lib.math.fit as f; reload(f)
import qt
from module_slaven import updateInstruments

class Agilent_9000A(Instrument):
	'''
	This is the python driver for the Rohde & Schwarz SMR40
	signal generator

	Usage:
	Initialize with
	<name> = instruments.create('name', 'Agilent_9000A', address='<GPIBaddress>',
		reset=<bool>)
	'''

	def __init__(self, name, address, reset=False):
		'''
		Initializes the Agilent 9000A, and communicates with the wrapper.

		Input:
			name (string)    : name of the instrument
			address (string) : GPIB address
			reset (bool)     : resets to default values, default=false

		Output:
			None
        '''
		logging.info(__name__ + ' : Initializing instrument')
		Instrument.__init__(self, name, tags=['physical'])

		self._address = address
		self._visainstrument = visa.instrument(self._address)
		self._visainstrument.timeout = 300 #in seconds

		self.add_parameter('BW', type=types.FloatType,
			flags=Instrument.FLAG_GETSET,
			units='Hz',
			format='%0.2e',
			persist=True,)

		self.add_parameter('sweepTime', type=types.FloatType,
			flags=Instrument.FLAG_GETSET,
			units='s',
			format='%0.2e',
			persist=True,)

		self.add_parameter('SPAN', type=types.FloatType,
			flags=Instrument.FLAG_GETSET,
			units='Hz',
			format='%0.2e',
			persist=True,)

		self.add_parameter('CENTER', type=types.FloatType,
			flags=Instrument.FLAG_GETSET,
			units='Hz',
			format='%0.2e',
			persist=True,)

		self.add_parameter('START', type=types.FloatType,
			flags=Instrument.FLAG_GETSET,
			units='Hz',
			format='%0.2e',
			persist=True,)

		self.add_parameter('STOP', type=types.FloatType,
			flags=Instrument.FLAG_GETSET,
			units='Hz',
			format='%0.2e',
			persist=True,)

		self.add_parameter('AVERAGES', type=types.IntType,
			flags=Instrument.FLAG_GETSET,
			persist=True,)

		self.add_parameter('AMPLITUDE', type=types.FloatType,
			flags=Instrument.FLAG_GETSET,
			units='V',
			format='%0.2e',
			persist=True,)

		self.add_parameter('OUTPUT', type=types.StringType,
			flags=Instrument.FLAG_GETSET,
			option_list=('on', 'off'),
			persist=True,)

		self.add_function('get_all')
		self.add_function('fitPeak')
		self.add_function('makeFreqAxis')

		self.get_all()

	def get_all(self):
		self.get_AMPLITUDE()
		self.get_AVERAGES()
		self.get_BW()
		self.get_CENTER()
		self.get_OUTPUT()
		self.get_SPAN()
		self.get_START()
		self.get_STOP()
		self.get_sweepTime()
		return True


	def fitPeak(self,spectrum=1,freq_axis=1):
		'''
		fitPeak(self,spectrum=1,freq_axis=1)
		by default it takes current soectrum to fit
		by defualt it takes current span to fit
		'''
		if (freq_axis==1):
			freq_axis=self.makeFreqAxis()
		if (spectrum==1):
			spectrum=self.get_spectrum()
		lor=f.Lorentzian()
		lor.fittin(freq_axis,spectrum)
		return lor

	def makeFreqAxis(self):
		'''
		return frequency axes
		'''
		start_freq=self.get_start_freq()
		stop_freq=self.get_stop_freq()
		nb_points=self.get_nb_points()
		return numpy.linspace(start_freq,stop_freq,nb_points)

	def setCentar(self, treshold = 3E-11):

		lor=self.fitPeak()
		center = self.get_CENTER()
		span = self.get_SPAN()*0.5
		print lor.get_height()*self.get_bw()
		if(lor.get_height()*self.get_bw()>treshold and lor.get_position()<center+span and lor.get_position()>center-span and lor.get_fwhm()>0 and self.get_bw()!=1):
			self.set_CENTER(lor.get_position())
		return lor.get_position()

	def zoomPeak(self,fwInit=15):

		lor=self.fitPeak()

		if(lor.get_height()*self.get_bw()>1E-12):
			self.set_CENTER(lor.get_position())
			self.set_span(lor.get_fwhm()*fwInit)

	def go_right(self):
		self.set_CENTER(self.get_CENTER()+self.get_SPAN())

	def go_left(self):
		self.set_CENTER(self.get_CENTER()-self.get_SPAN())


    # Functions
	def get_spectrum(self, square = True ,trace='1'):
		self._visainstrument.write(':TRAC:DATA? TRACE' + trace)
		data = self._visainstrument.read()
		spectrum = numpy.array(data.split(','),dtype=float)
		if square:
			return spectrum*spectrum/self.get_bw()
		return spectrum

	def setTracking(self, state):
		if state == 1:
			self._visainstrument.write('INST:SOUR TRAC')
		elif state == 0:
			self._visainstrument.write('INST:SOUR OFF')
		else:
			print 'wrong argument. Use 0 (OFF) or 1(On)'


	def get_span(self):
		self._visainstrument.write(':FREQuency:SPAN?')
		span = self._visainstrument.read()
		span=float(span)
		return span

	def set_span(self,span):
		self._visainstrument.write(':FREQuency:SPAN '+str(span)+'Hz')

	def set_center_freq(self,centerfreq):
		self._visainstrument.write(':FREQuency:CENTER '+str(centerfreq)+'Hz')

	def set_start_freq(self,startfreq):
		self._visainstrument.write(':FREQuency:START '+str(startfreq)+'Hz')

	def set_stop_freq(self,stopfreq):
		self._visainstrument.write(':FREQuency:STOP '+str(stopfreq)+'Hz')

	def set_averages(self,av):
		self._visainstrument.write(':AVERage:COUNt '+str(av))

	def set_sweeptime(self,sweeptime):
		self._visainstrument.write(':SWE:TIME '+str(sweeptime))


	def get_center_freq(self):
		self._visainstrument.write(':FREQuency:CENTER?')
		centerfreq = self._visainstrument.read()
		centerfreq = float(centerfreq)
		return centerfreq


	def set_amplitude(self,amplitude):
		self._visainstrument.write(':SOUR:POW '+ str(amplitude)+'mV')

	def on(self):
		'''
		Set RF output  to 'on'
		'''
		self._visainstrument.write('OUTPut ON')

	def off(self):
		'''
		Set RF output  to 'off'
		'''
		self._visainstrument.write('OUTPut OFF')

	def get_sweep_time(self):
		self._visainstrument.write(':SWE:TIME?')
		sweeptime = self._visainstrument.read()
		sweeptime = float(sweeptime)
		return sweeptime

	def restart(self):
		self._visainstrument.write(':INIT:REST')

	def get_average_count(self):
		self._visainstrument.write(':AVER:COUN?')
		averagecount=self._visainstrument.read()
		averagecount=float(averagecount)
		return averagecount

	def get_nb_points(self):
		self._visainstrument.write(':SWEep:POINts?')
		nb_points=self._visainstrument.read()
		nb_points=float(nb_points)
		return nb_points

	def get_start_freq(self):
		self._visainstrument.write(':FREQuency:STARt?')
		start_freq=self._visainstrument.read()
		start_freq = float(start_freq)
		return start_freq

	def get_stop_freq(self):
		self._visainstrument.write(':FREQuency:STOP?')
		stop_freq=self._visainstrument.read()
		stop_freq=float(stop_freq)
		return stop_freq

	def get_y_axis_units(self):
		self._visainstrument.write('UNIT:POW?')
		y_axis_units=self._visainstrument.read()
		return y_axis_units

	def get_marker(self):
		self._visainstrument.write(':CALCulate:MARKer:Y?')
		marker=self._visainstrument.read()
		return float(marker)

	def get_marker_improved(self):
		a = self.get_marker()
		b = self.get_bw()
		return a*a/b

	def get_marker_X(self):
		self._visainstrument.write(':CALCulate:MARKer:X?')
		marker=self._visainstrument.read()
		return float(marker)

	def set_bw(self,bw):
		self._visainstrument.write(':BAND '+ str(bw)+'Hz')

	def get_bw(self):
		self._visainstrument.write(':BAND?')
		bwidth=self._visainstrument.read()
		return float(bwidth)

	def get_status(self):
		logging.debug(__name__ + ' : get status')
		stat = self._visainstrument.ask(':OUTP?')
		if (stat=='1'):
			return 'on'
		elif (stat=='0'):
			return 'off'
		else:
			raise ValueError('Output status not specified : %s' % stat)
		return

	def get_amplitude(self):
		self._visainstrument.write(':SOUR:POW?')
		amplitude=self._visainstrument.read()
		return float(amplitude)

	def do_get_BW(self):
		return self.get_bw()

	def do_set_BW(self,bw):
		self.set_bw(bw)

	def do_get_SPAN(self):
		return self.get_span()

	def do_set_SPAN(self,span):
		self.set_span(span)

	def do_get_START(self):
		return self.get_start_freq()

	def do_set_START(self,freq):
		self.set_start_freq(freq)

	def do_get_STOP(self):
		return self.get_stop_freq()

	def do_set_STOP(self,freq):
		self.set_stop_freq(freq)

	def do_get_CENTER(self):
		return self.get_center_freq()

	def do_set_CENTER(self,freq):
		self.set_center_freq(freq)

	def do_get_AVERAGES(self):
		return self.get_average_count()

	def do_set_AVERAGES(self,av):
		self.set_averages(av)

	def do_get_AMPLITUDE(self):
		return self.get_amplitude()

	def do_set_AMPLITUDE(self,ampl):
		self.set_amplitude(ampl)

	def do_get_OUTPUT(self):
		return self.get_status()

	def do_set_OUTPUT(self,out):
		if out=='on':
			self.set_off(out)
		elif out=='off':
			self.set_on()
		else:
			print 'Wrong value. Try on or off'

	def do_get_sweepTime(self):
		return self.get_sweep_time()

	def do_set_sweepTime(self,sweeptime):
		self.set_sweeptime(self,sweeptime)

	def set_IQ_mode(self):
		centralFreq = self.get_center_freq()
		self._visainstrument.write(':INSTrument:SELect BASIC')
		self._visainstrument.write(':FREQuency:CENTER '+str(centralFreq)+'Hz')

	def get_IQ_BW(self):
		self._visainstrument.write(':SPECtrum:BANDwidth?')
		data = self._visainstrument.read()
		return data

## read and fetch functions

	def setAveragesWithTime(self, time):
		self.set_averages(int(time/self.get_sweep_time()))

	def runMeasurement(self, square = True):
		self._visainstrument.write(':READ:SAN?')
		data = self._visainstrument.read()
		spectrumAndFrequency = numpy.array(data.split(','),dtype=float)
		freq = spectrumAndFrequency[::2]
		spectrum = spectrumAndFrequency[1::2]
		if square:
			return freq, spectrum*spectrum/self.get_bw()
		return freq, spectrum

	def saveSpectrum(self, square = True):
		self._visainstrument.write(':FETCh:SAN?')
		data = self._visainstrument.read()
		spectrumAndFrequency = numpy.array(data.split(','),dtype=float)
		freq = spectrumAndFrequency[::2]
		spectrum = spectrumAndFrequency[1::2]
		if square:
			return freq, spectrum*spectrum/self.get_bw()
		return freq, spectrum


## IQ functions
	def get_IQ_data(self):
		self._visainstrument.write(':FETCh:SPECtrum3?')
		data = self._visainstrument.read()
		spectrum = numpy.array(data.split(','),dtype=float)
		I = spectrum[0::2]
		Q = spectrum[1::2]
		self._visainstrument.write(':FETCh:SPECtrum1?')
		data = self._visainstrument.read()
		spectrum = numpy.array(data.split(','),dtype=float)
		time = spectrum[9]
		return [I,Q,time];

	def get_IQ_spectrum(self):
		self._visainstrument.write(':FETCh:SPECtrum4?')
		data = self._visainstrument.read()
		spectrum = numpy.array(data.split(','),dtype=float)
		self._visainstrument.write(':FETCh:SPECtrum7?')
		data = self._visainstrument.read()
		spectrumAvr = numpy.array(data.split(','),dtype=float)
		self._visainstrument.write(':FETCh:SPECtrum1?')
		data = self._visainstrument.read()
		spectrumInfo = numpy.array(data.split(','),dtype=float)
		#conversion to volts^2/hz
		bw = float(self.get_IQ_BW())
		spectrum = numpy.power(10,(spectrum-30)/10)*50/bw
		spectrumAvr = numpy.power(10,(spectrumAvr-30)/10)*50/bw
		return [spectrum, spectrumAvr, spectrumInfo[3], spectrumInfo[4]]
