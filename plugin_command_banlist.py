import xmpp
from magnet_api import *
from magnet_utils import *
import textwrap
 
wait_banlist = {}
 
def command_banlist(bot, room, nick, access_level, parameters, message):
  iq = xmpp.Iq('get', xmpp.NS_MUC_ADMIN, {}, room)
  item = iq.getTag('query').setTag('item')
  item.setAttr('affiliation', 'outcast')
  wait_banlist[bot.client.send(iq)] = message.getFrom()
 
def command_unban(bot, room, nick, access_level, parameters, message):
  if parameters == '': return "Expected <target jid>"
  (target, reason) = separate_target_reason(bot, room, parameters)
  iq = xmpp.Iq('set', xmpp.NS_MUC_ADMIN, {}, room)
  item = iq.getTag('query').setTag('item')
  item.setAttr('affiliation', 'none')
  item.setAttr('jid', target)
  bot.client.send(iq)
 
def event_room_iq(bot, (iq, room, nick)):
  if iq.getID() in wait_banlist:
    target = wait_banlist[iq.getID()]
    output = 'Banned users: %s.'%(', '.join(sorted(["'%s'"%(x.getAttr('jid')) for x in iq.getQueryChildren()])))
    for out in textwrap.wrap(output, 1000):
      bot.send_room_message(str(target), out)
 
def load(bot):
  bot.add_command('banlist', command_banlist, LEVEL_ADMIN)
  bot.add_command('unban', command_unban, LEVEL_ADMIN)
 
def unload(bot):
  pass
 
def info(bot):
  return 'Banlist plugin v1.0.0'
