# -*- coding: utf-8 -*-
import six
import os
from kodi_six import xbmc, xbmcgui, xbmcplugin, xbmcaddon, xbmcvfs
addon = xbmcaddon.Addon()
addonname = addon.getAddonInfo('name')
icon = addon.getAddonInfo('icon')
translate = xbmcvfs.translatePath if six.PY3 else xbmc.translatePath
userdata_kodi = translate('special://home/userdata')
player = os.path.join(userdata_kodi, "playercorefactory.xml")
buffer = os.path.join(userdata_kodi, "advancedsettings.xml")
home = translate(addon.getAddonInfo('path')) if six.PY3 else translate(addon.getAddonInfo('path')).decode('utf-8')
folder_players = os.path.join(home, "players")
folder_buffers = os.path.join(home, "buffers")

def platform():
    from kodi_six import xbmc

    if xbmc.getCondVisibility('system.platform.android'):
        return 'android'
    elif xbmc.getCondVisibility('system.platform.linux') or xbmc.getCondVisibility('system.platform.linux.Raspberrypi'):
        return 'linux'
    elif xbmc.getCondVisibility('system.platform.windows'):
        return 'windows'
    elif xbmc.getCondVisibility('system.platform.osx'):
        return 'osx'
    elif xbmc.getCondVisibility('system.platform.atv2'):
        return 'atv2'
    elif xbmc.getCondVisibility('system.platform.ios') or xbmc.getCondVisibility('system.platform.darwin'):
        return 'ios'

def msg(name):
    new_msg = '%s player applied!'%str(name)
    ok = xbmcgui.Dialog().ok(addonname, new_msg)

def msg2(name):
    new_msg = '%s buffer applied!'%str(name)
    ok = xbmcgui.Dialog().ok(addonname, new_msg)

def copy2folder(folder):
    try:
        os.remove(player)
    except:
        pass    
    source = os.path.join(folder_players, folder, "playercorefactory.xml")
    destination = player
    xbmcvfs.copy(source,destination)
    msg(folder)

def copy2folder2(folder):
    try:
        os.remove(buffer)
    except:
        pass    
    source = os.path.join(folder_buffers, folder, "advancedsettings.xml")
    destination = buffer
    xbmcvfs.copy(source,destination)
    msg2(folder)

def alert(s):
    new_msg = 'your system is not %s!'%str(s)
    ok = xbmcgui.Dialog().ok(addonname, new_msg)

def select_op(name,items):
    op = xbmcgui.Dialog().select(name, items)
    return op

def change_player():
    items = ['DEFAULT PLAYER', 'ArchosVideo', 'BSPlayerFree', 'DaroonPlayer', 'DicePlayerFree', 'DicePlayerPaid', 'JustPlayer', 'MoboplayerFree', 'mVideoplayerFree', 'MXPayerFree', 'MXPlayerPro', 'PotPlayer(windows)', 'RockPlayer', 'RockPlayerLite', 'SopCast', 'TPlayer', 'VLC(windows 64)', 'VLC(windows x86)', 'VLCPayer', 'Vplater', 'WondersharePlayer', 'VLC(Linux)', 'Celluloid(Linux)', 'Exit']
    op = select_op(name='SELECT A PLAYER BELOW:',items=items)
    if op == 0:
        try:
            os.remove(player)
        except:
            pass
        msg('default')
    elif op == 1:
        if platform() == 'android':
            copy2folder('ArchosVideo')
        else:
            alert('android')
    elif op == 2:
        if platform() == 'android':
            copy2folder('BSPlayerFree')
        else:
            alert('android')
    elif op == 3:
        if platform() == 'android':
            copy2folder('DaroonPlayer')
        else:
            alert('android')
    elif op == 4:
        if platform() == 'android':
            copy2folder('DicePlayerFree')
        else:
            alert('android')
    elif op == 5:
        if platform() == 'android':
            copy2folder('DicePlayerPaid')
        else:
            alert('android')
    elif op == 6:
        if platform() == 'android':
            copy2folder('JustPlayer')
        else:
            alert('android')
    elif op == 7:
        if platform() == 'android':
            copy2folder('MoboplayerFree')
        else:
            alert('android')
    elif op == 8:
        if platform() == 'android':
            copy2folder('mVideoplayerFree')
        else:
            alert('android')  
    elif op == 9:
        if platform() == 'android':
            copy2folder('MXPayerFree')
        else:
            alert('android')
    elif op == 10:
        if platform() == 'android':
            copy2folder('MXPlayerPro')
        else:
            alert('android')
    elif op == 11:
        if platform() == 'windows':
            copy2folder('PotPlayer(windows)')
        else:
            alert('windows')
    elif op == 12:
        if platform() == 'android':
            copy2folder('RockPlayer')
        else:
            alert('android')
    elif op == 13:
        if platform() == 'android':
            copy2folder('RockPlayerLite')
        else:
            alert('android')
    elif op == 14:
        if platform() == 'android':
            copy2folder('SopCast')
        else:
            alert('android')
    elif op == 15:
        if platform() == 'android':
            copy2folder('TPlayer')
        else:
            alert('android')
    elif op == 16:
        if platform() == 'windows':
            copy2folder('VLC(windows 64)')
        else:
            alert('windows')
    elif op == 17:
        if platform() == 'windows':
            copy2folder('VLC(windows x86)')
        else:
            alert('windows')
    elif op == 18:
        if platform() == 'android':
            copy2folder('VLCPayer')
        else:
            alert('android')
    elif op == 19:
        if platform() == 'android':
            copy2folder('Vplater')
        else:
            alert('android')
    elif op == 20:
        if platform() == 'android':
            copy2folder('WondersharePlayer')
        else:
            alert('android')
    elif op == 21:
        if platform() == 'linux':
            copy2folder('VLC(Linux)')
        else:
            alert('linux')
    elif op == 21:
        if platform() == 'linux':
            copy2folder('Celluloid(Linux)')
        else:
            alert('linux')

def change_buffer():
    items = ['DEFAULT', 'firetv', 'less than 1GB RAM', 'more than 1GB RAM', 'shield', 'stick', '1GB-RAM(Windows)', '2GB-RAM(Windows)', '3GB-RAM(Windows)', '4GB-RAM(Windows)', '6GB-RAM(Windows)', '8GB-RAM(Windows)', '12GB-RAM(Windows)', '16GB-RAM(Windows)', 'linux', 'Exit']
    op = select_op(name='SELECT BUFFER TYPE BELOW:',items=items)
    if op == 0: 
        copy2folder2('default')
    elif op == 1:
        if platform() == 'android':
            copy2folder2('firetv')
        else:
            alert('android')
    elif op == 2:
        copy2folder2('lessthan1GB')
    elif op == 3:
        copy2folder2('morethan1GB')
    elif op == 4:
        if platform() == 'android':
            copy2folder2('shield')
        else:
            alert('android')            
    elif op == 5:
        if platform() == 'android':
            copy2folder2('stick')
        else:
            alert('android')
    elif op == 6:
        if platform() == 'windows':
            copy2folder2('1GB-RAM(Windows)')
        else:
            alert('windows')
    elif op == 7:
        if platform() == 'windows':
            copy2folder2('2GB-RAM(Windows)')
        else:
            alert('windows')
    elif op == 8:
        if platform() == 'windows':
            copy2folder2('3GB-RAM(Windows)')
        else:
            alert('windows')
    elif op == 9:
        if platform() == 'windows':
            copy2folder2('4GB-RAM(Windows)')
        else:
            alert('windows')
    elif op == 10:
        if platform() == 'windows':
            copy2folder2('6GB-RAM(Windows)')
        else:
            alert('windows')
    elif op == 11:
        if platform() == 'windows':
            copy2folder2('8GB-RAM(Windows)')
        else:
            alert('windows')
    elif op == 12:
        if platform() == 'windows':
            copy2folder2('12GB-RAM(Windows)')
        else:
            alert('windows')
    elif op == 13:
        if platform() == 'windows':
            copy2folder2('16GB-RAM(Windows)')
        else:
            alert('windows')
    elif op == 14:            
        if platform() == 'linux':
            copy2folder2('linux')
        else:
            alert('linux')                                                                                       



def options():
    items = ['Change Player', 'Optimize Buffer', 'Exit']
    op = select_op(name='SELECT A MENU BELOW:',items=items)
    if op == 0: 
        change_player()
    elif op == 1: 
        change_buffer()        

if __name__ == '__main__': options()