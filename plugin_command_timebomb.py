#
#  This file is part of Magnet2.
#  Copyright (c) 2011  Grom PE
#
#  Magnet2 is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  Magnet2 is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with Magnet2.  If not, see <http://www.gnu.org/licenses/>.
#
import random, time
from magnet_api import *
from magnet_utils import *

WIRE_COLORS = ("czerwony", "pomaranczowy", "zolty", "zielony", "niebieski", "indygo",
  "fioletowy", "czarny", "bialy", "szary", "helupa", "rozowy", "pedalski", "lososiowy",
  "wodny", "sraki", "mietowy", "pawi", "fuksja", "zloty",
  "kebabowy", "khaki", "gin", "limonka", "magenta", "jasnawy", "ciemnawy",
  "oliwkowy", "śliwkowy", "łyzeczkowy", "wieczorny", "ogniowy", "turkus")

lastbombed = {}
timebombed = {}

def timer_timebomb(bot, arg):
  for room in timebombed.keys():
    if time.time() >= timebombed[room]['time']:
      nick = timebombed[room]['nick']
      if bot.in_roster(room, nick):
        if timebombed[room]['dud']:
          bot.send_room_message(room,
            "%s Pechowiec! Bombka się nie władowała!"%(nick))
        else:
          bot.send_room_message(room,
            "%s Nie zdąrzył zarzucić! Faza go rozjebała!"%(nick))
      else:
        if timebombed[room]['dud']:
          bot.send_room_message(room,
            "Wygląda na to, ze %s znow lamusiarsko odmawia fazy."%(nick))
        else:
          bot.send_room_message(room,
            "Słyszysz jak %s dolewa resztki giebela łkając cichutko"%(nick))
      del timebombed[room]

timebomb_timer = TimedEventHandler(timer_timebomb, 2)

def event_nick_changed(bot, (presence, room, nick, newnick)):
  # bug/feature: reattaching the bomb to different person if original
  # has left and someone else changed their nick to timebombed person
  if room in timebombed and nick == timebombed[room]['nick']:
    timebombed[room]['nick'] = newnick

def command_timebomb(bot, room, nick, access_level, parameters, message):
  if not parameters: return 'Target expected.'
  if message.getType() != 'groupchat':
    return 'Sprytnie w pizde! Ale dziala tylko gdy wszyscy wiedza'
  if room in timebombed:
    if nick == timebombed[room]['nick']:
      return 'Zajmij sie wpierw soba i swoimi kablami cpaku '
    return ' Jedna bomba jeden cpunix '
  target = parameters
  if target[-1] == ' ': target = target[0:-1]
  if target == bot.self_nick[room]:
    return "Nawet tego nie odpierdalaj.."
  if target == nick:
    return 'Zapomnij! Pomoge Ci sie zabic, Ty sobie spokojnie bedziesz lezal i gnil a mnie rozmontuja? Zapomnij!'
  if not bot.in_roster(room, target):
    return "Prawdopodobnie %s sie odcial i nic nie widzi."%(target)
  if room in lastbombed and target in lastbombed[room]:
    return 'Podziel dragi i daj mu odetchnac przed nastepna faza !'

  bombtimer = random.randint(15, 60)
  bombtime = time.time() + bombtimer

  bombwires = []
  for i in range(random.randint(2, 8)):
    bombwires.append(random.choice(WIRE_COLORS))

  lastbombed[room] = target
  timebombed[room] = {
    'nick': target,
    'dud': random.getrandbits(1),
    'time': bombtime,
    'wires': bombwires
  }
  return (
    "/me wrzucil towar %s's do kieszeni. Towar straci swa moc za %d sekund.\r\n"+
    "Zmien swoj stan walac towiec w odpowiedni kabel(!cutwire color).\r\n"+
    "Masz do wyboru %d kolorowych kabli gotowych do przyjecia: %s."
  )%(target, bombtimer, len(bombwires), ', '.join(bombwires))


def command_cutwire(bot, room, nick, access_level, parameters, message):
  if not room in timebombed:
    return 'Przestan cpac tu nikt nie ma bomby.'
  if not parameters: return 'Color expected.'
  if message.getType() != 'groupchat':
    return 'Sprytnie w chuj! Ale dziala tylko jak widza wszyscy'
  if nick != timebombed[room]['nick']:
    return '%s zaraz wyrwie z papci!'%(timebombed[room]['nick'])
  wire = parameters.lower()
  if wire[-1] == ' ': wire = wire[0:-1]
  if wire in timebombed[room]['wires']:
    timebombed[room]['wires'].remove(wire)

    result = random.randint(1, 3)
    if not timebombed[room]['wires']: result = 2
    if result == 1:
      return " Tym kablem nie wejdzie!"
    elif result == 2:
      timeleft = timebombed[room]['time']-time.time()
      if timeleft > 2:
        res = "Hahah! Zbiłeś sobie banie %d sekund przed jej wejsciem !"%(timeleft)
      else:
        res = " W ostatnim momencie pozbawiles sie dobrej bani "
      del timebombed[room]
      return res
    else:
      del timebombed[room]
      return "Zly kabel! Rozjebales se serce!"
  else:
    return 'Nie ma "%s" kabla ktorego szukasz !'%(wire)

def command_defuse(bot, room, nick, access_level, parameters, message):
  if not room in timebombed:
    return 'Przestan cpac tu nikt nie ma bomby.'
  del timebombed[room]
  return 'Yebac admina yebac!'

def load(bot):
  bot.add_command('timebomb', command_timebomb, LEVEL_GUEST, 'timebomb')
  bot.add_command('cutwire', command_cutwire, LEVEL_GUEST, 'timebomb')
  bot.add_command('defuse', command_defuse, LEVEL_ADMIN, 'timebomb')
  bot.timed_events.add(timebomb_timer)

def unload(bot):
  bot.timed_events.remove(timebomb_timer)

def info(bot):
  return 'Timebomb plugin v1.0.1'
