import glob
import urwid


class Room(object):

    def __init__(self, link_id, title, exits, description):
        self.link_id = link_id
        self.title = title
        self.exits = exits
        self.description = description

    @staticmethod
    def validate_and_clean(expected_row_name, unsafe_row):
        expected_row_name_with_syntax = expected_row_name.upper() + ": "
        assert unsafe_row.startswith(expected_row_name_with_syntax)
        row_without_name = unsafe_row.replace(expected_row_name_with_syntax, " ", 1) 
        return row_without_name.strip()
    
    @classmethod
    def from_string(cls, room_string):
        room_file_contents = room_string.split('\n')
        link_id = cls.validate_and_clean("link_id", room_file_contents[0]).lower()
        title = cls.validate_and_clean("title", room_file_contents[1])
        exits = cls.validate_and_clean("exits", room_file_contents[2]).split(",")
        description = '\n'.join(room_file_contents[3:]).strip()

        return cls(link_id, title, exits, description)


class Adventure(object):
    ROOM_NAME_PATTERN = "*.room.txt"

    def __init__(self, rooms):
        self.rooms = rooms
        self.current_room = self.rooms["first_room"]

    @classmethod
    def from_directory(cls, directory):
        rooms = {}

        for room_file_name in glob.glob(directory + '/' + cls.ROOM_NAME_PATTERN):

            with open(room_file_name) as f:
                room_file_string = f.read()
                room = Room.from_string(room_file_string)
                rooms[room.link_id] = room

        return cls(rooms)

    # FIXME: refactor
    def play(self):
        """The main loop and urwid demon magic from hell.

        """

        # URWID STUFF
        def goto_room_or_exit(key):

            # autocomplete
            if key == 'tab':
                
                for exit in self.current_room.exits:
                    exit = exit.lower()
                    edit_text_value = ask_text.edit_text.lower()

                    # first check if is exact same to suggest next
                    if exit == edit_text_value:
                        continue
                    elif exit.startswith(edit_text_value):
                        ask_text.set_edit_text(exit)
                        ask_text.set_edit_pos(len(ask_text.edit_text))

            if not key == 'enter':
                return

            if ask_text.edit_text == 'quit':
                raise urwid.ExitMainLoop()
            elif ask_text.edit_text.lower() in self.rooms:
                self.current_room = self.rooms[ask_text.edit_text.lower()]
                title_text.set_text(self.current_room.title.upper())
                description_text.set_text(self.current_room.description)
                exit_text.set_text("Exits: " + ', '.join(self.current_room.exits))
                ask_text.set_edit_text("")

        palette = [('ask', 'default,bold', 'default', 'bold'),]
        title_text = urwid.Text(self.current_room.title.upper())
        description_text = urwid.Text(self.current_room.description)
        exit_text = urwid.Text("Exits: " + ', '.join(self.current_room.exits))
        ask_text = urwid.Edit(("ask", "Which exit? > "))

        description_filler = urwid.Filler(description_text)
        title_filler = urwid.Filler(title_text, valign="top")
        exit_filler = urwid.Filler(exit_text, valign="bottom")
        ask_filler = urwid.Filler(ask_text, valign="bottom")

        pile = urwid.Pile([title_filler,
                           description_filler,
                           exit_filler,
                           ask_filler])
        # could use this to color input when word match?
        #urwid.connect_signal(ask_text, 'change', goto_room_or_exit)
        loop = urwid.MainLoop(pile, palette, unhandled_input=goto_room_or_exit).run()


adventure = Adventure.from_directory("rooms")
adventure.play()
