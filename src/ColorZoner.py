'''
Created on May 6, 2011

@author: jvolkmar

pseudo code originally by Cody Scharfe
'''

from collections import deque
from PIL import Image, ImageStat, ImageDraw
import sys
import math

# TYPES
# region = (image, x, y, mean, variance) 
# blob = ([region1, ...], mean, variance )
class blob:
    def __init__(self, regions=[]):
        self.regions=regions
        self.stats = blobStats(self)
        pass
    def refreshStats(self):
        self.stats = blobStats(self)

def getRegions(img, thresh, minsize): # img : PIL Image
    rq = deque() # region queue
    ret = []
    
    #first region = whole image
    stat = ImageStat.Stat(img)
    r = (img, 0, 0, stat.mean, stat.var)
    rq.append(r)
    
    while len(rq) > 0:
        img, x, y, mean, var = rq.popleft()
        var_magnitude = math.sqrt(var[0]*var[0]+var[1]*var[1]+var[2]*var[2])
        #print "x: %d y: %d mean: %s var: %s" % (x,y,str(mean),str(var_magnitude))
        
        width, height = img.size
        if width < minsize or height < minsize:
            ret.append((img, x, y, mean, var))
        elif var_magnitude < thresh:
            ret.append((img, x, y, mean, var))
            print "x: %d , y: %d, width: %d, height: %d, mean: %s, var: %s" % (x,y,width,height,str(mean),str(var))
        else:
            #split region in 4
            width, height = img.size
            w1 = width/2
            h1 = height/2
            
            # quad 1: upper left  
            img1 = img.crop( (0,0,w1,h1) )
            stat1 = ImageStat.Stat(img1)
            r1 = (img1, x, y, stat1.mean, stat1.var)
                
            # quad 2: upper right
            x2 = x+w1
            img2 = img.crop( (w1,0,width,h1) )
            img2.load()
            stat2 = ImageStat.Stat(img2)
            r2 = (img2, x2, y, stat2.mean, stat2.var)
            
            # quad 3: bottom left
            y2 = y + h1
            img3 = img.crop( (0,h1,w1,height) )
            img3.load()
            stat3 = ImageStat.Stat(img3)
            r3 = (img3, x, y2, stat3.mean, stat3.var)
            
            # quad 4: bottom right
            img4= img.crop( (w1,h1,width,height) )
            img4.load()
            stat4 = ImageStat.Stat(img4)
            r4 = (img4, x2, y2, stat4.mean, stat4.var)
            
            # add the 4 resultant regions into the queue
            # TODO: add in random order?
            rq.append(r1)
            rq.append(r2)
            rq.append(r3)
            rq.append(r4)

    return ret
    
def blobSize(blob):
    regions = blob[0]
    size = 0
    for r in regions:    
        w,h = r[0].size
        size += w*h
    return size

def blobStats(blob): #returns (mean, var)
    size = blobSize(blob)
    mean = [0,0,0]
    var = [0,0,0]
    for r in blob.regions:
        im = r[0]
        stat = ImageStat.Stat(im)
        for i in range(3):
            mean[i] += stat.mean[i]/size
            var[i] += stat.var[i]/size
    return (mean,var)

def getNeighbors(region,regions): #AWFUL METHOD
    ns = []
    im, x, y, _, _ = region
    w, h = im.size
    for r in regions:
        im1, x1, y1, _,_ = r
        w1,h1 = im1.size
        
        #touches left?
        if x1+w1==x and y1+h1>=y and y1+h1<=y+h:
            ns.add(r)
            continue
        #touches right?
        if x1==x+w and y1+h1>=y and y1+h1<=y+h:
            ns.add(r)
            continue
        #touches top?
        if y1+h1==y and x1+w1>=x and x1+x1<=x+w:
            ns.add(r)
            continue
        #touches bottom?
        if y1==y+h and x1+w1>=x and x1+x1<=x+w:
            ns.add(r)
            continue
        
    return ns
    
#def getBlobs(regions):
#    blobs = []
#    
#    curblob = blob([regions[0]])
#    
#    if len(regions) == 1:
#        return [curblob]
#    
#    del regions[0]
#    curblob_checkrs = curblob.regions #regions in cur blob yet to be checked for neibors
#    candidate_regions = set()
#    while len(regions) > 0:        
#        #add neighbors to candidate list
#        for r in curblob_checkrs:
#             nbors = getNeighbors(r, regions)
#             for n in nbors: candidate_regions.add(n)
#             curblobl_checkrs.remove(r)
#        
#    
#    return blobs

def testRegions(img, thresh, minsize):
    regions = getRegions(img, thresh, minsize)
    #make an image based on the regions
    img1 = Image.new('RGB',img.size)
    draw = ImageDraw.Draw(img1)
    print '%d regions' % len(regions)
    for r in regions:
        #draw a rectangle with the mean
        i,x,y,mean,_ = r
        width, height = i.size
        draw.rectangle([(x,y),(x+width,y+height)],outline=tuple(mean), fill=tuple(mean))        
    return img1
#    img1.save('testregions.png','PNG')  
#    print 'saved'

if __name__ == '__main__':
    DEFAULT_THRESH = 1200
    DEFAULT_MINSIZE = 20
    
    def print_usage():
        print '''usage:
python ColorZoner.py <in_filename> <out_filename> [<color_threshold> [<min_region_size>]]
default color_threshold: %s
default min_region_size: %s
NOTE: file will be saved in PNG format (hint hint.. use PNG extension)''' % (DEFAULT_THRESH, DEFAULT_MINSIZE)
    
    #get arguments
    try:
        in_filename = sys.argv[1]
        out_filename = sys.argv[2]
        
        if len(sys.argv)>3:  thresh = int(sys.argv[3])
        else: thresh = DEFAULT_THRESH
         
        if len(sys.argv)>4: min_size = int(sys.argv[4])
        else: min_size = DEFAULT_MINSIZE
    except:
        print 'Error processing command line arguments!'
        print_usage()
        exit()
    
        
    img = Image.open(in_filename)
    print 'Testing regions on %s' % in_filename 
    img1 = testRegions(img, thresh, min_size)
    img1.save(out_filename,'PNG')  
    print 'Saved to %s' % out_filename



