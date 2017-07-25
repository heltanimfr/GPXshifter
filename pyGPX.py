import datetime
import xml.etree.ElementTree
import re
import os
import sys

class cGPXReader():
    def __init__(self, directory):
        self.dir            = directory
        self.file_list      = []
        self.copy_file_list = []
        tmp_file_list       = [file for file in os.listdir(self.dir) if re.search('[a-zA-Z0-9]*\.gpx',file)]
        # search file not already processed
        for file in tmp_file_list:
            str = "_" + file
            if not str in tmp_file_list and "_" not in file:
                self.file_list.append(directory + file)
                self.copy_file_list.append( directory + '_' + file )
        print self.file_list
        self.hour_shift = 1
        pass
    def __del__(self):
        pass

    def process(self):
        if len(self.file_list) == 0:
            return False, "No GPX file to analyze"
        for file, copy in zip(self.file_list, self.copy_file_list):
            print "Opening %s" % file
            root = xml.etree.ElementTree.parse(file).getroot()
            ns = {'n': 'http://www.topografix.com/GPX/1/1',
                  'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
                  'gpxtpx': 'http://www.garmin.com/xmlschemas/TrackPointExtension/v1',
                  'gpxx': 'http://www.garmin.com/xmlschemas/GpxExtensions/v3'}
            expr = 'n:trk/n:trkseg/n:trkpt/n:time'
            last_rawtime  = datetime.timedelta()
            first_rawtime = datetime.timedelta()
            iter = 0
            list_datetime = []
            for element in root.findall(expr, namespaces=ns):
                timestr         = element.text
                rawtime         = datetime.datetime.strptime(timestr,'%Y-%m-%dT%H:%M:%SZ')
                last_rawtime    = rawtime
                list_datetime.append(rawtime)
                if iter == 0:
                    first_rawtime = rawtime
                    iter += 1
            delta_rawtime = last_rawtime - first_rawtime
            print 'first date: ' + str(first_rawtime)
            print 'last  date: ' + str(last_rawtime)
            print 'delta     : ' + str(delta_rawtime)

            if len(list_datetime) > 0:
                f_c = open(copy,"w")
                with open(file) as f:
                    lines = f.readlines()
                    for line in lines:
                        if len(list_datetime) != 0:
                            time = datetime.datetime.strftime(list_datetime[0],'%Y-%m-%dT%H:%M:%SZ')
                            if time in line:
                                new_time = datetime.datetime.strftime(list_datetime[0] - delta_rawtime,'%Y-%m-%dT%H:%M:%SZ')
                                line = line.replace(time, new_time)
                                list_datetime.pop(0)
                        f_c.write(line)
                f_c.close()
                f.close()
            else:
                return False, 'No time info detected'
        return True, 'Done converting'

if __name__ == '__main__':
    directory = r'/home/lcarminati/GPX/TRK/'
    gpxReader = cGPXReader(directory)
    bRet, msg = gpxReader.process()
    print msg
