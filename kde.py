#!/usr/bin/env python3

framework_packages = [
  'attica',
  'kapidox',
  'karchive',
  'kcodecs',
  'kconfig',
  'kcoreaddons',
  'kdbusaddons',
  'kdnssd',
  'kguiaddons',
  'ki18n',
  'kidletime',
  'kimageformats',
  'kitemmodels',
  'kitemviews',
  'kplotting',
  'kwidgetsaddons',
  'kwindowsystem',
  'networkmanager-qt',
  'solid',
  'sonnet',
  'threadweaver',
  'kauth',
  'kcompletion',
  'kcrash',
  'kdoctools',
  'kpty',
  'kunitconversion',
  'kconfigwidgets',
  'kservice',
  'kglobalaccel',
  'kpackage',
  'kdesu',
  'kemoticons',
  'kiconthemes',
  'kjobwidgets',
  'knotifications',
  'ktextwidgets',
  'kxmlgui',
  'kbookmarks',
  'kwallet',
  'kded',
  'kio',
  'kdeclarative',
  'kcmutils',
  'kirigami',
  'knewstuff',
  'frameworkintegration',
  'kinit',
  'knotifyconfig',
  'kparts',
  'kactivities',
  'syntax-highlighting',
  'ktexteditor',
  'kwayland',
  'plasma-framework',
  'kpeople',
  'kxmlrpcclient',
  'bluez-qt',
  'kfilemetadata',
  'baloo',
  'kactivities-stats',
  'krunner',
  'prison',
  'qqc2-desktop-style',
  'kjs',
  'kdesignerplugin',
  'kdelibs4support',
  'khtml',
  'kjsembed',
  'kmediaplayer',
  'kross',
  'kholidays',
  'purpose',
  'kcalendarcore',
  'kcontacts',
  'kquickcharts',
  'kdav'
]

plasma_packages = [
  'kdecoration',
  'libkscreen',
  'libksysguard',
  'breeze',
  'breeze-gtk',
  'kscreenlocker',
  'oxygen',
  'kinfocenter',
  'ksysguard',
  'kwayland-server',
  'kwin',
  'plasma-workspace',
  'plasma-disks',
  'bluedevil',
  'kde-gtk-config',
  'khotkeys',
  'kmenuedit',
  'kscreen',
  'kwallet-pam',
  'kwayland-integration',
  'kwrited',
  'milou',
  'plasma-nm',
  'plasma-pa',
  'plasma-workspace-wallpapers',
  'polkit-kde-agent-1',
  'powerdevil',
  'plasma-desktop',
  'kdeplasma-addons',
  'kgamma5',
  'ksshaskpass',
  'sddm-kcm',
  'discover',
  'kactivitymanagerd',
  'plasma-integration',
  'plasma-tests',
  'xdg-desktop-portal-kde',
  'drkonqi',
  'plasma-vault',
  'plasma-browser-integration',
  'kde-cli-tools',
  'systemsettings',
  'plasma-thunderbolt',
  'plasma-firewall',
  'plasma-systemmonitor',
  'qqc2-breeze-style'
]

framework_version='5.82.0'

for package in framework_packages:
  url = 'https://github.com/KDE/' + package + '/archive/v' + framework_version + '/' + package + '-' + framework_version + '.tar.gz'
  version = framework_version + '.0'
  name = package
  
  with open('kftemplate.sh', 'r') as fp:
    data = fp.read()
    replaced = data.replace('__NAME__', name)
    replaced = replaced.replace('__VERSION__', version)
    replaced = replaced.replace('__URL__', url)
    with open('/home/chandrakant/aryalinux/aryalinux/applications/' + name + '.sh', 'w') as fout:
      fout.write(replaced)

plasma_version='5.21.1'

for package in plasma_packages:
  url = 'https://github.com/KDE/' + package + '/archive/v' + plasma_version + '/' + package + '-' + plasma_version + '.tar.gz'
  version = plasma_version
  name = package
  
  with open('kftemplate.sh', 'r') as fp:
    data = fp.read()
    replaced = data.replace('__NAME__', name)
    replaced = replaced.replace('__VERSION__', version)
    replaced = replaced.replace('__URL__', url)
    with open('/home/chandrakant/aryalinux/aryalinux/applications/' + name + '.sh', 'w') as fout:
      fout.write(replaced)


