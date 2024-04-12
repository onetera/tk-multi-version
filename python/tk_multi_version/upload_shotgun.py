# -*- coding: utf-8 -*-

import sgtk
import os
import sys
import platform
import subprocess
from .ext_packages import pyseq
import shutil
import datetime

import logging

codecs = {
    "Apple ProRes 4444":"ap4h",
    "Apple ProRes 422 HQ":"apch",
    "Apple ProRes 422":"apcn",
    "Apple ProRes 422 LT":"apcs",
    "Apple ProRes 422 Proxy":"apco",
    "Avid DNxHD 444": "AVdn",
    "Avid DNxHD 422":"AVdn"}

class Output(object):
    

    def __init__(self,info,shot_info):
        
        self.mov_fps = float(info['sg_fps'])
        self.shot_info = shot_info
        self._set_file_type(info['sg_out_format'])
        self._set_colorspace(info['sg_colorspace'],info)
        self.mov_codec = codecs["Apple ProRes 422 HQ"]
        # self.mov_codec = codecs[info['sg_mov_codec']]
        if info['sg_mov_codec'] == "Avid DNxHD 444":
            self.dnxhd_profile = 'DNxHD 444 10-bit 440Mbit'
        
        elif info['sg_mov_codec'] == "Avid DNxHD 422":
            self.dnxhd_profile = 'DNxHD 422 10-bit 220Mbit'
        else:
            self.dnxhd_profile = ''

    def _set_file_type(self,text):
        
        if text =="exr 32bit":
            self.file_type = "exr"
            self.datatype = "32 bit float"
        if text =="exr 16bit":
            self.file_type = "exr"
            self.datatype = "16 bit half"
        if text =="dpx 10bit":
            self.file_type = "dpx"
            self.datatype = "10 bit"
    
    def _set_colorspace(self,text,info):
        
        if not text.find("ACES") == -1 :
            self.colorspace = "ACES - %s"%text
            self.mov_colorspace = info['sg_mov_colorspace']
        else:
            if not info['sg_mov_colorspace'] :
                self.colorspace = text
                self.mov_colorspace = text
            else:
                self.colorspace = text
                self.mov_colorspace = info['sg_mov_colorspace']

        if self.shot_info:
            if self.shot_info['sg_colorspace']:
                shot_colorspace = self.shot_info['sg_colorspace']
                #if not shot_colorspace.find("ACES") == -1 :
                #    shot_colorspace = "ACES - %s"%shot_colorspace
                if not text.find("ACES") == -1 and\
                    shot_colorspace == 'rec709':
                    self.colorspace = 'Output - Rec.709'
                elif not text.find("Sony") == -1 and\
                    shot_colorspace == 'Sony.rec709':
                    self.colorspace = 'rec709'
                elif not text.find("Arri4") == -1 and\
                    shot_colorspace == 'Arri.rec709':
                    self.colorspace = 'rec709'
                elif not self.colorspace == shot_colorspace:
                    self.colorspace = shot_colorspace
                    self.mov_colorspace = shot_colorspace


class Transcoding(object):

    def __init__(self,fileinfo,context,selected_type,seq_colorspace, desc,mov_colorspace,fps_is_checked):

        
        if selected_type in ["mov","image"]:
            self.fileinfo = fileinfo
        else:
            self.fileinfo = fileinfo.seq_info
        self.selected_type = selected_type
        self.context = context
        self.selected_type = selected_type
        self.desc = desc
        self.mov_colorspace = mov_colorspace
        self.seq_colorspace = seq_colorspace
        self.fps_checked = fps_is_checked
            

    def create_mov(self, qc = False ):
        if self.selected_type == "image":
            return
        if self.selected_type == "mov":
            return
        
        nuke_ver = 'nuke-13' if qc else 'nuke-12'
        command = ['rez-env', nuke_ver,'--','nuke','-ix']

        if not self.output_info['sg_colorspace'].find("ACES") == -1 and self.fileinfo.tail() in ['.dpx','.exr']:
            command = ['rez-env', nuke_ver ,'ocio_config','--','nuke','-ix']
        if not self.output_info['sg_colorspace'].find("Alexa") == -1 and self.fileinfo.tail() in ['.dpx','.exr']:
            command = ['rez-env', nuke_ver,'alexa_config','--','nuke','-ix']
        if not self.output_info['sg_colorspace'].find("legacy") == -1 and self.fileinfo.tail() in ['.dpx','.exr']:
            command = ['rez-env', nuke_ver,'legacy_config','--','nuke','-ix']
        if not self.output_info['sg_colorspace'].find("Sony") == -1 and self.fileinfo.tail() in ['.dpx','.exr']:
            command = ['rez-env', nuke_ver,'sony_config','--','nuke','-ix']
        if not self.output_info['sg_colorspace'].find("Arri4") == -1 and self.fileinfo.tail() in ['.dpx','.exr']:
            command = ['rez-env', nuke_ver,'alexa4_config','--','nuke','-ix']
            
        nuke_script_file = self.qc_tmp_nuke_script_file if qc else self.tmp_nuke_script_file

        command.append( nuke_script_file )

        try:
            print(command)
            mov_p = subprocess.check_call(command)
        except Exception as e:
            raise Exception("make mov {}".format(e))

    def create_hdr_mov( self, qc = False ):
        if self.selected_type == "image" or self.selected_type == "mov":
            return
        if self.setting.colorspace.find('ACES') == -1:
            return
        hdr_nuke_script = self.create_hdr_nuke_script( qc )

        if hdr_nuke_script:
            nuke_ver = 'nuke-13' if qc else 'nuke-12'
            command = ['rez-env', nuke_ver ,'hdr_config','--','nuke','-ix']
            command.append( hdr_nuke_script )

            try:
                hdr_p = subprocess.check_call(command)
            except Exception as e:
                raise Exception("make hdr mov {}".format(e))
    
    def create_hdr_nuke_script( self, qc = False ):
        if qc:
            tmp_hdr_nuke_script_file = os.path.join(os.path.abspath(
                                os.path.join(self.fileinfo.path(),"../..")),
                                 self.fileinfo.format("%h")+ "hdr" + ".py")
        else:
            tmp_hdr_nuke_script_file = os.path.join(os.path.abspath(
                                os.path.join(self.fileinfo.path(),"../..")),
                                 self.fileinfo.format("%h")+ "hdr" + ".py")
        qc_prefix = 'qc_' if qc else '' 
        print( "=======HDR settting info============"   )
        print(    "color space : ACES - ACES2065-1"     )
        print(   "mov color space : Output - Rec.709"   )
        print(   "mov codec : Apple ProRes 4444 "   )
        print( "=======HDR settting info============"   )
        if qc :
            hdr_path = self.qc_hdr_path
        else :
            hdr_path = self.hdr_path
        
        if platform.system() in ('Windows',"Microsoft"):
            return 
            hdr_log_path = '\\\\10.0.40.12\\user\\user\\pipeline\\kyoungmin\\work\\toolkit\\tk-multi-version\\log_HDR.log'
        else:
            hdr_log_path = '/storenext/user/pipeline/kyoungmin/work/toolkit/tk-multi-version/log_HDR.log'
        now = datetime.datetime.now()
        temp = sys.stdout
        with open( hdr_log_path, 'a+') as sys.stdout:
            print( now.strftime('%Y-%m-%d %H:%M:%S') + ' - [PATH] : {0}'.format(hdr_path))
        sys.stdout = temp

        nk = ''
        nk += '#-*- coding: utf-8 -*-\n'
        nk += 'import nuke\n'
        nk += 'import os\n'
        nk += 'nuke.knob("root.first_frame", "{}" )\n'.format(self.fileinfo.start())
        nk += 'nuke.knob("root.last_frame", "{}" )\n'.format(self.fileinfo.end() )

        if platform.system() in ('Windows',"Microsoft"):
            nk += 'read = nuke.nodes.Read( name="Read1",file="{}" )\n'.format( self.read_path.replace("\\","/") )
        else:
            nk += 'read = nuke.nodes.Read( name="Read1",file="{}" )\n'.format( self.read_path )
        nk += 'read["first"].setValue( {} )\n'.format(self.fileinfo.start() )
        nk += 'read["last"].setValue( {} )\n'.format(self.fileinfo.end())
        nk += 'read["colorspace"].setValue( "{}")\n'.format("ACES - ACES2065-1")
        if platform.system() in ('Windows',"Microsoft"):
            nk += 'output = "{}"\n'.format( self.hdr_path.replace("\\","/") )
        else:
            nk += 'output = "{}"\n'.format( self.hdr_path )
            
        nk += 'write = nuke.nodes.Write(name="hdr_write", inputs = [read],file=output )\n'
        nk += 'write["file_type"].setValue( "mov" )\n'
        nk += 'write["create_directories"].setValue(True)\n'
        nk += 'write["mov64_codec"].setValue("{}")\n'.format("ap4h")
        nk += 'write["mov64_fps"].setValue({})\n'.format(self.setting.mov_fps)
        nk += 'write["colorspace"].setValue( "{}")\n'.format("Output - Rec.709")
        nk += 'nuke.execute(write,{0},{1},1)\n'.format(self.fileinfo.start(),
                                                     self.fileinfo.end())
        if not platform.system() in ('Windows',"Microsoft"):
            nk += 'os.remove("{}")\n'.format( tmp_hdr_nuke_script_file )
        nk += 'exit()\n'

        if not os.path.exists( os.path.dirname( tmp_hdr_nuke_script_file) ):
            cur_umask = os.umask(0)
            os.makedirs(os.path.dirname( tmp_hdr_nuke_script_file), 0o777 )
            os.umask(cur_umask)

        with open( tmp_hdr_nuke_script_file, 'w' ) as f:
            f.write( nk )
        
        os.chmod(tmp_hdr_nuke_script_file, 0o777)
        
        return tmp_hdr_nuke_script_file 


    def create_mp4(self, qc = False ):
        qc_prefix = 'qc_' if qc else '' 
        if self.selected_type == "image":
            if qc:
                self.qc_mp4_path = self.qc_mov_path
            else:
                self.mp4_path = self.mov_path
            return
        if self.selected_type == "mov":
            if self.fileinfo.suffix() == "mp4":
                if qc:
                    self.qc_mp4_path = self.qc_mov_path
                else:
                    self.mp4_path = self.mov_path
                return 
            if qc:
                self.qc_mp4_path = self.qc_mov_path.replace(self.fileinfo.suffix(),"mp4")
            else:
                self.mp4_path = self.mov_path.replace(self.fileinfo.suffix(),"mp4")
        else:
            if qc:
                self.qc_mp4_path = os.path.join(os.path.abspath(
                                os.path.join(self.fileinfo.path(),"../..")),
                                 qc_prefix + self.fileinfo.format("%h")+"mp4")
            else:
                self.mp4_path = os.path.join(os.path.abspath(
                                os.path.join(self.fileinfo.path(),"../..")),
                                 self.fileinfo.format("%h")+"mp4")


        if qc :
            mov_path = os.path.dirname( self.mov_path ) + os.sep + qc_prefix + os.path.basename( self.mov_path )
            mp4_path = self.qc_mp4_path
        else:
            mov_path = self.mov_path 
            mp4_path = self.mp4_path
        
        command = ['rez-env','ffmpeg','--','ffmpeg','-y']
        command.append("-i")
        command.append( mov_path )
        command.append("-vcodec")
        command.append("libx264")
        #command.append("-r")
        #command.append("24")
        command.append("-pix_fmt")
        command.append("yuv420p")
        #command.append("-preset")
        #command.append("veryslow")
        command.append("-crf")
        command.append("18")
        if platform.system() == "Linux":
            command.append("-vf")
            command.append("pad='ceil(iw/2)*2:ceil(ih/2)*2'")
        command.append( mp4_path )
        

        try:
            mp4_p = subprocess.check_call(command)
        except Exception as e:
            raise Exception("make mp4 {}".format(e))

    def create_webm(self, qc = False ):
        qc_prefix = 'qc_' if qc else '' 
        if self.selected_type == "image":
            self.webm_path = ""
            return
        if self.selected_type == "mov":
            if qc:
                self.qc_webm_path = self.qc_mov_path.replace(self.fileinfo.suffix(),"webm")
            else:
                self.webm_path = self.mov_path.replace(self.fileinfo.suffix(),"webm")
        else:
            if qc:
                self.qc_webm_path = os.path.join(os.path.abspath(
                                os.path.join(self.fileinfo.path(),"../..")),
                                 qc_prefix + self.fileinfo.format("%h")+"webm")
            else:
                self.webm_path = os.path.join(os.path.abspath(
                                os.path.join(self.fileinfo.path(),"../..")),
                                 self.fileinfo.format("%h")+"webm")

        if qc:
            webm_path     = self.qc_webm_path
            mov_path      = self.qc_mov_path
            mov_webm_path = self.qc_mov_webm_path
        else:
            webm_path     = self.webm_path
            mov_path      = self.mov_path
            mov_webm_path = self.mov_webm_path

        if platform.system() == "Linux":

            command = ['rez-env','ffmpeg','--','ffmpeg','-y']
            command.append("-i")
            if mov_webm_path :
                command.append( mov_webm_path )
            else:
                command.append( mov_path )
            command.append("-vcodec")
            command.append("libvpx")
            command.append("-pix_fmt")
            command.append("yuv420p")
            command.append("-g")
            command.append("30")
            command.append("-b:v")
            command.append("2000k")
            command.append("-quality")
            command.append("realtime")
            command.append("-cpu-used")
            command.append("0")
            command.append("-qmin")
            command.append("10")
            command.append("-qmax")
            command.append("42")
            command.append("-vf")
            command.append("pad='ceil(iw/2)*2:ceil(ih/2)*2'")
            command.append(webm_path)

        else:
        
            command = ['rez-env','ffmpeg','--','ffmpeg','-y']
            command.append("-i")
            if mov_webm_path :
                command.append(mov_webm_path.replace("/","\\"))
            else:
                command.append(mov_path.replace("/","\\"))
            command.append("-vcodec")
            command.append("libvpx")
            command.append("-pix_fmt")
            command.append("yuv420p")
            command.append("-g")
            command.append("30")
            command.append("-b:v")
            command.append("2000k")
            command.append("-quality")
            command.append("realtime")
            command.append("-cpu-used")
            command.append("0")
            command.append("-qmin")
            command.append("10")
            command.append("-qmax")
            command.append("42")
            command.append(webm_path.replace("/","\\"))

        try:
            webm_p = subprocess.check_call(command)
        except Exception as e:
            raise Exception("make webm {}".format(e))

    def create_nuke_script(self, qc = False ):

        if qc:
            self.qc_mov_webm_path = None
        else:
            self.mov_webm_path = None
        qc_prefix = 'qc_' if qc else '' 

        if self.selected_type == "mov":
            if qc:
                self.qc_read_path = ""
                self.qc_mov_path = self.fileinfo.absoluteFilePath()
                self.qc_hdr_path = ""
            else:
                self.read_path = ""
                self.hdr_path = ""
                self.mov_path = self.fileinfo.absoluteFilePath()
            return
        if self.selected_type == "image":
            if qc:
                self.qc_read_path = self.fileinfo.absoluteFilePath()
                self.qc_hdr_path = ""
                self.qc_mov_path = self.fileinfo.absoluteFilePath()
            else:
                self.read_path = self.fileinfo.absoluteFilePath()
                self.hdr_path = ""
                self.mov_path = self.fileinfo.absoluteFilePath()

            return

        engine = sgtk.platform.current_engine()
        project = self.context.project
        shot_info = None
        check_tag = None
        shotgun = engine.shotgun
        entity_ent = self.context.entity
        plate_ent = shotgun.find_one("PublishedFileType",[['id','is',54]]) # id 54 => Plate
        # print( "=======entity_ent============"   )
        # print(entity_ent)
        if entity_ent['type'] == "Shot":
            filter_pub = [
                ['entity','is',entity_ent],
                ['published_file_type','is',plate_ent]
            ]
            publishfile_ents = shotgun.find("PublishedFile",filter_pub,['sg_colorspace'])
            if publishfile_ents : 
                shot_info = publishfile_ents[-1]
            
            shot_ent = shotgun.find_one("Shot",[['id','is',entity_ent['id']]],['tags'])
            #check_tag = [ x['id'] for x in shot_ent['tags'] if x['id'] in [4591,4830]] 
        
        
        
        self.output_info = shotgun.find_one("Project",[['id','is',project['id']]],
                               ['sg_colorspace','sg_mov_codec',
                               'sg_out_format','sg_fps','sg_mov_colorspace'])
        
        if entity_ent['type'] == "Asset" :
            shot_info = {'sg_colorspace':''}
        
        # print( "=======test info============"   ):
        if self.seq_colorspace != "NONE":
            # print(self.seq_colorspace)
            self.output_info['sg_colorspace'] = str(self.seq_colorspace)
            shot_info['sg_colorspace'] = str(self.seq_colorspace)
        if self.mov_colorspace != "NONE":
            # print(self.mov_colorspace)
            self.output_info['sg_mov_colorspace'] = str(self.mov_colorspace)

        setting = Output(self.output_info,shot_info)
        self.setting = setting


        print( "=======settting info============"   )
        print( entity_ent['type'] )
        print( self.setting.colorspace              )
        print( self.setting.mov_colorspace          )
        print( "=======settting info============"   )

        if qc :
            self.qc_read_path = os.path.join(os.path.abspath(
                                os.path.join(self.fileinfo.path(),"..")),
                                qc_prefix + self.fileinfo.format("%h%p%t"))
        
        
            self.qc_mov_path = os.path.join(os.path.abspath(
                                os.path.join(self.fileinfo.path(),"../..")),
                                 qc_prefix + self.fileinfo.format("%h")+"mov")

            self.qc_hdr_path = os.path.join(os.path.abspath(
                                os.path.join(self.fileinfo.path(),"../..")),
                                 qc_prefix + self.fileinfo.format("%h") + "hdr" + ".mov")

            self.qc_tmp_nuke_script_file = os.path.join(os.path.abspath(
                                os.path.join(self.fileinfo.path(),"../..")),
                                 qc_prefix + self.fileinfo.format("%h")+"py")
        else:
            self.read_path = os.path.join(os.path.abspath(
                                os.path.join(self.fileinfo.path(),"..")),
                                self.fileinfo.format("%h%p%t"))
        
            self.mov_path = os.path.join(os.path.abspath(
                                os.path.join(self.fileinfo.path(),"../..")),
                                 self.fileinfo.format("%h")+"mov")

            self.hdr_path = os.path.join(os.path.abspath(
                                os.path.join(self.fileinfo.path(),"../..")),
                                 self.fileinfo.format("%h") + "hdr" + ".mov")

            self.tmp_nuke_script_file = os.path.join(os.path.abspath(
                                os.path.join(self.fileinfo.path(),"../..")),
                                 self.fileinfo.format("%h")+"py")

        ## qc file path redefine
        if qc:
            read_path = self.qc_read_path
            mov_path  = self.qc_mov_path
            hdr_path  = self.qc_hdr_path
            tmp_nuke_script_file = self.qc_tmp_nuke_script_file
        else:
            read_path = self.read_path
            mov_path  = self.mov_path
            hdr_path  = self.hdr_path
            tmp_nuke_script_file = self.tmp_nuke_script_file


        timecard = sum([ x['duration'] for x  in 
                    shotgun.find("TimeLog",
                                 [['entity','is',self.context.task]],
                                 ['duration']) ])
        
        if not timecard :
            timecard = 0
        else:
            timecard = timecard / 60
        


        nk = ''
        nk += '#-*- coding: utf-8 -*-\n'
        nk += 'import nuke\n'
        nk += 'import os\n'
        nk += 'nuke.knob("root.first_frame", "{}" )\n'.format(self.fileinfo.start())
        nk += 'nuke.knob("root.last_frame", "{}" )\n'.format(self.fileinfo.end() )
        #if not setting.colorspace.find("ACES") == -1:
        #    nk += 'nuke.root()["colorManagement"].setValue("OCIO")\n'
        #    nk += 'nuke.root()["OCIO_config"].setValue("aces_1.0.1")\n'

        if platform.system() in ('Windows',"Microsoft"):
            nk += 'read = nuke.nodes.Read( name="Read1",file="{}" )\n'.format( self.read_path.replace("\\","/") )
        else:
            nk += 'read = nuke.nodes.Read( name="Read1",file="{}" )\n'.format( self.read_path )
        nk += 'read["first"].setValue( {} )\n'.format(self.fileinfo.start() )
        nk += 'read["last"].setValue( {} )\n'.format(self.fileinfo.end())
        if self.fileinfo.tail() in ['.dpx','.exr']:
            if self.seq_colorspace != "NONE":
                nk += 'read["colorspace"].setValue( "{}")\n'.format(self.seq_colorspace)
            else:
                nk += 'read["colorspace"].setValue( "{}")\n'.format(setting.colorspace)
        else:
            nk += 'read["colorspace"].setValue( "{}")\n'.format("rec709")
        
        if platform.system() in ('Windows',"Microsoft"):
            nk += 'output = "{}"\n'.format( mov_path.replace("\\","/") )
        else:
            nk += 'output = "{}"\n'.format( mov_path )

        nk += 'width = int(nuke.tcl("expression {0}.width".format(read.name())))\n'


        if qc:
            nk += 'qc = nuke.nodes.SQCV(name="SQCV", inputs = [read])\n'
            nk += 'qc["which"].setValue(3)\n'
            previous_node = 'qc'
        else:
            previous_node = 'read'

        if self.context.project['name'] in ['westworld','asd2']:
            nk += 'burnin = nuke.nodes.m83_gizmo(name="m83_gizmo", inputs = [{}])\n'.format( previous_node )
            nk += 'burnin["seq"].setValue("{}")\n'.format(self.context.entity['name'].split("_")[0])
            nk += 'burnin["shot"].setValue("{}")\n'.format(self.context.entity['name'].split("_")[1])
            nk += 'burnin["team"].setValue("{}")\n'.format(self.context.step['name'])
            # nk += 'burnin["artist"].setValue("{}")\n'.format(self.context.user['name'])
            nk += 'burnin["version"].setValue("{}")\n'.format(self.fileinfo.format("%h").split(".")[0].split("_")[-1])
            #nk += 'burnin["input.first"].setValue("{}")\n'.format(self.context.task['name'])
            #nk += 'burnin["input.last"].setValue("{}")\n'.format(self.context.task['name'])
        else:
            nk += 'if width > 3000 : \n'
            nk += '    reformat = nuke.nodes.Reformat(inputs=[{}],type=2,scale=.5)\n'.format( previous_node )
            nk += '    burnin = nuke.nodes.ww_burnin(name="ww_burn", inputs = [reformat])\n'
            nk += 'else : \n'
            nk += '    burnin = nuke.nodes.ww_burnin(name="ww_burn", inputs = [{}])\n'.format( previous_node )

            nk += 'burnin["project_name"].setValue("{}")\n'.format(self.context.project['name'])
            nk += 'burnin["file_name"].setValue("{}")\n'.format(self.fileinfo.format("%h").split(".")[0])
            nk += 'burnin["user"].setValue("{}")\n'.format(self.context.user['name'])
            nk += 'burnin["task"].setValue("{}")\n'.format(self.context.task['name'])
            if self.context.project['name'] in ['sweethome','westworld']:
                nk += 'burnin["timecard"].setValue("")\n'
            else:
                nk += 'burnin["timecard"].setValue("{}hrs")\n'.format(timecard)
            nk += 'burnin["description"].setValue("{}")\n'.format(self.desc.replace("\n","_"))
        nk += 'write = nuke.nodes.Write(name="mov_write", inputs = [burnin],file=output )\n'
        if self.context.project['name'] in ['westworld','asd2']:
            nk += 'write["raw"].setValue(True)\n'
        nk += 'write["file_type"].setValue( "mov" )\n'
        nk += 'write["create_directories"].setValue(True)\n'
        if self.context.project['name'] in ['westworld','asd2']:
            nk += 'write["mov64_codec"].setValue("h264")\n'
            nk += 'write["mov64_quality"].setValue(2)\n'
        else:
            nk += 'write["mov64_codec"].setValue("{}")\n'.format(setting.mov_codec)
        if self.setting.dnxhd_profile:
            nk += 'write["mov64_dnxhd_codec_profile"].setValue( "{}")\n'.format(self.setting.dnxhd_profile )
        #nk += 'write["mov64_fps"].setValue( {})\n'.format(setting.mov_fps)
        if self.context.project['name'] in ['voice4', 'robin', 'westworld']:
            nk += 'write["mov64_fps"].setValue({})\n'.format(setting.mov_fps)
        else:
            if self.context.project['name'] in ['westworld','asd2'] or self.fps_checked:
                nk += 'write["mov64_fps"].setValue(23.976)\n'
            else:
                nk += 'write["mov64_fps"].setValue(24)\n'
        if self.fileinfo.tail() in ['.dpx','.exr']:
            if self.mov_colorspace != "NONE":
                nk += 'write["colorspace"].setValue( "{}")\n'.format(self.mov_colorspace)
            else:
                nk += 'write["colorspace"].setValue( "{}")\n'.format(self.setting.mov_colorspace)
        else:
            nk += 'write["colorspace"].setValue( "{}")\n'.format("rec709")
        nk += 'nuke.execute(write,{0},{1},1)\n'.format(self.fileinfo.start(),
                                                     self.fileinfo.end())
        #fix play webm in chrome and firefox 
        

        if not setting.mov_fps == "24":
            if qc:
                self.qc_mov_webm_path = os.path.join(os.path.abspath(
                                        os.path.join(self.fileinfo.path(),"../..")),
                                        qc_prefix + self.fileinfo.format("%h").split(".")[0]+"_for_webm.mov")
            else:
                self.mov_webm_path = os.path.join(os.path.abspath(
                                        os.path.join(self.fileinfo.path(),"../..")),
                                        self.fileinfo.format("%h").split(".")[0]+"_for_webm.mov")


            if qc:
                mov_webm_path = self.qc_mov_webm_path
            else:
                mov_webm_path = self.mov_webm_path
            
            
            if platform.system() in ('Windows',"Microsoft"):
                nk += 'webm_output = "{}"\n'.format( mov_webm_path.replace("\\","/") )
            else:
                nk += 'webm_output = "{}"\n'.format( mov_webm_path )

            
            nk += 'write = nuke.nodes.Write(name="mov_write", inputs = [burnin],file=webm_output )\n'
            nk += 'write["file_type"].setValue( "mov" )\n'
            nk += 'write["create_directories"].setValue(True)\n'
            if self.context.project['name'] in ['westworld','asd2']:
                nk += 'write["raw"].setValue(True)\n'
                nk += 'write["mov64_codec"].setValue("h264")\n'
                nk += 'write["mov64_quality"].setValue(2)\n'
            else:
                nk += 'write["mov64_codec"].setValue("{}")\n'.format(setting.mov_codec)
            if self.setting.dnxhd_profile:
                nk += 'write["mov64_dnxhd_codec_profile"].setValue( "{}")\n'.format(self.setting.dnxhd_profile )

            if self.context.project['name'] in ['voice4','robin', 'westworld']:
                nk += 'write["mov64_fps"].setValue({})\n'.format(setting.mov_fps)
            elif self.fps_checked:
                nk += 'write["mov64_fps"].setValue(23.976)\n'
            else:
                nk += 'write["mov64_fps"].setValue(24)\n'
            if self.fileinfo.tail() in ['.dpx','.exr']:
                if self.mov_colorspace != "NONE":
                    nk += 'write["colorspace"].setValue( "{}")\n'.format(setting.mov_colorspace)
                else:
                    nk += 'write["colorspace"].setValue( "{}")\n'.format(self.setting.mov_colorspace)
                
            else:
                nk += 'write["colorspace"].setValue( "{}")\n'.format("rec709")
            nk += 'nuke.execute(write,{0},{1},1)\n'.format(self.fileinfo.start(),
                                                     self.fileinfo.end())


        if not platform.system() in ('Windows',"Microsoft"):
            nk += 'os.remove("{}")\n'.format( tmp_nuke_script_file)
        nk += 'exit()\n'
        
        if not os.path.exists( os.path.dirname( tmp_nuke_script_file) ):
            cur_umask = os.umask(0)
            os.makedirs(os.path.dirname( tmp_nuke_script_file),0o777 )
            os.umask(cur_umask)


        with open( tmp_nuke_script_file, 'w' ) as f:
            f.write( nk )
        
        os.chmod( tmp_nuke_script_file, 0o777 )

        return tmp_nuke_script_file 

    
    def create_thumbnail_for_image(self , qc = False ):
        qc_prefix = 'qc_' if qc else ''

        if not self.selected_type == "image":
            return

        if qc:
            self.qc_thumbnail_file = self.fileinfo.absoluteFilePath().replace(
                self.fileinfo.suffix(),"qc_thumb.jpg")

            thumbnail_file = self.qc_thumbnail_file
            read_path = self.qc_read_path
        else:
            self.thumbnail_file = self.fileinfo.absoluteFilePath().replace(
                self.fileinfo.suffix(),"thumb.jpg")
            thumbnail_file = self.thumbnail_file
            read_path = self.read_path

        command = ['rez-env',"ffmpeg","--","ffmpeg","-y"]
        command.append("-i")
        command.append(read_path)
        command.append("-f")
        command.append("image2")
        command.append( thumbnail_file )

        try:
            webm_p = subprocess.check_call(command)
        except Exception as e:
            raise Exception("make webm {}".format(e))


    def _get_mov_frame(self,mov_file):
        
        if self.selected_type == "mov":
            if self.fileinfo.suffix() in ['ogv']:
                mov_file = self.mp4_path

        command = ['rez-env',"ffmpeg","--","ffprobe"]
        command.append(mov_file)
        command.append("-select_streams")
        command.append("v")
        command.append("-show_entries")
        command.append("stream=nb_frames")
        command.append("-of")
        command.append("default=nk=1:nw=1")
        command.append("-v")
        command.append("quiet")

        try:
            webm_p = subprocess.Popen(command,stdout=subprocess.PIPE)
            output,err = webm_p.communicate()
            return int(output)
        except Exception as e:
            raise Exception("make webm {}".format(e))
        
        

    def create_thumbnail(self, qc = False ):
        qc_prefix = 'qc_' if qc else ''

        if self.selected_type == "image":
            self.filmstream_file = ""
            return
        if self.selected_type == "mov":
            self.thumbnail_path = self.mov_path.replace(
                self.fileinfo.suffix(), "thumb")
        else:
            self.thumbnail_path = os.path.join(os.path.abspath(
                                os.path.join(self.fileinfo.path(),"../..")),
                                 self.fileinfo.format("%h")+"_thumb")
        
        ## qc folder 변경
        if qc:
            if self.selected_type == "mov":
                self.qc_thumbnail_path = self.qc_mov_path.replace(
                    self.fileinfo.suffix(), "qc_thumb")
            else:
                self.qc_thumbnail_path = os.path.join(os.path.abspath(
                                    os.path.join(self.fileinfo.path(),"../..")),
                                     qc_prefix + self.fileinfo.format("%h")+"qc_thumb")

            thumbnail_path = self.qc_thumbnail_path 
        else:
            thumbnail_path = self.thumbnail_path


        if not os.path.exists( thumbnail_path ):
            cur_umask = os.umask(0)
            os.makedirs( thumbnail_path, 0o777 )
            os.umask(cur_umask)
        if self.selected_type == "mov":
            thumb_template = os.path.join( thumbnail_path,
                                      qc_prefix + self.fileinfo.fileName()+".%04d.jpg")
        else:
            thumb_template = os.path.join( thumbnail_path,
                                      qc_prefix + self.fileinfo.format("%h%p")+".jpg")

        ## 인스턴스 멤버변수로 사용되는 함수는 메소드 내에서 qc_prefix를 
        ## 파일명앞에 붙여서 로컬 변수로 다시 정의 해서 사용
        mov_path = self.qc_mov_path if qc else self.mov_path
        

        select_code = self._get_mov_frame( mov_path )
        select_code /= 30
        if select_code == 0:
            select_code = 1
        if platform.system() == "Linux":
            command = ['rez-env',"ffmpeg","--","ffmpeg","-y"]
            command.append("-r")
            command.append("24")
            command.append("-i")
            command.append(mov_path)
            command.append("-vf")
            command.append("select='gte(n\,{0})*not(mod(n\,{0}))'".format(select_code))
            command.append("-vsync")
            command.append("0")
            command.append("-f")
            command.append("image2")
            command.append(thumb_template)
        
        else:
            command = ['rez-env',"ffmpeg","--","ffmpeg","-y"]
            command.append("-r")
            command.append("24")
            command.append("-i")
            command.append(mov_path.replace("/","\\"))
            command.append("-vf")
            command.append("select=gte(n\,{0})*not(mod(n\,{0}))".format(select_code))
            command.append("-vsync")
            command.append("0")
            command.append("-f")
            command.append("image2")
            thumb_template =  thumb_template.replace("%","%%")
            command.append(thumb_template.replace("/","\\"))

        try:
            webm_p = subprocess.check_call(command)
        except Exception as e:
            raise Exception("make images {}".format(e))
        

        if self.selected_type == "mov":
            thumb_template = os.path.join( thumbnail_path,
                                      qc_prefix + self.fileinfo.fileName()+"*")
        else:
            thumb_template = os.path.join( thumbnail_path,
                                      qc_prefix + self.fileinfo.format("%h")+"*")

        if self.selected_type == "mov":
            self.filmstream_file = mov_path.replace(self.fileinfo.suffix(),"_film-0.jpg")
        else:
            self.filmstream_file = os.path.join(os.path.abspath(
                                os.path.join(self.fileinfo.path(),"../..")),
                                 self.fileinfo.format("%h")+"_film_-0.jpg")

        if qc:
            self.qc_filmstream_file = os.path.dirname( self.filmstream_file ) + os.sep + qc_prefix + os.path.basename( self.filmstream_file )
            filmstream_file = self.qc_filmstream_file
        else:
            filmstream_file = self.filmstream_file

        if platform.system() == "Linux":
            command = ['montage']
            command.append(thumb_template)
            command.append("-geometry")
            command.append("240x+0+0")
            command.append("-tile")
            command.append("x1")
            command.append("-format")
            command.append("jpeg")
            command.append("-quality")
            command.append("92")
            command.append( filmstream_file )
        else:
            command = ['magick','montage']
            command.append(thumb_template.replace("/","\\"))
            command.append("-geometry")
            command.append("240x+0+0")
            command.append("-tile")
            command.append("x1")
            command.append("-format")
            command.append("jpeg")
            command.append("-quality")
            command.append("92")
            command.append( filmstream_file.replace("/","\\"))

        try:
            webm_p = subprocess.check_call(command)
        except Exception as e:
            raise Exception("make montage {}".format(e))
        
        thumbnail_files = os.listdir(thumbnail_path)
        thumbnail_file = os.path.join(
                            thumbnail_path,
                            thumbnail_files[len(thumbnail_files)/2]
                            )
        
            
        shutil.copyfile(thumbnail_file , thumbnail_path+".jpg")

        if qc:
            self.qc_thumbnail_file = thumbnail_path + ".jpg"
        else:
            self.thumbnail_file    = thumbnail_path + ".jpg"

        if platform.system() == "Linux":
            command = ['rm','-rf', thumbnail_path]
        #else:
            #command = ['rd','/S','/Q',self.thumbnail_path.replace("/","\\")]
            try:
                webm_p = subprocess.check_call(command)
            except Exception as e:
                raise Exception("rm thumbnail_path {0},{1}".format(e,command))

class UploadVersion(object):
    
    def __init__(self,fileinfo,context,selected_type):
        
        if selected_type in ["mov","image"]:
            self.fileinfo = fileinfo
        else:
            self.fileinfo = fileinfo.seq_info

        self.selected_type = selected_type
        self.context = context
        self.sg = self.context.sgtk.shotgun


    def create_version(self, frame_path, mov_path, desc, hdr_path, qc = False):
        qc_prefix = 'qc_' if qc else ''
        
        if self.selected_type in ["mov","image"]:
            # code = self.fileinfo.fileName().replace(self.fileinfo.suffix(),"")
            code = self.fileinfo.fileName()
        else:
            code = self.fileinfo.format("%h").split(".")[0]

        code = qc_prefix + code

        data = {
            "project" : self.context.project,
            "code":code,
            "entity":self.context.entity,
            "sg_task":self.context.task,
            "sg_version_type" : "review",
            "sg_path_to_movie" :mov_path,
            "sg_path_to_frames" :frame_path,
            "sg_path_to_hdr" : hdr_path,
            "sg_first_frame" :1,
            "description" :desc
        }
        
        search_filter = [
            ['code','is',code],
            ['project','is',self.context.project],
            ['sg_task','is',self.context.task]
            ]

        current_version = self.sg.find("Version",search_filter)
        if current_version:
            self.version = current_version[0]
            data = {
            "sg_path_to_movie" :mov_path,
            "sg_path_to_frames" :frame_path,
            "sg_path_to_hdr" : hdr_path,
            "description" :desc
                }
            self.sg.update("Version",self.version['id'],data)
        else:
            self.version = self.sg.create("Version",data)

    
    def upload_thumbnail(self,thumbnail_file):

        self.sg.upload_thumbnail("Version",self.version['id'],thumbnail_file)
        os.remove(thumbnail_file)

    def upload_filmstrip_thumbnail(self,filmstream_file):

        if self.selected_type == "image":
            return

        self.sg.upload_filmstrip_thumbnail("Version",self.version['id'],filmstream_file)
        os.remove(filmstream_file)
    
    def upload_mov(self,mov_file):

        if self.selected_type == "image":
            return
        self.sg.upload("Version",self.version['id'],mov_file,'sg_uploaded_movie')

    def upload_mp4(self,mp4_file):

        if self.selected_type == "image":
            self.sg.upload("Version",self.version['id'],mp4_file,'sg_uploaded_movie_image')
            return
        self.sg.upload("Version",self.version['id'],mp4_file,'sg_uploaded_movie_mp4')
    
    def upload_webm(self,webm_file,mov_webm_path):

        if self.selected_type == "image":
            return
        self.sg.upload("Version",self.version['id'],webm_file,'sg_uploaded_movie_webm')
        os.remove(webm_file)
        if mov_webm_path:
            os.remove(mov_webm_path)


