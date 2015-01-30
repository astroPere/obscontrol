#!/usr/bin/env python
# -*- coding: utf-8 -*-
#CTois.py
#
from __future__ import with_statement
#~ import xml.etree.ElementTree as et
import re,os,math
import ephem as ep
import datetime

resetc = '\033[0m'
black = '\033[7;20m'
green = '\033[0;102m'
red = '\033[1;101m'
blue = '\033[0;104m'
red2 = '\033[31m'
green2 ='\033[32m'
yellow2 = '\033[33m'
blue2 = '\033[34m'
bold = '\033[1m'
nbold = '\033[0m'
pline = '\033[4m'



print '@@@@ CTOIS_2 @@@@'

#------------------------------------------------------------------------#
#                          Class CTois.py                                #
#------------------------------------------------------------------------#

class CTois:

    prt_exopl = 0

    def __init__(self):
        self.oadm = ep.Observer()
        self.oadm.lat='42.0514'
        self.oadm.lon='0.7294'
        self.oadm.horizon = '-18'
        self.oadm.pressure = 0.0
        self.oadm.elevation = 1570.0
        self.oadm.epoch = '2000.0'
        self.oadm.date = 0
        self.XMLP = os.path.realpath('.')
        self.XMLT = 'tois_TOTAL.xml'
        self.XMLS = 'sequences_TOTAL.xml'
        self.STRLT = 'staralt.txt'
        self.tois = []
        self.seqs = []
        self.extract_seqs_items = []
        self.extract_seqs2_items = []
        self.EQTOI = []
        self.time_acc = 150  #seconds
        self.set_datetime(1)
        self.allowed_offset = 600.0 #seconds


    def set_datetime(self, D = 1, v = 0):
        """ set and compute all times for observatory
            v = 'v' for verbose """

        k = '{:0=+3.0f}'.format(int(D))
        k = int(k)
        t = datetime.date.today()+datetime.timedelta(+k)
        tt = datetime.time(0,0)
        self.comp_date = datetime.datetime.combine(t,tt)
        self.oadm.date = self.comp_date
        self.Dat1 = self.oadm.next_rising(ep.Sun(), use_center=True)
        self.Dat0 = self.oadm.previous_setting(ep.Sun(), use_center=True)
        self.start_night = self.Dat0.datetime()
        self.end_night = self.Dat1.datetime()
        self.night_len = (self.end_night - self.start_night)
        self.lst = self.oadm.sidereal_time()
        self.utc = ep.now().datetime()
        self.jd0 = ep.julian_date(0)
        self.jd_now = ep.julian_date(ep.now())
        self.jd_comp = ep.julian_date(self.comp_date)
        self.jd_start = ep.julian_date(self.start_night)
        self.jd_end = ep.julian_date(self.end_night)
        if v == 'v':
            D = str(D)
            print '> set_datetime >  d'+D,' > ', self.oadm.date,'-', self.jd_comp      #self.print_date()
        return

    def set_time_acc(self,acc=100, v=0):
        self.time_acc = acc
        if v == 'v':
            print '> set_time_acc > ',self.time_acc,'s.'
        return

    def set_XMLP(self,XMLP, v=0):
        if '/' not in XMLP[-1]:
            XMLP = XMLP+'/'
        self.XMLP = XMLP
        if v == 'v':
            print 'xml path set to:', self.XMLP
        return

    def set_XMLT(self,xmlf, v=0):
        self.XMLT = xmlf
        if v == 'v':
            print 'xml tois file set to:',self.XMLT
        return

    def set_XMLS(self,xmlf, v=0):
        self.XMLS = xmlf
        if v == 'v':
            print 'sequences file set to:',self.XMLS
        return



    def print_date(self):
        print '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'
        print 'Computed at JD :',self.jd2UT(self.jd_comp),'UT ','%.5f'%float(ep.julian_date(self.comp_date)),'JD'
        print 'Sun set/rise UT:',(self.Sun_RS(0)[1]),'UT ',(self.Sun_RS(0)[0]),'UT '
        print 'L Sideral Time : SSet: {}  MNight: {}  SRise: {}'.format( self.LST_SunsetHorizon('0')[0],self.lst,self.LST_SunsetHorizon(0)[1])
        print 'start_night UT :', self.start_night.strftime('%Y/%m/%d %a %H:%M:%S'),'  ','%.5f'%float(self.jd_start),'JD'
        print 'end_night UT   :', self.end_night.strftime('%Y/%m/%d %a %H:%M:%S'),'  ','%.5f'%float(self.jd_end),'JD'
        print 'night_length   :','%sh:%sm' % self.tdelta_HMS(self.night_len)[:2]
        print 'UTC Now        :',self.utc.strftime('%H:%M:%S'),'UT'
        print 'Moon:', '%.0f'%self.moon_sky(self.comp_date)[0],'%', ' Sky-',self.moon_sky(self.comp_date)[1]
        print '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'
        return

    def print_date_short(self):
        print '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'
        print 'Computed at JD :',self.jd2UT(self.jd_comp),'UT ','%.5f'%float(ep.julian_date(self.comp_date)),'JD'
        print 'start_night UT :', self.start_night.strftime('%Y/%m/%d %a %H:%M:%S'),'  ','%.5f'%float(self.jd_start),'JD'
        print 'end_night UT   :', self.end_night.strftime('%Y/%m/%d %a %H:%M:%S'),'  ','%.5f'%float(self.jd_end),'JD'
        print 'Moon:', '%.0f'%self.moon_sky(self.comp_date)[0],'%', ' Sky-',self.moon_sky(self.comp_date)[1]
        print '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'
        return



    def jd2UT(self,jd):
        """convert JD to UT """
        jd2 = jd - self.jd0
        return ep.Date(jd2)

    def UT2jd(self,t):
        """convert t string to JD """
        jd = ep.julian_date(t)
        return jd

    def LST_SunsetHorizon(self,hor=0):
        """Calculate LST at Sun rising/set with horizon """
        self.oadm.horizon = hor
        rising = self.oadm.next_rising(ep.Sun(), use_center=True)
        self.oadm.date = rising
        lst_r = self.oadm.sidereal_time()
        setting = self.oadm.previous_setting(ep.Sun(), use_center=True)
        self.oadm.date = setting
        lst_s = self.oadm.sidereal_time()
        self.oadm.horizon = '-18'
        return lst_s,lst_r

    def UT2LST(self,t):
        """Calculate LST at t UT Timefor observatory"""
        self.oadm.date = t
        lst = self.oadm.sidereal_time()
        return lst

    def Sun_RS(self,hor=0):
        """Calculate Sun rising/set at horizon = 0 deg"""
        self.oadm.horizon = hor
        rising = self.oadm.next_rising(ep.Sun(), use_center=True)
        setting = self.oadm.previous_setting(ep.Sun(), use_center=True)
        self.oadm.horizon = '-18'

        return rising, setting

    def parse_staralt(self,ob):
        """parse targets to 'staralt' format file"""
        self.oadm.date = self.comp_date
        Obj = ep.readdb(ob)
        Obj.compute(self.oadm)
        name = Obj.name
        line = (name+' '+str(Obj.a_ra)+' '+str(Obj.a_dec)+' 2000.0')
        return line

    def write_STRLT(self,pro):                               # writes 'staralt_coord' in a file
        kk = []
        targets_staralt = open(self.STRLT,'w')
        for x in self.tois:
            if str(pro) in x['id']:
                if x['staralt_coord'] not in kk:
                    targets_staralt.write(x['staralt_coord']+'\n')
                    kk.append(x['staralt_coord'])
        targets_staralt.close()




    def moon_sky(self,t):
        """compute Moon phase and Sky brightness at (t) time"""
        self.oadm.date = t
        moon_phase=ep.Moon(self.oadm).phase
        moon_alt = ep.Moon(self.oadm).alt
        if moon_phase > 30:
            skyb = 'Bright ◐'
            if moon_phase > 60:
                skyb = 'Bright ●'
            skyb_v =1
        else:
            skyb = 'Dark ○'
            skyb_v = 0
        self.oadm.date = self.comp_date
        return moon_phase,skyb,skyb_v,moon_alt

    def tdelta_HMS(self,td):
        """split a timedelta (td) to  h,m,s strings"""
        total_seconds = int(td.total_seconds())
        h_td, remainder = divmod(total_seconds,60*60)
        m_td, s_td = divmod(remainder,60)
        return h_td,m_td,s_td

    def parse_all_xml(self):
        self.parse_XMLS()
        self.parse_XMLT()
        self.parse_EQTOI()
        return


    def parse_XMLS(self):
        """read the XML file and convert it in a list of dictionarys"""
        DD = str(self.XMLS)
        #DD = str(self.XMLP+self.XMLS)
        tree = et.parse(DD)
        root = tree.getroot()
        for t in range(len(root[2])):
            kk=[]
            i=0
            seq={}
            for j in root[2][t]:
                if j.tag not in kk:
                    seq[str(j.tag)]=j.text
                else:
                    i +=1
                    seq[str(j.tag)+str(i)] = j.text
                kk.append(j.tag)

            self.seqs.append(seq.copy())
        return

    def parse_EQTOI(self):
        for i in self.seqs:
            EQU = []
            eq = i['equation']
            k = 0
            if '[' in eq:
                s1,s2 = '[', ']'
                while '[' in eq:
                    k += 1
                    x = eq.find(s1,1)
                    x2 = eq.find(s2,x)
                    eq1= eq[x:x2+1]
                    if len(eq1) == 1:
                        EQU.append(['EQ'+str(k),eq])
                        break
                    else:
                        eq = eq.replace(eq1,'EQ'+str(k))
                        EQU.append(['EQ'+str(k),eq1])
                else:
                    if '(' in eq[1:-1]:
                        s1,s2 = '(',')'
                        while '(' in eq[1:-1]:
                            k += 1
                            x = eq.find(s1,1)
                            x2 = eq.find(s2,x)
                            eq1= eq[x:x2+1]
                            if len(eq1) == 1:
                                break
                            else:
                                eq = eq.replace(eq1,'EQ'+str(k))
                                EQU.append(['EQ'+str(k),eq1])
            elif '('in eq[1:-1]:
                s1,s2 = '(',')'
                while '(' in eq[1:-1]:
                    k += 1
                    x = eq.find(s1,1)
                    x2 = eq.find(s2,x)
                    eq1= eq[x:x2+1]
                    if len(eq1) == 1:
                        break
                    else:
                        eq = eq.replace(eq1,'EQ'+str(k))
                        EQU.append(['EQ'+str(k),eq1])
            else:
                if '(' in eq:
                    k += 1
                else:
                    k += 1
                    eq = '('+eq+')'
                EQU.append(['EQ'+str(k),eq])
            k = 0
            j = 1
            EQU2 = []
            for e in EQU:
                if '(' in e[1][1:-1]:
                    s1,s2 = '(',')'
                    while '(' in e[1][1:-1]:
                        x = e[1].find(s1,1)
                        x2 = e[1].find(s2,x)
                        eq1 = e[1][x:x2+1]
                        if len(eq1) == 1:
                            break
                        else:
                            e[1] = e[1].replace(eq1,e[0]+str(j))
                            EQU2.append([e[0]+str(j),eq1])
                            j += 1
                else:
                    EQU2.append(e)
            eq2,j = i['equation'],1
            for e in sorted(EQU2):
                if 'EQ' not in e[1]:
                    eq2 = eq2.replace(e[1],e[0])
                    j += 1
            EqSeq = {}
            eq2,j = i['equation'],1
            EqSeq['id'] = i['id']
            for e in sorted(EQU2):
                if 'EQ' not in e[1]:
                    EqSeq['SQ'+str(j)] = e[1]
                    j += 1
            for k,v in sorted(EqSeq.iteritems()):
                if 'SQ' in k:
                    eq2 = eq2.replace(v,k)

            EqSeq['sequence'] = eq2

            self.EQTOI.append(EqSeq)

        return self.EQTOI

    def parse_XMLT(self):
        """read the XML file and convert it in a dictionarys"""
        DD = str(self.XMLT)
        #DD = str(self.XMLP+self.XMLT)
        tree = et.parse(DD)
        root = tree.getroot()
        for t in range(len(root[2])):
            kk=[]
            i=0
            toi={}
            for j in root[2][t]:
                if j.tag not in kk:
                    toi[str(j.tag)]=j.text
                else:
                    i +=1
                    toi[str(j.tag)+str(i)] = j.text
                kk.append(j.tag)
            self.tois.append(toi.copy())
        root.clear()

        for x in self.tois:
            if 'window' not in x:
                x['window'] = str(self.jd_start)+','+str(self.jd_end)+',added'
            if 'SkyV_period' not in x:
                x['SkyV_period'] = [None]
        return

    def extract_pstoi(self,j):
        """extract names from toi id."""
        self.pstoi = []
        for x in ['p','s','t','o','i']:
            xx =re.findall(r'{0}\d+'.format(x),j)
            xxx =''.join(xx)
            self.pstoi.append(xxx)
        return self.pstoi


#################################### INUTIL???? #######################
    def extract_seqs(self):#,S):
        for SQ in self.EQTOI: # TODO: fer que ho busqui a una seq.S (S={})
            #if S == SQ['id']:
            for k,v in sorted(SQ.iteritems()):
                if k not in ['id','sequence']:
                    xx = re.findall(r't\w+',v)
                    self.extract_seqs_items.append([SQ['id'],k,v,xx])
        return self.extract_seqs_items
#######################################################################
#################################### INUTIL???? #######################
    def extract_seqs2(self,eqtoi):
        #print red,eqtoi
        #for SQ in eqtoi: # TODO: fer que ho busqui a una seq.S (S={})
            #if S in SQ['id']:
        for k,v in sorted(eqtoi.iteritems()):
            if k not in ['id','sequence']:
                xx = re.findall(r't\w+',v)
                self.extract_seqs2_items.append([eqtoi['id'],k,v,xx])
        return self.extract_seqs2_items
#######################################################################


    def comp_alt(self,ob,t):
        """compute object object alt at t time
        ob = line coord. object
        t = time to compute"""
        obj = ep.readdb(ob)
        self.oadm.date = t
        obj.compute(self.oadm)
        alt = obj.alt
        #self.oadm.date = self.comp_date
        return alt

    def comp_moon_dist(self,ob,t):
        """compute moon distance to an object at t time
        ob = line coord. object
        t = time to compute"""
        obj = ep.readdb(ob)
        self.oadm.date = t
        obj.compute(self.oadm)
        moon= ep.Moon(self.oadm)
        moon_dist = ep.separation(moon,obj)
        return moon_dist



    def comp_air(self,ob,t):
        """compute object airmass at t time
        ob = line coord. object
        t = time to compute"""
        obj = ep.readdb(ob)
        self.oadm.date = t
        obj.compute(self.oadm)
        if obj.alt < 0:
            self.airmass = 1000
        else:
            self.airmass = 1/math.cos(ep.pi/2-obj.alt)       # compute object airmass aproximation
        self.oadm.date = self.comp_date
        return self.airmass


    def cp_obs_time_airm(self,x,ob,t1,t2,k='+'):
        """compute visibility time (from airmass req. A)
            ob = coordinates line in ephem format
            x = {toi} data
            t1,t2 = start/end time to compute
            k = '+' to set values of V,NV,WV periods in {toi}"""
        self.V_period, self.WV_period,self.NV_period = [],[],[]
        obj = ep.readdb(ob)
        td = datetime.timedelta(seconds=self.time_acc)
        obsv = []
        period = []
        i=0
        #t1 = t1-td
        while t1 <= t2:
            self.oadm.date = t1
            obj.compute(self.oadm)
            air0 = self.comp_air(ob,t1)
            if air0 > float(x['airmass_max']) or air0 < float(x['airmass_min']):
                obsv0 = 0
            else:
                obsv0 = 1
            obsv.append([obsv0,t1])
            t1 += td
        period.append([0,obsv[0]])
        period.append([obsv.index(obsv[-1]),obsv[-1]])
        for i in range(len(obsv)-1):
            if obsv [i][0] != obsv[i+1][0]:
                period.append([obsv.index(obsv[i]),obsv[i]])
        sort_period=sorted(period)
        for i in range(len(sort_period)-1):
            kk = [sort_period[i+1][1][0],x['id'],ep.julian_date(sort_period[i][1][1]),ep.julian_date(sort_period[i+1][1][1])]
            self.V_period.append(kk)
            if kk[0] == 0:
                self.NV_period.append(kk)
            else:
                self.WV_period.append(kk)
        self.oadm.date = self.comp_date
        if k == '+':
            x['V_period'] = self.V_period
            x['WV_period'] = self.WV_period
            x['NV_period'] = self.NV_period

        return self.V_period, self.WV_period,self.NV_period

#######################################################################
    def cp_obs_time_skybright(self,x,ob,t1,t2,k='+'):
        """compute visibility time (from skybrightness req. S)
            ob = coordinates line in ephem format
            x = {toi} data
            t1,t2 = start/end time to compute
            k = '+' to set values of V,NV,WV periods in {toi}"""
        self.SkyV_period = []
        sky = x['skybright'].split(',')
        obj = ep.readdb(ob)
        obsv = []
        period = []
        i=0
        skybright = 0
        td = datetime.timedelta(seconds=self.time_acc)
        #t1 = t1 - td
        while t1 <= t2:
            self.oadm.date = t1
            obj.compute(self.oadm)
            moon= ep.Moon(self.oadm)
            if moon.phase < float(sky[1]):
                skybright = 1
            elif float(sky[2]) <= moon.alt*180/ep.pi <= float(sky[3]):
                skybright = 1
            else:
                skybright = 0
            obsv.append([skybright,t1])
            t1 += td
        period.append([0,obsv[0]])
        period.append([obsv.index(obsv[-1]),obsv[-1]])
        for i in range(len(obsv)-1):
            if obsv [i][0] != obsv[i+1][0]:
                period.append([obsv.index(obsv[i]),obsv[i]])
        sort_period=sorted(period)
        for i in range(len(sort_period)-1):
            kk = [sort_period[i+1][1][0],x['id'],ep.julian_date(sort_period[i][1][1]),ep.julian_date(sort_period[i+1][1][1])]
            if kk[0] != 0:
                self.SkyV_period.append(kk)
        self.oadm.date = self.comp_date
        if k == '+':
            x['SkyV_period'] = self.SkyV_period

        return self.SkyV_period



#######################################################################

    def line_coord(self,targ, coord_val,coord_acro):
        """parse pyephem coordinates format
            targ = target name
            coord_val = coordinates value from {toi} data
            coord_acro = coordinates acronym from {toi} data""" # TODO: Revisar coord. dels asteroides!!
        if coord_acro == 'e':
            coord_val_1 = coord_val.split(' ')
            self.coord_line=(targ+',f,'+ coord_val_1[0]+','+coord_val_1[2]+', ,'+coord_val_1[-1]+', "')
        elif coord_acro == 'm':
            coord_val_1 = coord_val.split(' ')
            self.coord_line = (targ+',e,'+coord_val_1[6]+','+coord_val_1[5]+','+coord_val_1[4]+','+coord_val_1[9]+',' \
            +coord_val_1[8]+','+coord_val_1[7]+','+coord_val_1[3]+','+coord_val_1[1]+'/'+coord_val_1[2]+'/' \
            +coord_val_1[0]+',2000,,')
        elif coord_acro == 'c':
            coord_val_1 = coord_val.split(' ')
            self.coord_line = (targ+',h,'+coord_val_1[1]+'/'+coord_val_1[2]+'/'+coord_val_1[0]+','+coord_val_1[7]+',' \
            +coord_val_1[6]+','+coord_val_1[5]+','+coord_val_1[4]+','+coord_val_1[3]+',2000,,')
        return self.coord_line


    def cp_targ(self,x,ob,t1,t2):
        """Validate a toi, computing airmass and moon distance,
        ob = coordinates line in ephem format
        t1,t2 = start/end time to compute"""
        self.cp_obs_time_airm(x,ob,t1,t2)
        obj = ep.readdb(ob)
        obj.compute(self.oadm)
        moon= ep.Moon(self.oadm)
        moon_dist = ep.separation(moon,obj)

        if len(x['WV_period']) == 0:
            airm = 0
        else:
            airm = 1
        if moon_dist*180.0/ep.pi > float(x['moon_distance']):
            moonD = 1
        else:
            moonD = 0

        self.Vtoi = [airm,moonD]
        return self.Vtoi

    def toi_window(self,i):

        for x in self.tois:
            if i == x['id']:
                for key in sorted(x.keys()):
                    if 'window' in key:
                        if x[key].split(',')[2] == 'added':
                            per = 0.0
                            pe0 = float(self.jd_start)
                            pe1 = float(self.jd_end)
                        else:
                            per = float(x[key].split(',')[2])
                            pe0 = float(x[key].split(',')[0])
                            pe1 = float(x[key].split(',')[1])
        return pe0,pe1,per


    def date_window_2(self,x):
        """ compute if visibility period is within window
            x = {toi}"""
        self.date_window_result = []
        for WV in x['WV_period']:
            jdS, jdE = WV[2:4]
            for key in sorted(x.keys()):
                if 'window' in key:
                    if x[key].split(',')[2] == 'added':
                        per = 0.0
                        pe0 = float(self.jd_start)
                        pe1 = float(self.jd_end)
                    else:
                        per = float(x[key].split(',')[2])
                        pe0 = float(x[key].split(',')[0])
                        pe1 = float(x[key].split(',')[1])

                    if per != 0:
                        while float(jdS) > float(pe1) or float(jdE) < float(pe0):
                            pe0 = pe0 + per
                            pe1 = pe1 + per
                            if pe0 > jdE :
                                self.date_window_result = []
                                break
                        else:
                            #print blue2,'x:{}  jdS:{} pe0:{} > jdE:{} pe1:{} per:{}'.format(x['id'],self.jd_start,pe0,self.jd_end,pe1,per),resetc
                            if pe1-pe0 !=1.0:  ### <<< Chapuza!!!! pero funciona per exoplanetes¿?¿?
                                #if pe0 > (self.jd_start - self.allowed_offset/86400.0) or (self.jd_end + self.allowed_offset/86400.0) < pe1:
                                if self.prt_exopl == 1:
                                    print blue2,'exoplanet? > {}  pe0: {}  pe1: {}  per:{}'.format(x['id'],pe0,pe1,per),resetc
                                self.date_window_result.append([x['id'],max(jdS,pe0),min(jdE,pe1),per])
                                break

                            elif pe0 < jdS:
                                if (jdE-jdS)*24*3600 < self.cp_exp_time(x):
                                    self.date_window_result = []
                                    break
                                else:
                                    self.date_window_result.append([x['id'],max(jdS,pe0),min(jdE,pe1),per])
                            elif pe0 >= jdS:
                                if (jdE-pe0)*24*3600 < self.cp_exp_time(x):
                                    self.date_window_result = []
                                    break
                                else:
                                    self.date_window_result.append([x['id'],max(jdS,pe0),min(jdE,pe1),per])
                    else:
                        if float(jdS) > float(pe1) or float(jdE) < float(pe0):
                            self.date_window_result = []
                            break
                        elif pe0 < jdS:
                            if (jdE-jdS)*24*3600 < self.cp_exp_time(x):
                                self.date_window_result = []
                                break
                            else:
                                self.date_window_result.append([x['id'],max(jdS,pe0),min(jdE,pe1),per])
                        elif pe0 >= jdS:
                            if (jdE-pe0)*24*3600 < self.cp_exp_time(x):
                                self.date_window_result = []
                                break
                            else:
                                self.date_window_result.append([x['id'],max(jdS,pe0),min(jdE,pe1),per])
                        else:
                            print red2,'WARNING x:{}  pe0:{} pe1:{} per:{}'.format(x['id'],pe0,pe1,per),resetc
                            self.date_window_result = []
                            break

        return self.date_window_result

    def cp_exp_time(self,x):                                  # toi aprox. exposures duration
        self.exp_time = float(x['exposures'])*float(x['exposure_time'])
        return self.exp_time


    def cp_transit(self,ob,x,k='+'):   #TODO: revisar transits next i previous!
        """ returns the JD of previous/next object transit
            ob = coordinate line in ephem format """
        obj = ep.readdb(ob)
        self.Transit =ep.julian_date(self.oadm.previous_transit(obj))
        if self.Transit < self.jd_start:
            self.Transit =ep.julian_date(self.oadm.next_transit(obj))
        if k == '+':
            x['transit'] = self.Transit
        return self.Transit


