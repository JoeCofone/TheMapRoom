#Plan:
#BACKUP THE FILES!!!
# -1: Read files,
# -2: get timestamps,
     #compare to previous imports
# -3: move to "yyyy-mm(Mon)" folder
     #document import
# 4: files sorted and labeled by day and time
from PIL import Image
from PIL.ExifTags import TAGS
import os
import datetime
import calendar
import shutil
import csv
today = datetime.datetime.today().strftime('%Y-%m-%d')
srcdir = 'C:/Users/joeco/Pictures/To Import 2018-10-08'#look this up
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
pics = os.listdir(srcdir)
for pic in pics:#forTS: pic = 'IMG_9688.JPG'
     if pic.upper().rfind('.JPG') >= 0:
          fname = srcdir + '/' + pic
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
#this is the thorough and methodical way to import:
try:#load pics into a dictionary and go down the rabbit hole to see if any match
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
               if key == 'Lat' or key == 'Lon':
                    piclist[key].append(float(row[key].strip().replace('"', '')))
               else:
                    piclist[key].append(row[key].strip().replace('"', ''))
          piccount = piccount + 1
     implist = {}
     implist['Model'] = []
     implist['Date'] = []
     implist['Time'] = []
     implist['Lat'] = []
     implist['Lon'] = []
     implist['Pic'] = []
     implist['Fldr'] = []
     implist['Path'] = []
     comprec = 0
     impcount = 0
     while comprec < compcount:#comprec = 1953
          keep = 1
          picrec = 0
          while picrec < piccount:#picrec = 4437
               if complist['Pic'][comprec] == 'IMG_9514.JPG' and piclist['Pic'][picrec] == 'IMG_9514.JPG':
                    print(str(comprec), str(picrec))
                    print(complist['Model'][comprec] + 'and' + piclist['Model'][picrec])
                    print(complist['Model'][comprec] == piclist['Model'][picrec])
                    print(complist['Date'][comprec] + 'and' + piclist['Date'][picrec])
                    print(complist['Date'][comprec] == piclist['Date'][picrec])
                    print(complist['Time'][comprec] + 'and' + piclist['Time'][picrec])
                    print(complist['Time'][comprec] == piclist['Time'][picrec])
                    print(round(complist['Lat'][comprec],6) == round(piclist['Lat'][picrec],6))
                    print(round(complist['Lon'][comprec],6) == round(piclist['Lon'][picrec],6))
               if complist['Model'][comprec] == piclist['Model'][picrec]:
                    if complist['Date'][comprec] == piclist['Date'][picrec]:
                         if complist['Time'][comprec] == piclist['Time'][picrec]:
                              if round(complist['Lat'][comprec],6) == round(piclist['Lat'][picrec],6):
                                   if round(complist['Lon'][comprec],6) == round(piclist['Lon'][picrec],6):
                                        keep = 0#if all the above are the same, then it's the same picture
               picrec = picrec + 1
          if keep == 1:
               implist['Model'].append(complist['Model'][comprec])
               implist['Date'].append(complist['Date'][comprec])
               implist['Time'].append(complist['Time'][comprec])
               implist['Lat'].append(complist['Lat'][comprec])
               implist['Lon'].append(complist['Lon'][comprec])
               implist['Pic'].append(complist['Pic'][comprec])
               implist['Fldr'].append(complist['Fldr'][comprec])
               implist['Path'].append(complist['Path'][comprec])
               impcount = impcount + 1
          #print(str(comprec))
          comprec = comprec + 1
except:#if the picture file is empty...which should only be once!!!
     implist = complist
     impcount = compcount
     print("Something's wrong")
#this will give the "count" number just enough zero-padding
zfmt = '0' + str(len(str(impcount))) + 'd'
print(zfmt)
#this will loop through the implist, copy the files, and append to the "Pictures List.csv"
pic2imp = 0
while pic2imp < impcount:
     imported = open(destdir + '/' + 'Picture List.csv', 'a')
     for key in implist.keys():
          #this first part will handle the folder creation
          if key == 'Fldr':
               #if the fldr_name is already spoken for, don't add it ot the list of ones to be created
               fldr_presence = 0
               for new_fldr in fldrs:
                    if implist['Fldr'][pic2imp] == new_fldr:
                         fldr_presence = 1
               if fldr_presence == 0:
                    nxtfldr = implist['Fldr'][pic2imp]
                    fldrs.append(nxtfldr)
                    os.mkdir(destdir + '/' + implist['Fldr'][pic2imp])
          #this second part will handle the file import and printing to the "Pictures List".
          if key == 'Path':
               #The easy part is copying...the hard part is naming
               destfname = destdir + '/' + implist['Fldr'][pic2imp] + '/' + today + '.' + f"{pic2imp:04d}" + '.jpg'
               #print(destfname)
               shutil.copy2(implist[key][pic2imp], destfname)
               nfinfo = '"' + implist['Model'][pic2imp] + '", ' + implist['Date'][pic2imp] + ', "' + implist['Time'][pic2imp] + '", ' + str(implist['Lat'][pic2imp]) + ', ' + str(implist['Lon'][pic2imp]) + ', "' + implist['Pic'][pic2imp] + '", "' + implist['Fldr'][pic2imp] + '", "' + destfname + '"\n'
               imported.write(nfinfo)
     pic2imp = pic2imp + 1
     print(pic2imp)
imported.close()
