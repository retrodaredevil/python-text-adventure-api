from typing import List, Optional

from ninjagame.data import EventsObject
from ninjagame.entites import OtherPerson, LauraPerson, NinjaDude, PlayerFriend

from ninjagame.items import Sword, SwordType
from textadventure.handler import Handler
from textadventure.input import InputHandler
from textadventure.input import InputObject, InputHandle, InputHandleType
from textadventure.item import Item
from textadventure.items import Wallet, Coin, CoinType
from textadventure.location import Location, GoAction
from textadventure.message import Message, MessageType
from textadventure.player import Player
from textadventure.utils import is_string_true, Point, SOUTH, EAST, WEST, NORTH, UP, DOWN, DIRECTIONS, CanDo


"""
Don't be scared by the size of this file, each location has a few abstract methods that must be implemented, and \
    each method may be very short or a bit long (ex: The go_to_other_location method is long)
"""


DONT_HEAR = "You don't hear anything."
DONT_SMELL = "You don't smell anything."
DONT_TASTE = "You don't taste anything."

# These should not be compared to returned values because these are meant to be more private and constant
CAN_GO_TO_LOCATION: CanDo = (True, "The player was able to change locations.")

CANT_JUMP_LOCATION: CanDo = (False, "You can't jump locations.")
CANT_MOVE_DIRECTION: CanDo = (False, "There's no noticeable opening in this direction.")
# we don't have a CANT_MOVE_NOW because many locations will want to give custom reasons
CANT_PASS: CanDo = (False, "You cannot pass.")

LEAVING_LOCATION: str = "You are leaving '{}'."


def create_leave_message(location: Location) -> Message:
    return Message(LEAVING_LOCATION, named_variables=[location])


class NameTaker(InputHandler):
    def __init__(self, player: Player):
        self.current_name = None
        self.current_friend_name = None
        self.player: Player = player

        message = "Oh hey! You've just accepted to start your journey too! I just did too. Wait, what's you name again?"
        player[PlayerFriend].tell(player, message)

    def on_input(self, handler: Handler, player: Player, player_input: InputObject) -> Optional[InputHandle]:
        if player != self.player:
            return None

        def handle_function(already_handled: List[InputHandleType]):
            if not self._should_handle_input(already_handled):
                raise Exception("NameTaker is the number one priority! What happened?")
            split = player_input.get_split()
            if len(split) > 1:
                player[PlayerFriend].tell(player, "Hey, I can't remember that many words!")
                return InputHandleType.INCORRECT_RESPONSE

            friend = player[PlayerFriend]
            if player.name is not None:  # all for the friend's name
                if self.current_friend_name is None:
                    self.current_friend_name = split[0]
                    friend.tell(player, Message("I'm {}, right? (y/n)", named_variables=[self.current_friend_name]))
                    return InputHandleType.HANDLED
                if is_string_true(split[0]):
                    friend.name = self.current_friend_name
                    friend.tell(player, "Ok, right.")
                    player.send_wait(0.5)
                    friend.tell(player, Message("I'm {}.", named_variables=[friend]))
                    friend.tell(player, "Welp... I guess I'll smell you later. I'm off on my journey!")
                    friend.tell(player, "If you get stuck, use the help command and try to use all of your senses.")
                    return InputHandleType.REMOVE_HANDLER
                friend.tell(player, "It's not? Gosh, just tell me my name.")
                self.current_friend_name = None
                return InputHandleType.HANDLED
            # stuff below is for the player's name (think like an else statement from cuz it returns above)
            if self.current_name is None:
                self.current_name = split[0]
                player[PlayerFriend].tell(player, Message("Are you sure your name is {}? (y/n)",
                                                          named_variables=[self.current_name]))
                return InputHandleType.HANDLED
            if is_string_true(split[0]):
                player.name = self.current_name
                friend.tell(player, Message("Right! {}... I remember now", named_variables=[player]))
                friend.tell(player, "Wait... I can't remember my name. What's my name?")

                return InputHandleType.HANDLED
            friend.tell(player, "Oops. I guess I didn't hear it right. What is it?")
            self.current_name = None  # reset
            return InputHandleType.HANDLED

        return InputHandle(2, handle_function, self)


class Entrance(Location):  # players should only be in this location when starting the ninjagame

    FEEL_MESSAGE = "You feel your clothes on your back and a nice Autumn day."

    def __init__(self):
        super(Entrance, self).__init__("Entrance to the Trail",
                                       "An interesting area that has a large door that goes into the trail.",
                                       Point(0, 0))

    def on_enter(self, player, previous_location: 'Location', handler: Handler):
        if previous_location is None:
            player.send_message("Welcome to the entrance to The Trail.")
            player.send_wait(0.3)
            player.send_message("Would you like to start your journey on this trail?")

    def on_input(self, handler: Handler, player: Player, player_input: InputObject):
        if not self._should_take_input(handler, player, player_input):
            return None

        def handle_function(already_handled: List[InputHandleType]):
            if not self._should_handle_input(already_handled):
                return InputHandleType.NOT_HANDLED

            if "n" in player_input.string_input:
                player.send_message("What? Are you sure?")
            else:
                player.send_message("OK, that's great")
                player.send_message("The door opens with a loud creek...")
                player.send_wait(0.5)
                player.send_message(Message("ERrreeeek", MessageType.TYPE_SLOW))
                player.send_wait(0.5)
                player.send_message("You walk in...")
                player.send_wait(1)
                player.send_message(Message("BOOOOOOM", MessageType.TYPE_SLOW))
                player.send_message("The door has closed behind you")

                player.location = handler.get_location(InsideEntrance)
                player.location.on_enter(player, self, handler)

                player.send_wait(1.3)
                handler.input_handlers.append(NameTaker(player))
            return InputHandleType.HANDLED

        return InputHandle(10, handle_function, self)

    def feel(self, handler: Handler, player: Player):
        player.send_message(self.__class__.FEEL_MESSAGE)

    def listen(self, handler: Handler, player: Player):
        player.send_message("You hear birds chirping and the occasional car go by.")

    def see(self, handler: Handler, player: Player):
        player.send_message("You see two large double doors." +
                            " Maybe you can start your journey if you stopped typing commands and just said 'yeah'.")

    def smell(self, handler: Handler, player: Player):
        player.send_message("You smell leaves around you and the Autumn smell")

    def taste(self, handler: Handler, player: Player):
        player.send_message("You taste bugs inside your mouth. JK JK. Just say you want to start your journey already!")

    def go_to_other_location(self, handler: Handler, new_location, direction: Point, player: Player) -> CanDo:
        return (False, "Well, I see a player who's trying to go to another location. Just say that you "
                       "want to start your journey already.")


class InsideEntrance(Location):
    def __init__(self):
        super(InsideEntrance, self).__init__("Inside the Entrance to the Trail",
                                             "There are double doors and lots of trees",
                                             Point(0, 1))

    def on_enter(self, player: Player, previous_location: 'Location', handler: Handler):
        player.send_message(
            "You now see a very long trail ahead of you. You see forests on both sides and double doors behind you.")
        player.send_line()

    def on_input(self, handler: Handler, player: Player, player_input: InputObject):
        return None

    def feel(self, handler: Handler, player: Player):
        player.send_message(Entrance.FEEL_MESSAGE)

    def listen(self, handler: Handler, player: Player):
        player.send_message(DONT_HEAR)

    def see(self, handler: Handler, player: Player):
        player.send_message("You see double doors behind you and openings all around you.")

    def smell(self, handler: Handler, player: Player):
        player.send_message(DONT_SMELL)

    def taste(self, handler: Handler, player: Player):
        player.send_message(DONT_TASTE)

    def go_to_other_location(self, handler: Handler, new_location, direction: Point, player: Player) -> CanDo:
        if new_location is None:
            return CANT_MOVE_DIRECTION
        # debug("point: {}".format(str(direction)))
        if direction == SOUTH:
            return False, "The double doors won't open."
        elif direction == EAST:
            # done
            pass
        elif direction == WEST:
            # DONE go west to (-1, 1) -> Get sword from Laura
            pass
        elif direction == NORTH:
            # DONE go north to entrance of spider web forest
            pass
        elif direction == UP or direction == DOWN:
            return CANT_MOVE_DIRECTION
        else:
            return CANT_JUMP_LOCATION
        # player.send_message(create_leave_message(self)) < original code which was moved into GoAction's _do_action
        #
        # previous_location = player.location  # I know this is self, but shut up. I've already done this for 4 of these
        # player.location = new_location
        #
        # player.location.on_enter(player, previous_location, handler)
        action = GoAction(player, player.location, new_location, create_leave_message(self))
        action.can_do = CAN_GO_TO_LOCATION
        handler.do_action(action)
        return action.try_action(handler)


class EastInsideEntrance(Location):  # where the furry monster is/was

    def __init__(self):
        super().__init__("East Inside Entrance",
                         "There just enough light peeking through the trees to see.",
                         Point(1, 1))

    def on_enter(self, player: Player, previous_location: 'Location', handler: Handler):
        self.send_welcome(player)
        if not player[EventsObject].been_introduced_to_furry:
            player.send_message("You hear screaming.")
            player.send_wait(0.3)
            player[PlayerFriend].tell(player, "H-Help me! This furry monster is chasing me!")
            player[PlayerFriend].tell(player,
                                      "Take my wallet! It's on the ground! Maybe you can distract it!")
            wallet = Wallet()
            penny = Coin(CoinType.PENNY)
            wallet.change_holder(None, player.location)
            penny.change_holder(None, wallet)

    def go_to_other_location(self, handler: Handler, new_location, direction: Point, player: Player) -> CanDo:
        if not player[EventsObject].been_introduced_to_furry:
            return False, "You should probably try to save your friend."
        if new_location is None:
            return CANT_MOVE_DIRECTION

        if direction == WEST:
            action = GoAction(player, player.location, new_location, create_leave_message(self))
            action.can_do = CAN_GO_TO_LOCATION
            handler.do_action(action)
            return action.try_action(handler)
        elif direction in DIRECTIONS:
            return CANT_MOVE_DIRECTION
        return CANT_JUMP_LOCATION

    def on_take(self, handler: Handler, item: Item):
        if not isinstance(item.holder, Player):
            return
        player: Player = item.holder
        if isinstance(item, Wallet):
            if player[EventsObject].been_introduced_to_furry:
                handler.get_livings(OtherPerson, 1)[0].tell(player, "Hey that's not yours!")
                player.send_message("You set the wallet back on the ground.")
                player.items.remove(item)
                item.change_holder(player, player.location)
                return
            friend = player[PlayerFriend]
            player[EventsObject].been_introduced_to_furry = True  # has now been introduced
            player.send_message(Message("You throw all of {}'s cash at the furry monster.",
                                        named_variables=[friend]))
            player.send_wait(0.2)
            player.send_message("The furry monster fainted. You ga-")
            friend.tell(player, "THANK YOU, THANK YOU!!! You just saved my life from the furry monster!")
            friend.tell(player, "You can keep my wallet. It doesn't have much left anyway.")
            friend.tell(player, "Oh, and I met this really awesome person. If you go west past the double doors,"
                                " you'll find her.")
            player.send_wait(0.5)
            friend.tell(player,
                        "She's pretty shy so you can use the yell command to yell out to her.")
            friend.tell(player, "Well, 'shy' isn't really the word. Good luck.")

    def see(self, handler: Handler, player: Player):
        if player[EventsObject].been_introduced_to_furry:
            player.send_message("You see nothing. There is just enough light to move around.")
        else:
            player.send_message("You see your friend being chased by a furry monster.")

    def listen(self, handler: Handler, player: Player):
        if player[EventsObject].been_introduced_to_furry:
            player.send_message(DONT_HEAR)
        else:
            player.send_message("You hear your friend screaming.")

    def feel(self, handler: Handler, player: Player):
        if player[EventsObject].been_introduced_to_furry:
            player.send_message("You remember the moment you met the furry monster.")
        else:
            player.send_message("You feel scared. You should probably do something about the furry monster")

    def taste(self, handler: Handler, player: Player):
        player.send_message(DONT_TASTE)

    def smell(self, handler: Handler, player: Player):
        player.send_message(DONT_SMELL)

    def on_input(self, handler: Handler, player: Player, player_input: InputObject):
        return None


class WestInsideEntrance(Location):  # introduce Laura

    def __init__(self):
        super().__init__("West of Inside the Entrance",
                         "Lots of trees around with the only exit going back to the double doors.",
                         Point(-1, 1))

    def on_enter(self, player: Player, previous_location: 'Location', handler: Handler):
        self.send_welcome(player)

    def go_to_other_location(self, handler: Handler, new_location, direction: Point, player: Player):
        if new_location is None:
            return CANT_MOVE_DIRECTION

        if direction == EAST:
            pass
        elif direction in DIRECTIONS:
            return CANT_MOVE_DIRECTION
        else:
            return CANT_JUMP_LOCATION

        action = GoAction(player, player.location, new_location, create_leave_message(self))
        action.can_do = CAN_GO_TO_LOCATION
        handler.do_action(action)
        return action.try_action(handler)

    def see(self, handler: Handler, player: Player):
        player.send_message("You see lots of trees and an exit back to the double doors")

    def listen(self, handler: Handler, player: Player):  # test
        if player[EventsObject].knows_laura or not player[EventsObject].been_introduced_to_furry:
            player.send_message(DONT_HEAR)
        else:
            player.send_message("You hear someone in the bushes. Maybe you can yell out to them.")

    def feel(self, handler: Handler, player: Player):
        player.send_message("You feel a little bit spooked.")

    def taste(self, handler: Handler, player: Player):
        player.send_message(DONT_TASTE)

    def smell(self, handler: Handler, player: Player):
        player.send_message(DONT_SMELL)

    def on_input(self, handler: Handler, player: Player, player_input: InputObject) -> Optional[InputHandle]:
        return None

    def on_yell(self, handler: Handler, player: Player, player_input: InputObject, is_there_response=False):
        if player[EventsObject].knows_laura:
            super().on_yell(handler, player, player_input, False)
        else:
            super().on_yell(handler, player, player_input, True)
            player.send_message("You feel a hand go over your mouth.")
            player.send_message("You see a rock coming at your fa-")
            player.clear_screen()
            player.send_wait(1)
            laura = handler.get_livings(LauraPerson, 1)[0]
            laura.tell(player, "Who are you?")
            player.send_wait(0.5)
            laura.tell(player, Message("You have {}'s wallet! What did you do to them?",
                                       named_variables=[player[PlayerFriend]]))
            player.send_wait(0.3)
            player.tell(player, "He's my fri-")
            laura.tell(player, "Lies!")
            player.send_wait(0.7)
            player.clear_screen()
            player.send_wait(1)
            laura.tell(player, Message("Hi I'm {}. Sorry about that. Everything is cleared up now.",
                                       named_variables=[laura]))
            player[EventsObject].knows_laura = True
            sword = Sword(SwordType.WOODEN)
            sword.change_holder(None, player.location)
            laura.tell(player, Message("How about for all your troubles I'll give you this {}. Take it.",
                                       named_variables=[sword]))
            Sword(SwordType.CHINESE_STEEL).change_holder(None, player.location)


class EntranceSpiderWebForest(Location):
    def __init__(self):
        super().__init__("Entrance to Spider Web Forest",
                         "There are lots of spider webs around. No spiders though.",
                         Point(0, 2))

    def on_enter(self, player: Player, previous_location: 'Location', handler: Handler):
        self.send_welcome(player)
        if not player[EventsObject].been_introduced_to_furry:
            player.send_message("You hear your friend off in the distance screaming. "
                                "It's coming from the east of the double doors")

    def go_to_other_location(self, handler: Handler, new_location, direction: Point, player: Player) -> CanDo:
        if new_location is None:
            return CANT_MOVE_DIRECTION

        if direction == SOUTH:
            pass  # back to entrance/double doors
        elif direction == NORTH:
            # Going through, so check if the player has cleared the spider webs
            if not player[EventsObject].has_cleared_spider_webs_at_entrance:
                return False, "You can't get through, there are too many spider webs."
            pass
        elif direction in DIRECTIONS:
            return CANT_MOVE_DIRECTION
        else:
            return CANT_JUMP_LOCATION

        action = GoAction(player, player.location, new_location, create_leave_message(self))
        action.can_do = CAN_GO_TO_LOCATION
        handler.do_action(action)
        return action.try_action(handler)

    def on_item_use(self, handler: Handler, player: Player, item: Item):
        if isinstance(item, Sword):
            self.do_player_clear(player)
        else:
            super().on_item_use(handler, player, item)

    @staticmethod
    def do_player_clear(player: Player):
        if player[EventsObject].has_cleared_spider_webs_at_entrance:
            player.send_message("You've already cleared the spider webs")
        else:
            player.send_message("You used your sword to clear the spider webs")
            player[EventsObject].has_cleared_spider_webs_at_entrance = True

    def on_input(self, handler: Handler, player: Player, player_input: InputObject):
        return None

    def see(self, handler: Handler, player: Player):
        if player[EventsObject].has_cleared_spider_webs_at_entrance:
            player.send_message("You see a lot of spider webs and an entrance north and south.")
        else:
            player.send_message("You see a lot of spider webs. It doesn't look passable.")

    def listen(self, handler: Handler, player: Player):
        player.send_message("Silence. Kinda spooky.")

    def feel(self, handler: Handler, player: Player):
        player.send_message("You feel that it's cooler here than at the entrance.")

    def taste(self, handler: Handler, player: Player):
        player.send_message(DONT_TASTE)

    def smell(self, handler: Handler, player: Player):
        player.send_message(DONT_SMELL)


class CenterSpiderWebForest(Location):
    def __init__(self):
        super().__init__("Center of the Spider Web Forest",
                         "There's an old fountain in the middle that doesn't work and lots of spider webs",
                         Point(0, 3))

    def send_welcome(self, player: Player):
        player.send_line()
        player.send_message(Message("The {}.", named_variables=[self]))
        player.send_message(self.description)
        player.send_line()

    def on_enter(self, player: Player, previous_location: 'Location', handler: Handler):
        self.send_welcome(player)
        events_object = player[EventsObject]
        if not events_object.has_been_in_center_spider_web_forest:
            events_object.has_been_in_center_spider_web_forest = True
            # TODO 

    def listen(self, handler: Handler, player: Player):
        player.send_message("You hear nothing except for the occasional drop of water out of the fountain.")

    def see(self, handler: Handler, player: Player):
        player.send_message("You see an old fountain and a ninja dude ")

    def smell(self, handler: Handler, player: Player):
        player.send_message("You smell BO. It's yours!")

    def feel(self, handler: Handler, player: Player):
        player.send_message("You feel glad you've made it this far.")

    def taste(self, handler: Handler, player: Player):
        player.send_message(DONT_TASTE)

    def on_input(self, handler: Handler, player: Player, player_input: InputObject):
        return None

    def go_to_other_location(self, handler: Handler, new_location, direction: 'Point', player: Player):
        if new_location is None:
            return CANT_MOVE_DIRECTION

        if direction == SOUTH:
            pass
        elif direction == EAST:
            pass
        elif direction == WEST:
            pass
        elif direction == NORTH:
            ninja = handler.get_livings(NinjaDude, 1)[0]
            ninja.tell(player, "You want to pass huh? The king doesn't like to be disturbed.")
            ninja.tell(player, "Wait, are you looking to face me? Ha ha ha... Yeah not gonna happen.")
            ninja.tell(player, "If you want to pass hear, you should at least have all shiny steel armor "
                               "and some decent weaponry.")
            return CANT_PASS
        elif direction in DIRECTIONS:
            return CANT_MOVE_DIRECTION
        else:
            return CANT_JUMP_LOCATION

        action = GoAction(player, player.location, new_location, create_leave_message(self))
        action.can_do = CAN_GO_TO_LOCATION
        handler.do_action(action)
        return action.try_action(handler)


class EastCenterSpiderWebForest(Location):

    def __init__(self):
        super().__init__("East of the Center of the Spider Web Forest",
                         "A nice big field with trees all around. You can see the exit to the fountain.",
                         Point(1, 3))

    def on_input(self, handler: Handler, player: Player, player_input: InputObject):
        return None

    def listen(self, handler: Handler, player: Player):
        pass  # TODO

