from scrapy.selector import Selector
from scrapy.spider import Spider
from scrapy.http import Request, FormRequest
from scrapy.selector import HtmlXPathSelector

class MySpider(Spider):
    name = 'pachinko'
    start_urls = [
        'http://fe.site777.tv/data/yahoo/login.php',
    ]

    def parse(self, response):
    	hxs = HtmlXPathSelector(response)
	input_names = hxs.select('//form[@name="login_form"]//input/@name').extract()
	form_action = hxs.select('//form[@name="login_form"]/@action').extract()[0]
	form_request = {}
	for i in xrange(len(input_names)):
		input_value = hxs.select('//form[@name="login_form"]//input[@name="' + input_names[i] + '"]/@value').extract()
		if(len(input_value)>0):
			form_request[input_names[i]] = input_value[0]

	form_request['login'] = 'gopachipro'
	form_request['passwd'] = 'pachi.pro.2014'
	headers = {}
	headers['Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
	headers['Accept-Type'] = 'gzip,deflate,sdch'
	headers['Accept-Language'] = 'en-US,en;q=0.8,en-GB;q=0.6'
	headers['Cache-Control'] = 'max-age=0'
	headers['Connection'] = 'keep-alive'
	headers['Content-Type'] = 'application/x-www-form-urlencoded'
	headers['Host'] = 'login.yahoo.co.jp'
	headers['Origin'] = 'https://login.yahoo.co.jp'
	headers['Referer'] = response.url
	headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1700.107 Safari/537.36'
	form_request['.reg1'] = '1440'
	form_request['.reg2'] = '900'
	form_request['.reg3'] = '-330'
	form_request['.reg4'] = """Widevine Content Decryption Module,undefined,,application/x-ppapi-widevine-cdm,Shockwave Flash,undefined,swf,application/x-shockwave-flash,FutureSplash Player,undefined,spl,application/futuresplash,,undefined,,application/vnd.chromium.remoting-viewer,Native Client Executable,undefined,,application/x-nacl,Portable Native Client Executable,undefined,,application/x-pnacl,Portable Document Format,undefined,pdf,application/pdf,Portable Document Format,undefined,pdf,application/x-google-chrome-print-preview-pdf,Citrix Online Application Detector,undefined,,application/x-col-application-detector,gpc,undefined,,application/webx-gpc-plugin64,Provides information about the default web browser,undefined,,application/apple-default-browser,Shockwave Flash,undefined,swf,application/x-shockwave-flash,FutureSplash Player,undefined,spl,application/futuresplash,Windows Media Video,undefined,wm,video/x-ms-wm,Windows Media Plugin,undefined,,video/x-ms-asf-plugin,Windows Media Video,undefined,asf,video/x-ms-asf,Windows Media Plugin,undefined,,application/x-ms-wmp,Windows Media Plugin,undefined,,application/asx,Windows Media Playlist,undefined,asx,video/x-ms-asx,Windows Media Video,undefined,wmv,video/x-ms-wmv,Windows Media Playlist,undefined,wax,audio/x-ms-wax,Windows Media Playlist,undefined,wvx,video/x-ms-wvx,Windows Media Video,undefined,wmp,video/x-ms-wmp,Windows Media Playlist,undefined,wmx,video/x-ms-wmx,Windows Media Audio,undefined,wma,audio/x-ms-wma,Windows Media Plugin,undefined,,application/x-mplayer2,Google voice and video chat,undefined,googletalk,application/googletalk,Google Talk Plugin Video Accelerator Type,undefined,,application/vnd.gtpo3d.auto,Google Talk Plugin Video Renderer,undefined,o1d,application/o1d,3GPP media,undefined,3gp,3gpp,audio/3gpp,uLaw/AU audio,undefined,au,snd,ulw,audio/basic,AIFF audio,undefined,aiff,aif,aifc,cdda,audio/aiff,MPEG media,undefined,mpeg,mpg,m1s,m1v,m1a,m75,m15,mp2,mpm,mpv,mpa,video/mpeg,Video For Windows (AVI),undefined,avi,vfw,video/x-msvideo,QuickTime Movie,undefined,mov,qt,mqv,video/quicktime,SDP stream descriptor,undefined,sdp,application/x-sdp,MP3 audio,undefined,mp3,swa,audio/x-mpeg3,AMR audio,undefined,amr,audio/amr,QUALCOMM PureVoice audio,undefined,qcp,audio/vnd.qcelp,MP3 audio,undefined,mp3,swa,audio/x-mp3,AAC audio,undefined,aac,adts,audio/aac,3GPP2 media,undefined,3g2,3gp2,video/3gpp2,MPEG media,undefined,mpeg,mpg,m1s,m1v,m1a,m75,m15,mp2,mpm,mpv,mpa,video/x-mpeg,SDP stream descriptor,undefined,sdp,application/sdp,Video For Windows (AVI),undefined,avi,vfw,video/msvideo,RTSP stream descriptor,undefined,rtsp,rts,application/x-rtsp,MPEG audio,undefined,mpeg,mpg,m1s,m1a,mp2,mpm,mpa,m2a,mp3,swa,audio/x-mpeg,AAC audio book,undefined,m4b,audio/x-m4b,AMC media,undefined,amc,application/x-mpeg,MPEG audio,undefined,mpeg,mpg,m1s,m1a,mp2,mpm,mpa,m2a,mp3,swa,audio/mpeg,AAC audio (protected),undefined,m4p,audio/x-m4p,Video For Windows (AVI),undefined,avi,vfw,video/avi,MPEG-4 media,undefined,mp4,video/mp4,GSM audio,undefined,gsm,audio/x-gsm,AAC audio,undefined,aac,adts,audio/x-aac,MP3 audio,undefined,mp3,swa,audio/mp3,AAC audio,undefined,m4a,audio/x-m4a,3GPP media,undefined,3gp,3gpp,video/3gpp,WAVE audio,undefined,wav,bwf,audio/wav,MPEG-4 media,undefined,mp4,audio/mp4,CAF audio,undefined,caf,audio/x-caf,SD video,undefined,sdv,video/sd-video,AIFF audio,undefined,aiff,aif,aifc,cdda,audio/x-aiff,WAVE audio,undefined,wav,bwf,audio/x-wav,Video (protected),undefined,m4v,video/x-m4v,MP3 audio,undefined,mp3,swa,audio/mpeg3,3GPP2 media,undefined,3g2,3gp2,audio/3gpp2,Microsoft Office for Mac SharePoint Browser Plug-in,undefined,,application/x-sharepoint,Microsoft Silverlight,undefined,xaml,application/x-silverlight,Microsoft Silverlight,undefined,xaml,application/x-silverlight-2"""
	form_request['.reg5'] = 'Enables Widevine licenses for playback of HTML audio/video content.,widevinecdmadapter.plugin,Widevine Content Decryption Module,Shockwave Flash 12.0 r0,PepperFlashPlayer.plugin,Shockwave Flash,This plugin allows you to securely access other computers that have been shared with you. To use this plugin you must first install the <a href="https://chrome.google.com/remotedesktop">Chrome Remote Desktop</a> webapp.,internal-remoting-viewer,Chrome Remote Desktop Viewer,,ppGoogleNaClPluginChrome.plugin,Native Client,,PDF.plugin,Chrome PDF Viewer,Plugin that detects installed Citrix Online products (visit www.citrixonline.com).,CitrixOnlineWebDeploymentPlugin.plugin,Citrix Online Web Deployment Plugin 1.0.0.105,WebEx64 General Plugin Container Version 205,WebEx64.plugin,WebEx64 General Plugin Container,Provides information about the default web browser,Default Browser.plugin,Default Browser Helper,Shockwave Flash 12.0 r0,Flash Player.plugin,Shockwave Flash,The Flip4Mac WMV Plugin allows you to view Windows Media content using QuickTime.,Flip4Mac WMV Plugin.plugin,Flip4Mac Windows Media Plugin,Version 5.1.4.17398,googletalkbrowserplugin.plugin,Google Talk Plugin,Google Talk Plugin Video Accelerator version:0.1.44.29,npgtpo3dautoplugin.plugin,Google Talk Plugin Video Accelerator,Version 5.1.4.17398,o1dbrowserplugin.plugin,Google Talk Plugin Video Renderer,The QuickTime Plugin allows you to view a wide variety of multimedia content in web pages. For more information, visit the <A HREF=http://www.apple.com/quicktime>QuickTime</A> Web site.,QuickTime Plugin.plugin,QuickTime Plug-in 7.7.3,Microsoft Office for Mac SharePoint Browser Plug-in,SharePointBrowserPlugin.plugin,SharePoint Browser Plug-in,5.1.20513.0,Silverlight.plugin,Silverlight Plug-In'
	form_request['.reg6'] = ''
	form_request['.reg7'] = ''
	form_request['.reg8'] = ''
	form_request['.reg9'] = '31.064'
	form_request['.persistent'] = 'y'
	del form_request[".nojs"]
	for h in sorted(form_request.keys()):
		print h, ": ", form_request[h]
	print len(form_request), "number of post params"
	r = FormRequest(url=form_action, formdata=form_request, callback=self.parse3, headers=headers, dont_filter=True)
	r2 = Request(url=hxs.select('//img[@width="1"]/@src').extract()[0], callback=self.parse2, dont_filter=True)
	r2.meta['q'] = r
	return r2

    def parse2(self, response):
    	return response.meta['q']

    def parse3(self, response):
    	print response.body
	raw_input()
