import random
import argparse
import os
import re
import time

thingstring = 'aggiimmt'
INVALID_INPUT_MESSAGE = 'Invalid input.'
DEATH_MESSAGE = 'YOU DIED. SCORE 0'
DICE_NOTATION = re.compile(r'(\d+)d(\d+)(kh|kl)?(\d+)?')
TREASURE_TABLE = ['scroll of smiting', 'scroll of seeing', 'scroll of charming', 'healing potion', 'power potion',
                  'invisibility potion']
MUNDANE_TABLE = ['torch', 'torch', 'torch', 'sword', 'shield']

MONSTER_NAMES = ['ai', 'ei', 'ar', 'ou', 'no', 'na', 'ra', 'ta', 'th', 'iu', 'ou', 'ga', 'ka','ma', ' ']


def roll(dice_string) -> int:
    dice_string = str(dice_string)
    # Selectively find and replace all instances of dice notation e.g. 3d6 or 2d6kh1
    found_string = DICE_NOTATION.finditer(dice_string)
    for dice in found_string:
        curr = [int(dice.group(1)), int(dice.group(2)), dice.group(3), dice.group(4)] # xdy kh/kl n
        result_list = [random.randint(1, curr[1]) for _ in range(curr[0])]
        if curr[2] == 'kh':
            if curr[3]:
                result_list = sorted(result_list, reverse=True)[0:int(curr[3])]
            else:
                result_list = sorted(result_list, reverse=True)[0:1]
        elif curr[2] == 'kl':
            if curr[3]:
                result_list = sorted(result_list)[0:int(curr[3])]
            else:
                result_list = sorted(result_list)[0:1]
        dice_string = dice_string.replace(dice.group(0), str(sum(result_list)))
    return eval(dice_string)


def generate_new_level(curr_depth):
    level_rooms = roll('2d6')+curr_depth
    curr_level = []
    for i in range(level_rooms):
        curr_room = []
        objects_in_room = roll('1d10')
        for j in range(objects_in_room):
            object_type = random.choice(thingstring)
            curr_room.append(object_type)
        curr_level.append(curr_room)
    return curr_level


def run_fight(player):
    mon_hp = roll(f'{max(round(player["level"]/5),1)}d6')+player['level']
    mon_atk = roll('1d6')+player['level']
    mon_name = ''
    for _ in range(roll('1d6')):
        mon_name += random.choice(MONSTER_NAMES)
    print(f'You are fighting {mon_name}.')
    while True:
        dam = roll('1d6') + player['power'] + player['level']
        print(f'You deal {dam} damage to {mon_name}!')
        mon_hp -= dam
        if mon_hp <= 0:
            print(f'{mon_name} dies!')
            break
        mdam = roll('1d6') + mon_atk
        print(f'{mon_name} deals {mdam} damage to you!')
        player['hp'] -= dam
        if player['hp'] <= 0:
            print(DEATH_MESSAGE)
            exit()
    return player


def score_calc(player):
    score = player['gold']
    for item in player['items']:
        first_part = '\t'.join(item.split('\t')[:-1])
        if first_part in MUNDANE_TABLE:
            score += 1
        elif first_part in TREASURE_TABLE:
            score += 10


def check_exists(array, thing):
    for obj in array:
        if '\t'.join(obj.split('\t')[:-1]) == thing:
            return True
    return False


def modify_array(array, thing, amt):
    narray = []
    added = True
    for obj in array:
        if '\t'.join(obj.split('\t')[:-1]) == thing:
            namt = int(obj.split('\t')[-1])+amt
            if namt > 0:
                narray.append('\t'.join(obj.split('\t')[:-1])+'\t'+str(namt))
        else:
            narray.append(obj)
    if not added and amt > 0:
        narray.append(thing+'\t'+amt)
    return narray


def use_item(curr_room, player, item, amt):
    if item == 'torch':
        player['effects'] = modify_array(player['effects'], 'light', 5 * amt)
    elif item == 'scroll of smiting' or item == 'scroll of charming':
        for _ in range(amt):
            curr_room.remove('m')
    elif item == 'scroll of seeing':
        for _ in range(amt):
            print(''.join(curr_room))
    elif item == 'healing potion':
        for _ in range(amt):
            player['hp'] += roll('1d6')
    elif item == 'power potion':
        for _ in range(amt):
            player['power'] += 1
    elif item == 'invisibility potion':
        player['effects'] = modify_array(player['effects'], 'invisibility', 3 * amt)
    return curr_room, player


def main(verbose_mode):
    player = {'hp': 10, 'power': 0, 'level': 1, 'gold': 0,
              'items': ['torch\t3'], 'effects': ['light\t10']}
    while True:
        curr_level = generate_new_level(player['level'])
        curr_room_id = 0
        while True:
            curr_room = curr_level[curr_room_id]
            curr_enc = 0
            done_encs = []
            while True:
                os.system('cls' if os.name == 'nt' else 'clear')
                if not verbose_mode:
                    display_string = f'l{player["level"]}\tr{curr_room_id+1}/{len(curr_level)}\te{curr_enc+1}/{len(curr_room)}\thp{player["hp"]}\tp{player["power"]}\tg{player["gold"]}\n'
                    if check_exists(player['effects'], 'light'):
                        for char in 'agimt':
                            display_string += char+str(curr_room.count(char)-done_encs.count(char))+'\t'
                    else:
                        print('?'+str(len(curr_room)))
                    print(display_string)
                else:
                    print('ROOM CONTENTS:')
                    if check_exists(player['effects'], 'light'):
                        print(f'Altars: {curr_room.count("a")-done_encs.count("a")}')
                        print(f'Gold: {curr_room.count("g")-done_encs.count("g")}')
                        print(f'Monsters: {curr_room.count("m")-done_encs.count("m")}')
                        print(f'Items: {curr_room.count("i")-done_encs.count("i")}')
                        print(f'Traps: {curr_room.count("t")-done_encs.count("t")}')
                    else:
                        print(f'???: {len(curr_room)}')
                    print('\nPLAYER STATUS:')
                    print(f'Current level: {player["level"]}')
                    print(f'Rooms in this level: {curr_room_id+1}/{len(curr_level)}')
                    print(f'Encounters in this room: {curr_enc+1}/{len(curr_room)}')
                    print(f'HP: {player["hp"]}')
                    print(f'POWER: {player["power"]}')
                    print(f'GOLD: {player["gold"]}')
                choice = input('> ').lower()
                if not choice:
                    if curr_enc == len(curr_room):
                        break
                    encounter = curr_room[curr_enc]
                    done_encs.append(encounter)
                    if encounter == 't':
                        print('Trap!')
                        if roll('2d6') < 7:
                            player['hp'] -= roll('1d6')
                            print('You get hit!')
                        else:
                            print('It misses you.')
                    elif encounter == 'g':
                        print('Gold!')
                        player['gold'] += roll('2d6')+player['level']
                        print(f'You now have {player["gold"]} gold.')
                    elif encounter == 'm':
                        print('Monster!')
                        player = run_fight(player)
                    elif encounter == 'a':
                        print('Altar!')
                        while True:
                            pray = input('(Pray y/n)> ').lower()
                            if pray == 'y':
                                if roll('1d100') <= player['level']:
                                    print('A god notices!')
                                    attention = roll('1d6')
                                    if attention == 1:
                                        print('Smote!')
                                        player['hp'] -= roll('1d6')
                                    elif attention == 6:
                                        print('Boon!')
                                        found_item = random.choice(TREASURE_TABLE)
                                        print(f'You are give a {found_item}.')
                                        player['items'] = modify_array(player['items'], found_item, 1)
                            elif pray == 'n':
                                print('You give it a pass.')
                                break
                            else:
                                print(INVALID_INPUT_MESSAGE)
                    elif encounter == 'i':
                        print('Item!')
                        if roll('1d6') == 1:
                            found_item = random.choice(TREASURE_TABLE)
                        else:
                            found_item = random.choice(MUNDANE_TABLE)
                        print(f'It\'s a {found_item}.')
                        player['items'] = modify_array(player['items'], found_item, 1)
                    curr_enc += 1
                    for effect in player['effects']:
                        player['effects'] = modify_array(player['effects'], effect, -1)
                    if player['hp'] <= 0:
                        print(DEATH_MESSAGE)
                        exit()

                elif choice == 'h' or choice == 'help':
                    print('Commands:')
                    print('(nothing): next encounter\nh: display help\nq: exit dungeon (finalise score)\nu: use item\nc: check status')
                    print('Options (use when starting new game from command line):')
                    print('--vb: verbose descriptions\n--seed: starting seed')

                elif choice == 'q':
                    atk_chance = 0
                    for enc in curr_room:
                        if enc == 'm':
                            atk_chance += 10
                    if roll('1d100') < atk_chance:
                        print('A monster caught up!')
                        player = run_fight(player)
                    if player['hp'] <= 0:
                        print(DEATH_MESSAGE)
                        exit()
                    else:
                        print('YOU ESCAPED. SCORE', score_calc(player))
                elif choice == 'u':
                    id = 1
                    for item in player['items']:
                        print('ID\tNAME\tAMT')
                        print(str(id)+'\t'+item)
                    while True:
                        item_choice = input(f'(1-{id} OR q)>')
                        if item_choice == 'q':
                            break
                        else:
                            try:
                                item_choice = item_choice.split(' ')
                                item_code = int(item_choice[0])
                                if len(item_choice) > 1:
                                    item_amt = int(item_choice[1])
                                else:
                                    item_amt = 1
                                target_item = player['items'][item_code-1]
                                player['items'] = modify_array(player['items'], target_item, item_amt)
                                curr_room, player = use_item(curr_room, player, target_item, item_amt)
                            except ValueError:
                                print(INVALID_INPUT_MESSAGE)
                elif choice == 'c':
                    print('EFFECT\tLENGTH')
                    for effect in player['effects']:
                        print(effect)
                input('<Press ENTER to continue>')

            curr_room_id += 1
            if curr_room_id == len(curr_level):
                break
        player['level'] += 1
        print('You descend...')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Dimly-lit dungeons, deep delving dooms.')
    parser.add_argument('--seed', type=str, help='Seed for the game.', default='')
    parser.add_argument('--verbose', '--vb', help='Verbose mode.', action='store_true', default=False)
    args = parser.parse_args()
    if args.seed:
        random.seed(args.seed)
    print('===DROGUE v0.5===')
    print('By UtilityHotbar')
    print('Enter h for help.')
    print('Remember: You only get a score if you escape alive!')
    input('<Press ENTER to start>')
    main(args.verbose)
