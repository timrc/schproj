import base64
from json import loads, dumps
from wepo.settings import MEDIA_ROOT


## Encode files config dictionary
#
#  @param files_config Files configuration
#
#  @return Encoded files configuration
#
def files_config_enc(files_config):
   data = dumps(files_config)
   return base64.b64encode(data)


## Decode files config dictionary
#
#  @param files_config Files configuration
#
#  @return Decoded files configuration
#
def files_config_dec(files_config):
   if files_config:
      data = base64.b64decode(files_config)
      return loads(data)

   return files_config


## Get directory tree configuration
#
#  @return list of directory tree
#
def get_directory_tree():
   directories = create_directory_tree()
   return directories


## Get directories based on parent and add them to the list
#
#  @param data Current directory data
#  @param parent Parent to start building view
#
#  @return list of directory tree
#
def create_directory_tree(parent=None):
   directories = []

   from core.models import Directory
   childs = Directory.objects.filter(parent=parent)

   for directory in childs:
      directories.append({
         'id': directory.id,
         'name': directory.name,
         'parent': directory.parent,
         'childs': create_directory_tree(parent=directory)
      })

   return directories


## Scale image to default settings
#
#  @param file File (image) to crop
#  @param scale Scale type
#
def scale_image(file, scale):
   file_path = '%s/%s' % (MEDIA_ROOT, file.path)
   full_file_path = '%s/%s' % (file_path, file.file_name)

   #
   #  crop image
   #
   if is_image(file):
      from pgmagick import Image, Geometry

      image = Image(full_file_path)

      #
      # sizes
      #
      image_width = image.size().width()
      image_height = image.size().height()

      file.data['meta'] = dict(width=image_width, height=image_height)
      file.data['scale'] = {}

      scale_width = scale['width']
      scale_height = scale['height']

      # scale image to original image ratio
      ratio_width = float(scale_width) / float(image_width)
      ratio_height = float(scale_height) / float(image_height)

      #
      #  scale image
      #

      crop_geometry = Geometry(scale_width, scale_height, 0, 0)

      scale_steps = []

      if image_width < scale_width and image_height < scale_height:
         if image_height * ratio_width < scale_height:
            # scale to height
            g = Geometry(int(image_width * ratio_height), scale_height, 0, 0)
            image.scale(g)
            scale_steps.append(dict(name='scale', width=int(image_width * ratio_height), height=scale_height, top=0, left=0))
            # crop width
            image.crop(crop_geometry)
            scale_steps.append(dict(name='crop', width=scale_width, height=scale_height, top=0, left=0))
         else:
            # scale to width
            g = Geometry(scale_width, int(image_height * ratio_width), 0, 0)
            image.scale(g)
            scale_steps.append(dict(name='scale', width=scale_width, height=int(image_height * ratio_width), top=0, left=0))
            # crop width
            image.crop(crop_geometry)
            scale_steps.append(dict(name='crop', width=scale_width, height=scale_height, top=0, left=0))

      elif image_width < scale_width and image_height == scale_height:
         # scale to width
         g = Geometry(scale_width, int(image_height * ratio_width), 0, 0)
         image.scale(g)
         scale_steps.append(dict(name='scale', width=scale_width, height=int(image_height * ratio_width), top=0, left=0))
         # crop height
         image.crop(crop_geometry)
         scale_steps.append(dict(name='crop', width=scale_width, height=scale_height, top=0, left=0))

      elif image_width == scale_width and image_height < scale_height:
         # scale to height
         g = Geometry(int(image_width * ratio_height), scale_height, 0, 0)
         image.scale(g)
         scale_steps.append(dict(name='scale', width=int(image_width * ratio_height), height=scale_height, top=0, left=0))
         # crop width
         image.crop(crop_geometry)
         scale_steps.append(dict(name='crop', width=scale_width, height=scale_height, top=0, left=0))

      elif image_width > scale_width and image_height < scale_height:
         # scale to height
         g = Geometry(int(image_width * ratio_height), scale_height, 0, 0)
         image.scale(g)
         scale_steps.append(dict(name='scale', width=int(image_width * ratio_height), height=scale_height, top=0, left=0))
         # crop height
         image.crop(crop_geometry)
         scale_steps.append(dict(name='crop', width=scale_width, height=scale_height, top=0, left=0))

      elif image_width < scale_width and image_height > scale_height:
         # scale to width
         g = Geometry(scale_width, int(image_height * ratio_width), 0, 0)
         image.scale(g)
         scale_steps.append(dict(name='scale', width=scale_width, height=int(image_height * ratio_width), top=0, left=0))
         # crop height
         image.crop(crop_geometry)
         scale_steps.append(dict(name='crop', width=scale_width, height=scale_height, top=0, left=0))

      elif image_width > scale_width and image_height == scale_height:
         # crop width
         image.crop(crop_geometry)
         scale_steps.append(dict(name='crop', width=scale_width, height=scale_height, top=0, left=0))

      elif image_width == scale_width and image_height > scale_height:
         # crop width
         image.crop(crop_geometry)
         scale_steps.append(dict(name='crop', width=scale_width, height=scale_height, top=0, left=0))

      elif image_width > scale_width and image_height > scale_height:
         if image_height * ratio_width < scale_height:
            # scale to height
            g = Geometry(int(image_width * ratio_height), scale_height, 0, 0)
            scale_steps.append(dict(name='scale', width=int(image_width * ratio_height), height=scale_height, top=0, left=0))
            image.scale(g)
            # crop width
            image.crop(crop_geometry)
            scale_steps.append(dict(name='crop', width=scale_width, height=scale_height, top=0, left=0))
         else:
            # scale to width
            g = Geometry(scale_width, int(image_height * ratio_width), 0, 0)
            image.scale(g)
            scale_steps.append(dict(name='scale', width=scale_width, height=int(image_height * ratio_width), top=0, left=0))
            # crop width
            image.crop(crop_geometry)
            scale_steps.append(dict(name='crop', width=scale_width, height=scale_height, top=0, left=0))

      quality = scale.get('quality', 100)
      sharpen = scale.get('sharpen', 1.0)

      # set quality
      image.quality(quality)
      image.sharpen(sharpen)

      full_scaled_image_path = '%s/%s_%s' % (file_path, scale['prefix'], file.file_name)
      image.write(full_scaled_image_path)

      scale['steps'] = scale_steps
      scale['quality'] = quality
      scale['sharpen'] = sharpen
      file.data['scale'][scale['name']] = scale

      file.save()


## Get rough file mime type
#
#  @param file File
#
def get_file_rough_mime_type(file):
   file_type = get_file_type(file)

   known_ext = ['aac','aiff','ai','avi','bmp','c','cpp','css','dat','dmg','doc','dotx','dwg','dxf','eps','exe','flv','gif','h','hpp','html','ics','iso','java','jpg','key','mid','mp3','mp4','mpg','odf','ods','odt','otp','ots','ott','pdf','php','png','ppt','psd','py','qt','rar','rb','rtf','sql','tga','tgz','tiff','txt','wav','xls','xlsx','xml','yml','zip']
   ext = file_type['extension'].replace('.', '')

   if ext in known_ext:
      return ext

   return '_blank'


## Get file tag
#
#  @param file File
#
def get_file_tag(file):
   file_type = get_file_type(file)

   if file.mime_type.startswith('image'):
      return 'image'

   if file.mime_type.startswith('video'):
      return 'video'

   if file.mime_type.startswith('audio'):
      return 'audio'

   if file.mime_type.startswith('text'):
      return 'text'

   if file.mime_type.startswith('model'):
      return 'model'

   if file.mime_type.startswith('application'):
      if 'Archive' in file_type['description']:
         return 'archive'

      if file.mime_type.startswith('application/x-font'):
         return 'font'

      document_file_extensions = ['.doc', '.xls', '.ppt', '.pps', '.docx', '.xlsx', '.pptx', '.ppsx', '.pdf', '.rtf', '.ods', '.odt', '.odp', '']
      if file_type['extension'] in document_file_extensions:
         return 'document'

      return 'application'

   return 'other'


## Check if file is of type image
#
#  @param file File to search
#
def is_image(file):
   return file.mime_type.startswith('image')


## Get file type from file mime-type
#  http://www.freeformatter.com/mime-types-list.html
#
#  @param file File to search
#
def get_file_type(file):
   mime_types = {}
   mime_types['application/applixware'] = dict(description='Applixware', extension='.aw')
   mime_types['application/atom+xml'] = dict(description='Atom Syndication Format', extension='.atom')
   mime_types['application/atomcat+xml'] = dict(description='Atom Publishing Protocol', extension='.atomcat')
   mime_types['application/atomsvc+xml'] = dict(description='Atom Publishing Protocol Service Document', extension='.atomsvc')
   mime_types['application/ccxml+xml,'] = dict(description='Voice Browser Call Control', extension='.ccxml')
   mime_types['application/cdmi-capability'] = dict(description='Cloud Data Management Interface (CDMI) - Capability', extension='.cdmia')
   mime_types['application/cdmi-container'] = dict(description='Cloud Data Management Interface (CDMI) - Contaimer', extension='.cdmic')
   mime_types['application/cdmi-domain'] = dict(description='Cloud Data Management Interface (CDMI) - Domain', extension='.cdmid')
   mime_types['application/cdmi-object'] = dict(description='Cloud Data Management Interface (CDMI) - Object', extension='.cdmio')
   mime_types['application/cdmi-queue'] = dict(description='Cloud Data Management Interface (CDMI) - Queue', extension='.cdmiq')
   mime_types['application/cu-seeme'] = dict(description='CU-SeeMe', extension='.cu')
   mime_types['application/davmount+xml'] = dict(description='Web Distributed Authoring and Versioning', extension='.davmount')
   mime_types['application/dssc+der'] = dict(description='Data Structure for the Security Suitability of Cryptographic Algorithms', extension='.dssc')
   mime_types['application/dssc+xml'] = dict(description='Data Structure for the Security Suitability of Cryptographic Algorithms', extension='.xdssc')
   mime_types['application/ecmascript'] = dict(description='ECMAScript', extension='.es')
   mime_types['application/emma+xml'] = dict(description='Extensible MultiModal Annotation', extension='.emma')
   mime_types['application/epub+zip'] = dict(description='Electronic Publication', extension='.epub')
   mime_types['application/exi'] = dict(description='Efficient XML Interchange', extension='.exi')
   mime_types['application/font-tdpfr'] = dict(description='Portable Font Resource', extension='.pfr')
   mime_types['application/hyperstudio'] = dict(description='Hyperstudio', extension='.stk')
   mime_types['application/ipfix'] = dict(description='Internet Protocol Flow Information Export', extension='.ipfix')
   mime_types['application/java-archive'] = dict(description='Java Archive', extension='.jar')
   mime_types['application/java-serialized-object'] = dict(description='Java Serialized Object', extension='.ser')
   mime_types['application/java-vm'] = dict(description='Java Bytecode File', extension='.class')
   mime_types['application/javascript'] = dict(description='JavaScript', extension='.js')
   mime_types['application/json'] = dict(description='JavaScript Object Notation (JSON)', extension='.json')
   mime_types['application/mac-binhex40'] = dict(description='Macintosh BinHex 4.0', extension='.hqx')
   mime_types['application/mac-compactpro'] = dict(description='Compact Pro', extension='.cpt')
   mime_types['application/mads+xml'] = dict(description='Metadata Authority Description Schema', extension='.mads')
   mime_types['application/marc'] = dict(description='MARC Formats', extension='.mrc')
   mime_types['application/marcxml+xml'] = dict(description='MARC21 XML Schema', extension='.mrcx')
   mime_types['application/mathematica'] = dict(description='Mathematica Notebooks', extension='.ma')
   mime_types['application/mathml+xml'] = dict(description='Mathematical Markup Language', extension='.mathml')
   mime_types['application/mbox'] = dict(description='Mbox database files', extension='.mbox')
   mime_types['application/mediaservercontrol+xml'] = dict(description='Media Server Control Markup Language', extension='.mscml')
   mime_types['application/metalink4+xml'] = dict(description='Metalink', extension='.meta4')
   mime_types['application/mets+xml'] = dict(description='Metadata Encoding and Transmission Standard', extension='.mets')
   mime_types['application/mods+xml'] = dict(description='Metadata Object Description Schema', extension='.mods')
   mime_types['application/mp21'] = dict(description='MPEG-21', extension='.m21')
   mime_types['application/mp4'] = dict(description='MPEG4', extension='.mp4')
   mime_types['application/msword'] = dict(description='Microsoft Word', extension='.doc')
   mime_types['application/mxf'] = dict(description='Material Exchange Format', extension='.mxf')
   mime_types['application/octet-stream'] = dict(description='Binary Data', extension='.bin')
   mime_types['application/oda'] = dict(description='Office Document Architecture', extension='.oda')
   mime_types['application/oebps-package+xml'] = dict(description='Open eBook Publication Structure', extension='.opf')
   mime_types['application/ogg'] = dict(description='Ogg', extension='.ogx')
   mime_types['application/onenote'] = dict(description='Microsoft OneNote', extension='.onetoc')
   mime_types['application/patch-ops-error+xml'] = dict(description='XML Patch Framework', extension='.xer')
   mime_types['application/pdf'] = dict(description='Adobe Portable Document Format', extension='.pdf')
   mime_types['application/pgp-encrypted'] = dict(description='Pretty Good Privacy', extension='')
   mime_types['application/pgp-signature'] = dict(description='Pretty Good Privacy - Signature', extension='.pgp')
   mime_types['application/pics-rules'] = dict(description='PICSRules', extension='.prf')
   mime_types['application/pkcs10'] = dict(description='PKCS #10 - Certification Request Standard', extension='.p10')
   mime_types['application/pkcs7-mime'] = dict(description='PKCS #7 - Cryptographic Message Syntax Standard', extension='.p7m')
   mime_types['application/pkcs7-signature'] = dict(description='PKCS #7 - Cryptographic Message Syntax Standard', extension='.p7s')
   mime_types['application/pkcs8'] = dict(description='PKCS #8 - Private-Key Information Syntax Standard', extension='.p8')
   mime_types['application/pkix-attr-cert'] = dict(description='Attribute Certificate', extension='.ac')
   mime_types['application/pkix-cert'] = dict(description='Internet Public Key Infrastructure - Certificate', extension='.cer')
   mime_types['application/pkix-crl'] = dict(description='Internet Public Key Infrastructure - Certificate Revocation Lists', extension='.crl')
   mime_types['application/pkix-pkipath'] = dict(description='Internet Public Key Infrastructure - Certification Path', extension='.pkipath')
   mime_types['application/pkixcmp'] = dict(description='Internet Public Key Infrastructure - Certificate Management Protocole', extension='.pki')
   mime_types['application/pls+xml'] = dict(description='Pronunciation Lexicon Specification', extension='.pls')
   mime_types['application/postscript'] = dict(description='PostScript', extension='.ai')
   mime_types['application/prs.cww'] = dict(description='CU-Writer', extension='.cww')
   mime_types['application/pskc+xml'] = dict(description='Portable Symmetric Key Container', extension='.pskcxml')
   mime_types['application/rdf+xml'] = dict(description='Resource Description Framework', extension='.rdf')
   mime_types['application/reginfo+xml'] = dict(description='IMS Networks', extension='.rif')
   mime_types['application/relax-ng-compact-syntax'] = dict(description='Relax NG Compact Syntax', extension='.rnc')
   mime_types['application/resource-lists+xml'] = dict(description='XML Resource Lists', extension='.rl')
   mime_types['application/resource-lists-diff+xml'] = dict(description='XML Resource Lists Diff', extension='.rld')
   mime_types['application/rls-services+xml'] = dict(description='XML Resource Lists', extension='.rs')
   mime_types['application/rsd+xml'] = dict(description='Really Simple Discovery', extension='.rsd')
   mime_types['application/rss+xml'] = dict(description='RSS - Really Simple Syndication', extension='.rss')
   mime_types['application/rtf'] = dict(description='Rich Text Format', extension='.rtf')
   mime_types['application/sbml+xml'] = dict(description='Systems Biology Markup Language', extension='.sbml')
   mime_types['application/scvp-cv-request'] = dict(description='Server-Based Certificate Validation Protocol - Validation Request', extension='.scq')
   mime_types['application/scvp-cv-response'] = dict(description='Server-Based Certificate Validation Protocol - Validation Response', extension='.scs')
   mime_types['application/scvp-vp-request'] = dict(description='Server-Based Certificate Validation Protocol - Validation Policies - Request', extension='.spq')
   mime_types['application/scvp-vp-response'] = dict(description='Server-Based Certificate Validation Protocol - Validation Policies - Response', extension='.spp')
   mime_types['application/sdp'] = dict(description='Session Description Protocol', extension='.sdp')
   mime_types['application/set-payment-initiation'] = dict(description='Secure Electronic Transaction - Payment', extension='.setpay')
   mime_types['application/set-registration-initiation'] = dict(description='Secure Electronic Transaction - Registration', extension='.setreg')
   mime_types['application/shf+xml'] = dict(description='S Hexdump Format', extension='.shf')
   mime_types['application/smil+xml'] = dict(description='Synchronized Multimedia Integration Language', extension='.smi')
   mime_types['application/sparql-query'] = dict(description='SPARQL - Query', extension='.rq')
   mime_types['application/sparql-results+xml'] = dict(description='SPARQL - Results', extension='.srx')
   mime_types['application/srgs'] = dict(description='Speech Recognition Grammar Specification', extension='.gram')
   mime_types['application/srgs+xml'] = dict(description='Speech Recognition Grammar Specification - XML', extension='.grxml')
   mime_types['application/sru+xml'] = dict(description='Search/Retrieve via URL Response Format', extension='.sru')
   mime_types['application/ssml+xml'] = dict(description='Speech Synthesis Markup Language', extension='.ssml')
   mime_types['application/tei+xml'] = dict(description='Text Encoding and Interchange', extension='.tei')
   mime_types['application/thraud+xml'] = dict(description='Sharing Transaction Fraud Data', extension='.tfi')
   mime_types['application/timestamped-data'] = dict(description='Time Stamped Data Envelope', extension='.tsd')
   mime_types['application/vnd.3gpp.pic-bw-large'] = dict(description='3rd Generation Partnership Project - Pic Large', extension='.plb')
   mime_types['application/vnd.3gpp.pic-bw-small'] = dict(description='3rd Generation Partnership Project - Pic Small', extension='.psb')
   mime_types['application/vnd.3gpp.pic-bw-var'] = dict(description='3rd Generation Partnership Project - Pic Var', extension='.pvb')
   mime_types['application/vnd.3gpp2.tcap'] = dict(description='3rd Generation Partnership Project - Transaction Capabilities Application Part', extension='.tcap')
   mime_types['application/vnd.3m.post-it-notes'] = dict(description='3M Post It Notes', extension='.pwn')
   mime_types['application/vnd.accpac.simply.aso'] = dict(description='Simply Accounting', extension='.aso')
   mime_types['application/vnd.accpac.simply.imp'] = dict(description='Simply Accounting - Data Import', extension='.imp')
   mime_types['application/vnd.acucobol'] = dict(description='ACU Cobol', extension='.acu')
   mime_types['application/vnd.acucorp'] = dict(description='ACU Cobol', extension='.atc')
   mime_types['application/vnd.adobe.air-application-installer-package+zip'] = dict(description='Adobe AIR Application', extension='.air')
   mime_types['application/vnd.adobe.fxp'] = dict(description='Adobe Flex Project', extension='.fxp')
   mime_types['application/vnd.adobe.xdp+xml'] = dict(description='Adobe XML Data Package', extension='.xdp')
   mime_types['application/vnd.adobe.xfdf'] = dict(description='Adobe XML Forms Data Format', extension='.xfdf')
   mime_types['application/vnd.ahead.space'] = dict(description='Ahead AIR Application', extension='.ahead')
   mime_types['application/vnd.airzip.filesecure.azf'] = dict(description='AirZip FileSECURE', extension='.azf')
   mime_types['application/vnd.airzip.filesecure.azs'] = dict(description='AirZip FileSECURE', extension='.azs')
   mime_types['application/vnd.amazon.ebook'] = dict(description='Amazon Kindle eBook format', extension='.azw')
   mime_types['application/vnd.americandynamics.acc'] = dict(description='Active Content Compression', extension='.acc')
   mime_types['application/vnd.amiga.ami'] = dict(description='AmigaDE', extension='.ami')
   mime_types['application/vnd.android.package-archive'] = dict(description='Android Package Archive', extension='.apk')
   mime_types['application/vnd.anser-web-certificate-issue-initiation'] = dict(description='ANSER-WEB Terminal Client - Certificate Issue', extension='.cii')
   mime_types['application/vnd.anser-web-funds-transfer-initiation'] = dict(description='ANSER-WEB Terminal Client - Web Funds Transfer', extension='.fti')
   mime_types['application/vnd.antix.game-component'] = dict(description='Antix Game Player', extension='.atx')
   mime_types['application/vnd.apple.installer+xml'] = dict(description='Apple Installer Package', extension='.mpkg')
   mime_types['application/vnd.apple.mpegurl'] = dict(description='Multimedia Playlist Unicode', extension='.m3u8')
   mime_types['application/vnd.aristanetworks.swi'] = dict(description='Arista Networks Software Image', extension='.swi')
   mime_types['application/vnd.audiograph'] = dict(description='Audiograph', extension='.aep')
   mime_types['application/vnd.blueice.multipass'] = dict(description='Blueice Research Multipass', extension='.mpm')
   mime_types['application/vnd.bmi'] = dict(description='BMI Drawing Data Interchange', extension='.bmi')
   mime_types['application/vnd.businessobjects'] = dict(description='BusinessObjects', extension='.rep')
   mime_types['application/vnd.chemdraw+xml'] = dict(description='CambridgeSoft Chem Draw', extension='.cdxml')
   mime_types['application/vnd.chipnuts.karaoke-mmd'] = dict(description='Karaoke on Chipnuts Chipsets', extension='.mmd')
   mime_types['application/vnd.cinderella'] = dict(description='Interactive Geometry Software Cinderella', extension='.cdy')
   mime_types['application/vnd.claymore'] = dict(description='Claymore Data Files', extension='.cla')
   mime_types['application/vnd.cloanto.rp9'] = dict(description='RetroPlatform Player', extension='.rp9')
   mime_types['application/vnd.clonk.c4group'] = dict(description='Clonk Game', extension='.c4g')
   mime_types['application/vnd.cluetrust.cartomobile-config'] = dict(description='ClueTrust CartoMobile - Config', extension='.c11amc')
   mime_types['application/vnd.cluetrust.cartomobile-config-pkg'] = dict(description='ClueTrust CartoMobile - Config Package', extension='.c11amz')
   mime_types['application/vnd.commonspace'] = dict(description='Sixth Floor Media - CommonSpace', extension='.csp')
   mime_types['application/vnd.contact.cmsg'] = dict(description='CIM Database', extension='.cdbcmsg')
   mime_types['application/vnd.cosmocaller'] = dict(description='CosmoCaller', extension='.cmc')
   mime_types['application/vnd.crick.clicker'] = dict(description='CrickSoftware - Clicker', extension='.clkx')
   mime_types['application/vnd.crick.clicker.keyboard'] = dict(description='CrickSoftware - Clicker - Keyboard', extension='.clkk')
   mime_types['application/vnd.crick.clicker.palette'] = dict(description='CrickSoftware - Clicker - Palette', extension='.clkp')
   mime_types['application/vnd.crick.clicker.template'] = dict(description='CrickSoftware - Clicker - Template', extension='.clkt')
   mime_types['application/vnd.crick.clicker.wordbank'] = dict(description='CrickSoftware - Clicker - Wordbank', extension='.clkw')
   mime_types['application/vnd.criticaltools.wbs+xml'] = dict(description='Critical Tools - PERT Chart EXPERT', extension='.wbs')
   mime_types['application/vnd.ctc-posml'] = dict(description='PosML', extension='.pml')
   mime_types['application/vnd.cups-ppd'] = dict(description='Adobe PostScript Printer Description File Format', extension='.ppd')
   mime_types['application/vnd.curl.car'] = dict(description='CURL Applet', extension='.car')
   mime_types['application/vnd.curl.pcurl'] = dict(description='CURL Applet', extension='.pcurl')
   mime_types['application/vnd.data-vision.rdz'] = dict(description='RemoteDocs R-Viewer', extension='.rdz')
   mime_types['application/vnd.denovo.fcselayout-link'] = dict(description='FCS Express Layout Link', extension='.fe_launch')
   mime_types['application/vnd.dna'] = dict(description='New Moon Liftoff/DNA', extension='.dna')
   mime_types['application/vnd.dolby.mlp'] = dict(description='Dolby Meridian Lossless Packing', extension='.mlp')
   mime_types['application/vnd.dpgraph'] = dict(description='DPGraph', extension='.dpg')
   mime_types['application/vnd.dreamfactory'] = dict(description='DreamFactory', extension='.dfac')
   mime_types['application/vnd.dvb.ait'] = dict(description='Digital Video Broadcasting', extension='.ait')
   mime_types['application/vnd.dvb.service'] = dict(description='Digital Video Broadcasting', extension='.svc')
   mime_types['application/vnd.dynageo'] = dict(description='DynaGeo', extension='.geo')
   mime_types['application/vnd.ecowin.chart'] = dict(description='EcoWin Chart', extension='.mag')
   mime_types['application/vnd.enliven'] = dict(description='Enliven Viewer', extension='.nml')
   mime_types['application/vnd.epson.esf'] = dict(description='QUASS Stream Player', extension='.esf')
   mime_types['application/vnd.epson.msf'] = dict(description='QUASS Stream Player', extension='.msf')
   mime_types['application/vnd.epson.quickanime'] = dict(description='QuickAnime Player', extension='.qam')
   mime_types['application/vnd.epson.salt'] = dict(description='SimpleAnimeLite Player', extension='.slt')
   mime_types['application/vnd.epson.ssf'] = dict(description='QUASS Stream Player', extension='.ssf')
   mime_types['application/vnd.eszigno3+xml'] = dict(description='MICROSEC e-Szign', extension='.es3')
   mime_types['application/vnd.ezpix-album'] = dict(description='EZPix Secure Photo Album', extension='.ez2')
   mime_types['application/vnd.ezpix-package'] = dict(description='EZPix Secure Photo Album', extension='.ez3')
   mime_types['application/vnd.fdf'] = dict(description='Forms Data Format', extension='.fdf')
   mime_types['application/vnd.fdsn.seed'] = dict(description='Digital Siesmograph Networks - SEED Datafiles', extension='.seed')
   mime_types['application/vnd.flographit'] = dict(description='NpGraphIt', extension='.gph')
   mime_types['application/vnd.fluxtime.clip'] = dict(description='FluxTime Clip', extension='.ftc')
   mime_types['application/vnd.framemaker'] = dict(description='FrameMaker Normal Format', extension='.fm')
   mime_types['application/vnd.frogans.fnc'] = dict(description='Frogans Player', extension='.fnc')
   mime_types['application/vnd.frogans.ltf'] = dict(description='Frogans Player', extension='.ltf')
   mime_types['application/vnd.fsc.weblaunch'] = dict(description='Friendly Software Corporation', extension='.fsc')
   mime_types['application/vnd.fujitsu.oasys'] = dict(description='Fujitsu Oasys', extension='.oas')
   mime_types['application/vnd.fujitsu.oasys2'] = dict(description='Fujitsu Oasys', extension='.oa2')
   mime_types['application/vnd.fujitsu.oasys3'] = dict(description='Fujitsu Oasys', extension='.oa3')
   mime_types['application/vnd.fujitsu.oasysgp'] = dict(description='Fujitsu Oasys', extension='.fg5')
   mime_types['application/vnd.fujitsu.oasysprs'] = dict(description='Fujitsu Oasys', extension='.bh2')
   mime_types['application/vnd.fujixerox.ddd'] = dict(description='Fujitsu - Xerox 2D CAD Data', extension='.ddd')
   mime_types['application/vnd.fujixerox.docuworks'] = dict(description='Fujitsu - Xerox DocuWorks', extension='.xdw')
   mime_types['application/vnd.fujixerox.docuworks.binder'] = dict(description='Fujitsu - Xerox DocuWorks Binder', extension='.xbd')
   mime_types['application/vnd.fuzzysheet'] = dict(description='FuzzySheet', extension='.fzs')
   mime_types['application/vnd.genomatix.tuxedo'] = dict(description='Genomatix Tuxedo Framework', extension='.txd')
   mime_types['application/vnd.geogebra.file'] = dict(description='GeoGebra', extension='.ggb')
   mime_types['application/vnd.geogebra.tool'] = dict(description='GeoGebra', extension='.ggt')
   mime_types['application/vnd.geometry-explorer'] = dict(description='GeoMetry Explorer', extension='.gex')
   mime_types['application/vnd.geonext'] = dict(description='GEONExT and JSXGraph', extension='.gxt')
   mime_types['application/vnd.geoplan'] = dict(description='GeoplanW', extension='.g2w')
   mime_types['application/vnd.geospace'] = dict(description='GeospacW', extension='.g3w')
   mime_types['application/vnd.gmx'] = dict(description='GameMaker ActiveX', extension='.gmx')
   mime_types['application/vnd.google-earth.kml+xml'] = dict(description='Google Earth - KML', extension='.kml')
   mime_types['application/vnd.google-earth.kmz'] = dict(description='Google Earth - Zipped KML', extension='.kmz')
   mime_types['application/vnd.grafeq'] = dict(description='GrafEq', extension='.gqf')
   mime_types['application/vnd.groove-account'] = dict(description='Groove - Account', extension='.gac')
   mime_types['application/vnd.groove-help'] = dict(description='Groove - Help', extension='.ghf')
   mime_types['application/vnd.groove-identity-message'] = dict(description='Groove - Identity Message', extension='.gim')
   mime_types['application/vnd.groove-injector'] = dict(description='Groove - Injector', extension='.grv')
   mime_types['application/vnd.groove-tool-message'] = dict(description='Groove - Tool Message', extension='.gtm')
   mime_types['application/vnd.groove-tool-template'] = dict(description='Groove - Tool Template', extension='.tpl')
   mime_types['application/vnd.groove-vcard'] = dict(description='Groove - Vcard', extension='.vcg')
   mime_types['application/vnd.hal+xml'] = dict(description='Hypertext Application Language', extension='.hal')
   mime_types['application/vnd.handheld-entertainment+xml'] = dict(description='ZVUE Media Manager', extension='.zmm')
   mime_types['application/vnd.hbci'] = dict(description='Homebanking Computer Interface (HBCI)', extension='.hbci')
   mime_types['application/vnd.hhe.lesson-player'] = dict(description='Archipelago Lesson Player', extension='.les')
   mime_types['application/vnd.hp-hpgl'] = dict(description='HP-GL/2 and HP RTL', extension='.hpgl')
   mime_types['application/vnd.hp-hpid'] = dict(description='Hewlett Packard Instant Delivery', extension='.hpid')
   mime_types['application/vnd.hp-hps'] = dict(description='Hewlett-Packards WebPrintSmart', extension='.hps')
   mime_types['application/vnd.hp-jlyt'] = dict(description='HP Indigo Digital Press - Job Layout Languate', extension='.jlt')
   mime_types['application/vnd.hp-pcl'] = dict(description='HP Printer Command Language', extension='.pcl')
   mime_types['application/vnd.hp-pclxl'] = dict(description='PCL 6 Enhanced (Formely PCL XL)', extension='.pclxl')
   mime_types['application/vnd.hydrostatix.sof-data'] = dict(description='Hydrostatix Master Suite', extension='.sfd-hdstx')
   mime_types['application/vnd.hzn-3d-crossword'] = dict(description='3D Crossword Plugin', extension='.x3d')
   mime_types['application/vnd.ibm.minipay'] = dict(description='MiniPay', extension='.mpy')
   mime_types['application/vnd.ibm.modcap'] = dict(description='MO:DCA-P', extension='.afp')
   mime_types['application/vnd.ibm.rights-management'] = dict(description='IBM DB2 Rights Manager', extension='.irm')
   mime_types['application/vnd.ibm.secure-container'] = dict(description='IBM Electronic Media Management System - Secure Container', extension='.sc')
   mime_types['application/vnd.iccprofile'] = dict(description='ICC profile', extension='.icc')
   mime_types['application/vnd.igloader'] = dict(description='igLoader', extension='.igl')
   mime_types['application/vnd.immervision-ivp'] = dict(description='ImmerVision PURE Players', extension='.ivp')
   mime_types['application/vnd.immervision-ivu'] = dict(description='ImmerVision PURE Players', extension='.ivu')
   mime_types['application/vnd.insors.igm'] = dict(description='IOCOM Visimeet', extension='.igm')
   mime_types['application/vnd.intercon.formnet'] = dict(description='Intercon FormNet', extension='.xpw')
   mime_types['application/vnd.intergeo'] = dict(description='Interactive Geometry Software', extension='.i2g')
   mime_types['application/vnd.intu.qbo'] = dict(description='Open Financial Exchange', extension='.qbo')
   mime_types['application/vnd.intu.qfx'] = dict(description='Quicken', extension='.qfx')
   mime_types['application/vnd.ipunplugged.rcprofile'] = dict(description='IP Unplugged Roaming Client', extension='.rcprofile')
   mime_types['application/vnd.irepository.package+xml'] = dict(description='iRepository / Lucidoc Editor', extension='.irp')
   mime_types['application/vnd.is-xpr'] = dict(description='Express by Infoseek', extension='.xpr')
   mime_types['application/vnd.isac.fcs'] = dict(description='International Society for Advancement of Cytometry', extension='.fcs')
   mime_types['application/vnd.jam'] = dict(description='Lightspeed Audio Lab', extension='.jam')
   mime_types['application/vnd.jcp.javame.midlet-rms'] = dict(description='Mobile Information Device Profile', extension='.rms')
   mime_types['application/vnd.jisp'] = dict(description='RhymBox', extension='.jisp')
   mime_types['application/vnd.joost.joda-archive'] = dict(description='Joda Archive', extension='.joda')
   mime_types['application/vnd.kahootz'] = dict(description='Kahootz', extension='.ktz')
   mime_types['application/vnd.kde.karbon'] = dict(description='KDE KOffice Office Suite - Karbon', extension='.karbon')
   mime_types['application/vnd.kde.kchart'] = dict(description='KDE KOffice Office Suite - KChart', extension='.chrt')
   mime_types['application/vnd.kde.kformula'] = dict(description='KDE KOffice Office Suite - Kformula', extension='.kfo')
   mime_types['application/vnd.kde.kivio'] = dict(description='KDE KOffice Office Suite - Kivio', extension='.flw')
   mime_types['application/vnd.kde.kontour'] = dict(description='KDE KOffice Office Suite - Kontour', extension='.kon')
   mime_types['application/vnd.kde.kpresenter'] = dict(description='KDE KOffice Office Suite - Kpresenter', extension='.kpr')
   mime_types['application/vnd.kde.kspread'] = dict(description='KDE KOffice Office Suite - Kspread', extension='.ksp')
   mime_types['application/vnd.kde.kword'] = dict(description='KDE KOffice Office Suite - Kword', extension='.kwd')
   mime_types['application/vnd.kenameaapp'] = dict(description='Kenamea App', extension='.htke')
   mime_types['application/vnd.kidspiration'] = dict(description='Kidspiration', extension='.kia')
   mime_types['application/vnd.kinar'] = dict(description='Kinar Applications', extension='.kne')
   mime_types['application/vnd.koan'] = dict(description='SSEYO Koan Play File', extension='.skp')
   mime_types['application/vnd.kodak-descriptor'] = dict(description='Kodak Storyshare', extension='.sse')
   mime_types['application/vnd.las.las+xml'] = dict(description='Laser App Enterprise', extension='.lasxml')
   mime_types['application/vnd.llamagraphics.life-balance.desktop'] = dict(description='Life Balance - Desktop Edition', extension='.lbd')
   mime_types['application/vnd.llamagraphics.life-balance.exchange+xml'] = dict(description='Life Balance - Exchange Format', extension='.lbe')
   mime_types['application/vnd.lotus-approach'] = dict(description='Lotus Approach', extension='.apr')
   mime_types['application/vnd.lotus-freelance'] = dict(description='Lotus Freelance', extension='.pre')
   mime_types['application/vnd.lotus-notes'] = dict(description='Lotus Notes', extension='.nsf')
   mime_types['application/vnd.lotus-organizer'] = dict(description='Lotus Organizer', extension='.org')
   mime_types['application/vnd.lotus-screencam'] = dict(description='Lotus Screencam', extension='.scm')
   mime_types['application/vnd.lotus-wordpro'] = dict(description='Lotus Wordpro', extension='.lwp')
   mime_types['application/vnd.macports.portpkg'] = dict(description='MacPorts Port System', extension='.portpkg')
   mime_types['application/vnd.mcd'] = dict(description='Micro CADAM Helix D&D', extension='.mcd')
   mime_types['application/vnd.medcalcdata'] = dict(description='MedCalc', extension='.mc1')
   mime_types['application/vnd.mediastation.cdkey'] = dict(description='MediaRemote', extension='.cdkey')
   mime_types['application/vnd.mfer'] = dict(description='Medical Waveform Encoding Format', extension='.mwf')
   mime_types['application/vnd.mfmp'] = dict(description='Melody Format for Mobile Platform', extension='.mfm')
   mime_types['application/vnd.micrografx.flo'] = dict(description='Micrografx', extension='.flo')
   mime_types['application/vnd.micrografx.igx'] = dict(description='Micrografx iGrafx Professional', extension='.igx')
   mime_types['application/vnd.mif'] = dict(description='FrameMaker Interchange Format', extension='.mif')
   mime_types['application/vnd.mobius.daf'] = dict(description='Mobius Management Systems - UniversalArchive', extension='.daf')
   mime_types['application/vnd.mobius.dis'] = dict(description='Mobius Management Systems - Distribution Database', extension='.dis')
   mime_types['application/vnd.mobius.mbk'] = dict(description='Mobius Management Systems - Basket file', extension='.mbk')
   mime_types['application/vnd.mobius.mqy'] = dict(description='Mobius Management Systems - Query File', extension='.mqy')
   mime_types['application/vnd.mobius.msl'] = dict(description='Mobius Management Systems - Script Language', extension='.msl')
   mime_types['application/vnd.mobius.plc'] = dict(description='Mobius Management Systems - Policy Definition Language File', extension='.plc')
   mime_types['application/vnd.mobius.txf'] = dict(description='Mobius Management Systems - Topic Index File', extension='.txf')
   mime_types['application/vnd.mophun.application'] = dict(description='Mophun VM', extension='.mpn')
   mime_types['application/vnd.mophun.certificate'] = dict(description='Mophun Certificate', extension='.mpc')
   mime_types['application/vnd.mozilla.xul+xml'] = dict(description='XUL - XML User Interface Language', extension='.xul')
   mime_types['application/vnd.ms-artgalry'] = dict(description='Microsoft Artgalry', extension='.cil')
   mime_types['application/vnd.ms-cab-compressed'] = dict(description='Microsoft Cabinet File', extension='.cab')
   mime_types['application/vnd.ms-excel'] = dict(description='Microsoft Excel', extension='.xls')
   mime_types['application/vnd.ms-excel.addin.macroenabled.12'] = dict(description='Microsoft Excel - Add-In File', extension='.xlam')
   mime_types['application/vnd.ms-excel.sheet.binary.macroenabled.12'] = dict(description='Microsoft Excel - Binary Workbook', extension='.xlsb')
   mime_types['application/vnd.ms-excel.sheet.macroenabled.12'] = dict(description='Microsoft Excel - Macro-Enabled Workbook', extension='.xlsm')
   mime_types['application/vnd.ms-excel.template.macroenabled.12'] = dict(description='Microsoft Excel - Macro-Enabled Template File', extension='.xltm')
   mime_types['application/vnd.ms-fontobject'] = dict(description='Microsoft Embedded OpenType', extension='.eot')
   mime_types['application/vnd.ms-htmlhelp'] = dict(description='Microsoft Html Help File', extension='.chm')
   mime_types['application/vnd.ms-ims'] = dict(description='Microsoft Class Server', extension='.ims')
   mime_types['application/vnd.ms-lrm'] = dict(description='Microsoft Learning Resource Module', extension='.lrm')
   mime_types['application/vnd.ms-officetheme'] = dict(description='Microsoft Office System Release Theme', extension='.thmx')
   mime_types['application/vnd.ms-pki.seccat'] = dict(description='Microsoft Trust UI Provider - Security Catalog', extension='.cat')
   mime_types['application/vnd.ms-pki.stl'] = dict(description='Microsoft Trust UI Provider - Certificate Trust Link', extension='.stl')
   mime_types['application/vnd.ms-powerpoint'] = dict(description='Microsoft PowerPoint', extension='.ppt')
   mime_types['application/vnd.ms-powerpoint.addin.macroenabled.12'] = dict(description='Microsoft PowerPoint - Add-in file', extension='.ppam')
   mime_types['application/vnd.ms-powerpoint.presentation.macroenabled.12'] = dict(description='Microsoft PowerPoint - Macro-Enabled Presentation File', extension='.pptm')
   mime_types['application/vnd.ms-powerpoint.slide.macroenabled.12'] = dict(description='Microsoft PowerPoint - Macro-Enabled Open XML Slide', extension='.sldm')
   mime_types['application/vnd.ms-powerpoint.slideshow.macroenabled.12'] = dict(description='Microsoft PowerPoint - Macro-Enabled Slide Show File', extension='.ppsm')
   mime_types['application/vnd.ms-powerpoint.template.macroenabled.12'] = dict(description='Micosoft PowerPoint - Macro-Enabled Template File', extension='.potm')
   mime_types['application/vnd.ms-project'] = dict(description='Microsoft Project', extension='.mpp')
   mime_types['application/vnd.ms-word.document.macroenabled.12'] = dict(description='Micosoft Word - Macro-Enabled Document', extension='.docm')
   mime_types['application/vnd.ms-word.template.macroenabled.12'] = dict(description='Micosoft Word - Macro-Enabled Template', extension='.dotm')
   mime_types['application/vnd.ms-works'] = dict(description='Microsoft Works', extension='.wps')
   mime_types['application/vnd.ms-wpl'] = dict(description='Microsoft Windows Media Player Playlist', extension='.wpl')
   mime_types['application/vnd.ms-xpsdocument'] = dict(description='Microsoft XML Paper Specification', extension='.xps')
   mime_types['application/vnd.mseq'] = dict(description='3GPP MSEQ File', extension='.mseq')
   mime_types['application/vnd.musician'] = dict(description='MUsical Score Interpreted Code Invented for the ASCII designation of Notation', extension='.mus')
   mime_types['application/vnd.muvee.style'] = dict(description='Muvee Automatic Video Editing', extension='.msty')
   mime_types['application/vnd.neurolanguage.nlu'] = dict(description='neuroLanguage', extension='.nlu')
   mime_types['application/vnd.noblenet-directory'] = dict(description='NobleNet Directory', extension='.nnd')
   mime_types['application/vnd.noblenet-sealer'] = dict(description='NobleNet Sealer', extension='.nns')
   mime_types['application/vnd.noblenet-web'] = dict(description='NobleNet Web', extension='.nnw')
   mime_types['application/vnd.nokia.n-gage.data'] = dict(description='N-Gage Game Data', extension='.ngdat')
   mime_types['application/vnd.nokia.n-gage.symbian.install'] = dict(description='N-Gage Game Installer', extension='.n-gage')
   mime_types['application/vnd.nokia.radio-preset'] = dict(description='Nokia Radio Application - Preset', extension='.rpst')
   mime_types['application/vnd.nokia.radio-presets'] = dict(description='Nokia Radio Application - Preset', extension='.rpss')
   mime_types['application/vnd.novadigm.edm'] = dict(description='Novadigms RADIA and EDM products', extension='.edm')
   mime_types['application/vnd.novadigm.edx'] = dict(description='Novadigms RADIA and EDM products', extension='.edx')
   mime_types['application/vnd.novadigm.ext'] = dict(description='Novadigms RADIA and EDM products', extension='.ext')
   mime_types['application/vnd.oasis.opendocument.chart'] = dict(description='OpenDocument Chart', extension='.odc')
   mime_types['application/vnd.oasis.opendocument.chart-template'] = dict(description='OpenDocument Chart Template', extension='.otc')
   mime_types['application/vnd.oasis.opendocument.database'] = dict(description='OpenDocument Database', extension='.odb')
   mime_types['application/vnd.oasis.opendocument.formula'] = dict(description='OpenDocument Formula', extension='.odf')
   mime_types['application/vnd.oasis.opendocument.formula-template'] = dict(description='OpenDocument Formula Template', extension='.odft')
   mime_types['application/vnd.oasis.opendocument.graphics'] = dict(description='OpenDocument Graphics', extension='.odg')
   mime_types['application/vnd.oasis.opendocument.graphics-template'] = dict(description='OpenDocument Graphics Template', extension='.otg')
   mime_types['application/vnd.oasis.opendocument.image'] = dict(description='OpenDocument Image', extension='.odi')
   mime_types['application/vnd.oasis.opendocument.image-template'] = dict(description='OpenDocument Image Template', extension='.oti')
   mime_types['application/vnd.oasis.opendocument.presentation'] = dict(description='OpenDocument Presentation', extension='.odp')
   mime_types['application/vnd.oasis.opendocument.presentation-template'] = dict(description='OpenDocument Presentation Template', extension='.otp')
   mime_types['application/vnd.oasis.opendocument.spreadsheet'] = dict(description='OpenDocument Spreadsheet', extension='.ods')
   mime_types['application/vnd.oasis.opendocument.spreadsheet-template'] = dict(description='OpenDocument Spreadsheet Template', extension='.ots')
   mime_types['application/vnd.oasis.opendocument.text'] = dict(description='OpenDocument Text', extension='.odt')
   mime_types['application/vnd.oasis.opendocument.text-master'] = dict(description='OpenDocument Text Master', extension='.odm')
   mime_types['application/vnd.oasis.opendocument.text-template'] = dict(description='OpenDocument Text Template', extension='.ott')
   mime_types['application/vnd.oasis.opendocument.text-web'] = dict(description='Open Document Text Web', extension='.oth')
   mime_types['application/vnd.olpc-sugar'] = dict(description='Sugar Linux Application Bundle', extension='.xo')
   mime_types['application/vnd.oma.dd2+xml'] = dict(description='OMA Download Agents', extension='.dd2')
   mime_types['application/vnd.openofficeorg.extension'] = dict(description='Open Office Extension', extension='.oxt')
   mime_types['application/vnd.openxmlformats-officedocument.presentationml.presentation'] = dict(description='Microsoft Office - OOXML - Presentation', extension='.pptx')
   mime_types['application/vnd.openxmlformats-officedocument.presentationml.slide'] = dict(description='Microsoft Office - OOXML - Presentation (Slide)', extension='.sldx')
   mime_types['application/vnd.openxmlformats-officedocument.presentationml.slideshow'] = dict(description='Microsoft Office - OOXML - Presentation (Slideshow)', extension='.ppsx')
   mime_types['application/vnd.openxmlformats-officedocument.presentationml.template'] = dict(description='Microsoft Office - OOXML - Presentation Template', extension='.potx')
   mime_types['application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'] = dict(description='Microsoft Office - OOXML - Spreadsheet', extension='.xlsx')
   mime_types['application/vnd.openxmlformats-officedocument.spreadsheetml.template'] = dict(description='Microsoft Office - OOXML - Spreadsheet Teplate', extension='.xltx')
   mime_types['application/vnd.openxmlformats-officedocument.wordprocessingml.document'] = dict(description='Microsoft Office - OOXML - Word Document', extension='.docx')
   mime_types['application/vnd.openxmlformats-officedocument.wordprocessingml.template'] = dict(description='Microsoft Office - OOXML - Word Document Template', extension='.dotx')
   mime_types['application/vnd.osgeo.mapguide.package'] = dict(description='MapGuide DBXML', extension='.mgp')
   mime_types['application/vnd.osgi.dp'] = dict(description='OSGi Deployment Package', extension='.dp')
   mime_types['application/vnd.palm'] = dict(description='PalmOS Data', extension='.pdb')
   mime_types['application/vnd.pawaafile'] = dict(description='PawaaFILE', extension='.paw')
   mime_types['application/vnd.pg.format'] = dict(description='Proprietary P&G Standard Reporting System', extension='.str')
   mime_types['application/vnd.pg.osasli'] = dict(description='Proprietary P&G Standard Reporting System', extension='.ei6')
   mime_types['application/vnd.picsel'] = dict(description='Pcsel eFIF File', extension='.efif')
   mime_types['application/vnd.pmi.widget'] = dict(description='Qualcomms Plaza Mobile Internet', extension='.wg')
   mime_types['application/vnd.pocketlearn'] = dict(description='PocketLearn Viewers', extension='.plf')
   mime_types['application/vnd.powerbuilder6'] = dict(description='PowerBuilder', extension='.pbd')
   mime_types['application/vnd.previewsystems.box'] = dict(description='Preview Systems ZipLock/VBox', extension='.box')
   mime_types['application/vnd.proteus.magazine'] = dict(description='EFI Proteus', extension='.mgz')
   mime_types['application/vnd.publishare-delta-tree'] = dict(description='PubliShare Objects', extension='.qps')
   mime_types['application/vnd.pvi.ptid1'] = dict(description='Princeton Video Image', extension='.ptid')
   mime_types['application/vnd.quark.quarkxpress'] = dict(description='QuarkXpress', extension='.qxd')
   mime_types['application/vnd.realvnc.bed'] = dict(description='RealVNC', extension='.bed')
   mime_types['application/vnd.recordare.musicxml'] = dict(description='Recordare Applications', extension='.mxl')
   mime_types['application/vnd.recordare.musicxml+xml'] = dict(description='Recordare Applications', extension='.musicxml')
   mime_types['application/vnd.rig.cryptonote'] = dict(description='CryptoNote', extension='.cryptonote')
   mime_types['application/vnd.rim.cod'] = dict(description='Blackberry COD File', extension='.cod')
   mime_types['application/vnd.rn-realmedia'] = dict(description='RealMedia', extension='.rm')
   mime_types['application/vnd.route66.link66+xml'] = dict(description='ROUTE 66 Location Based Services', extension='.link66')
   mime_types['application/vnd.sailingtracker.track'] = dict(description='SailingTracker', extension='.st')
   mime_types['application/vnd.seemail'] = dict(description='SeeMail', extension='.see')
   mime_types['application/vnd.sema'] = dict(description='Secured eMail', extension='.sema')
   mime_types['application/vnd.semd'] = dict(description='Secured eMail', extension='.semd')
   mime_types['application/vnd.semf'] = dict(description='Secured eMail', extension='.semf')
   mime_types['application/vnd.shana.informed.formdata'] = dict(description='Shana Informed Filler', extension='.ifm')
   mime_types['application/vnd.shana.informed.formtemplate'] = dict(description='Shana Informed Filler', extension='.itp')
   mime_types['application/vnd.shana.informed.interchange'] = dict(description='Shana Informed Filler', extension='.iif')
   mime_types['application/vnd.shana.informed.package'] = dict(description='Shana Informed Filler', extension='.ipk')
   mime_types['application/vnd.simtech-mindmapper'] = dict(description='SimTech MindMapper', extension='.twd')
   mime_types['application/vnd.smaf'] = dict(description='SMAF File', extension='.mmf')
   mime_types['application/vnd.smart.teacher'] = dict(description='SMART Technologies Apps', extension='.teacher')
   mime_types['application/vnd.solent.sdkm+xml'] = dict(description='SudokuMagic', extension='.sdkm')
   mime_types['application/vnd.spotfire.dxp'] = dict(description='TIBCO Spotfire', extension='.dxp')
   mime_types['application/vnd.spotfire.sfs'] = dict(description='TIBCO Spotfire', extension='.sfs')
   mime_types['application/vnd.stardivision.calc'] = dict(description='StarOffice - Calc', extension='.sdc')
   mime_types['application/vnd.stardivision.draw'] = dict(description='StarOffice - Draw', extension='.sda')
   mime_types['application/vnd.stardivision.impress'] = dict(description='StarOffice - Impress', extension='.sdd')
   mime_types['application/vnd.stardivision.math'] = dict(description='StarOffice - Math', extension='.smf')
   mime_types['application/vnd.stardivision.writer'] = dict(description='StarOffice - Writer', extension='.sdw')
   mime_types['application/vnd.stardivision.writer-global'] = dict(description='StarOffice - Writer (Global)', extension='.sgl')
   mime_types['application/vnd.stepmania.stepchart'] = dict(description='StepMania', extension='.sm')
   mime_types['application/vnd.sun.xml.calc'] = dict(description='OpenOffice - Calc (Spreadsheet)', extension='.sxc')
   mime_types['application/vnd.sun.xml.calc.template'] = dict(description='OpenOffice - Calc Template (Spreadsheet)', extension='.stc')
   mime_types['application/vnd.sun.xml.draw'] = dict(description='OpenOffice - Draw (Graphics)', extension='.sxd')
   mime_types['application/vnd.sun.xml.draw.template'] = dict(description='OpenOffice - Draw Template (Graphics)', extension='.std')
   mime_types['application/vnd.sun.xml.impress'] = dict(description='OpenOffice - Impress (Presentation)', extension='.sxi')
   mime_types['application/vnd.sun.xml.impress.template'] = dict(description='OpenOffice - Impress Template (Presentation)', extension='.sti')
   mime_types['application/vnd.sun.xml.math'] = dict(description='OpenOffice - Math (Formula)', extension='.sxm')
   mime_types['application/vnd.sun.xml.writer'] = dict(description='OpenOffice - Writer (Text - HTML)', extension='.sxw')
   mime_types['application/vnd.sun.xml.writer.global'] = dict(description='OpenOffice - Writer (Text - HTML)', extension='.sxg')
   mime_types['application/vnd.sun.xml.writer.template'] = dict(description='OpenOffice - Writer Template (Text - HTML)', extension='.stw')
   mime_types['application/vnd.sus-calendar'] = dict(description='ScheduleUs', extension='.sus')
   mime_types['application/vnd.svd'] = dict(description='SourceView Document', extension='.svd')
   mime_types['application/vnd.symbian.install'] = dict(description='Symbian Install Package', extension='.sis')
   mime_types['application/vnd.syncml+xml'] = dict(description='SyncML', extension='.xsm')
   mime_types['application/vnd.syncml.dm+wbxml'] = dict(description='SyncML - Device Management', extension='.bdm')
   mime_types['application/vnd.syncml.dm+xml'] = dict(description='SyncML - Device Management', extension='.xdm')
   mime_types['application/vnd.tao.intent-module-archive'] = dict(description='Tao Intent', extension='.tao')
   mime_types['application/vnd.tmobile-livetv'] = dict(description='MobileTV', extension='.tmo')
   mime_types['application/vnd.trid.tpt'] = dict(description='TRI Systems Config', extension='.tpt')
   mime_types['application/vnd.triscape.mxs'] = dict(description='Triscape Map Explorer', extension='.mxs')
   mime_types['application/vnd.trueapp'] = dict(description='True BASIC', extension='.tra')
   mime_types['application/vnd.ufdl'] = dict(description='Universal Forms Description Language', extension='.ufd')
   mime_types['application/vnd.uiq.theme'] = dict(description='User Interface Quartz - Theme (Symbian)', extension='.utz')
   mime_types['application/vnd.umajin'] = dict(description='UMAJIN', extension='.umj')
   mime_types['application/vnd.unity'] = dict(description='Unity 3d', extension='.unityweb')
   mime_types['application/vnd.uoml+xml'] = dict(description='Unique Object Markup Language', extension='.uoml')
   mime_types['application/vnd.vcx'] = dict(description='VirtualCatalog', extension='.vcx')
   mime_types['application/vnd.visio'] = dict(description='Microsoft Visio', extension='.vsd')
   mime_types['application/vnd.visionary'] = dict(description='Visionary', extension='.vis')
   mime_types['application/vnd.vsf'] = dict(description='Viewport+', extension='.vsf')
   mime_types['application/vnd.wap.wbxml'] = dict(description='WAP Binary XML (WBXML)', extension='.wbxml')
   mime_types['application/vnd.wap.wmlc'] = dict(description='Compiled Wireless Markup Language (WMLC)', extension='.wmlc')
   mime_types['application/vnd.wap.wmlscriptc'] = dict(description='WMLScript', extension='.wmlsc')
   mime_types['application/vnd.webturbo'] = dict(description='WebTurbo', extension='.wtb')
   mime_types['application/vnd.wolfram.player'] = dict(description='Mathematica Notebook Player', extension='.nbp')
   mime_types['application/vnd.wordperfect'] = dict(description='Wordperfect', extension='.wpd')
   mime_types['application/vnd.wqd'] = dict(description='SundaHus WQ', extension='.wqd')
   mime_types['application/vnd.wt.stf'] = dict(description='Worldtalk', extension='.stf')
   mime_types['application/vnd.xara'] = dict(description='CorelXARA', extension='.xar')
   mime_types['application/vnd.xfdl'] = dict(description='Extensible Forms Description Language', extension='.xfdl')
   mime_types['application/vnd.yamaha.hv-dic'] = dict(description='HV Voice Dictionary', extension='.hvd')
   mime_types['application/vnd.yamaha.hv-script'] = dict(description='HV Script', extension='.hvs')
   mime_types['application/vnd.yamaha.hv-voice'] = dict(description='HV Voice Parameter', extension='.hvp')
   mime_types['application/vnd.yamaha.openscoreformat'] = dict(description='Open Score Format', extension='.osf')
   mime_types['application/vnd.yamaha.openscoreformat.osfpvg+xml'] = dict(description='OSFPVG', extension='.osfpvg')
   mime_types['application/vnd.yamaha.smaf-audio'] = dict(description='SMAF Audio', extension='.saf')
   mime_types['application/vnd.yamaha.smaf-phrase'] = dict(description='SMAF Phrase', extension='.spf')
   mime_types['application/vnd.yellowriver-custom-menu'] = dict(description='CustomMenu', extension='.cmp')
   mime_types['application/vnd.zul'] = dict(description='Z.U.L. Geometry', extension='.zir')
   mime_types['application/vnd.zzazz.deck+xml'] = dict(description='Zzazz Deck', extension='.zaz')
   mime_types['application/voicexml+xml'] = dict(description='VoiceXML', extension='.vxml')
   mime_types['application/widget'] = dict(description='Widget Packaging and XML Configuration', extension='.wgt')
   mime_types['application/winhlp'] = dict(description='WinHelp', extension='.hlp')
   mime_types['application/wsdl+xml'] = dict(description='WSDL - Web Services Description Language', extension='.wsdl')
   mime_types['application/wspolicy+xml'] = dict(description='Web Services Policy', extension='.wspolicy')
   mime_types['application/x-7z-compressed'] = dict(description='7-Zip', extension='.7z')
   mime_types['application/x-abiword'] = dict(description='AbiWord', extension='.abw')
   mime_types['application/x-ace-compressed'] = dict(description='Ace Archive', extension='.ace')
   mime_types['application/x-authorware-bin'] = dict(description='Adobe (Macropedia) Authorware - Binary File', extension='.aab')
   mime_types['application/x-authorware-map'] = dict(description='Adobe (Macropedia) Authorware - Map', extension='.aam')
   mime_types['application/x-authorware-seg'] = dict(description='Adobe (Macropedia) Authorware - Segment File', extension='.aas')
   mime_types['application/x-bcpio'] = dict(description='Binary CPIO Archive', extension='.bcpio')
   mime_types['application/x-bittorrent'] = dict(description='BitTorrent', extension='.torrent')
   mime_types['application/x-bzip'] = dict(description='Bzip Archive', extension='.bz')
   mime_types['application/x-bzip2'] = dict(description='Bzip2 Archive', extension='.bz2')
   mime_types['application/x-cdlink'] = dict(description='Video CD', extension='.vcd')
   mime_types['application/x-chat'] = dict(description='pIRCh', extension='.chat')
   mime_types['application/x-chess-pgn'] = dict(description='Portable Game Notation (Chess Games)', extension='.pgn')
   mime_types['application/x-cpio'] = dict(description='CPIO Archive', extension='.cpio')
   mime_types['application/x-csh'] = dict(description='C Shell Script', extension='.csh')
   mime_types['application/x-debian-package'] = dict(description='Debian Package', extension='.deb')
   mime_types['application/x-director'] = dict(description='Adobe Shockwave Player', extension='.dir')
   mime_types['application/x-doom'] = dict(description='Doom Video Game', extension='.wad')
   mime_types['application/x-dtbncx+xml'] = dict(description='Navigation Control file for XML (for ePub)', extension='.ncx')
   mime_types['application/x-dtbook+xml'] = dict(description='Digital Talking Book', extension='.dtb')
   mime_types['application/x-dtbresource+xml'] = dict(description='Digital Talking Book - Resource File', extension='.res')
   mime_types['application/x-dvi'] = dict(description='Device Independent File Format (DVI)', extension='.dvi')
   mime_types['application/x-font-bdf'] = dict(description='Glyph Bitmap Distribution Format', extension='.bdf')
   mime_types['application/x-font-ghostscript'] = dict(description='Ghostscript Font', extension='.gsf')
   mime_types['application/x-font-linux-psf'] = dict(description='PSF Fonts', extension='.psf')
   mime_types['application/x-font-otf'] = dict(description='OpenType Font File', extension='.otf')
   mime_types['application/x-font-pcf'] = dict(description='Portable Compiled Format', extension='.pcf')
   mime_types['application/x-font-snf'] = dict(description='Server Normal Format', extension='.snf')
   mime_types['application/x-font-ttf'] = dict(description='TrueType Font', extension='.ttf')
   mime_types['application/x-font-type1'] = dict(description='PostScript Fonts', extension='.pfa')
   mime_types['application/x-font-woff'] = dict(description='Web Open Font Format', extension='.woff')
   mime_types['application/x-futuresplash'] = dict(description='FutureSplash Animator', extension='.spl')
   mime_types['application/x-gnumeric'] = dict(description='Gnumeric', extension='.gnumeric')
   mime_types['application/x-gtar'] = dict(description='GNU Tar Files', extension='.gtar')
   mime_types['application/x-hdf'] = dict(description='Hierarchical Data Format', extension='.hdf')
   mime_types['application/x-java-jnlp-file'] = dict(description='Java Network Launching Protocol', extension='.jnlp')
   mime_types['application/x-latex'] = dict(description='LaTeX', extension='.latex')
   mime_types['application/x-mobipocket-ebook'] = dict(description='Mobipocket', extension='.prc')
   mime_types['application/x-ms-application'] = dict(description='Microsoft ClickOnce', extension='.application')
   mime_types['application/x-ms-wmd'] = dict(description='Microsoft Windows Media Player Download Package', extension='.wmd')
   mime_types['application/x-ms-wmz'] = dict(description='Microsoft Windows Media Player Skin Package', extension='.wmz')
   mime_types['application/x-ms-xbap'] = dict(description='Microsoft XAML Browser Application', extension='.xbap')
   mime_types['application/x-msaccess'] = dict(description='Microsoft Access', extension='.mdb')
   mime_types['application/x-msbinder'] = dict(description='Microsoft Office Binder', extension='.obd')
   mime_types['application/x-mscardfile'] = dict(description='Microsoft Information Card', extension='.crd')
   mime_types['application/x-msclip'] = dict(description='Microsoft Clipboard Clip', extension='.clp')
   mime_types['application/x-msdownload'] = dict(description='Microsoft Application', extension='.exe')
   mime_types['application/x-msmediaview'] = dict(description='Microsoft MediaView', extension='.mvb')
   mime_types['application/x-msmetafile'] = dict(description='Microsoft Windows Metafile', extension='.wmf')
   mime_types['application/x-msmoney'] = dict(description='Microsoft Money', extension='.mny')
   mime_types['application/x-mspublisher'] = dict(description='Microsoft Publisher', extension='.pub')
   mime_types['application/x-msschedule'] = dict(description='Microsoft Schedule+', extension='.scd')
   mime_types['application/x-msterminal'] = dict(description='Microsoft Windows Terminal Services', extension='.trm')
   mime_types['application/x-mswrite'] = dict(description='Microsoft Wordpad', extension='.wri')
   mime_types['application/x-netcdf'] = dict(description='Network Common Data Form (NetCDF)', extension='.nc')
   mime_types['application/x-pkcs12'] = dict(description='PKCS #12 - Personal Information Exchange Syntax Standard', extension='.p12')
   mime_types['application/x-pkcs7-certificates'] = dict(description='PKCS #7 - Cryptographic Message Syntax Standard (Certificates)', extension='.p7b')
   mime_types['application/x-pkcs7-certreqresp'] = dict(description='PKCS #7 - Cryptographic Message Syntax Standard (Certificate Request Response)', extension='.p7r')
   mime_types['application/x-rar-compressed'] = dict(description='RAR Archive', extension='.rar')
   mime_types['application/x-sh'] = dict(description='Bourne Shell Script', extension='.sh')
   mime_types['application/x-shar'] = dict(description='Shell Archive', extension='.shar')
   mime_types['application/x-shockwave-flash'] = dict(description='Adobe Flash', extension='.swf')
   mime_types['application/x-silverlight-app'] = dict(description='Microsoft Silverlight', extension='.xap')
   mime_types['application/x-stuffit'] = dict(description='Stuffit Archive', extension='.sit')
   mime_types['application/x-stuffitx'] = dict(description='Stuffit Archive', extension='.sitx')
   mime_types['application/x-sv4cpio'] = dict(description='System V Release 4 CPIO Archive', extension='.sv4cpio')
   mime_types['application/x-sv4crc'] = dict(description='System V Release 4 CPIO Checksum Data', extension='.sv4crc')
   mime_types['application/x-tar'] = dict(description='Tar File (Tape Archive)', extension='.tar')
   mime_types['application/x-tcl'] = dict(description='Tcl Script', extension='.tcl')
   mime_types['application/x-tex'] = dict(description='TeX', extension='.tex')
   mime_types['application/x-tex-tfm'] = dict(description='TeX Font Metric', extension='.tfm')
   mime_types['application/x-texinfo'] = dict(description='GNU Texinfo Document', extension='.texinfo')
   mime_types['application/x-ustar'] = dict(description='Ustar (Uniform Standard Tape Archive)', extension='.ustar')
   mime_types['application/x-wais-source'] = dict(description='WAIS Source', extension='.src')
   mime_types['application/x-x509-ca-cert'] = dict(description='X.509 Certificate', extension='.der')
   mime_types['application/x-xfig'] = dict(description='Xfig', extension='.fig')
   mime_types['application/x-xpinstall'] = dict(description='XPInstall - Mozilla', extension='.xpi')
   mime_types['application/xcap-diff+xml'] = dict(description='XML Configuration Access Protocol - XCAP Diff', extension='.xdf')
   mime_types['application/xenc+xml'] = dict(description='XML Encryption Syntax and Processing', extension='.xenc')
   mime_types['application/xhtml+xml'] = dict(description='XHTML - The Extensible HyperText Markup Language', extension='.xhtml')
   mime_types['application/xml'] = dict(description='XML - Extensible Markup Language', extension='.xml')
   mime_types['application/xml-dtd'] = dict(description='Document Type Definition', extension='.dtd')
   mime_types['application/xop+xml'] = dict(description='XML-Binary Optimized Packaging', extension='.xop')
   mime_types['application/xslt+xml'] = dict(description='XML Transformations', extension='.xslt')
   mime_types['application/xspf+xml'] = dict(description='XSPF - XML Shareable Playlist Format', extension='.xspf')
   mime_types['application/xv+xml'] = dict(description='MXML', extension='.mxml')
   mime_types['application/yang'] = dict(description='YANG Data Modeling Language', extension='.yang')
   mime_types['application/yin+xml'] = dict(description='YIN (YANG - XML)', extension='.yin')
   mime_types['application/zip'] = dict(description='Zip Archive', extension='.zip')
   mime_types['audio/adpcm'] = dict(description='Adaptive differential pulse-code modulation', extension='.adp')
   mime_types['audio/basic'] = dict(description='Sun Audio - Au file format', extension='.au')
   mime_types['audio/midi'] = dict(description='MIDI - Musical Instrument Digital Interface', extension='.mid')
   mime_types['audio/mp4'] = dict(description='MPEG-4 Audio', extension='.mp4a')
   mime_types['audio/mpeg'] = dict(description='MPEG Audio', extension='.mpga')
   mime_types['audio/ogg'] = dict(description='Ogg Audio', extension='.oga')
   mime_types['audio/vnd.dece.audio'] = dict(description='DECE Audio', extension='.uva')
   mime_types['audio/vnd.digital-winds'] = dict(description='Digital Winds Music', extension='.eol')
   mime_types['audio/vnd.dra'] = dict(description='DRA Audio', extension='.dra')
   mime_types['audio/vnd.dts'] = dict(description='DTS Audio', extension='.dts')
   mime_types['audio/vnd.dts.hd'] = dict(description='DTS High Definition Audio', extension='.dtshd')
   mime_types['audio/vnd.lucent.voice'] = dict(description='Lucent Voice', extension='.lvp')
   mime_types['audio/vnd.ms-playready.media.pya'] = dict(description='Microsoft PlayReady Ecosystem', extension='.pya')
   mime_types['audio/vnd.nuera.ecelp4800'] = dict(description='Nuera ECELP 4800', extension='.ecelp4800')
   mime_types['audio/vnd.nuera.ecelp7470'] = dict(description='Nuera ECELP 7470', extension='.ecelp7470')
   mime_types['audio/vnd.nuera.ecelp9600'] = dict(description='Nuera ECELP 9600', extension='.ecelp9600')
   mime_types['audio/vnd.rip'] = dict(description='HitnMix', extension='.rip')
   mime_types['audio/webm'] = dict(description='Open Web Media Project - Audio', extension='.weba')
   mime_types['audio/x-aac'] = dict(description='Advanced Audio Coding (AAC)', extension='.aac')
   mime_types['audio/x-aiff'] = dict(description='Audio Interchange File Format', extension='.aif')
   mime_types['audio/x-mpegurl'] = dict(description='M3U (Multimedia Playlist)', extension='.m3u')
   mime_types['audio/x-ms-wax'] = dict(description='Microsoft Windows Media Audio Redirector', extension='.wax')
   mime_types['audio/x-ms-wma'] = dict(description='Microsoft Windows Media Audio', extension='.wma')
   mime_types['audio/x-pn-realaudio'] = dict(description='Real Audio Sound', extension='.ram')
   mime_types['audio/x-pn-realaudio-plugin'] = dict(description='Real Audio Sound', extension='.rmp')
   mime_types['audio/x-wav'] = dict(description='Waveform Audio File Format (WAV)', extension='.wav')
   mime_types['chemical/x-cdx'] = dict(description='ChemDraw eXchange file', extension='.cdx')
   mime_types['chemical/x-cif'] = dict(description='Crystallographic Interchange Format', extension='.cif')
   mime_types['chemical/x-cmdf'] = dict(description='CrystalMaker Data Format', extension='.cmdf')
   mime_types['chemical/x-cml'] = dict(description='Chemical Markup Language', extension='.cml')
   mime_types['chemical/x-csml'] = dict(description='Chemical Style Markup Language', extension='.csml')
   mime_types['chemical/x-xyz'] = dict(description='XYZ File Format', extension='.xyz')
   mime_types['image/bmp'] = dict(description='Bitmap Image File', extension='.bmp')
   mime_types['image/cgm'] = dict(description='Computer Graphics Metafile', extension='.cgm')
   mime_types['image/g3fax'] = dict(description='G3 Fax Image', extension='.g3')
   mime_types['image/gif'] = dict(description='Graphics Interchange Format', extension='.gif')
   mime_types['image/ief'] = dict(description='Image Exchange Format', extension='.ief')
   mime_types['image/jpeg'] = dict(description='JPEG Image', extension='.jpg')
   mime_types['image/ktx'] = dict(description='OpenGL Textures (KTX)', extension='.ktx')
   mime_types['image/png'] = dict(description='Portable Network Graphics (PNG)', extension='.png')
   mime_types['image/prs.btif'] = dict(description='BTIF', extension='.btif')
   mime_types['image/svg+xml'] = dict(description='Scalable Vector Graphics (SVG)', extension='.svg')
   mime_types['image/tiff'] = dict(description='Tagged Image File Format', extension='.tiff')
   mime_types['image/vnd.adobe.photoshop'] = dict(description='Photoshop Document', extension='.psd')
   mime_types['image/vnd.dece.graphic'] = dict(description='DECE Graphic', extension='.uvi')
   mime_types['image/vnd.djvu'] = dict(description='DjVu', extension='.djvu')
   mime_types['image/vnd.dvb.subtitle'] = dict(description='Close Captioning - Subtitle', extension='.sub')
   mime_types['image/vnd.dwg'] = dict(description='DWG Drawing', extension='.dwg')
   mime_types['image/vnd.dxf'] = dict(description='AutoCAD DXF', extension='.dxf')
   mime_types['image/vnd.fastbidsheet'] = dict(description='FastBid Sheet', extension='.fbs')
   mime_types['image/vnd.fpx'] = dict(description='FlashPix', extension='.fpx')
   mime_types['image/vnd.fst'] = dict(description='FAST Search & Transfer ASA', extension='.fst')
   mime_types['image/vnd.fujixerox.edmics-mmr'] = dict(description='EDMICS 2000', extension='.mmr')
   mime_types['image/vnd.fujixerox.edmics-rlc'] = dict(description='EDMICS 2000', extension='.rlc')
   mime_types['image/vnd.ms-modi'] = dict(description='Microsoft Document Imaging Format', extension='.mdi')
   mime_types['image/vnd.net-fpx'] = dict(description='FlashPix', extension='.npx')
   mime_types['image/vnd.wap.wbmp'] = dict(description='WAP Bitamp (WBMP)', extension='.wbmp')
   mime_types['image/vnd.xiff'] = dict(description='eXtended Image File Format (XIFF)', extension='.xif')
   mime_types['image/webp'] = dict(description='WebP Image', extension='.webp')
   mime_types['image/x-cmu-raster'] = dict(description='CMU Image', extension='.ras')
   mime_types['image/x-cmx'] = dict(description='Corel Metafile Exchange (CMX)', extension='.cmx')
   mime_types['image/x-freehand'] = dict(description='FreeHand MX', extension='.fh')
   mime_types['image/x-icon'] = dict(description='Icon Image', extension='.ico')
   mime_types['image/x-pcx'] = dict(description='PCX Image', extension='.pcx')
   mime_types['image/x-pict'] = dict(description='PICT Image', extension='.pic')
   mime_types['image/x-portable-anymap'] = dict(description='Portable Anymap Image', extension='.pnm')
   mime_types['image/x-portable-bitmap'] = dict(description='Portable Bitmap Format', extension='.pbm')
   mime_types['image/x-portable-graymap'] = dict(description='Portable Graymap Format', extension='.pgm')
   mime_types['image/x-portable-pixmap'] = dict(description='Portable Pixmap Format', extension='.ppm')
   mime_types['image/x-rgb'] = dict(description='Silicon Graphics RGB Bitmap', extension='.rgb')
   mime_types['image/x-xbitmap'] = dict(description='X BitMap', extension='.xbm')
   mime_types['image/x-xpixmap'] = dict(description='X PixMap', extension='.xpm')
   mime_types['image/x-xwindowdump'] = dict(description='X Window Dump', extension='.xwd')
   mime_types['message/rfc822'] = dict(description='Email Message', extension='.eml')
   mime_types['model/iges'] = dict(description='Initial Graphics Exchange Specification (IGES)', extension='.igs')
   mime_types['model/mesh'] = dict(description='Mesh Data Type', extension='.msh')
   mime_types['model/vnd.collada+xml'] = dict(description='COLLADA', extension='.dae')
   mime_types['model/vnd.dwf'] = dict(description='Autodesk Design Web Format (DWF)', extension='.dwf')
   mime_types['model/vnd.gdl'] = dict(description='Geometric Description Language (GDL)', extension='.gdl')
   mime_types['model/vnd.gtw'] = dict(description='Gen-Trix Studio', extension='.gtw')
   mime_types['model/vnd.mts'] = dict(description='Virtue MTS', extension='.mts')
   mime_types['model/vnd.vtu'] = dict(description='Virtue VTU', extension='.vtu')
   mime_types['model/vrml'] = dict(description='Virtual Reality Modeling Language', extension='.wrl')
   mime_types['text/calendar'] = dict(description='iCalendar', extension='.ics')
   mime_types['text/css'] = dict(description='Cascading Style Sheets (CSS)', extension='.css')
   mime_types['text/csv'] = dict(description='Comma-Seperated Values', extension='.csv')
   mime_types['text/html'] = dict(description='HyperText Markup Language (HTML)', extension='.html')
   mime_types['text/n3'] = dict(description='Notation3', extension='.n3')
   mime_types['text/plain'] = dict(description='Text File', extension='.txt')
   mime_types['text/plain-bas'] = dict(description='BAS Partitur Format', extension='.par')
   mime_types['text/prs.lines.tag'] = dict(description='PRS Lines Tag', extension='.dsc')
   mime_types['text/richtext'] = dict(description='Rich Text Format (RTF)', extension='.rtx')
   mime_types['text/sgml'] = dict(description='Standard Generalized Markup Language (SGML)', extension='.sgml')
   mime_types['text/tab-separated-values'] = dict(description='Tab Seperated Values', extension='.tsv')
   mime_types['text/troff'] = dict(description='troff', extension='.t')
   mime_types['text/turtle'] = dict(description='Turtle (Terse RDF Triple Language)', extension='.ttl')
   mime_types['text/uri-list'] = dict(description='URI Resolution Services', extension='.uri')
   mime_types['text/vnd.curl'] = dict(description='Curl - Applet', extension='.curl')
   mime_types['text/vnd.curl.dcurl'] = dict(description='Curl - Detached Applet', extension='.dcurl')
   mime_types['text/vnd.curl.mcurl'] = dict(description='Curl - Manifest File', extension='.mcurl')
   mime_types['text/vnd.curl.scurl'] = dict(description='Curl - Source Code', extension='.scurl')
   mime_types['text/vnd.fly'] = dict(description='mod_fly / fly.cgi', extension='.fly')
   mime_types['text/vnd.fmi.flexstor'] = dict(description='FLEXSTOR', extension='.flx')
   mime_types['text/vnd.graphviz'] = dict(description='Graphviz', extension='.gv')
   mime_types['text/vnd.in3d.3dml'] = dict(description='In3D - 3DML', extension='.3dml')
   mime_types['text/vnd.in3d.spot'] = dict(description='In3D - 3DML', extension='.spot')
   mime_types['text/vnd.sun.j2me.app-descriptor'] = dict(description='J2ME App Descriptor', extension='.jad')
   mime_types['text/vnd.wap.wml'] = dict(description='Wireless Markup Language (WML)', extension='.wml')
   mime_types['text/vnd.wap.wmlscript'] = dict(description='Wireless Markup Language Script (WMLScript)', extension='.wmls')
   mime_types['text/x-asm'] = dict(description='Assembler Source File', extension='.s')
   mime_types['text/x-c'] = dict(description='C Source File', extension='.c')
   mime_types['text/x-fortran'] = dict(description='Fortran Source File', extension='.f')
   mime_types['text/x-java-source,java'] = dict(description='Java Source File', extension='.java')
   mime_types['text/x-pascal'] = dict(description='Pascal Source File', extension='.p')
   mime_types['text/x-setext'] = dict(description='Setext', extension='.etx')
   mime_types['text/x-uuencode'] = dict(description='UUEncode', extension='.uu')
   mime_types['text/x-vcalendar'] = dict(description='vCalendar', extension='.vcs')
   mime_types['text/x-vcard'] = dict(description='vCard', extension='.vcf')
   mime_types['video/3gpp'] = dict(description='3GP', extension='.3gp')
   mime_types['video/3gpp2'] = dict(description='3GP2', extension='.3g2')
   mime_types['video/h261'] = dict(description='H.261', extension='.h261')
   mime_types['video/h263'] = dict(description='H.263', extension='.h263')
   mime_types['video/h264'] = dict(description='H.264', extension='.h264')
   mime_types['video/jpeg'] = dict(description='JPGVideo', extension='.jpgv')
   mime_types['video/jpm'] = dict(description='JPEG 2000 Compound Image File Format', extension='.jpm')
   mime_types['video/mj2'] = dict(description='Motion JPEG 2000', extension='.mj2')
   mime_types['video/mp4'] = dict(description='MPEG-4 Video', extension='.mp4')
   mime_types['video/mpeg'] = dict(description='MPEG Video', extension='.mpeg')
   mime_types['video/ogg'] = dict(description='Ogg Video', extension='.ogv')
   mime_types['video/quicktime'] = dict(description='Quicktime Video', extension='.qt')
   mime_types['video/vnd.dece.hd'] = dict(description='DECE High Definition Video', extension='.uvh')
   mime_types['video/vnd.dece.mobile'] = dict(description='DECE Mobile Video', extension='.uvm')
   mime_types['video/vnd.dece.pd'] = dict(description='DECE PD Video', extension='.uvp')
   mime_types['video/vnd.dece.sd'] = dict(description='DECE SD Video', extension='.uvs')
   mime_types['video/vnd.dece.video'] = dict(description='DECE Video', extension='.uvv')
   mime_types['video/vnd.fvt'] = dict(description='FAST Search & Transfer ASA', extension='.fvt')
   mime_types['video/vnd.mpegurl'] = dict(description='MPEG Url', extension='.mxu')
   mime_types['video/vnd.ms-playready.media.pyv'] = dict(description='Microsoft PlayReady Ecosystem Video', extension='.pyv')
   mime_types['video/vnd.uvvu.mp4'] = dict(description='DECE MP4', extension='.uvu')
   mime_types['video/vnd.vivo'] = dict(description='Vivo', extension='.viv')
   mime_types['video/webm'] = dict(description='Open Web Media Project - Video', extension='.webm')
   mime_types['video/x-f4v'] = dict(description='Flash Video', extension='.f4v')
   mime_types['video/x-fli'] = dict(description='FLI/FLC Animation Format', extension='.fli')
   mime_types['video/x-flv'] = dict(description='Flash Video', extension='.flv')
   mime_types['video/x-m4v'] = dict(description='M4v', extension='.m4v')
   mime_types['video/x-ms-asf'] = dict(description='Microsoft Advanced Systems Format (ASF)', extension='.asf')
   mime_types['video/x-ms-wm'] = dict(description='Microsoft Windows Media', extension='.wm')
   mime_types['video/x-ms-wmv'] = dict(description='Microsoft Windows Media Video', extension='.wmv')
   mime_types['video/x-ms-wmx'] = dict(description='Microsoft Windows Media Audio/Video Playlist', extension='.wmx')
   mime_types['video/x-ms-wvx'] = dict(description='Microsoft Windows Media Video Playlist', extension='.wvx')
   mime_types['video/x-msvideo'] = dict(description='Audio Video Interleave (AVI)', extension='.avi')
   mime_types['video/x-sgi-movie'] = dict(description='SGI Movie', extension='.movie')
   mime_types['x-conference/x-cooltalk'] = dict(description='CoolTalk', extension='.ice')

   if file.mime_type in mime_types:
      return mime_types[file.mime_type]
   else:
      return dict(description='Unknown', extension='')