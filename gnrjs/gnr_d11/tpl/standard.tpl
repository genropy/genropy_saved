<?xml version="1.0" encoding="${charset}"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
    <head>
        <meta http-equiv="content-type" content="text/html; charset=${charset}" />
        <meta http-equiv="X-UA-Compatible" content="chrome=1">

		<!-- Prevent iPad/iPhone resize and enable full screen mode (if you bookmark the app on the home screen) -->
		<meta name="apple-mobile-web-app-capable" content="yes">
        <meta name="viewport" content="width=device-width, user-scalable=no, initial-scale=1.0, maximum-scale=1.0;" />
        <meta name="apple-mobile-web-app-status-bar-style" content="black">
        <link rel="apple-touch-icon" href="_rsrc/mobile/ios/images/app_icon.png">
        <link rel="apple-touch-startup-image" href="_rsrc/mobile/ios/images/startup_image.jpg">

        <%include file="gnr_header.tpl" />
        <style type="text/css" title="localcss">
            html, body, #mainWindow{width: 100%;height: 100%; overflow-x:hidden;}
        </style>
    </head>
    <body class="${bodyclasses}" >
        <div id="mainWindow" class='waiting'></div>
    </body>
</html>
