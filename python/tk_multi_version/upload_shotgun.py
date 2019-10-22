# -*- coding: utf-8 -*-

import sgtk
import os
import subprocess
import pyseq
import shutil


codecs = {
    "Apple ProRes 4444":"ap4h",
    "Apple ProRes 422 HQ":"apch",
    "Apple ProRes 422":"apcn",
    "Apple ProRes 422 LT":"apcs",
    "Apple ProRes 422 Proxy":"apco",
    "Avid DNxHD Codec":"AVdn"}

class Output(object):
    

    def __init__(self,info):
        
        self.mov_fps = float(info['sg_fps'])
        self._set_file_type(info['sg_out_format'])
        self._set_colorspace(info['sg_colorspace'],info)
        self.mov_codec = codecs[info['sg_mov_codec']]
    
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
            self.colorspace = text
            self.mov_colorspace = text

class Transcoding(object):

    def __init__(self,fileinfo,context,selected_type):

        
        if selected_type in ["mov","image"]:
            self.fileinfo = fileinfo
        else:
            self.fileinfo = fileinfo.seq_info
        self.selected_type = selected_type
        self.context = context
        self.selected_type = selected_type
            

    def create_mov(self):

        if self.selected_type == "image":
            return
        if self.selected_type == "mov":
            return
        command = ['rez-env','nuke','--','nuke','-ix']
        if not self.setting.colorspace.find("ACES") == -1:
            command = ['rez-env','nuke','ocio_config','--','nuke','-ix']
        command.append(self.tmp_nuke_script_file)
        try:
            mov_p = subprocess.check_call(command)
        except Exception as e:
            raise Exception("make mov {}".format(e))

    def create_mp4(self):
        if self.selected_type == "image":
            self.mp4_path = ""
            return
        if self.selected_type == "mov":
            if self.fileinfo.suffix() == "mp4":
                self.mp4_path = self.mov_path
                return 
            self.mp4_path = self.mov_path.replace(self.fileinfo.suffix(),"mp4")
        else:
            self.mp4_path = os.path.join(os.path.abspath(
                                os.path.join(self.fileinfo.path(),"../..")),
                                 self.fileinfo.format("%h")+"mp4")
        
        command = ['rez-env','ffmpeg','--','ffmpeg','-y']
        command.append("-i")
        command.append(self.mov_path)
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
        command.append("-vf")
        command.append("pad='ceil(iw/2)*2:ceil(ih/2)*2'")
        command.append(self.mp4_path)
        

        try:
            mp4_p = subprocess.check_call(command)
        except Exception as e:
            raise Exception("make mp4 {}".format(e))

    def create_webm(self):
        if self.selected_type == "image":
            self.webm_path = ""
            return
        if self.selected_type == "mov":
            self.webm_path = self.mov_path.replace(self.fileinfo.suffix(),"webm")
        else:
            self.webm_path = os.path.join(os.path.abspath(
                                os.path.join(self.fileinfo.path(),"../..")),
                                 self.fileinfo.format("%h")+"webm")
        
        command = ['rez-env','ffmpeg','--','ffmpeg','-y']
        command.append("-i")
        command.append(self.mov_path)
        command.append("-vcodec")
        command.append("libvpx")
        #command.append("-r")
        #command.append("24")
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
        command.append(self.webm_path)
        

        try:
            webm_p = subprocess.check_call(command)
        except Exception as e:
            raise Exception("make webm {}".format(e))

    def create_nuke_script(self):

        if self.selected_type == "mov":
            self.read_path = ""
            self.mov_path = self.fileinfo.absoluteFilePath()
            return
        if self.selected_type == "image":
            self.read_path = self.fileinfo.absoluteFilePath()
            self.mov_path = ""
            return

        engine = sgtk.platform.current_engine()
        project = self.context.project

        shotgun = engine.shotgun
        output_info = shotgun.find_one("Project",[['id','is',project['id']]],
                               ['sg_colorspace','sg_mov_codec',
                               'sg_out_format','sg_fps','sg_mov_colorspace'])

    
    
        setting = Output(output_info)
        self.setting = setting

        self.read_path = os.path.join(os.path.abspath(
                                os.path.join(self.fileinfo.path(),"..")),
                                self.fileinfo.format("%h%p%t"))
        
        
        self.mov_path = os.path.join(os.path.abspath(
                                os.path.join(self.fileinfo.path(),"../..")),
                                 self.fileinfo.format("%h")+"mov")

        self.tmp_nuke_script_file = os.path.join(os.path.abspath(
                                os.path.join(self.fileinfo.path(),"../..")),
                                 self.fileinfo.format("%h")+"py")


        nk = ''
        nk += 'import nuke\n'
        nk += 'import os\n'
        nk += 'nuke.knob("root.first_frame", "{}" )\n'.format(self.fileinfo.start())
        nk += 'nuke.knob("root.last_frame", "{}" )\n'.format(self.fileinfo.end() )
        #if not setting.colorspace.find("ACES") == -1:
        #    nk += 'nuke.root()["colorManagement"].setValue("OCIO")\n'
        #    nk += 'nuke.root()["OCIO_config"].setValue("aces_1.0.1")\n'
        nk += 'read = nuke.nodes.Read( name="Read1",file="{}" )\n'.format(self.read_path )
        nk += 'read["first"].setValue( {} )\n'.format(self.fileinfo.start() )
        nk += 'read["last"].setValue( {} )\n'.format(self.fileinfo.end())
        if self.fileinfo.tail() in ['.jpg','.jpeg','.dpx']:
            nk += 'read["colorspace"].setValue( "{}")\n'.format(setting.mov_colorspace)
        tg = 'read'
    
        nk += 'output = "{}"\n'.format( self.mov_path )
        nk += 'write   = nuke.nodes.Write(name="mov_write", inputs = [%s],file=output )\n'% tg
        nk += 'write["file_type"].setValue( "mov" )\n'
        nk += 'write["create_directories"].setValue(True)\n'
        nk += 'write["mov64_codec"].setValue("{}")\n'.format(setting.mov_codec)
        nk += 'write["mov64_fps"].setValue( {})\n'.format(setting.mov_fps)
        #if self.fileinfo.tail() in ['.jpg','.jpeg']:
        nk += 'write["colorspace"].setValue( "{}")\n'.format(setting.mov_colorspace)
        nk += 'nuke.execute(write,{0},{1},1)\n'.format(self.fileinfo.start(),
                                                     self.fileinfo.end())

        nk += 'os.remove("{}")\n'.format(self.tmp_nuke_script_file)
        nk += 'exit()\n'


        
        if not os.path.exists( os.path.dirname(self.tmp_nuke_script_file) ):
            cur_umask = os.umask(0)
            os.makedirs(os.path.dirname(self.tmp_nuke_script_file),0777 )
            os.umask(cur_umask)

        with open( self.tmp_nuke_script_file, 'w' ) as f:
            f.write( nk )
        return self.tmp_nuke_script_file

    
    def create_thumbnail_for_image(self):

        if not self.selected_type == "image":
            return

        self.thumbnail_file = self.fileinfo.absoluteFilePath().replace(
            self.fileinfo.suffix(),"_thumb.jpg")

        command = ['rez-env',"ffmpeg","--","ffmpeg","-y"]
        command.append("-i")
        command.append(self.read_path)
        command.append("-f")
        command.append("image2")
        command.append(self.thumbnail_file)

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

        print " ".join(command)

        try:
            webm_p = subprocess.Popen(command,stdout=subprocess.PIPE)
            output,err = webm_p.communicate()
            return int(output)
        except Exception as e:
            raise Exception("make webm {}".format(e))
        
        

    def create_thumbnail(self):

        if self.selected_type == "image":
            self.filmstream_file = ""
            return
        if self.selected_type == "mov":
            self.thumbnail_path = self.mov_path.replace(
                self.fileinfo.suffix(),"")
        else:
            self.thumbnail_path = os.path.join(os.path.abspath(
                                os.path.join(self.fileinfo.path(),"../..")),
                                 self.fileinfo.format("%h")+"_thumb")


        if not os.path.exists(self.thumbnail_path ):
            cur_umask = os.umask(0)
            os.makedirs(self.thumbnail_path,0777 )
            os.umask(cur_umask)
        if self.selected_type == "mov":
            thumb_template = os.path.join(self.thumbnail_path,
                                      self.fileinfo.fileName()+".%04d.jpg")
        else:
            thumb_template = os.path.join(self.thumbnail_path,
                                      self.fileinfo.format("%h%p")+".jpg")

        select_code = self._get_mov_frame(self.mov_path)
        select_code /= 30
        if select_code == 0:
            select_code = 1
        command = ['rez-env',"ffmpeg","--","ffmpeg","-y"]
        command.append("-r")
        command.append("24")
        command.append("-i")
        command.append(self.mov_path)
        command.append("-vf")
        command.append("select='gte(n\,{0})*not(mod(n\,{0}))'".format(select_code))
        command.append("-vsync")
        command.append("0")
        command.append("-f")
        command.append("image2")
        command.append(thumb_template)
        

        try:
            webm_p = subprocess.check_call(command)
        except Exception as e:
            raise Exception("make images {}".format(e))
        

        if self.selected_type == "mov":
            thumb_template = os.path.join(self.thumbnail_path,
                                      self.fileinfo.fileName()+"*")
        else:
            thumb_template = os.path.join(self.thumbnail_path,
                                      self.fileinfo.format("%h")+"*")
        if self.selected_type == "mov":
            self.filmstream_file = self.mov_path.replace(self.fileinfo.suffix(),"_film-0.jpg")
        else:
            self.filmstream_file = os.path.join(os.path.abspath(
                                os.path.join(self.fileinfo.path(),"../..")),
                                 self.fileinfo.format("%h")+"_film_-0.jpg")
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
        command.append(self.filmstream_file)
        

        try:
            webm_p = subprocess.check_call(command)
        except Exception as e:
            raise Exception("make montage {}".format(e))
        
        thumbnail_files = os.listdir(self.thumbnail_path)
        thumbnail_file = os.path.join(
                            self.thumbnail_path,
                            thumbnail_files[len(thumbnail_files)/2]
                            )
        
        shutil.copyfile(thumbnail_file , self.thumbnail_path+".jpg")
        self.thumbnail_file = self.thumbnail_path + ".jpg"

        command = ['rm','-rf',self.thumbnail_path]
        try:
            webm_p = subprocess.check_call(command)
        except Exception as e:
            raise Exception("rm thumbnail_path {}".format(e))

class UploadVersion(object):
    
    def __init__(self,fileinfo,context,selected_type):
        
        if selected_type in ["mov","image"]:
            self.fileinfo = fileinfo
        else:
            self.fileinfo = fileinfo.seq_info

        self.selected_type = selected_type
        self.context = context
        self.sg = self.context.sgtk.shotgun


    def create_version(self,frame_path,mov_path,desc):
        
        if self.selected_type in ["mov","image"]:
            code = self.fileinfo.fileName().replace(self.fileinfo.suffix(),"")
        else:
            code = self.fileinfo.format("%h").split(".")[0]

        data = {
            "project" : self.context.project,
            "code":code,
            "entity":self.context.entity,
            "sg_task":self.context.task,
            "sg_version_type" : "review",
            "sg_path_to_movie" :mov_path,
            "sg_path_to_frames" :frame_path,
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
            return
        self.sg.upload("Version",self.version['id'],mp4_file,'sg_uploaded_movie_mp4')
    
    def upload_webm(self,webm_file):

        if self.selected_type == "image":
            return
        self.sg.upload("Version",self.version['id'],webm_file,'sg_uploaded_movie_webm')
        os.remove(webm_file)
