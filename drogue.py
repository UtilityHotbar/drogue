import random
import argparse
import os
import re


thingstring = 'agiiimmt'
INVALID_INPUT_MESSAGE = 'Invalid input.'
DEATH_MESSAGE = 'YOU DIED. SCORE 0'
CONTINUE_MESSAGE = '<Press ENTER to continue>'
DICE_NOTATION = re.compile(r'(\d+)d(\d+)(kh|kl)?(\d+)?')
TREASURE_TABLE = ['scroll of smiting', 'scroll of seeing', 'scroll of charming', 'healing potion', 'power potion',
                  'invisibility potion', 'scroll of fireball', 'holy water']
MUNDANE_TABLE = ['torch', 'torch', 'torch', 'food', 'food', 'sword', 'shield', 'oil']
SPECIAL_TABLE = ['scroll of smiting', 'scroll of charming', 'scroll of fireball', 'holy water', 'oil']
SELF_TABLE = ['healing potion', 'power potion', 'invisibility potion',]

MONSTER_NAMES = ['ai', 'ei', 'ar', 'ou', 'po', 'no', 'ne', 'ra', 'ta', 'th', 'ch', 'iu', 'ou', 'ga', 'ka', 'ma', 'pa']


def get_tab_split(obj, get_last=False):
    if get_last:
        return '\t'.join(obj.split('\t')[-1])
    return '\t'.join(obj.split('\t')[:-1])


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


def reduce_effects(player):
    for effect in player['effects']:
        effect_name = get_tab_split(effect)
        player['effects'] = modify_array(player['effects'], effect_name, -1)
    if not check_exists(player['effects'], 'saturation'):
        print('You are hungry!')
        player['hp'] -= 1
    if check_exists(player['effects'], 'poison'):
        player['hp'] -= 1
    if player['hp'] <= 0:
        print(DEATH_MESSAGE)
        exit()
    return player


def run_fight(player):
    if check_exists(player['effects'], 'invisibility'):
        print('Invisible, you sneak by!')
        return player
    mon_hp = roll(f'{max(round(player["level"]/5),1)}d6')+player['level']
    mon_atk = roll('1d6')+player['level']
    mon_name = ''
    for _ in range(roll('1d6')):
        mon_name += random.choice(MONSTER_NAMES)
    print(f'You encounter {mon_name}.\n[F]ight, [R]un, or [U]se item?')
    while True:
        choice = input('(f/r/u)> ').lower()
        if not choice in 'fru':
            print(INVALID_INPUT_MESSAGE)
        else:
            break
    if choice == 'r':
        if roll('1d6') < 3:
            print('You escape!')
        else:
            print(f'{mon_name} catches up, and it attacks first!')
            player['effects'] = modify_array(player['effects'], 'paralysis', 1)
    elif choice == 'u':
        print('Common combat items are automatically used. You can also use a special item before combat.')
        print('ID\tNAME\tAMT')
        id = 1
        available_items = []
        for item in player['items']:
            item_name = get_tab_split(item)
            if item_name in SPECIAL_TABLE+SELF_TABLE:
                print(str(id)+'\t'+item)
                available_items.append(item_name)
                id += 1
        if available_items:
            while True:
                c = input('(ID OR q)> ').lower()
                if c == 'q':
                    break
                try:
                    choice = available_items[int(c)-1]
                    break
                except ValueError:
                    print(INVALID_INPUT_MESSAGE)
            if choice in SELF_TABLE:
                _, player, used = use_item(None, player, choice, 1)
                if used:
                    player['items'] = modify_array(player['items'], choice, -1)
            elif choice in SPECIAL_TABLE:
                if choice == 'scroll of fireball':
                    print('Your fireball scorches the monster!')
                    mon_hp -= roll('4d6')
                    if mon_hp <= 0:
                        print('It dies!')
                        return player
                elif choice == 'scroll of smiting':
                    print('Your missile smites the monster!')
                    mon_hp -= roll('2d6')
                    if mon_hp <= 0:
                        print('It dies!')
                        return player
                elif choice == 'scroll of charming':
                    print('You charm the monster to get past!')
                    return player
                elif choice == 'holy water':
                    if 'ne' in mon_name:
                        print('The holy water repels the undead creature!')
                        return player
                    else:
                        print('The holy water has no effect!')
                elif choice == 'oil':
                    if check_exists(player['effects'], 'light'):
                        print('You light the monster on fire with your torch!')
                        mon_hp -= roll('1d6')
                        if mon_hp <= 0:
                            print('It dies!')
                            return player
                    else:
                        print('You splash oil, but you can\'t light it on fire in the dark...')
        else:
            print('Sorry. You don\'t have any useable items.')

    while True:
        player = reduce_effects(player)
        if not (check_exists(player['effects'], 'charm') or check_exists(player['effects'], 'paralysis')):
            dam = roll('1d6') + player['power'] + player['level']
            if check_exists(player['items'], 'sword'):
                print('You use your sword!')
                dam += roll ('1d6')
                player['items'] = modify_array(player['items'], 'sword', -1)
            print(f'You deal {dam} damage to {mon_name}!')
            mon_hp -= dam
        else:
            print('You can\'t attack this round!')
        if mon_hp <= 0:
            print(f'{mon_name} dies!')
            break
        atkdone = False
        if 'po' in mon_name:
            if roll('1d6') > 3:
                rounds = roll('1d6')
                print(f'{mon_name} poisons you for {rounds} rounds!')
                player['effects'] = modify_array(player['effects'], 'poison', rounds)
                atkdone = True
        elif 'pa' in mon_name:
            if roll('1d6') > 5:
                rounds = roll('1d3')
                print(f'{mon_name} paralyses you for {rounds} rounds!')
                player['effects'] = modify_array(player['effects'], 'paralysis', rounds)
                atkdone = True
        elif 'ch' in mon_name:
            if roll('1d6') > 5:
                rounds = roll('1d6')
                print(f'{mon_name} charms you for {rounds} rounds!')
                player['effects'] = modify_array(player['effects'], 'charm', rounds)
                atkdone = True
        if 'ne' in mon_name:
            print(f'{mon_name}\'s necrotic aura saps life from you!')
            player['hp'] -= roll('1d3')
        if not atkdone:
            mdam = roll('1d6') + mon_atk
            print(f'{mon_name} deals {mdam} damage to you!')
            if check_exists(player['items'], 'shield'):
                print('You use your shield!')
                mdam -= roll('1d6')
                player['items'] = modify_array(player['items'], 'shield', -1)
            player['hp'] -= mdam
        if player['hp'] <= 0:
            print(DEATH_MESSAGE)
            exit()
    player['effects'] = modify_array(player['effects'], 'paralysis', -999)
    player['effects'] = modify_array(player['effects'], 'charm', -999)

    return player


def score_calc(player):
    score = player['gold']+player['level']*10
    for item in player['items']:
        first_part = '\t'.join(item.split('\t')[:-1])
        if first_part in MUNDANE_TABLE:
            score += 1
        elif first_part in TREASURE_TABLE:
            score += 10
    return score


def check_exists(array, thing, amt=None):
    for obj in array:
        if get_tab_split(obj) == thing:
            if not amt:
                return True
            else:
                return int(get_tab_split(obj, get_last=True)) >= amt
    return False


def modify_array(array, thing, amt):
    narray = []
    added = False
    for obj in array:
        if get_tab_split(obj) == thing:
            namt = int(obj.split('\t')[-1])+amt
            if namt > 0:
                narray.append(get_tab_split(obj)+'\t'+str(namt))
            added = True
        else:
            narray.append(obj)
    if not added and amt > 0:
        narray.append(thing+'\t'+str(amt))
    return narray


def use_item(curr_room, player, item, amt):
    if item == 'torch':
        player['effects'] = modify_array(player['effects'], 'light', 5 * amt)
    elif item == 'food':
        player['hp'] += amt
        player['effects'] = modify_array(player['effects'], 'saturation', 15 * amt)
    elif item == 'scroll of smiting' or item == 'scroll of charming':
        for _ in range(amt):
            curr_room.remove('m')
    elif item == 'scroll of seeing':
        for _ in range(amt):
            print(''.join(curr_room))
    elif item == 'scroll of fireball':
        curr_room = []
    elif item == 'healing potion':
        for _ in range(amt):
            player['hp'] += roll('1d6')
    elif item == 'power potion':
        for _ in range(amt):
            player['power'] += 1
    elif item == 'invisibility potion':
        player['effects'] = modify_array(player['effects'], 'invisibility', 3 * amt)
    else:
        return curr_room, player, False
    return curr_room, player, True


def main(verbose_mode):
    player = {'hp': 10, 'power': 0, 'level': 1, 'gold': 0, 'escape_diff': 0,
              'items': ['torch\t3', 'scroll of fireball\t1'], 'effects': ['light\t10', 'saturation\t30']}
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
                        print('?'+str(len(curr_room[curr_enc:])))
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
                        print('You are in darkness!')
                        print(f'???: {len(curr_room[curr_enc:])}')
                    print('\nPLAYER STATUS:')
                    print(f'Current level: {player["level"]}')
                    print(f'Rooms in this level: {curr_room_id+1}/{len(curr_level)}')
                    print(f'Encounters in this room: {curr_enc+1}/{len(curr_room)}')
                    print(f'HP: {player["hp"]}')
                    print(f'POWER: {player["power"]}')
                    print(f'GOLD: {player["gold"]}')
                choice = input('> ').lower()
                if not choice:
                    if curr_enc >= len(curr_room):
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
                                else:
                                    print('Nobody\'s on the other side...')
                                break
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
                    player = reduce_effects(player)

                elif choice == 'h' or choice == 'help':
                    print('Commands:')
                    print('(nothing): next encounter\nr: run to next room\nh: display help\nq: exit dungeon (finalise score)\nu: use item\nc: check status')
                    print('Options (use when starting new game from command line):')
                    print('--vb: verbose descriptions\n--seed: starting seed')

                elif choice == 'r':
                    atk_chance = 0
                    for enc in curr_room:
                        if enc == 'm':
                            atk_chance += 10
                    if roll('1d100') < atk_chance:
                        print('A monster caught up!')
                        player = run_fight(player)
                    player['escape_diff'] += roll('1d6')
                    input(CONTINUE_MESSAGE)
                    break

                elif choice == 'q':
                    atk_chance = player['escape_diff']
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
                        quit()

                elif choice == 'u':
                    id = 1
                    print('ID\tNAME\tAMT')
                    for item in player['items']:
                        print(str(id)+'\t'+item)
                        id += 1
                    while True:
                        item_choice = input(f'(ID OR q)> ').lower()
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
                                target_item = get_tab_split(player['items'][item_code-1])
                                if check_exists(player['items'], target_item, amt=item_amt):
                                    print(f'Using {item_amt} {target_item}.')
                                    curr_room, player, used_item = use_item(curr_room, player, target_item, item_amt)
                                    if used_item:
                                        player['items'] = modify_array(player['items'], target_item, -item_amt)
                                    else:
                                        print('You cannot use that item right now.')
                                    break
                                else:
                                    print('You don\'t have that item or enough of that item.')
                            except ValueError:
                                print(INVALID_INPUT_MESSAGE)
                elif choice == 'c':
                    print('EFFECT\tLENGTH')
                    for effect in player['effects']:
                        print(effect)
                input(CONTINUE_MESSAGE)

            curr_room_id += 1
            if curr_room_id >= len(curr_level):
                break
        player['level'] += 1
        print('You descend...')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Dimly-lit dungeons, deep delving dooms.')
    parser.add_argument('--seed', type=str, help='Seed for the game.', default='')
    parser.add_argument('--verbose', '-vb', help='Verbose mode.', action='store_true', default=False)
    args = parser.parse_args()
    if args.seed:
        random.seed(args.seed)
    print('===DROGUE v0.7===')
    print('By UtilityHotbar')
    print('Enter h for help.')
    print('Remember: You only get a score if you escape alive!')
    input('<Press ENTER to start>')
    main(args.verbose)
