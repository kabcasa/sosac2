import zipfile, xbmcaddon, xbmc, sys, os, time




def all(_in, _out, dp=None):
	if dp:
		return allWithProgress(_in, _out, dp)

	return allNoProgress(_in, _out)
		

def allNoProgress(_in, _out):
        try:
                zin = zipfile.ZipFile(_in, 'r')
                zin.extractall(_out)
        except Exception as e:
                print("extract error ", str(e))
                return False

        return True


def allWithProgress(_in, _out, dp):

	zin = zipfile.ZipFile(_in,  'r')

	nFiles = float(len(zin.infolist()))
	count  = 0

	try:
		for item in zin.infolist():
			count += 1
			update = count / nFiles * 100
			affupdate = str(int(update)) + '%s'%' %'
			dp.update(int(update),'Extracting : [COLOR %s][B]%s[/B][/COLOR]  Please Wait'% ('cyan', affupdate))
			zin.extract(item, _out)
	except Exception as e:
                print("error extract ",str(e))
                return False
	return True
