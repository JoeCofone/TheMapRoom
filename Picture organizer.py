#Plan:
#BACKUP THE FILES!!!
# 1: Read files,
# 2: get timestamps,
# 3: move to "yyyy-mm(Mon)" folder
# 4: files sorted and labeled by day and time
# 5: add lookup text for 
from PIL import Image
from PIL.ExifTags import TAGS
import os
import datetime
import calendar
import shutil
import csv
today = datetime.datetime.today().strftime('%Y-%m-%d')
srcdir = 'C:/Users/joeco/Pictures/To Import 2018-08-02'#look this up
destdir = 'C:/Users/joeco/Pictures'
srcfldrs = os.listdir(srcdir)#srcfldrs
fldrs = os.listdir(destdir)#fldrs
try:
     os.remove(destdir + '/' + 'Import List.csv')
except:
     print('No Import List.')
#new_fldr = '2018-02(Feb)'
#fldrs.append(new_fldr)
#fldrs
#
#########Define the process to extract pic metadata ##
def get_exif_data(fname):
     ret = {}
     try:
         img = Image.open(fname)
         if hasattr( img, '_getexif' ):
              exifinfo = img._getexif()
              if exifinfo != None:
                   #print(exifinfo)
                   for tag, value in exifinfo.items():
                        decoded = TAGS.get(tag, tag)
                        ret[decoded] = value
     except IOError:
          print('IOERROR ' + fname)
     return ret
#first figure when the pic was taken/created
def get_datetime(all_attrs):
     try:
          dto = all_attrs['DateTimeOriginal']
          dt = datetime.datetime.strptime(dto, '%Y:%m:%d %H:%M:%S')
     except:
          info = os.stat(fname)
          serial = info.st_ctime
          dt = datetime.datetime.utcfromtimestamp(serial)
     if dt.hour < 12:
          hour = dt.hour
          ampm = ' AM'
     else:
          hour = dt.hour - 12
          ampm = ' PM'
     fday = str(dt.year) + '-' + f"{dt.month:02d}" + '-' + f"{dt.day:02d}"
     fhms = f"{hour:02d}" + ':' + f"{dt.minute:02d}" + ':' + f"{dt.second:02d}" + ampm
     fldr_name = str(dt.year) + '-'+f"{dt.month:02d}"+'('+calendar.month_abbr[dt.month]+')'
     return (fldr_name, fday, fhms)
####Define the process to extract the GPSInfo########
def get_gpsinfo(all_attrs):
     gpsi = {}
     try:
          gpsinfo = all_attrs['GPSInfo']
          #Lat Calc
          lat = gpsinfo[2]
          if (gpsinfo[1] == 'N'):
               lat_sign = 1
          else:
               lat_sign = -1
          dlat = lat_sign*((lat[0][0]/(lat[0][1]*1.0)) + (lat[1][0]*1.0/lat[1][1])/60 + (lat[2][0]*1.0/lat[2][1])/3600)
          #Lon Calc
          lon = gpsinfo[4]
          if (gpsinfo[3] == 'E'):
               lon_sign = 1
          else:
               lon_sign = -1
          dlon = lon_sign*((lon[0][0]/(lon[0][1]*1.0)) + (lon[1][0]*1.0/lon[1][1])/60 + (lon[2][0]*1.0/lon[2][1])/3600)
          gpsi = {'Lat': dlat, 'Lon': dlon}
     except:
          gpsi = {'Lat': 42.279768, 'Lon': -72.407835}
     return gpsi
def get_model(all_attrs):
     try:
          model = all_attrs['Model']
     except:
          model = 'Anonymous'
     return model
count = 0
#The process should be:
#-Loop through the source folders and get pic info
#-Compare current import list to current folder list
#-eliminate any pictures already imported (based on Date, Time, model, and GPS)
#-use that list to find and import pictures that qualify
complist = {}
complist['Model'] = []
complist['Date'] = []
complist['Time'] = []
complist['Lat'] = []
complist['Lon'] = []
complist['Pic'] = []
complist['Fldr'] = []
complist['Path'] = []
compcount = 0
for fldr in srcfldrs:#forTS: fldr = '2018-05'
     print(fldr)
     if fldr.rfind('.') < 0:
          pics = os.listdir(srcdir + '/' + fldr)
          for pic in pics:#forTS: pic = 'IMG_9688.JPG'
               if pic.upper().rfind('.JPG') >= 0:
                    fname = srcdir + '/' + fldr + '/' + pic
                    all_attrs = get_exif_data(fname)
                    #first figure when the pic was taken/created
                    fldr_name, fday, fhms = get_datetime(all_attrs)
                    #now get the GPS info
                    gpsi = get_gpsinfo(all_attrs)
                    #now get the Model
                    model = get_model(all_attrs)
                    #finfo == file information
                    #??Needed??: finfo = fname + ', ' + model + ', ' + destdir + '/' + fldr_name + ', ' + fday + ', ' + fhms + ', ' + str(gpsi['Lat']) + ', ' + str(gpsi['Lon']) + '\n'
                    #ofinfo == original file information
                    ofinfo = '"' + model + '", ' + fday + ', "' + fhms + '", ' + str(gpsi['Lat']) + ', ' + str(gpsi['Lon']) + ', "' + pic + '", "' + fldr_name + '", "' + fname + '"\n'
                    complist['Model'].append(model)
                    complist['Date'].append(fday)
                    complist['Time'].append(fhms)
                    complist['Lat'].append(gpsi['Lat'])
                    complist['Lon'].append(gpsi['Lon'])
                    complist['Pic'].append(pic)
                    complist['Fldr'].append(fldr_name)
                    complist['Path'].append(fname)
                    #picinfo = open(destdir + '/' + 'Comparison List.csv', 'a')
                    #picinfo.write(ofinfo)
                    #picinfo.close()
                    compcount = compcount + 1
#This process will compare the "Comparison List" (from the folder inventoried for download)
#to the "Picture List" and see what files haven't been downloaded already.
#Those will be added to the "Import List".
try:
     imported = open(destdir + '/' + 'Picture List.csv', 'r')
     files_imported = imported.readlines()
     to_import = open(destdir + '/' + 'Comparison List.csv', 'r')
     files_to_import = to_import.readlines()
     with open(destdir + '/' + 'Import List.csv', 'w') as import_list:
         for line in files_to_import:
             if line not in files_imported:
                 import_list.write(line)
     imported.close()
     to_import.close()
     import_list.close()
except:
     try:
          open(destdir + '/' + 'Picture List.csv', 'r').close()
     except:
          open(destdir + '/' + 'Comparison List.csv', 'r').close()
     comp_list = destdir + '/' + 'Comparison List.csv'
     imp_list = destdir + '/' + 'Import List.csv'
     os.rename(comp_list, imp_list)
#this is the thorough and methodical way to import:
try:
     piclist = {}
     piclist['Model'] = []
     piclist['Date'] = []
     piclist['Time'] = []
     piclist['Lat'] = []
     piclist['Lon'] = []
     piclist['Pic'] = []
     piclist['Fldr'] = []
     piclist['Path'] = []
     piccount = 0
     pic_csv = csv.DictReader(open(destdir + '/' + 'Picture List.csv', 'r'), fieldnames = ['Model', 'Date', 'Time', 'Lat', 'Lon', 'Pic', 'Fldr', 'Path'], delimiter = ',', quotechar = '"')
     for row in pic_csv:
          for key in row:
               if key == 'Date' or key == 'Pic' or key == 'Path' or key == 'Fldr':
                    piclist[key].append(row[key].strip().replace('"', ''))
               else:     
                    piclist[key].append(row[key])
          piccount = piccount + 1
except:#if the picture file is empty...which should only be once!!!
     implist = complist
     impcount = compcount
#action items below...to be handled once final import list is vetted
#Need to go row-by-row in the import file, parse the row, and move and rename the file
implist = {}
implist['Model'] = []
implist['Date'] = []
implist['Time'] = []
implist['Lat'] = []
implist['Lon'] = []
implist['Pic'] = []
implist['Fldr'] = []
implist['Path'] = []
count = 0
# Make sure list of keys is consistent in the line below
csv_file = csv.DictReader(open(destdir + '/' + 'Import List.csv', 'r'), fieldnames = ['Model', 'Date', 'Time', 'Lat', 'Lon', 'Pic', 'Fldr', 'Path'], delimiter = ',', quotechar = '"')
for row in csv_file:
     for key in row:
          if key == 'Date' or key == 'Pic' or key == 'Path' or key == 'Fldr':
               flist[key].append(row[key].strip().replace('"', ''))
          else:     
               flist[key].append(row[key])
          if count == 0:
               print(key + ' is ' + row[key])
     count = count + 1
print(count)
#this will give the "count" number just enough zero-padding
zfmt = '0' + str(len(str(count))) + 'd'
print(zfmt)
#print(flist['Date'][6041:6150])
#print(flist['Path'][6041])
#print(flist['Pic'][6041:6142])
#print(destdir + '/' + flist['Pic'][6041])
pic2imp = 0
while pic2imp < count:
     imported = open(destdir + '/' + 'Picture List.csv', 'a')
     for key in flist.keys():
          #this first part will handle the folder creation
          if key == 'Fldr':
               #if the fldr_name is already spoken for, don't add it ot the list of ones to be created
               fldr_presence = 0
               for new_fldr in fldrs:
                    if flist['Fldr'][pic2imp] == new_fldr:
                         fldr_presence = 1
               if fldr_presence == 0:
                    nxtfldr = flist['Fldr'][pic2imp]
                    fldrs.append(nxtfldr)
                    os.mkdir(srcdir + '/' + flist['Fldr'][pic2imp])
          #this second part will handle the file import and printing to the "Pictures List".
          if key == 'Path':
               #The easy part is copying...the hard part is naming
               destfname = destdir + '/' + flist['Fldr'][pic2imp] + '/' + today + '.' + f"{pic2imp:04d}" + '.jpg'
               #print(destfname)
               #shutil.copy2(flist[key][pic2imp], destfname)
               nfinfo = '"' + flist['Model'][pic2imp] + '", ' + flist['Date'][pic2imp] + ', "' + flist['Time'][pic2imp] + '", ' + str(flist['Lat'][pic2imp]) + ', ' + str(flist['Lon'][pic2imp]) + ', "' + flist['Pic'][pic2imp] + '", "' + flist['Fldr'][pic2imp] + '", "' + destfname + '"\n'
               imported.write(nfinfo)
     pic2imp = pic2imp + 1
     print(pic2imp)
imported.close()